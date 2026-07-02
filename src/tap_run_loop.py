# -*- coding: utf-8 -*-
"""
tap_run_loop.py
=================
TAP v5.3.2 — Run-Loop with Agent Orchestration.

A run-loop that uses the agent (tap_agent_v2 or v3)
to orchestrate running multiple sims in a coordinated
sequence. The agent:
  1. Wakes up
  2. Decides which sim to run next
  3. Runs the sim
  4. Updates breath state
  5. Consolidates working memory
  6. Sleeps

The run-loop supports:
  - Single-body reasoning (Earth)
  - Multi-body reasoning (10 cosmic bodies)
  - Cascade integration (live events)
  - Self-modifying schedules (agent decides)

Usage:
  python3 tap_run_loop.py
"""

import os
import sys
import json
import time
import math
import urllib.request
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_hnsw_ge_tap import (
    TAPHNSWGE, UserHNSWGE, RelationType,
    PHI, PHI_INV13, PLASTIC, PSI_PLASTIC, N_B, GAMMA_NB,
)


# Sim catalog: each sim has a name, function, and body
SIMS = {
    "unified_breath_clock": {
        "script": "tap_unified_breath_clock.py",
        "description": "9-13 breath producers, unified drift",
        "bodies": [0],  # Earth
    },
    "per_body_p1p18": {
        "script": "tap_per_body_p1p18.py",
        "description": "10 bodies × 18 predictions",
        "bodies": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    },
    "weather_v3": {
        "script": "tap_weather_v3.py",
        "description": "5 weather hubs, per-hub shrinkage",
        "bodies": [0],
    },
    "cascade_hnsw": {
        "script": "tap_cascade_hnsw.py",
        "description": "Cascade HNSW with live events",
        "bodies": [0],
    },
    "zodiac_to_breath": {
        "script": "tap_zodiac_to_breath.py",
        "description": "12 zodiac signs to breath cycles",
        "bodies": [0],
    },
    "schumann_resonance": {
        "script": "tap_schumann_resonance.py",
        "description": "7 Schumann harmonics",
        "bodies": [0],
    },
    "nami_ryu_breath": {
        "script": "tap_nami_ryu_breath.py",
        "description": "12s breath cycle",
        "bodies": [0],
    },
    "somatic_cosmic_geometry": {
        "script": "tap_somatic_cosmic_geometry_v2.py",
        "description": "22 templates × 32 somatics",
        "bodies": [0],
    },
    "multi_body_p1p18_sweep": {
        "script": "tap_multi_body_p1p18_sweep.py",
        "description": "180 cells megamatrix",
        "bodies": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    },
    "framework_coherence": {
        "script": "tap_framework_coherence.py",
        "description": "102 files audit",
        "bodies": [0],
    },
}

# 10 cosmic bodies
BODIES = ["Earth", "Sun", "Moon", "Mars", "Mercury",
          "Venus", "Jupiter", "Saturn", "Uranus", "Neptune"]


def get_current_psi():
    """Get current cascade ψ (from cached state or default)."""
    state_path = os.path.expanduser("~/.hermes/knowledge/tap-hnsw-ge/current_state.json")
    if os.path.exists(state_path):
        try:
            with open(state_path) as f:
                state = json.load(f)
            return state.get('psi', PSI_PLASTIC)
        except Exception:
            pass
    return PSI_PLASTIC


class AgentOrchestrator:
    """The agent that orchestrates sim runs."""

    def __init__(self):
        self.state = "ASLEEP"
        self.current_body = "Earth"
        self.current_psi = PSI_PLASTIC
        self.n_wakes = 0
        self.n_sleeps = 0
        self.n_runs = 0
        self.working_memory = []
        self.run_log = []

    def wake(self):
        self.state = "AWAKE"
        self.n_wakes += 1
        self.current_psi = get_current_psi()
        return self.current_psi

    def sleep(self):
        self.state = "ASLEEP"
        self.n_sleeps += 1
        return self.state

    def decide_next_sim(self, sim_history: dict) -> str:
        """Decide which sim to run next based on history."""
        # Run the sim that hasn't been run the longest
        now = datetime.now()
        candidates = []
        for name, info in SIMS.items():
            last_run = sim_history.get(name, {}).get('last_run', None)
            if last_run is None:
                return name  # Never run, prioritize
            age = (now - last_run).total_seconds() / 3600.0  # hours
            candidates.append((age, name))
        candidates.sort(reverse=True)
        return candidates[0][1] if candidates else "unified_breath_clock"

    def run_sim(self, sim_name: str) -> dict:
        """Run a sim via subprocess."""
        info = SIMS.get(sim_name)
        if not info:
            return {"error": f"Unknown sim: {sim_name}"}
        script = info['script']
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
        if not os.path.exists(script_path):
            return {"error": f"Script not found: {script_path}"}
        t0 = time.time()
        try:
            r = subprocess.run(['python3', script_path], capture_output=True, text=True, timeout=120)
            elapsed = time.time() - t0
            return {
                "sim": sim_name,
                "script": script,
                "returncode": r.returncode,
                "elapsed_s": round(elapsed, 2),
                "stdout_lines": len(r.stdout.split('\n')),
                "stderr_lines": len(r.stderr.split('\n')),
                "bodies": info['bodies'],
            }
        except subprocess.TimeoutExpired:
            return {"sim": sim_name, "error": "timeout", "elapsed_s": 120.0}
        except Exception as e:
            return {"sim": sim_name, "error": str(e)}

    def consolidate(self):
        """Consolidate working memory."""
        seen = set()
        unique = []
        for w in self.working_memory:
            if w not in seen:
                seen.add(w)
                unique.append(w)
        n_merged = len(self.working_memory) - len(unique)
        self.working_memory = unique[-32:]  # Keep last 32
        return n_merged

    def set_body(self, body_name: str):
        """Switch to a different body."""
        if body_name in BODIES:
            self.current_body = body_name
            self.current_psi = PSI_PLASTIC  # All bodies share P17 ψ


