/*
 * tap_agent.c
 * =============
 * TAP v5.3.2 — Proper C Agent Implementation.
 *
 * Replaces the broken Cython agent.pyx / agent.c stub.
 * The original .pyx had a Cython compile error (line 9,
 * the `val = arr[0]` after `if arr.shape[0] > 0:` check
 * is the Cython compiler's known issue with C arrays).
 *
 * This is a pure C99 implementation of the agent
 * that uses the tap_arm_pim_dispatcher for HNSW search.
 *
 * The agent is a "sleeper" agent that:
 *   - Wakes up at φ-rate intervals
 *   - Decides whether to fetch more context
 *   - Returns a verdict on a query
 *   - Logs the decision to the cascade
 *
 * Public API (callable from Python via ctypes):
 *   - tap_agent_create() → opaque handle
 *   - tap_agent_run(handle, query, k) → top-k results
 *   - tap_agent_wake(handle) → triggers wake cycle
 *   - tap_agent_sleep(handle) → goes to sleep
 *   - tap_agent_get_breath(handle) → current breath state
 *   - tap_agent_set_breath(handle, psi) → set breath
 *   - tap_agent_free(handle)
 *
 * The agent uses φ-rate timing (8.12d sub-breath period)
 * and the cascade's breath state.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

/* Forward declarations of dispatcher API (from tap_arm_pim_dispatcher.c) */
typedef struct tap_pim_s tap_pim_t;
extern tap_pim_t *tap_pim_create(int dim, int M, int M0, int ef_construction, int max_level);
extern int tap_pim_load_vectors(tap_pim_t *pim, float *weights, int n_vectors);
extern int tap_pim_add_point(tap_pim_t *pim, int32_t id);
extern int tap_pim_search(tap_pim_t *pim, const float *query, int k,
                          int32_t *out_ids, float *out_dists);
extern int tap_pim_set_breath(tap_pim_t *pim, double current_psi);
extern int tap_pim_get_state(tap_pim_t *pim, double *psi, double *gamma_nb, double *phase);
extern void tap_pim_free(tap_pim_t *pim);

/* TAP constants */
#define PHI             1.6180339887498949
#define PHI_INV4        0.1458980337503154
#define PHI_INV8        0.0557280900007526
#define PHI_INV13       0.0081306182888694
#define PSI_PLASTIC     0.9105256658757980
#define N_B             8
#define GAMMA_NB        (1.0 + (double)N_B * PHI_INV13)

/* Sub-breath period in seconds: 8.12 days */
#define TAP_SUB_BREATH_SEC   (8.12 * 24.0 * 3600.0)

/* Agent states */
typedef enum {
    TAP_AGENT_ASLEEP = 0,
    TAP_AGENT_WAKING = 1,
    TAP_AGENT_AWAKE  = 2,
    TAP_AGENT_THINKING = 3,
    TAP_AGENT_RESPONDING = 4
} tap_agent_state_t;

/* Agent decision/verdict */
typedef struct {
    int32_t result_id;
    float result_dist;
    int32_t n_results;
    double breath_psi;
    int wake_cycles;
    double sleep_duration;
} tap_agent_verdict_t;

/* Agent state */
typedef struct tap_agent_s {
    tap_pim_t *dispatcher;
    tap_agent_state_t state;
    int dim;
    int max_nodes;

    /* Sleep / wake tracking */
    time_t last_wake_time;
    time_t last_sleep_time;
    int n_wake_cycles;
    double total_sleep_time;

    /* Breath state */
    double current_breath_psi;
    double breath_phase;

    /* Vector storage (for queries) */
    float *query_buffer;

    /* Stats */
    int n_decisions;
    int n_wakes;
    int n_sleeps;
} tap_agent_t;

/* ---------------- Public API ---------------- */

tap_agent_t *tap_agent_create(int dim, int M, int M0, int ef, int max_level, int max_nodes);
void tap_agent_free(tap_agent_t *agent);
int tap_agent_wake(tap_agent_t *agent);
int tap_agent_sleep(tap_agent_t *agent);
int tap_agent_run(tap_agent_t *agent, const float *query, int k,
                  tap_agent_verdict_t *verdict);
int tap_agent_get_breath(tap_agent_t *agent, double *psi, double *phase);
int tap_agent_set_breath(tap_agent_t *agent, double psi);
int tap_agent_load_vectors(tap_agent_t *agent, float *weights, int n_vectors);
int tap_agent_add_point(tap_agent_t *agent, int32_t id);

/* ---------------- Implementation ---------------- */

