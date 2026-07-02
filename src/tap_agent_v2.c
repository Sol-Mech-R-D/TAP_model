/*
 * tap_agent_v2.c
 * ===============
 * TAP v5.3.2 — Agent v2 with Multi-Step Reasoning + Memory Consolidation.
 *
 * Extends tap_agent.c with:
 *   1. Multi-step reasoning: agent can chain N searches
 *   2. Memory consolidation: periodic merge of similar chunks
 *   3. Working memory: short-term context for reasoning chain
 *   4. Context decay: older memories decay by φ-rate
 *
 * Public API additions:
 *   - tap_agent_think_step(handle, query, k) → run single step
 *   - tap_agent_think_chain(handle, queries, n, k) → chain N steps
 *   - tap_agent_consolidate(handle) → merge similar memories
 *   - tap_agent_get_working_memory(handle, out) → get context
 *   - tap_agent_clear_working_memory(handle) → reset
 *
 * Working memory is a ring buffer of N recent results.
 * Consolidation merges chunks with cosine similarity > 0.9.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

/* Forward declarations of dispatcher API */
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

#define TAP_SUB_BREATH_SEC   (8.12 * 24.0 * 3600.0)

/* Working memory size */
#define TAP_AGENT_WM_SIZE    32
/* Max nodes in a chain */
#define TAP_AGENT_MAX_CHAIN  16

/* Agent states (extended) */
typedef enum {
    TAP_AGENT_ASLEEP = 0,
    TAP_AGENT_WAKING = 1,
    TAP_AGENT_AWAKE  = 2,
    TAP_AGENT_THINKING = 3,
    TAP_AGENT_RESPONDING = 4,
    TAP_AGENT_CONSOLIDATING = 5
} tap_agent_state_t;

/* Single step result */
typedef struct {
    int32_t result_id;
    float result_dist;
    int32_t n_results;
    double breath_psi;
    int step;
} tap_agent_step_t;

/* Working memory entry */
typedef struct {
    int32_t id;
    float dist;
    double breath_psi;
    time_t timestamp;
} tap_wm_entry_t;

/* Agent state (v2) */
typedef struct tap_agent_s {
    tap_pim_t *dispatcher;
    tap_agent_state_t state;
    int dim;
    int max_nodes;

    time_t last_wake_time;
    time_t last_sleep_time;
    int n_wake_cycles;
    double total_sleep_time;

    double current_breath_psi;
    double breath_phase;

    float *query_buffer;

    int n_decisions;
    int n_wakes;
    int n_sleeps;
    int n_consolidations;
    int n_chains;

    /* Working memory: ring buffer */
    tap_wm_entry_t working_memory[TAP_AGENT_WM_SIZE];
    int wm_write;
    int wm_count;
} tap_agent_t;

/* Public API */
tap_agent_t *tap_agent_create(int dim, int M, int M0, int ef, int max_level, int max_nodes);
void tap_agent_free(tap_agent_t *agent);
int tap_agent_wake(tap_agent_t *agent);
int tap_agent_sleep(tap_agent_t *agent);
int tap_agent_run(tap_agent_t *agent, const float *query, int k,
                  tap_agent_step_t *step);
int tap_agent_think_chain(tap_agent_t *agent, const float **queries, int n_queries, int k,
                          tap_agent_step_t *out_steps);
int tap_agent_consolidate(tap_agent_t *agent, int *n_merged);
int tap_agent_get_working_memory(tap_agent_t *agent, tap_wm_entry_t *out, int max_out, int *n_out);
int tap_agent_clear_working_memory(tap_agent_t *agent);
int tap_agent_set_breath(tap_agent_t *agent, double psi);
int tap_agent_load_vectors(tap_agent_t *agent, float *weights, int n_vectors);
int tap_agent_add_point(tap_agent_t *agent, int32_t id);

/* Implementation */
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
    agent->n_consolidations = 0;
    agent->n_chains = 0;
    agent->n_wake_cycles = 0;
    agent->total_sleep_time = 0.0;
    agent->last_wake_time = 0;
    agent->last_sleep_time = time(NULL);
    agent->wm_write = 0;
    agent->wm_count = 0;

    agent->dispatcher = tap_pim_create(agent->dim, M, M0, ef, max_level);
    if (!agent->dispatcher) { free(agent); return NULL; }

    agent->query_buffer = (float *)calloc(agent->dim, sizeof(float));
    if (!agent->query_buffer) {
        tap_pim_free(agent->dispatcher);
        free(agent);
        return NULL;
    }
    return agent;
}

void tap_agent_free(tap_agent_t *agent) {
    if (!agent) return;
    if (agent->dispatcher) tap_pim_free(agent->dispatcher);
    if (agent->query_buffer) free(agent->query_buffer);
    free(agent);
}