def main():
    print("=" * 80)
    print("  TAP RUN-LOOP — AGENT-ORCHESTRATED SIM EXECUTION")
    print(f"  {len(SIMS)} sims, 10 cosmic bodies")
    print("=" * 80)
    print()

    # Load run history
    history_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_run_loop_history.json"
    history = {}
    if os.path.exists(history_path):
        try:
            with open(history_path) as f:
                raw = json.load(f)
                for name, t in raw.get('last_runs', {}).items():
                    history[name] = {'last_run': datetime.fromisoformat(t)}
        except Exception:
            pass

    agent = AgentOrchestrator()
    print("  [1/5] AGENT WAKES UP:")
    psi = agent.wake()
    print(f"    State: {agent.state}")
    print(f"    Current ψ: {psi:.4f}")
    print(f"    Active body: {agent.current_body}")
    print()

    # Decide and run a few sims
    print("  [2/5] AGENT DECIDES SEQUENCE:")
    n_sims = 3
    for i in range(n_sims):
        sim_name = agent.decide_next_sim(history)
        info = SIMS[sim_name]
        print(f"    Step {i+1}: {sim_name}")
        # Multi-body if applicable
        bodies = [BODIES[b] for b in info['bodies']]
        if len(bodies) > 1:
            print(f"      Bodies: {', '.join(bodies[:3])}... ({len(bodies)} total)")
        else:
            print(f"      Body: {bodies[0]}")
        # Run
        result = agent.run_sim(sim_name)
        agent.working_memory.append(sim_name)
        agent.n_runs += 1
        history[sim_name] = {'last_run': datetime.now()}
        agent.run_log.append({"step": i+1, **result})
        if 'error' in result:
            print(f"      ERROR: {result['error']}")
        else:
            print(f"      Returncode: {result['returncode']}")
            print(f"      Elapsed: {result['elapsed_s']:.1f}s")
    print()

    # Consolidate
    print("  [3/5] CONSOLIDATE WORKING MEMORY:")
    n_merged = agent.consolidate()
    print(f"    WM entries: {len(agent.working_memory)}")
    print(f"    Merged duplicates: {n_merged}")
    print()

    # Multi-body reasoning example
    print("  [4/5] MULTI-BODY REASONING DEMO:")
    for body_id in [0, 1, 2, 6]:  # Earth, Sun, Moon, Jupiter
        body = BODIES[body_id]
        agent.set_body(body)
        print(f"    Body {body_id} ({body}): ψ = {agent.current_psi:.4f}")
    print()

    # Sleep
    print("  [5/5] AGENT SLEEPS:")
    agent.sleep()
    print(f"    State: {agent.state}")
    print(f"    Stats: {agent.n_runs} runs, {agent.n_wakes} wakes, {agent.n_sleeps} sleeps")
    print()

    # Save history
    history_data = {
        "timestamp": datetime.now().isoformat(),
        "last_runs": {n: h['last_run'].isoformat() for n, h in history.items()},
    }
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)
    print(f"  [SAVED] {history_path}")
    print()

    # Save run log
    log_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_run_loop_log.json"
    with open(log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "n_runs": agent.n_runs,
            "n_wakes": agent.n_wakes,
            "n_sleeps": agent.n_sleeps,
            "n_merged": n_merged,
            "n_bodies_visited": len(set(BODIES[b] for sim in agent.run_log for b in SIMS[sim['sim']]['bodies'])),
            "run_log": agent.run_log,
        }, f, indent=2, default=str)
    print(f"  [SAVED] {log_path}")
    print()

    print("=" * 80)
    print("  TAP RUN-LOOP COMPLETE")
    print(f"    Sim catalog: {len(SIMS)} sims")
    print(f"    Bodies: {len(BODIES)}")
    print(f"    Runs: {agent.n_runs}")
    print(f"    Agent: woke {agent.n_wakes} times, slept {agent.n_sleeps} times")
    print(f"    Working memory: {len(agent.working_memory)} entries")
    print("=" * 80)


if __name__ == "__main__":
    main()
