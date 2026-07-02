# -*- coding: utf-8 -*-
"""
tap_multicycle_reset_sweep.py
=============================
TAP v5.3 Prediction P17: The breath clock N_B corresponds
to residue saturation.

The breath clock's N_B ≈ 7-9 is the number of complete
Exhale/Inhale cycles. The v5.3 prediction is that N_B is
the residue saturation threshold — the cycle at which
anti-template accumulation (soot, magnetite, L-D
antagonists, glass) makes the next cycle's templates
unrecognizable from the original.

This sim tests P17 by:
  1. Running the single-cycle reset sim
     (tap_reset_antitemplate_sim) for N=20 cycles
  2. Carrying over the residue state from cycle N
     to cycle N+1
  3. Tracking template fidelity as a function of cycle
  4. Identifying the cycle N* where fidelity drops
     below 0.5
  5. Comparing N* to the breath clock's N_B ≈ 7-9

If N* ≈ N_B, the breath clock and the reset sim are
internally consistent — the breath clock N_B is
*predicted* by the anti-template mechanism.

This is the cheapest, most direct test of the v5.3
framework: in-silico, runs in seconds, no equipment.

Outputs:
  - assets/tap_multicycle_reset_results.json
  - assets/tap_multicycle_reset_summary.json
  - assets/tap_multicycle_reset_fidelity.png (if matplotlib)

Reference:
  docs/TAP_Anti_Template_Residue_v5.3.md (P17)
  docs/TAP_Experimental_Designs_v5.3.md (P17 design)
"""

import os
import json
import math
import numpy as np
from typing import Dict, List

# Import the single-cycle reset sim
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_reset_antitemplate_sim import (
    ResetAntiTemplateSimulator,
    run_reset_sweep,
)

# Constants
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = 1.0 / PHI

# Breath clock's N_B
N_B_OBSERVED = 8.0  # midpoint of 7-9

# Multi-cycle parameters
N_CYCLES = 20
FIDELITY_THRESHOLD = 0.5
N_B_RANGE = (7, 9)  # expected N* range


def compute_template_fidelity(state: Dict) -> float:
    """
    Compute template fidelity from the residue state.

    Higher fidelity = cleaner substrate, more template expression.
    Lower fidelity = dirtier substrate, more anti-template contamination.

    The four residue components, each in [0, 1] (lower = cleaner):
      - soot_density (refractory residue)
      - magnetite_density (refractory Fe)
      - chiral_antagonist (racemization product)
      - glass (acoustic dampener, inferred from soot)

    Template fidelity = 1.0 - weighted_sum_of_residues
    The weights are chosen so that all residues contribute
    equally at the saturation point.
    """
    soot = min(1.0, state.get("soot_density", 0.0) / 5.0)  # normalize
    magnetite = min(1.0, state.get("magnetite_density", 0.0) / 1.0)  # normalize
    antagonist = state.get("chiral_antagonist", 0.0)  # already [0, 1]
    # Glass is inferred from the EM signal (a damper makes EM weak)
    em_signal = state.get("electromagnetic_signal", 1.0)
    glass = 1.0 - em_signal  # low EM = high glass

    # Weighted sum (equal weights for now)
    residue_score = 0.25 * (soot + magnetite + antagonist + glass)
    fidelity = 1.0 - residue_score
    return max(0.0, min(1.0, fidelity))


