# -*- coding: utf-8 -*-
"""
tap_lymphatic_cascade_sim.py
==============================
TAP Model — Lymphatic Cascade: s_setpoint → cortisol → fascia → lymph

The v5.0 lymphatic channel. Demonstrates the full chain from
epigenetic setpoint down to lymphatic flow:

  parent_sim s_setpoint (0.5)
    → systemic cortisol (chronic stress or tensegrity)
      → myofascial tension (12 trains)
        → piezo amplitude (collagen braid coherence)
          → EM reading fidelity
            → lymph flow rate (compressed or hydrated)
              → blood circulation (coupled to lymph via thoracic duct)

USAGE:
  python3 src/tap_lymphatic_cascade_sim.py [--plot]
"""

import os
import json
import math
import argparse
import numpy as np
from science_constants import PHI

# Local imports
from tap_fascia_sim import (
    FasciaSimulator, MYERS_TRAINS, run_stress_scenario,
    run_tensegrity_scenario, run_ayahuasca_scenario
)
from tap_epigenetic_flop_sim import EpigeneticFlopSimulator

PHI_INV2 = PHI ** -2
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10


# ─────────────────────────────────────────────────────────────────────────────
# s_setpoint → systemic cortisol mapping
# ─────────────────────────────────────────────────────────────────────────────

def s_setpoint_to_cortisol(s_setpoint):
    """
    Map the parent sim's s_setpoint to a systemic cortisol level.
    Higher s_setpoint (tensegrity) → lower cortisol (relaxed).
    Lower s_setpoint (chronic ayahuasca) → moderate cortisol.
    """
    # Baseline cortisol is 0.5 (midrange)
    # s_setpoint = 0.5 → cortisol = 0.5
    # s_setpoint = 0.6 (tensegrity) → cortisol = 0.3 (relaxed)
    # s_setpoint = 0.4 (ayahuasca) → cortisol = 0.7 (stressed)
    return np.clip(1.0 - s_setpoint, 0.0, 1.0)


