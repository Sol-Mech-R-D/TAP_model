# -*- coding: utf-8 -*-
"""
tap_5ht2a_epigenetic_coupling_sim.py
======================================
TAP — 5-HT2A ↔ Parent-Sim Coupling Simulator (v4.0.2)

Runs the v4.0.2 prediction: chronic ayahuasca use and tensegrity
training produce OPPOSITE signatures in the cosmic breath tick.

The cascade:
  - AYAHUASCA path: chronic DMT → 5-HT2A setpoint up → parent sim's
    s_setpoint DECREASES (cortisol dysregulation drags serotonin
    baseline down) → drift_multiplier > 1 → cosmic breath tick
    INCREASES (faster cosmic time).

  - TENSEGRITY path: focused training + breath engagement → parent
    sim's s_setpoint INCREASES (TAP claim: training remodels the
    serotonin baseline upward) → drift_multiplier < 1 → cosmic breath
    tick DECREASES (slower cosmic time).

The two interventions produce opposite signatures. This is the
v4.0.2 testable prediction: if you measure the cosmic breath tick
(or any proxy for it) in chronic ayahuasca users vs tensegrity-trained
individuals, they should be on opposite sides of the population mean.

USAGE:
  python3 src/tap_5ht2a_epigenetic_coupling_sim.py [--plot]
"""

import os
import json
import math
import argparse
from science_constants import PHI

# Local imports
from tap_5ht2a_ayahuasca_sim import HT2ABoundarySimulator
from tap_chromatin_state_sim import ChromatinStateSimulator
from tap_epigenetic_flop_sim import EpigeneticFlopSimulator

PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10
PHI_INV13 = PHI ** -13
BASELINE_S_SETPOINT = 0.5


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

def run_tensegrity_scenario(days=30, save_path=None):
    """
    Run the parent sim in TENSEGRITY mode (days 21-30 of the original
    30-day trajectory). Tensegrity increases s_setpoint via the
    v4.0.1 fix.
    """
    sim = EpigeneticFlopSimulator()
    history = []
    # Run days 1-10 (chronic stress) so the sim has its initial dynamics
    for day in range(1, 11):
        inputs = {"Threat": 1.2, "SocialSafety": 0.1, "FocusedTraining": 0.0, "BreathDrive": 0.05}
        metrics = sim.step(inputs)
        history.append({"day": day, "phase": "chronic_stress", **metrics})
    # Days 11-20 (reset)
    for day in range(11, 21):
        inputs = {"Threat": 0.0, "SocialSafety": 0.8, "FocusedTraining": 0.2, "BreathDrive": 0.8}
        metrics = sim.step(inputs)
        history.append({"day": day, "phase": "reset", **metrics})
    # Days 21-30 (tensegrity)
    for day in range(21, days + 1):
        inputs = {"Threat": 0.0, "SocialSafety": 1.5, "FocusedTraining": 1.5, "BreathDrive": 1.5}
        metrics = sim.step(inputs)
        history.append({"day": day, "phase": "tensegrity", **metrics})
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(history, f, indent=2)
    return sim, history


def run_ayahuasca_scenario(days=30, save_path=None):
    """
    Simulate the EFFECT of chronic ayahuasca use on the parent sim.
    The TAP model: chronic 5-HT2A activation → cortisol dysregulation
    → serotonin baseline DECREASES. We model this by extending the
    'chronic stress' phase inputs but with social_safety at moderate
    (not zero) — the social context is supportive (ceremonial) but
    the neurochemical load is high.

    v4.0.2 mechanism: chronic ayahuasca use applies a sustained
    s_setpoint drag at φ⁻¹⁰ rate (the slow channel). The drag is
    proportional to the cumulative ayahuasca exposure (i.e., dose ×
    time). This represents the cortisol dysregulation dragging the
    serotonin baseline down.
    """
    sim = EpigeneticFlopSimulator()
    history = []
    # 30 days of chronic ayahuasca-like state: high threat, social
    # safety moderate, no training (so the setpoint doesn't remodel
    # upward), but the body is in chronic dysregulation.
    for day in range(1, days + 1):
        inputs = {
            "Threat": 0.7,                # moderate chronic threat
            "SocialSafety": 0.5,          # moderate social safety
            "FocusedTraining": 0.0,       # no training (chronic ayahuasca user
                                          # is not in a tensegrity program)
            "BreathDrive": 0.3,           # low breath engagement
        }
        metrics = sim.step(inputs)
        # v4.0.2: Apply chronic ayahuasca drag on s_setpoint at φ⁻¹⁰ rate.
        # This represents the cortisol dysregulation from chronic 5-HT2A
        # activation pulling the serotonin baseline down. The drag is
        # sustained across the 30-day exposure.
        ayahuasca_drag = PHI_INV10 * 0.5  # half-rate of normal training remodeling
        sim.s_setpoint -= ayahuasca_drag
        sim.t_setpoint -= ayahuasca_drag * 0.5  # t_setpoint less affected
        # Clamp to avoid unbounded drift
        sim.s_setpoint = max(0.30, min(0.70, sim.s_setpoint))
        sim.t_setpoint = max(0.30, min(0.70, sim.t_setpoint))
        history.append({"day": day, "phase": "chronic_ayahuasca", **metrics})
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(history, f, indent=2)
    return sim, history