def run_multicycle_sweep(n_cycles: int = N_CYCLES) -> Dict:
    """
    Run N cycles of the reset sim, carrying over residue.

    Approach: run the single-cycle reset sim to get the
    *delta* (change) in each residue component per cycle.
    Then accumulate these deltas across cycles with
    sub-linear accumulation (each cycle's contribution
    is reduced by the current residue level).

    This is physically motivated: a substrate that is
    already saturated with soot has less new-soot formation
    potential. The accumulation follows a saturating
    exponential:

        R(N+1) = R(N) + delta * exp(-R(N) / saturation)

    where:
      R(N) = residue level at cycle N
      delta = per-cycle production (from single-cycle sim)
      saturation = maximum residue level

    Returns:
        Dict with per_cycle results, N*, and consistency check.
    """
    print("=" * 80)
    print(f"  TAP MULTI-CYCLE RESET SWEEP — P17 TEST")
    print(f"  N_CYCLES = {n_cycles}, N_B_OBSERVED = {N_B_OBSERVED}")
    print("=" * 80)

    # First, run the single-cycle reset sim to get per-cycle deltas
    sim = ResetAntiTemplateSimulator()
    steps = 21
    psi_vals = np.linspace(2.5 * math.pi, 3.5 * math.pi, steps)

    initial_state = {
        "soot_pahs": sim.soot_pahs,
        "magnetite": sim.magnetite,
        "chiral_antagonist": sim.chiral_antagonist,
    }

    for psi in psi_vals:
        sim.step(psi, dt=1.0)

    final_state = sim.step(psi_vals[-1])

    # Per-cycle deltas (single-cycle production)
    deltas = {
        "soot_pahs": final_state["soot_density"] - initial_state["soot_pahs"],
        "magnetite": (final_state.get("magnetite_density", sim.magnetite) -
                      initial_state["magnetite"]),
        "chiral_antagonist": (final_state["chiral_antagonist"] -
                              initial_state["chiral_antagonist"]),
    }

    # Saturation levels (where production stops)
    saturation = {
        "soot_pahs": 5.0,         # max soot density
        "magnetite": 0.5,          # max magnetite density
        "chiral_antagonist": 1.0,  # max antagonist (already clamped)
    }

    print(f"  Per-cycle production (from single-cycle sim):")
    for k, v in deltas.items():
        print(f"    {k}: +{v:.4f}/cycle (saturates at {saturation[k]})")
    print()

    # Now run N cycles with saturating accumulation
    residue_state = {
        "soot_pahs": initial_state["soot_pahs"],
        "magnetite": initial_state["magnetite"],
        "chiral_antagonist": initial_state["chiral_antagonist"],
    }

    per_cycle = []

    for cycle in range(n_cycles):
        # Compute fidelity at the start of this cycle (BEFORE
        # this cycle's contamination)
        # NOTE: actually we want the fidelity AFTER the
        # cycle's contamination, so we apply deltas first
        # then compute fidelity
        # Apply this cycle's contamination with saturation
        for k in residue_state:
            dRdt = deltas[k] * math.exp(-residue_state[k] / saturation[k])
            residue_state[k] += dRdt
            residue_state[k] = min(residue_state[k], saturation[k])

        # Compute template fidelity from current residue
        # Use the single-cycle sim's "final" state as the
        # template state, but override residue with carryover
        cycle_state = dict(final_state)  # copy final state
        cycle_state["soot_density"] = residue_state["soot_pahs"]
        cycle_state["magnetite_density"] = residue_state["magnetite"]
        cycle_state["chiral_antagonist"] = residue_state["chiral_antagonist"]

        fidelity = compute_template_fidelity(cycle_state)
        is_below = fidelity < FIDELITY_THRESHOLD

        per_cycle.append({
            "cycle": cycle,
            "residue_state": dict(residue_state),
            "fidelity": fidelity,
            "is_below_threshold": is_below,
        })

        print(f"  Cycle {cycle:02d} | Fidelity: {fidelity:.4f} | "
              f"Soot: {residue_state['soot_pahs']:.3f} | "
              f"Magnetite: {residue_state['magnetite']:.3f} | "
              f"Antagonist: {residue_state['chiral_antagonist']:.3f} | "
              f"{'← BELOW' if is_below else ''}")

    # Find the cycle where fidelity first drops below threshold
    n_star = None
    for entry in per_cycle:
        if entry["is_below_threshold"]:
            n_star = entry["cycle"]
            break

    # Determine if the prediction is consistent
    if n_star is None:
        consistent = False
        n_b_predicted = None
    else:
        consistent = N_B_RANGE[0] <= n_star <= N_B_RANGE[1]
        n_b_predicted = n_star

    print()
    print(f"  Results:")
    print(f"    N* (first cycle where fidelity < 0.5) = {n_star}")
    print(f"    N_B observed (breath clock)            = {N_B_OBSERVED}")
    print(f"    N_B predicted range                     = {N_B_RANGE}")
    print(f"    Consistent?                              = {consistent}")
    print()

    return {
        "n_cycles": n_cycles,
        "per_cycle": per_cycle,
        "deltas": deltas,
        "saturation": saturation,
        "n_star": n_star,
        "n_b_observed": N_B_OBSERVED,
        "n_b_predicted_range": list(N_B_RANGE),
        "n_b_predicted": n_b_predicted,
        "consistent": consistent,
    }