def s_setpoint_to_tensegrity(s_setpoint):
    """
    Map s_setpoint to a tensegrity score. Higher s_setpoint
    implies the body is in a more integrated state.
    """
    # s_setpoint = 0.5 → tensegrity = 0.5
    # s_setpoint = 0.6 (tensegrity) → tensegrity = 0.95
    # s_setpoint = 0.4 (ayahuasca) → tensegrity = 0.2
    if s_setpoint > 0.5:
        return np.clip(0.5 + (s_setpoint - 0.5) * 4.5, 0.0, 1.0)
    else:
        return np.clip(0.5 - (0.5 - s_setpoint) * 1.5, 0.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# FULL CASCADE: parent sim → fascia → lymph
# ─────────────────────────────────────────────────────────────────────────────

def run_full_lymphatic_cascade(days=30, save_path=None):
    """
    Run the full 30-day trajectory:
      day 1-10: chronic stress
      day 11-20: reset
      day 21-30: tensegrity
    For each day, run the parent sim, get s_setpoint, map to
    cortisol/tensegrity, run the fascia sim, compute lymph flow.
    """
    parent = EpigeneticFlopSimulator()
    cascade_history = []

    for day in range(1, days + 1):
        if day <= 10:
            inputs = {"Threat": 1.2, "SocialSafety": 0.1, "FocusedTraining": 0.0, "BreathDrive": 0.05}
            scenario = "chronic_stress"
        elif day <= 20:
            inputs = {"Threat": 0.0, "SocialSafety": 0.8, "FocusedTraining": 0.2, "BreathDrive": 0.8}
            scenario = "reset"
        else:
            inputs = {"Threat": 0.0, "SocialSafety": 1.5, "FocusedTraining": 1.5, "BreathDrive": 1.5}
            scenario = "tensegrity"

        # Run parent sim
        parent_metrics = parent.step(inputs)
        s_setpoint = parent_metrics["s_setpoint"]

        # Map to systemic inputs
        cortisol = s_setpoint_to_cortisol(s_setpoint)
        tensegrity_score = s_setpoint_to_tensegrity(s_setpoint)

        # Run fascia sim for 10 sub-steps
        fascia = FasciaSimulator(
            cortisol=cortisol, tensegrity=tensegrity_score,
            parent_s_setpoint=s_setpoint
        )
        for _ in range(10):
            fascia.step()

        f_sum = fascia.summary()

        cascade_history.append({
            "day": day,
            "scenario": scenario,
            "s_setpoint": round(s_setpoint, 4),
            "cortisol": round(cortisol, 4),
            "tensegrity_score": round(tensegrity_score, 4),
            "mean_fascia_tension": round(f_sum["mean_tension"], 4),
            "mean_piezo": round(f_sum["mean_piezo"], 4),
            "mean_lymph": round(f_sum["mean_lymph"], 4),
            "mean_coherence": round(f_sum["mean_coherence"], 4),
            "twin_dragon_lymph": round(f_sum["twin_dragon_lymph"], 4),
            "spiral_coupling": round(f_sum["spiral_coupling"], 4)
        })

    if save_path:
        with open(save_path, "w") as f:
            json.dump(cascade_history, f, indent=2)

    return cascade_history


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot_cascade(history, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    days = [d["day"] for d in history]
    s_setpoint = [d["s_setpoint"] for d in history]
    cortisol = [d["cortisol"] for d in history]
    lymph = [d["mean_lymph"] for d in history]
    tension = [d["mean_fascia_tension"] for d in history]
    twin_lymph = [d["twin_dragon_lymph"] for d in history]
    coupling = [d["spiral_coupling"] for d in history]
    coherence = [d["mean_coherence"] for d in history]

    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    # Panel 1: Parent sim output → systemic inputs
    axes[0].plot(days, s_setpoint, color="#3a86ff", lw=2, label="s_setpoint (parent sim)")
    axes[0].plot(days, cortisol, color="#ff006e", lw=1.5, label="cortisol (mapped)")
    axes[0].axhline(0.5, color="grey", ls="--", lw=0.8)
    axes[0].axvline(10, color="red", ls=":", lw=0.8, alpha=0.5)
    axes[0].axvline(20, color="green", ls=":", lw=0.8, alpha=0.5)
    axes[0].text(11, 0.55, "Tensegrity", fontsize=9, color="green")
    axes[0].set_ylabel("epigenetic /\nstress marker")
    axes[0].legend(loc="best", fontsize=8)
    axes[0].set_title("TAP v5.0 — Full lymphatic cascade (parent sim → fascia → lymph)")

    # Panel 2: Fascia state
    axes[1].plot(days, tension, color="#fb5607", lw=1.5, label="mean fascia tension")
    axes[1].plot(days, coherence, color="#06d6a0", lw=1.5, label="mean braid coherence")
    axes[1].set_ylabel("fascia /\ncollagen")
    axes[1].legend(loc="best", fontsize=8)

    # Panel 3: Lymph flow
    axes[2].plot(days, lymph, color="#118ab2", lw=2, label="mean lymph flow")
    axes[2].plot(days, twin_lymph, color="#8338ec", lw=2, label="twin dragon lymph")
    axes[2].plot(days, coupling, color="#ef476f", lw=1.5, label="spiral coupling (fidelity)")
    axes[2].set_ylabel("lymph /\ncoupling")
    axes[2].set_xlabel("day")
    axes[2].legend(loc="best", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    print("=" * 80)
    print("  TAP v5.0 — Full Lymphatic Cascade (30 days)")
    print("  parent sim → s_setpoint → cortisol → fascia → lymph")
    print("=" * 80)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
    os.makedirs(out_dir, exist_ok=True)

    history = run_full_lymphatic_cascade(
        days=30,
        save_path=os.path.join(out_dir, "tap_lymphatic_cascade_results.json")
    )

    # Print key days
    print("\n  [CASCADE TIMELINE]\n")
    print(f"  {'Day':<4} | {'Phase':<18} | {'s_set':<8} | {'corti':<7} | "
          f"{'tens':<7} | {'lymph':<7} | {'coupl':<7}")
    print(f"  {'-'*4}-+-{'-'*18}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}")
    for d in [history[0], history[4], history[9], history[10], history[14],
              history[19], history[20], history[24], history[29]]:
        print(f"  {d['day']:<4} | {d['scenario']:<18} | "
              f"{d['s_setpoint']:.3f}   | {d['cortisol']:.3f}   | "
              f"{d['tensegrity_score']:.3f}   | {d['mean_lymph']:.3f}   | "
              f"{d['spiral_coupling']:.4f}")

    # Verification
    print("\n" + "=" * 80)
    print("  CASCADE VERIFICATION")
    print("=" * 80)
    chronic = [d for d in history if d["scenario"] == "chronic_stress"]
    tensegrity_days = [d for d in history if d["scenario"] == "tensegrity"]
    chronic_lymph = np.mean([d["mean_lymph"] for d in chronic])
    tensegrity_lymph = np.mean([d["mean_lymph"] for d in tensegrity_days])
    chronic_coupling = np.mean([d["spiral_coupling"] for d in chronic])
    tensegrity_coupling = np.mean([d["spiral_coupling"] for d in tensegrity_days])

    print(f"\n  Mean lymph flow:")
    print(f"    Chronic stress (days 1-10): {chronic_lymph:.3f}")
    print(f"    Tensegrity (days 21-30):    {tensegrity_lymph:.3f}")
    print(f"  → Lymph increases under tensegrity: "
          f"{'PASS' if tensegrity_lymph > chronic_lymph else 'FAIL'}")

    print(f"\n  Mean spiral coupling:")
    print(f"    Chronic stress: {chronic_coupling:.4f}")
    print(f"    Tensegrity:     {tensegrity_coupling:.4f}")
    print(f"  → Coupling increases under tensegrity: "
          f"{'PASS' if tensegrity_coupling > chronic_coupling else 'FAIL'}")

    if args.plot:
        plot_path = os.path.join(out_dir, "tap_lymphatic_cascade.png")
        if plot_cascade(history, plot_path):
            print(f"\n  [PLOT] -> {plot_path}")

    print("=" * 80)


if __name__ == "__main__":
    main()