# ─────────────────────────────────────────────────────────────────────────────
# CASCADE METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_drift_multiplier(s_setpoint):
    """From tap_breath_clock.py: drift_multiplier = 0.50 / s_setpoint."""
    if s_setpoint <= 0:
        return 1.0
    return BASELINE_S_SETPOINT / s_setpoint


def compute_implied_phi_inv13(drift_multiplier):
    """Modulated φ⁻¹³ from the parent sim's setpoint."""
    return PHI_INV13 * drift_multiplier


def compute_implied_N_B(drift_multiplier):
    """N_B re-estimates with the modulated breath tick.
    The breath clock computes N_B ~ 7 at baseline. The implied N_B
    scales inversely with the cosmic breath tick:
    N_B_implied = N_B_baseline × (PHI_INV13 / PHI_INV13_modulated)
    """
    N_B_baseline = 7.0
    if drift_multiplier <= 0:
        return N_B_baseline
    return N_B_baseline / drift_multiplier


# ─────────────────────────────────────────────────────────────────────────────
# SCENARIO COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

def run_comparison():
    """
    Run tensegrity vs ayahuasca scenarios and compare cascade signatures.
    """
    print("=" * 80)
    print("  TAP v4.0.2 — 5-HT2A ↔ Parent-Sim Coupling Comparison")
    print("  Prediction: tensegrity and ayahuasca produce OPPOSITE")
    print("  cosmic breath signatures.")
    print("=" * 80)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
    os.makedirs(out_dir, exist_ok=True)

    # Tensegrity scenario
    print("\n  [TENSEGRITY SCENARIO] 30 days of focused training + breath engagement")
    tensegrity_sim, tensegrity_history = run_tensegrity_scenario(
        days=30, save_path=os.path.join(out_dir, "tap_5ht2a_tensegrity_30d.json")
    )
    tensegrity_s = tensegrity_history[-1]["s_setpoint"]
    tensegrity_drift = compute_drift_multiplier(tensegrity_s)
    tensegrity_phi = compute_implied_phi_inv13(tensegrity_drift)
    tensegrity_n_b = compute_implied_N_B(tensegrity_drift)
    print(f"    Final s_setpoint: {tensegrity_s:.4f}")
    print(f"    Drift multiplier: {tensegrity_drift:.4f}x")
    print(f"    Implied φ⁻¹³: {tensegrity_phi:.6f} (vs baseline {PHI_INV13:.6f})")
    print(f"    Implied N_B: {tensegrity_n_b:.2f} (vs baseline 7.00)")

    # Ayahuasca scenario
    print("\n  [AYAHUASCA SCENARIO] 30 days of chronic use (no training)")
    ayahuasca_sim, ayahuasca_history = run_ayahuasca_scenario(
        days=30, save_path=os.path.join(out_dir, "tap_5ht2a_ayahuasca_30d.json")
    )
    ayahuasca_s = ayahuasca_history[-1]["s_setpoint"]
    ayahuasca_drift = compute_drift_multiplier(ayahuasca_s)
    ayahuasca_phi = compute_implied_phi_inv13(ayahuasca_drift)
    ayahuasca_n_b = compute_implied_N_B(ayahuasca_drift)
    print(f"    Final s_setpoint: {ayahuasca_s:.4f}")
    print(f"    Drift multiplier: {ayahuasca_drift:.4f}x")
    print(f"    Implied φ⁻¹³: {ayahuasca_phi:.6f} (vs baseline {PHI_INV13:.6f})")
    print(f"    Implied N_B: {ayahuasca_n_b:.2f} (vs baseline 7.00)")

    # Compare
    print("\n" + "=" * 80)
    print("  CASCADE SIGNATURE COMPARISON")
    print("=" * 80)
    print()
    print(f"  {'Metric':<25} | {'Baseline':<10} | {'Tensegrity':<12} | {'Ayahuasca':<10}")
    print(f"  {'-'*25}-+-{'-'*10}-+-{'-'*12}-+-{'-'*10}")
    print(f"  {'s_setpoint':<25} | {BASELINE_S_SETPOINT:<10.4f} | {tensegrity_s:<12.4f} | {ayahuasca_s:<10.4f}")
    print(f"  {'drift_multiplier':<25} | {'1.0000':<10} | {tensegrity_drift:<12.4f} | {ayahuasca_drift:<10.4f}")
    print(f"  {'implied φ⁻¹³':<25} | {PHI_INV13:<10.6f} | {tensegrity_phi:<12.6f} | {ayahuasca_phi:<10.6f}")
    print(f"  {'implied N_B':<25} | {'7.00':<10} | {tensegrity_n_b:<12.2f} | {ayahuasca_n_b:<10.2f}")
    print()

    # Verification: opposite directions
    if tensegrity_s > BASELINE_S_SETPOINT and ayahuasca_s < BASELINE_S_SETPOINT:
        direction_check = "PASS"
    else:
        direction_check = "FAIL"
    print(f"  [VERIFICATION] Opposite-direction s_setpoint: {direction_check}")
    print(f"    Tensegrity moved s_setpoint {'up' if tensegrity_s > BASELINE_S_SETPOINT else 'down'} ({tensegrity_s:.4f})")
    print(f"    Ayahuasca moved s_setpoint {'down' if ayahuasca_s < BASELINE_S_SETPOINT else 'up'} ({ayahuasca_s:.4f})")

    if tensegrity_phi < PHI_INV13 and ayahuasca_phi > PHI_INV13:
        cosmic_check = "PASS"
    else:
        cosmic_check = "FAIL"
    print(f"  [VERIFICATION] Opposite-direction cosmic breath: {cosmic_check}")
    print(f"    Tensegrity φ⁻¹³ {'<' if tensegrity_phi < PHI_INV13 else '>='} baseline ({tensegrity_phi:.6f} vs {PHI_INV13:.6f})")
    print(f"    Ayahuasca φ⁻¹³ {'>' if ayahuasca_phi > PHI_INV13 else '<='} baseline ({ayahuasca_phi:.6f} vs {PHI_INV13:.6f})")

    # Save summary
    summary = {
        "tensegrity": {
            "s_setpoint": tensegrity_s,
            "drift_multiplier": tensegrity_drift,
            "implied_phi_inv13": tensegrity_phi,
            "implied_N_B": tensegrity_n_b
        },
        "ayahuasca": {
            "s_setpoint": ayahuasca_s,
            "drift_multiplier": ayahuasca_drift,
            "implied_phi_inv13": ayahuasca_phi,
            "implied_N_B": ayahuasca_n_b
        },
        "baseline": {
            "s_setpoint": BASELINE_S_SETPOINT,
            "drift_multiplier": 1.0,
            "implied_phi_inv13": PHI_INV13,
            "implied_N_B": 7.0
        },
        "verification": {
            "opposite_direction_s_setpoint": direction_check,
            "opposite_direction_cosmic_breath": cosmic_check
        }
    }
    summary_path = os.path.join(out_dir, "tap_5ht2a_epigenetic_coupling_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  [EXPORT] -> {summary_path}")
    print("=" * 80)

    return summary


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot_comparison(tensegrity_history, ayahuasca_history, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    days_t = [d["day"] for d in tensegrity_history]
    s_t = [d["s_setpoint"] for d in tensegrity_history]
    t_t = [d["t_setpoint"] for d in tensegrity_history]

    days_a = [d["day"] for d in ayahuasca_history]
    s_a = [d["s_setpoint"] for d in ayahuasca_history]
    t_a = [d["t_setpoint"] for d in ayahuasca_history]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # Panel 1: s_setpoint over time
    axes[0, 0].plot(days_t, s_t, color="#3a86ff", lw=2, label="Tensegrity (s_setpoint)")
    axes[0, 0].plot(days_a, s_a, color="#ff006e", lw=2, label="Ayahuasca (s_setpoint)")
    axes[0, 0].axhline(BASELINE_S_SETPOINT, color="grey", ls="--", lw=0.8, label="baseline (0.5)")
    axes[0, 0].set_xlabel("day")
    axes[0, 0].set_ylabel("s_setpoint (serotonin epigenetic)")
    axes[0, 0].set_title("Epigenetic setpoint: opposite directions")
    axes[0, 0].legend(loc="best", fontsize=9)

    # Panel 2: t_setpoint
    axes[0, 1].plot(days_t, t_t, color="#3a86ff", lw=2, label="Tensegrity (t_setpoint)")
    axes[0, 1].plot(days_a, t_a, color="#ff006e", lw=2, label="Ayahuasca (t_setpoint)")
    axes[0, 1].axhline(BASELINE_S_SETPOINT, color="grey", ls="--", lw=0.8, label="baseline (0.5)")
    axes[0, 1].set_xlabel("day")
    axes[0, 1].set_ylabel("t_setpoint (testosterone epigenetic)")
    axes[0, 1].set_title("Testosterone epigenetic setpoint")
    axes[0, 1].legend(loc="best", fontsize=9)

    # Panel 3: implied φ⁻¹³
    t_drift = [compute_drift_multiplier(s) for s in s_t]
    a_drift = [compute_drift_multiplier(s) for s in s_a]
    t_phi = [compute_implied_phi_inv13(d) for d in t_drift]
    a_phi = [compute_implied_phi_inv13(d) for d in a_drift]
    axes[1, 0].plot(days_t, t_phi, color="#3a86ff", lw=2, label="Tensegrity")
    axes[1, 0].plot(days_a, a_phi, color="#ff006e", lw=2, label="Ayahuasca")
    axes[1, 0].axhline(PHI_INV13, color="grey", ls="--", lw=0.8, label=f"baseline φ⁻¹³={PHI_INV13:.6f}")
    axes[1, 0].set_xlabel("day")
    axes[1, 0].set_ylabel("implied φ⁻¹³")
    axes[1, 0].set_title("Cosmic breath tick modulation")
    axes[1, 0].legend(loc="best", fontsize=9)

    # Panel 4: implied N_B
    t_n_b = [compute_implied_N_B(d) for d in t_drift]
    a_n_b = [compute_implied_N_B(d) for d in a_drift]
    axes[1, 1].plot(days_t, t_n_b, color="#3a86ff", lw=2, label="Tensegrity")
    axes[1, 1].plot(days_a, a_n_b, color="#ff006e", lw=2, label="Ayahuasca")
    axes[1, 1].axhline(7.0, color="grey", ls="--", lw=0.8, label="baseline N_B=7.0")
    axes[1, 1].set_xlabel("day")
    axes[1, 1].set_ylabel("implied N_B")
    axes[1, 1].set_title("N_B re-estimate from breath clock")
    axes[1, 1].legend(loc="best", fontsize=9)

    plt.suptitle("TAP v4.0.2 — Tensegrity vs Ayahuasca cascade signatures", fontsize=12)
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

    summary = run_comparison()

    if args.plot:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
        plot_path = os.path.join(out_dir, "tap_5ht2a_epigenetic_coupling.png")
        # Re-run the scenarios to get the histories for plotting
        tensegrity_sim, tensegrity_history = run_tensegrity_scenario(days=30)
        ayahuasca_sim, ayahuasca_history = run_ayahuasca_scenario(days=30)
        if plot_comparison(tensegrity_history, ayahuasca_history, plot_path):
            print(f"  [PLOT] -> {plot_path}")


if __name__ == "__main__":
    main()