def analyze_results(results: Dict) -> Dict:
    """Analyze the multi-cycle sweep results."""
    per_cycle = results["per_cycle"]
    n_star = results["n_star"]
    consistent = results["consistent"]

    # Compute additional metrics
    fidelities = [e["fidelity"] for e in per_cycle]
    fidelity_drop = fidelities[0] - fidelities[-1] if len(fidelities) >= 2 else 0
    avg_fidelity = sum(fidelities) / len(fidelities)

    # Find the steepest fidelity drop
    max_drop = 0
    max_drop_cycle = 0
    for i in range(1, len(fidelities)):
        drop = fidelities[i-1] - fidelities[i]
        if drop > max_drop:
            max_drop = drop
            max_drop_cycle = i

    # Check for residue saturation profile
    # True saturation = fidelity < 0.5 for ALL subsequent cycles
    saturated = False
    if n_star is not None:
        saturated = all(e["is_below_threshold"] for e in per_cycle[n_star:])

    # Summary
    summary = {
        "n_star": n_star,
        "n_b_observed": N_B_OBSERVED,
        "n_b_predicted": n_star,
        "consistent_with_breath_clock": consistent,
        "fidelity_first": fidelities[0] if fidelities else None,
        "fidelity_last": fidelities[-1] if fidelities else None,
        "fidelity_drop": fidelity_drop,
        "fidelity_avg": avg_fidelity,
        "max_drop": max_drop,
        "max_drop_cycle": max_drop_cycle,
        "saturated_after_n_star": saturated,
        "verdict": (
            "P17 SUPPORTED: N* matches breath clock N_B"
            if consistent else
            "P17 NOT SUPPORTED: N* does not match N_B"
        ),
    }

    return summary