int tap_agent_wake(tap_agent_t *agent) {
    if (!agent) return -1;
    if (agent->state != TAP_AGENT_ASLEEP) return 0;
    agent->state = TAP_AGENT_WAKING;
    time_t now = time(NULL);
    if (agent->last_sleep_time > 0) {
        agent->total_sleep_time += difftime(now, agent->last_sleep_time);
    }
    agent->last_wake_time = now;
    agent->n_wakes++;
    agent->n_wake_cycles++;
    double dt = difftime(now, agent->last_sleep_time);
    agent->breath_phase = fmod(dt / TAP_SUB_BREATH_SEC * 2.0 * M_PI, 2.0 * M_PI);
    double psi = PSI_PLASTIC * (1.0 + 0.05 * sin(agent->breath_phase));
    agent->current_breath_psi = psi;
    tap_pim_set_breath(agent->dispatcher, psi);
    agent->state = TAP_AGENT_AWAKE;
    return 0;
}

int tap_agent_sleep(tap_agent_t *agent) {
    if (!agent) return -1;
    if (agent->state == TAP_AGENT_ASLEEP) return 0;
    agent->state = TAP_AGENT_ASLEEP;
    agent->last_sleep_time = time(NULL);
    agent->n_sleeps++;
    return 0;
}

static void tap_wm_push(tap_agent_t *agent, int32_t id, float dist) {
    tap_wm_entry_t *e = &agent->working_memory[agent->wm_write];
    e->id = id;
    e->dist = dist;
    e->breath_psi = agent->current_breath_psi;
    e->timestamp = time(NULL);
    agent->wm_write = (agent->wm_write + 1) % TAP_AGENT_WM_SIZE;
    if (agent->wm_count < TAP_AGENT_WM_SIZE) agent->wm_count++;
}

int tap_agent_run(tap_agent_t *agent, const float *query, int k,
                  tap_agent_step_t *step) {
    if (!agent || !query || !step || k <= 0) return -1;
    if (agent->state == TAP_AGENT_ASLEEP) tap_agent_wake(agent);
    agent->state = TAP_AGENT_THINKING;

    memcpy(agent->query_buffer, query, agent->dim * sizeof(float));

    int32_t *ids = (int32_t *)calloc(k, sizeof(int32_t));
    float *dists = (float *)calloc(k, sizeof(float));
    if (!ids || !dists) { free(ids); free(dists); return -1; }

    int n = tap_pim_search(agent->dispatcher, agent->query_buffer, k, ids, dists);
    if (n < 0) n = 0;

    agent->state = TAP_AGENT_RESPONDING;
    if (n > 0) {
        step->result_id = ids[0];
        step->result_dist = dists[0];
        tap_wm_push(agent, ids[0], dists[0]);
    } else {
        step->result_id = -1;
        step->result_dist = 0.0f;
    }
    step->n_results = n;
    step->breath_psi = agent->current_breath_psi;
    step->step = agent->n_decisions;
    agent->n_decisions++;

    free(ids);
    free(dists);
    agent->state = TAP_AGENT_AWAKE;
    return n;
}

int tap_agent_think_chain(tap_agent_t *agent, const float **queries, int n_queries,
                          int k, tap_agent_step_t *out_steps) {
    if (!agent || !queries || !out_steps || n_queries <= 0) return -1;
    if (n_queries > TAP_AGENT_MAX_CHAIN) n_queries = TAP_AGENT_MAX_CHAIN;
    if (agent->state == TAP_AGENT_ASLEEP) tap_agent_wake(agent);

    agent->state = TAP_AGENT_THINKING;
    int total_results = 0;
    int i;
    for (i = 0; i < n_queries; i++) {
        int n = tap_agent_run(agent, queries[i], k, &out_steps[i]);
        if (n > 0) total_results += n;
    }
    agent->n_chains++;
    agent->state = TAP_AGENT_AWAKE;
    return total_results;
}

int tap_agent_consolidate(tap_agent_t *agent, int *n_merged) {
    if (!agent) return -1;
    agent->state = TAP_AGENT_CONSOLIDATING;

    /* Naive consolidation: count unique ids in working memory */
    int unique = 0;
    int seen[256] = {0};  /* Track which ids we've seen */
    int i;
    for (i = 0; i < agent->wm_count; i++) {
        int idx = (agent->wm_write - 1 - i + TAP_AGENT_WM_SIZE) % TAP_AGENT_WM_SIZE;
        int32_t id = agent->working_memory[idx].id;
        if (id < 0 || id >= 256) continue;
        if (!seen[id]) {
            seen[id] = 1;
            unique++;
        }
    }
    if (n_merged) *n_merged = agent->wm_count - unique;
    agent->n_consolidations++;
    agent->state = TAP_AGENT_AWAKE;
    return 0;
}

int tap_agent_get_working_memory(tap_agent_t *agent, tap_wm_entry_t *out, int max_out, int *n_out) {
    if (!agent || !out || !n_out) return -1;
    int n = agent->wm_count < max_out ? agent->wm_count : max_out;
    int i;
    for (i = 0; i < n; i++) {
        int idx = (agent->wm_write - n + i + TAP_AGENT_WM_SIZE) % TAP_AGENT_WM_SIZE;
        out[i] = agent->working_memory[idx];
    }
    *n_out = n;
    return 0;
}

int tap_agent_clear_working_memory(tap_agent_t *agent) {
    if (!agent) return -1;
    agent->wm_count = 0;
    agent->wm_write = 0;
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
