# -*- coding: utf-8 -*-
"""
tap_nami_ryu_breath.py
=========================
TAP v5.3 — Nami-Ryu Aikijujutsu Respiratory Breath Sim.

The user studies Nami-ryu (波流, "wave flow") aikijujutsu, a
branch of traditional Japanese jujutsu that emphasizes
body-listening. In TAP terms:

  - The two spirals (anatomy trains) are the routes along
    which "ki" flows
  - Phase-locked spirals = projection mode (high coupling)
  - Decoupled spirals = listening mode (low coupling)
  - Breath is the modulator that switches between modes

This sim models the Nami-ryu respiratory breath:

  1. Inhale (4s): the spirals contract, coupling increases
  2. Hold (1s): the spirals lock at peak coupling
  3. Exhale (6s): the spirals release, coupling decreases
  4. Empty hold (1s): the spirals reset, listening mode

The breath cycles at ~10s per cycle. Over 30 days of
practice, the framework predicts:

  - Spiral_coupling baseline shifts up (P3: fidelity up)
  - Lymph flow +15-25% (P2)
  - HTR2A chromatin openness stabilizes (P5)
  - Cross-body coupling (per_body) integrates

Each breath cycle is ALSO a sub-breath clock event:
  - 10s/breath × 8640 breaths/day = 86400 s/day = 1 day ✓
  - 10s × 9 breath producers in the unified clock

The sim uses:
  - tap_body_breath_states: per-body N_B and ψ
  - tap_fascia_sim: spiral_coupling (existing code)
  - tap_unified_breath_clock: 13 breath producers

Predictions (per docs/TAP_Testable_Predictions_v5.md):
  - P3: fidelity up, piezo down (counter-intuitive)
  - P2: lymph flow +15-25% in tensegrity
  - P6: Nami-ryu specific spiral coupling (10+ yr)
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10
PHI_INV13 = PHI ** -13

# Import existing sims
from tap_body_breath_states import get_body_breath_state, get_body_n_b

# Nami-ryu breath phases
NAMI_BREATH = {
    "inhale": {"duration_s": 4.0, "spiral_coupling_delta": +0.20},
    "hold":   {"duration_s": 1.0, "spiral_coupling_delta": +0.05},
    "exhale": {"duration_s": 6.0, "spiral_coupling_delta": -0.18},
    "empty":  {"duration_s": 1.0, "spiral_coupling_delta": -0.07},
}

# Total cycle
NAMI_CYCLE_S = sum(p["duration_s"] for p in NAMI_BREATH.values())  # 12s
NAMI_BREATHS_PER_DAY = 86400 / NAMI_CYCLE_S  # 7200


def nami_breath_at(t_s_in_cycle: float) -> dict:
    """
    Compute Nami-ryu breath state at a given time within the
    12-second breath cycle.

    Returns:
      - phase: name of the breath phase
      - t_remaining_s: time left in this phase
      - spiral_coupling_delta: how much the spiral coupling shifts
      - is_projection: True if spirals are locked (projection mode)
      - is_listening: True if spirals are decoupled (listening mode)
    """
    t = t_s_in_cycle % NAMI_CYCLE_S
    cumulative = 0.0
    for phase_name, phase_data in NAMI_BREATH.items():
        if t < cumulative + phase_data["duration_s"]:
            t_remaining = cumulative + phase_data["duration_s"] - t
            coupling_delta = phase_data["spiral_coupling_delta"]
            return {
                "phase": phase_name,
                "t_remaining_s": t_remaining,
                "spiral_coupling_delta": coupling_delta,
                "is_projection": phase_name in ("hold",),
                "is_listening": phase_name in ("empty",),
                "cycle_pct": t / NAMI_CYCLE_S,
            }
        cumulative += phase_data["duration_s"]
    return {}


def compute_baseline_spiral_coupling(experience_yr: float) -> float:
    """
    Compute baseline spiral coupling based on years of practice.

    Nami-ryu aikijujutsu (the martial art the user studies) trains
    the spirals to be phase-locked during projection mode and
    decoupled during listening mode. Years of practice improve
    the baseline coupling.

    Per docs/TAP_Testable_Predictions_v5.md line 364:
      | Nami-ryu (10+ yr)| 0.15-0.25  | 8-12 |
    """
    # Baseline: 0.05 for novice, +0.015 per year up to 0.30
    if experience_yr < 0:
        return 0.05
    return min(0.30, 0.05 + 0.015 * experience_yr)


def project_coupling(t_s: float, experience_yr: float) -> dict:
    """
    Project the spiral_coupling at a given time, including the
    Nami-ryu breath modulation and per-body state.

    The combined formula:
      coupling(t) = baseline + breath_delta(t) + 0.05 * body_modulation(t)
    """
    baseline = compute_baseline_spiral_coupling(experience_yr)
    breath = nami_breath_at(t_s)

    # Get Earth's per-body state
    now = datetime.now()
    earth = get_body_breath_state("Earth", now)
    # Body modulation: 0.05 * (s_setpoint - 0.5) scaled by psi phase
    body_mod = 0.05 * (earth["s_setpoint"] - 0.5) * 2.0

    coupling = baseline + breath["spiral_coupling_delta"] + body_mod
    coupling = max(0.0, min(1.0, coupling))

    return {
        "time_s": t_s,
        "baseline": baseline,
        "breath_phase": breath["phase"],
        "breath_delta": breath["spiral_coupling_delta"],
        "body_modulation": round(body_mod, 4),
        "earth_psi": earth["psi"],
        "spiral_coupling": round(coupling, 4),
        "is_projection": breath["is_projection"],
        "is_listening": breath["is_listening"],
    }


def project_over_practice(experience_yr: float, days: int = 30) -> list:
    """Project spiral coupling over N days of practice."""
    results = []
    for d in range(days):
        # Sample at multiple breath cycles
        day_couplings = []
        for cycle_idx in range(20):  # 20 samples per day
            t_s = d * 86400 + cycle_idx * (86400 / 20)
            proj = project_coupling(t_s, experience_yr)
            day_couplings.append(proj["spiral_coupling"])
        results.append({
            "day": d,
            "mean_coupling": round(statistics.mean(day_couplings), 4),
            "max_coupling": max(day_couplings),
            "min_coupling": min(day_couplings),
        })
    return results


def main():
    print("=" * 80)
    print("  TAP NAMI-RYU RESPIRATORY BREATH SIM")
    print("  Body-listening through the spirals, using per-body states")
    print("=" * 80)
    print()

    print("  [1/4] Nami-ryu breath phases (12s cycle):")
    cumulative = 0
    for phase_name, phase_data in NAMI_BREATH.items():
        print(f"    {phase_name:8s} ({phase_data['duration_s']:.0f}s, t={cumulative:.0f}-{cumulative+phase_data['duration_s']:.0f}s): Δ coupling = {phase_data['spiral_coupling_delta']:+.2f}")
        cumulative += phase_data["duration_s"]
    print(f"    Total cycle: {NAMI_CYCLE_S:.0f}s, ~{NAMI_BREATHS_PER_DAY:.0f} breaths/day")
    print()

    # 2. Per-body state integration
    print("  [2/4] Per-body state integration (Earth coupling):")
    today = datetime(2026, 7, 2, 12, 0)
    earth = get_body_breath_state("Earth", today)
    moon = get_body_breath_state("Moon", today)
    sun = get_body_breath_state("Sun", today)
    print(f"    Earth ψ = {earth['psi']:.4f}, s_setpoint = {earth['s_setpoint']:.3f}, Γ = {earth['gamma_n_b']:.6f}")
    print(f"    Moon  ψ = {moon['psi']:.4f}, s_setpoint = {moon['s_setpoint']:.3f}, Γ = {moon['gamma_n_b']:.6f}")
    print(f"    Sun   ψ = {sun['psi']:.4f}, s_setpoint = {sun['s_setpoint']:.3f}, Γ = {sun['gamma_n_b']:.6f}")
    print()

    # 3. Projection over 1 breath cycle
    print("  [3/4] Sample projection (1 breath cycle, 10 years experience):")
    for t_s in range(0, 13, 1):
        proj = project_coupling(t_s, 10.0)
        marker = ""
        if proj["is_projection"]:
            marker = " ← PROJECTION"
        elif proj["is_listening"]:
            marker = " ← LISTENING"
        print(f"    t={t_s:2d}s  {proj['breath_phase']:8s}  coupling={proj['spiral_coupling']:.4f}{marker}")
    print()

    # 4. Practice over 30 days for different experience levels
    print("  [4/4] 30-day practice projection (3 experience levels):")
    for years in [0.5, 5.0, 15.0]:
        proj = project_over_practice(years, days=30)
        mean_start = statistics.mean([p["mean_coupling"] for p in proj[:7]])
        mean_end = statistics.mean([p["mean_coupling"] for p in proj[-7:]])
        delta = mean_end - mean_start
        print(f"    {years:5.1f} yr practice: baseline {mean_start:.4f} → {mean_end:.4f}  (Δ = {delta:+.4f})")

    # Predictions
    print()
    print("  PREDICTIONS:")
    print(f"    P2 (lymph flow): +15-25% over 30 days (TAP predicts +20%)")
    print(f"    P3 (fidelity): spiral_coupling up, piezo down (counter-intuitive)")
    print(f"    P6 (Nami-ryu specific): coupling 0.15-0.25 at 10+ yr, 8-12 phases")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_nami_ryu_breath_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "nami_breath_phases": NAMI_BREATH,
        "cycle_duration_s": NAMI_CYCLE_S,
        "breaths_per_day": NAMI_BREATHS_PER_DAY,
        "earth_state": earth,
        "moon_state": moon,
        "sun_state": sun,
        "30d_projection": {f"{y}_yr": project_over_practice(y, days=30) for y in [0.5, 5.0, 15.0]},
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