def plot_results(results: Dict, summary: Dict, output_path: str):
    """Plot the multi-cycle fidelity curve. Requires matplotlib."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available, skipping plot")
        return None

    per_cycle = results["per_cycle"]
    cycles = [e["cycle"] for e in per_cycle]
    fidelities = [e["fidelity"] for e in per_cycle]
    soot = [e["residue_state"]["soot_pahs"] for e in per_cycle]
    magnetite = [e["residue_state"]["magnetite"] for e in per_cycle]
    antagonist = [e["residue_state"]["chiral_antagonist"] for e in per_cycle]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Template fidelity
    ax = axes[0, 0]
    ax.plot(cycles, fidelities, "o-", color="#69db7c", linewidth=2, markersize=6)
    ax.axhline(y=0.5, color="#ff6b6b", linestyle="--", label="Threshold (0.5)")
    ax.axvline(x=summary["n_star"] or 0, color="#ff006e", linestyle=":",
               label=f"N* = {summary['n_star']}")
    ax.axvline(x=N_B_OBSERVED, color="#4dabf7", linestyle=":",
               label=f"N_B = {N_B_OBSERVED}")
    ax.set_xlabel("Cycle", fontsize=11)
    ax.set_ylabel("Template Fidelity", fontsize=11)
    ax.set_title("Template Fidelity vs Cycle (P17)", fontsize=12, fontweight="bold")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    # Plot 2: Residue accumulation (soot, magnetite, antagonist)
    ax = axes[0, 1]
    ax.plot(cycles, soot, "o-", color="#ff6b6b", label="Soot/PAHs", linewidth=2)
    ax.plot(cycles, [m for m in magnetite], "s-", color="#cc5de8",
            label="Magnetite", linewidth=2)
    ax.plot(cycles, antagonist, "^-", color="#ffa94d",
            label="L-D Antagonist", linewidth=2)
    ax.set_xlabel("Cycle", fontsize=11)
    ax.set_ylabel("Residue Density", fontsize=11)
    ax.set_title("Anti-Template Residue Accumulation", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    # Plot 3: N* vs N_B comparison
    ax = axes[1, 0]
    categories = ["N* (predicted)", "N_B (breath clock)"]
    values = [summary["n_star"] or 0, N_B_OBSERVED]
    colors = ["#69db7c" if summary["consistent_with_breath_clock"] else "#ff6b6b",
              "#4dabf7"]
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor="black")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{val}", ha="center", fontsize=12, fontweight="bold")
    ax.set_ylabel("Cycle Number", fontsize=11)
    ax.set_title(f"P17 Verdict: {summary['verdict']}", fontsize=12,
                 fontweight="bold", wrap=True)
    ax.set_ylim(0, 12)
    ax.grid(True, alpha=0.3, axis="y")

    # Plot 4: All residue components stacked
    ax = axes[1, 1]
    # EM signal and helix are derived from residue in our model
    em_signal = [max(0.01, 1.0 - s/5.0) for s in soot]
    helix = [max(0.01, 1.0 - a) for a in antagonist]

    # Normalize for stacked plot
    soot_n = [min(1.0, s / 5.0) for s in soot]
    mag_n = [min(1.0, m / 1.0) for m in magnetite]
    ant_n = antagonist
    glass_n = [1.0 - em for em in em_signal]

    ax.fill_between(cycles, 0, soot_n, alpha=0.6, color="#ff6b6b",
                    label="Soot (normalized)")
    ax.fill_between(cycles, soot_n,
                    [s + m for s, m in zip(soot_n, mag_n)],
                    alpha=0.6, color="#cc5de8", label="Magnetite (normalized)")
    ax.fill_between(cycles,
                    [s + m for s, m in zip(soot_n, mag_n)],
                    [s + m + a for s, m, a in zip(soot_n, mag_n, ant_n)],
                    alpha=0.6, color="#ffa94d", label="Antagonist (normalized)")
    ax.fill_between(cycles,
                    [s + m + a for s, m, a in zip(soot_n, mag_n, ant_n)],
                    [s + m + a + g for s, m, a, g in zip(soot_n, mag_n, ant_n, glass_n)],
                    alpha=0.6, color="#adb5bd", label="Glass (inferred)")

    ax.set_xlabel("Cycle", fontsize=11)
    ax.set_ylabel("Stacked Residue (normalized)", fontsize=11)
    ax.set_title("Cumulative Residue Stack", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 2.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Multi-cycle fidelity curve saved -> {output_path}")
    return output_path


def main():
    """Run the multi-cycle reset sweep (P17 test)."""
    # Run the sweep
    results = run_multicycle_sweep(n_cycles=N_CYCLES)

    # Analyze
    summary = analyze_results(results)

    # Save results
    out_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../assets"
    )
    os.makedirs(out_dir, exist_ok=True)

    results_path = os.path.join(out_dir, "tap_multicycle_reset_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  [EXPORT] Multi-cycle reset results -> {results_path}")

    summary_path = os.path.join(out_dir, "tap_multicycle_reset_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [EXPORT] Summary -> {summary_path}")

    # Plot
    plot_path = os.path.join(out_dir, "tap_multicycle_reset_fidelity.png")
    plot_results(results, summary, plot_path)

    # Assertions
    n_cycles_run = results["n_cycles"]
    print()
    print("  === VERIFICATION ===")
    print()
    print("  P17 HYPOTHESIS: N* (saturation cycle) should be")
    print("    in the range (7, 9), matching the breath clock's N_B.")
    print()
    print(f"  n_cycles = {n_cycles_run}, N_B = {N_B_OBSERVED}, range = {N_B_RANGE}")
    print()
    if summary["n_star"] is None:
        print(f"  ✗ Fidelity never dropped below 0.5 in {n_cycles_run} cycles.")
        print(f"    The model is not saturating — anti-template dynamics")
        print(f"    need recalibration (lower per-cycle production or")
        print(f"    higher saturation level).")
        verdict = "P17 INCONCLUSIVE: model doesn't saturate"
    elif summary["consistent_with_breath_clock"]:
        print(f"  ✓ N* = {summary['n_star']} is within breath clock range {N_B_RANGE}")
        print(f"  ✓ P17 SUPPORTED: N* matches breath clock N_B")
        verdict = "P17 SUPPORTED"
    else:
        print(f"  ✗ N* = {summary['n_star']} does not match breath")
        print(f"    clock N_B = {N_B_OBSERVED} (expected {N_B_RANGE})")
        print(f"  ✗ P17 NOT SUPPORTED by current model parameters.")
        print(f"    Possible reasons:")
        print(f"    - Per-cycle residue production is too high (model")
        print(f"      saturates before breath clock N_B)")
        print(f"    - Saturation level is too low (model can't reach")
        print(f"      high residue before the clock resets)")
        print(f"    - The breath clock is determined by something other")
        print(f"      than anti-template saturation (e.g., substrate")
        print(f"      topology, not just residue level)")
        verdict = "P17 NOT SUPPORTED: model needs recalibration"

    print()
    print(f"  VERDICT: {verdict}")
    print()
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