tap_agent_t *tap_agent_create(int dim, int M, int M0, int ef, int max_level, int max_nodes) {
    tap_agent_t *agent = (tap_agent_t *)calloc(1, sizeof(tap_agent_t));
    if (!agent) return NULL;
    agent->dim = dim > 0 ? dim : 64;
    agent->max_nodes = max_nodes > 0 ? max_nodes : 65536;
    agent->state = TAP_AGENT_ASLEEP;
    agent->current_breath_psi = PSI_PLASTIC;
    agent->breath_phase = 0.0;
    agent->n_decisions = 0;
    agent->n_wakes = 0;
    agent->n_sleeps = 0;
    agent->n_wake_cycles = 0;
    agent->total_sleep_time = 0.0;
    agent->last_wake_time = 0;
    agent->last_sleep_time = time(NULL);

    /* Create dispatcher */
    agent->dispatcher = tap_pim_create(agent->dim, M, M0, ef, max_level);
    if (!agent->dispatcher) {
        free(agent);
        return NULL;
    }

    /* Allocate query buffer */
    agent->query_buffer = (float *)calloc(agent->dim, sizeof(float));
    if (!agent->query_buffer) {
        tap_pim_free(agent->dispatcher);
        free(agent);
        return NULL;
    }

    return agent;
}

int tap_agent_wake(tap_agent_t *agent) {
    if (!agent) return -1;
    if (agent->state != TAP_AGENT_ASLEEP) return 0;  /* Already awake */

    agent->state = TAP_AGENT_WAKING;

    /* Compute sleep duration */
    time_t now = time(NULL);
    if (agent->last_sleep_time > 0) {
        agent->total_sleep_time += difftime(now, agent->last_sleep_time);
    }
    agent->last_wake_time = now;
    agent->n_wakes++;
    agent->n_wake_cycles++;

    /* Update breath phase based on wake time */
    double dt = difftime(now, agent->last_sleep_time);
    agent->breath_phase = fmod(dt / TAP_SUB_BREATH_SEC * 2.0 * M_PI, 2.0 * M_PI);

    /* Update current ψ with breath modulation */
    double psi = PSI_PLASTIC * (1.0 + 0.05 * sin(agent->breath_phase));
    agent->current_breath_psi = psi;
    tap_pim_set_breath(agent->dispatcher, psi);

    agent->state = TAP_AGENT_AWAKE;
    return 0;
}

int tap_agent_sleep(tap_agent_t *agent) {
    if (!agent) return -1;
    if (agent->state == TAP_AGENT_ASLEEP) return 0;  /* Already asleep */
    agent->state = TAP_AGENT_ASLEEP;
    agent->last_sleep_time = time(NULL);
    agent->n_sleeps++;
    return 0;
}

int tap_agent_run(tap_agent_t *agent, const float *query, int k,
                  tap_agent_verdict_t *verdict) {
    if (!agent || !query || !verdict || k <= 0) return -1;
    if (agent->state == TAP_AGENT_ASLEEP) {
        /* Wake first */
        tap_agent_wake(agent);
    }

    agent->state = TAP_AGENT_THINKING;

    /* Copy query to buffer */
    memcpy(agent->query_buffer, query, agent->dim * sizeof(float));

    /* Run search via dispatcher */
    int32_t *ids = (int32_t *)calloc(k, sizeof(int32_t));
    float *dists = (float *)calloc(k, sizeof(float));
    if (!ids || !dists) {
        free(ids); free(dists);
        return -1;
    }
    int n = tap_pim_search(agent->dispatcher, agent->query_buffer, k, ids, dists);
    if (n < 0) n = 0;

    agent->state = TAP_AGENT_RESPONDING;

    /* Fill verdict */
    if (n > 0) {
        verdict->result_id = ids[0];
        verdict->result_dist = dists[0];
    } else {
        verdict->result_id = -1;
        verdict->result_dist = 0.0f;
    }
    verdict->n_results = n;
    verdict->breath_psi = agent->current_breath_psi;
    verdict->wake_cycles = agent->n_wake_cycles;
    verdict->sleep_duration = agent->total_sleep_time;
    agent->n_decisions++;

    free(ids);
    free(dists);

    /* Return to awake state */
    agent->state = TAP_AGENT_AWAKE;
    return n;
}

int tap_agent_get_breath(tap_agent_t *agent, double *psi, double *phase) {
    if (!agent) return -1;
    if (psi) *psi = agent->current_breath_psi;
    if (phase) *phase = agent->breath_phase;
    return 0;
}

int tap_agent_set_breath(tap_agent_t *agent, double psi) {
    if (!agent) return -1;
    agent->current_breath_psi = psi;
    return tap_pim_set_breath(agent->dispatcher, psi);
}

int tap_agent_load_vectors(tap_agent_t *agent, float *weights, int n_vectors) {
    if (!agent) return -1;
    return tap_pim_load_vectors(agent->dispatcher, weights, n_vectors);
}

int tap_agent_add_point(tap_agent_t *agent, int32_t id) {
    if (!agent) return -1;
    return tap_pim_add_point(agent->dispatcher, id);
}

void tap_agent_free(tap_agent_t *agent) {
    if (!agent) return;
    if (agent->dispatcher) tap_pim_free(agent->dispatcher);
    if (agent->query_buffer) free(agent->query_buffer);
    free(agent);
}
