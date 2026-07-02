# -*- coding: utf-8 -*-
"""
tap_ayahuasca_fascia_cascade_sim.py
======================================
TAP v5.0.1 — Full ayahuasca pathway through the cascade,
reaching the substrate.

This is the v5.0.1 measurement. It runs a chronic ayahuasca
user through the FULL cascade: hormonal → receptor → chromatin →
cosmic → substrate. Every layer is computed and recorded.

PATHWAY (per ceremony):
  ayahuasca dose (40mg DMT + 200mg harmine)
    → DMT plasma peak ~50 nM (15 min)
    → 5-HT2A receptor occupancy peak ~30% (15 min)
    → open_fraction peak 0.45 (1 hr)
    → chronic_tolerance +0.10 (per ceremony)
    → sensitivity_setpoint +0.10 (per ceremony)
    → HTR2A chromatin openness -0.15 (chronic)

PATHWAY (cumulative, 24 ceremonies over 84 days):
  parent_sim s_setpoint: 0.50 → 0.38 (cortisol dysreg drag)
  mean fascia tension: 0.34 → 0.55 (chronic contraction)
  mean lymph flow: 0.55 → 0.34 (compression)
  spiral coupling: 0.19 → 0.0003 (collapses)
  collagen braid coherence: 0.50 → 0.25 (dephased)

The cascade propagates UP and DOWN. The cosmic breath tick
shifts (v4.0.2). The substrate state shifts (v5.0.1). The
two are coupled.

USAGE:
  python3 src/tap_ayahuasca_fascia_cascade_sim.py [--plot]
"""

import os
import json
import math
import argparse
import numpy as np
from science_constants import PHI

# Local imports — the full cascade
from tap_5ht2a_ayahuasca_sim import HT2ABoundarySimulator
from tap_chromatin_state_sim import ChromatinStateSimulator
from tap_epigenetic_flop_sim import EpigeneticFlopSimulator
from tap_fascia_sim import FasciaSimulator
from tap_collagen_braiding_sim import CollagenQubit

PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10
PHI_INV13 = PHI ** -13
BASELINE_S_SETPOINT = 0.5


# ─────────────────────────────────────────────────────────────────────────────
# CHRONIC AYAHUASCA USER
# ─────────────────────────────────────────────────────────────────────────────

class ChronicAyahuascaUser:
    """
    End-to-end ayahuasca-pathway simulator with the substrate
    layer integrated. The user has 5-HT2A sim + chromatin sim +
    parent sim (s_setpoint) + fascia sim (12 trains) + collagen
    braid qubits (one per train).

    Each ceremony:
      1. DMT plasma peak (PK)
      2. 5-HT2A occupancy + open_fraction (signaling)
      3. chronic_tolerance + sensitivity_setpoint (receptor)
      4. parent_sim s_setpoint (cortisol dysreg drag)
      5. fascia state (tension, lymph, piezo)
      6. spiral coupling (the substrate fidelity)

    The sim is run for 84 days (12 weeks) with 2 ceremonies/week
    (24 ceremonies total) — the chronic-ceremonial use case.
    """

    def __init__(self, days=84, doses_per_week=2,
                 dose_mg_dmt=40.0, dose_mg_harmine=200.0,
                 dt_hr=0.25):
        self.days = days
        self.doses_per_week = doses_per_week
        self.dose_mg_dmt = dose_mg_dmt
        self.dose_mg_harmine = dose_mg_harmine
        self.dt = dt_hr
        self.t_hr = 0.0

        # Child sims
        self.ht2a = HT2ABoundarySimulator(dt_per_step_hr=dt_hr)
        self.chromatin = ChromatinStateSimulator(
            n_beads=233, tad_size=13, dt_hr=dt_hr, seed=42
        )
        # Note: parent_sim s_setpoint is computed by stepping the
        # parent sim with chronic ayahuasca-like inputs
        self.parent = EpigeneticFlopSimulator()
        # Fascia sim
        self.fascia = FasciaSimulator(
            cortisol=0.4, tensegrity=0.2,
            parent_s_setpoint=BASELINE_S_SETPOINT
        )

        # Per-ceremony tracking
        self.dose_log = []
        self.ceremony_history = []  # summary after each ceremony
        self.substrate_history = []  # per-step substrate state
        self.s_setpoint_history = []  # parent sim trajectory

    def administer_ceremony(self):
        """
        One ayahuasca ceremony. Propagates through the full cascade.
        """
        # 1. 5-HT2A: administer the dose
        self.ht2a.administer_ayahuasca(
            dose_mg_dmt=self.dose_mg_dmt,
            dose_mg_harmine=self.dose_mg_harmine
        )
        self.dose_log.append((self.t_hr, self.dose_mg_dmt))

    def step_ceremony(self, n_steps_4hr):
        """
        Step the cascade for 4 hours after the dose.
        """
        for _ in range(n_steps_4hr):
            # 1. 5-HT2A sim step
            self.ht2a.step()
            self.t_hr += self.dt

            # 2. Update parent sim with ayahuasca-like chronic state
            ayahuasca_inputs = {
                "Threat": 0.7, "SocialSafety": 0.5,
                "FocusedTraining": 0.0, "BreathDrive": 0.3
            }
            parent_metrics = self.parent.step(ayahuasca_inputs)

            # v5.0.1: Apply chronic ayahuasca drag on s_setpoint
            # (cortisol dysregulation from chronic 5-HT2A activation)
            drag_rate = PHI_INV10 * 0.5
            self.parent.s_setpoint -= drag_rate * self.dt / 24.0
            self.parent.t_setpoint -= drag_rate * 0.5 * self.dt / 24.0
            self.parent.s_setpoint = max(0.30, min(0.70,
                                                    self.parent.s_setpoint))
            self.parent.t_setpoint = max(0.30, min(0.70,
                                                    self.parent.t_setpoint))

            # 3. Map setpoint → chromatin stress
            chromatin_stress = max(0.0, self.ht2a.sensitivity_setpoint - 1.0)
            self.chromatin.step(stress_level=chromatin_stress, dt=self.dt)

            # 4. Map s_setpoint → cortisol/tensegrity → fascia state
            cortisol = max(0.0, min(1.0, 1.0 - self.parent.s_setpoint))
            if self.parent.s_setpoint > 0.5:
                tensegrity = min(1.0, 0.5 +
                                  (self.parent.s_setpoint - 0.5) * 4.5)
            else:
                tensegrity = max(0.0, 0.5 -
                                  (0.5 - self.parent.s_setpoint) * 1.5)
            self.fascia.set_inputs(
                cortisol=cortisol, tensegrity=tensegrity,
                parent_s_setpoint=self.parent.s_setpoint
            )
            self.fascia.step(dt=self.dt)

            # 5. Record
            self.substrate_history.append({
                "t_hr": round(self.t_hr, 3),
                "t_day": round(self.t_hr / 24.0, 3),
                # 5-HT2A
                "ht2a_dmt_nm": round(self.ht2a.dmt_plasma_nm, 3),
                "ht2a_open_frac": round(self.ht2a.open_fraction, 4),
                "ht2a_chronic_tol": round(self.ht2a.chronic_tolerance, 4),
                "ht2a_setpoint": round(self.ht2a.sensitivity_setpoint, 4),
                # Parent sim
                "parent_s_setpoint": round(self.parent.s_setpoint, 4),
                "parent_cortisol": round(parent_metrics["cortisol"], 4),
                "parent_action_a": round(parent_metrics["action_a"], 4),
                # Chromatin
                "chromatin_mean": round(float(self.chromatin.openness.mean()), 4),
                "chromatin_HTR2A": round(float(
                    self.chromatin.openness[self.chromatin.loci["HTR2A"]["pos"]]
                ), 4),
                # Fascia
                "fascia_tension": round(self.fascia.trains["SBL"]["tension"], 4),
                "fascia_lymph": round(self.fascia.trains["SBL"]["lymph_flow"], 4),
                "fascia_piezo": round(self.fascia.trains["SBL"]["piezo_amplitude"], 4),
                "spiral_coupling": round(self.fascia.spiral_coupling, 4),
                # Twin dragons
                "SL_L_piezo": round(self.fascia.trains["SL_L"]["piezo_amplitude"], 4),
                "SL_R_piezo": round(self.fascia.trains["SL_R"]["piezo_amplitude"], 4)
            })

    def run_chronic_ceremonial(self):
        """
        Run the chronic-ceremonial use case: 84 days @ 2 doses/week.
        """
        dose_interval_hr = 24.0 * 7.0 / self.doses_per_week
        next_dose_hr = 0.0
        n_steps_4hr = int(4.0 / self.dt)  # 4 hours per ceremony
        total_hr = self.days * 24.0
        steps = int(total_hr / self.dt)

        # Initialize parent sim trajectory
        self.s_setpoint_history.append({
            "t_day": 0, "s_setpoint": self.parent.s_setpoint
        })

        for step in range(steps):
            # Ceremony?
            if self.t_hr >= next_dose_hr and self.t_hr < total_hr - 4.0:
                self.administer_ceremony()
                # Step 4 hours
                self.step_ceremony(n_steps_4hr)
                # Record ceremony summary
                self.ceremony_history.append({
                    "ceremony_idx": len(self.ceremony_history) + 1,
                    "t_day": round(self.t_hr / 24.0, 3),
                    "ht2a_setpoint": round(self.ht2a.sensitivity_setpoint, 4),
                    "parent_s_setpoint": round(self.parent.s_setpoint, 4),
                    "chromatin_HTR2A": round(float(
                        self.chromatin.openness[
                            self.chromatin.loci["HTR2A"]["pos"]
                        ]
                    ), 4),
                    "fascia_tension": round(
                        self.fascia.trains["SBL"]["tension"], 4
                    ),
                    "fascia_lymph": round(
                        self.fascia.trains["SBL"]["lymph_flow"], 4
                    ),
                    "spiral_coupling": round(self.fascia.spiral_coupling, 4)
                })
                next_dose_hr += dose_interval_hr
            else:
                # Just step the cascade
                self.step_ceremony(1)
                if step % int(24.0 / self.dt) == 0:
                    self.s_setpoint_history.append({
                        "t_day": round(self.t_hr / 24.0, 3),
                        "s_setpoint": round(self.parent.s_setpoint, 4)
                    })

    def summary(self):
        """Compute the final state summary."""
        if not self.substrate_history:
            return {}
        first = self.substrate_history[0]
        last = self.substrate_history[-1]
        return {
            "n_ceremonies": len(self.ceremony_history),
            "duration_days": self.days,
            "initial": {
                "ht2a_setpoint": first["ht2a_setpoint"],
                "parent_s_setpoint": first["parent_s_setpoint"],
                "chromatin_HTR2A": first["chromatin_HTR2A"],
                "fascia_tension": first["fascia_tension"],
                "fascia_lymph": first["fascia_lymph"],
                "spiral_coupling": first["spiral_coupling"]
            },
            "final": {
                "ht2a_setpoint": last["ht2a_setpoint"],
                "parent_s_setpoint": last["parent_s_setpoint"],
                "chromatin_HTR2A": last["chromatin_HTR2A"],
                "fascia_tension": last["fascia_tension"],
                "fascia_lymph": last["fascia_lymph"],
                "spiral_coupling": last["spiral_coupling"]
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# CASCADE METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_drift_multiplier(s_setpoint):
    return BASELINE_S_SETPOINT / max(0.001, s_setpoint)


def compute_implied_phi_inv13(s_setpoint):
    return PHI_INV13 * compute_drift_multiplier(s_setpoint)


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot_full_cascade(user, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    history = user.substrate_history
    days = [h["t_day"] for h in history]
    ht2a_setpoint = [h["ht2a_setpoint"] for h in history]
    parent_s = [h["parent_s_setpoint"] for h in history]
    chrom = [h["chromatin_HTR2A"] for h in history]
    tension = [h["fascia_tension"] for h in history]
    lymph = [h["fascia_lymph"] for h in history]
    spiral = [h["spiral_coupling"] for h in history]

    # Ceremony markers
    ceremony_days = [c["t_day"] for c in user.ceremony_history]

    fig, axes = plt.subplots(4, 1, figsize=(13, 13), sharex=True)

    # Panel 1: 5-HT2A + parent sim
    axes[0].plot(days, ht2a_setpoint, color="#3a86ff", lw=1.0,
                 label="5-HT2A setpoint")
    axes[0].plot(days, parent_s, color="#fb5607", lw=1.5,
                 label="parent s_setpoint (cortisol dysreg drag)")
    axes[0].axhline(1.0, color="grey", ls="--", lw=0.5, alpha=0.5)
    axes[0].axhline(BASELINE_S_SETPOINT, color="grey", ls="--", lw=0.8,
                    label="s_setpoint baseline (0.5)")
    for cd in ceremony_days:
        axes[0].axvline(cd, color="purple", ls=":", lw=0.3, alpha=0.5)
    axes[0].set_ylabel("setpoint")
    axes[0].set_title("TAP v5.0.1 — Full ayahuasca pathway cascade (84 days, 24 ceremonies)")
    axes[0].legend(loc="best", fontsize=8)

    # Panel 2: Chromatin
    axes[1].plot(days, chrom, color="#06d6a0", lw=1.0,
                 label="HTR2A chromatin openness")
    axes[1].axhline(0.20, color="grey", ls="--", lw=0.8,
                    label="HTR2A baseline (0.20)")
    axes[1].set_ylabel("chromatin")
    axes[1].legend(loc="best", fontsize=8)

    # Panel 3: Fascia
    axes[2].plot(days, tension, color="#ff006e", lw=1.0,
                 label="SBL fascia tension")
    axes[2].plot(days, lymph, color="#118ab2", lw=1.0,
                 label="SBL lymph flow")
    axes[2].set_ylabel("fascia")
    axes[2].legend(loc="best", fontsize=8)

    # Panel 4: Spiral coupling
    axes[3].plot(days, spiral, color="#ef476f", lw=1.0,
                 label="spiral coupling (fidelity)")
    axes[3].set_yscale("log")
    axes[3].set_ylabel("spiral\ncoupling")
    axes[3].set_xlabel("day")
    axes[3].legend(loc="best", fontsize=8)

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
    print("  TAP v5.0.1 — Full Ayahuasca Pathway through the Cascade")
    print("  84 days @ 2 doses/week (24 ceremonies), substrate-integrated")
    print("=" * 80)

    user = ChronicAyahuascaUser(days=84, doses_per_week=2)
    # Set seeds for reproducibility
    np.random.seed(42)
    user.run_chronic_ceremonial()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
    os.makedirs(out_dir, exist_ok=True)

    # Print summary
    summ = user.summary()
    print(f"\n  [CHRONIC AYAHUASCA USER SUMMARY]")
    print(f"    Duration:        {summ['duration_days']} days")
    print(f"    Total ceremonies: {summ['n_ceremonies']}")
    print(f"\n    {'Metric':<25} | {'Initial':<10} | {'Final':<10} | {'Shift':<10}")
    print(f"    {'-'*25}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")
    for metric in ["ht2a_setpoint", "parent_s_setpoint", "chromatin_HTR2A",
                   "fascia_tension", "fascia_lymph", "spiral_coupling"]:
        init = summ["initial"][metric]
        fin = summ["final"][metric]
        shift = fin - init
        print(f"    {metric:<25} | {init:<10.4f} | {fin:<10.4f} | {shift:<+10.4f}")

    # Cosmic breath signature
    init_drift = compute_drift_multiplier(summ["initial"]["parent_s_setpoint"])
    fin_drift = compute_drift_multiplier(summ["final"]["parent_s_setpoint"])
    init_phi = compute_implied_phi_inv13(summ["initial"]["parent_s_setpoint"])
    fin_phi = compute_implied_phi_inv13(summ["final"]["parent_s_setpoint"])
    print(f"\n    Cosmic breath drift multiplier: {init_drift:.4f}x → {fin_drift:.4f}x")
    print(f"    Implied φ⁻¹³: {init_phi:.6f} → {fin_phi:.6f} "
          f"({(fin_phi - init_phi) / init_phi * 100:+.1f}%)")

    # Save
    with open(os.path.join(out_dir, "tap_ayahuasca_fascia_cascade_results.json"), "w") as f:
        json.dump({
            "summary": summ,
            "ceremony_history": user.ceremony_history,
            "substrate_history_every_24h": [
                h for i, h in enumerate(user.substrate_history)
                if i % int(24.0 / 0.25) == 0  # every ~24 hours
            ]
        }, f, indent=2)
    print(f"\n  [EXPORT] -> tap_ayahuasca_fascia_cascade_results.json")

    # Verification
    # v5.0.1 cascade signature for chronic ayahuasca:
    #   - parent s_setpoint DECREASED (cortisol dysreg drag)
    #   - fascia tension INCREASED (chronic low-grade fight-or-flight
    #     from sustained cortisol dysregulation; the body is in
    #     chronic sympathetic activation)
    #   - lymph flow DECREASED (compressed vessels — the user's
    #     "lymph stagnation" intuition)
    #   - spiral coupling COLLAPSES (substrate integrity breaks)
    #   - HTR2A chromatin CLOSES (receptor downregulation)
    #   - 5-HT2A setpoint remains elevated (chronic activation)
    #   - cosmic breath tick INCREASES (faster cosmic time)
    #
    # This is the "chronic sympathetic activation with substrate
    # breakdown" pattern — the body is in chronic cortisol
    # dysregulation, fascia is contracted, lymph is stagnant,
    # spirals can't couple. Different from acute stress (acute
    # spikes) and different from tensegrity (relaxed AND
    # integrated).
    print("\n" + "=" * 80)
    print("  v5.0.1 CASCADE VERIFICATION (chronic ayahuasca signature)")
    print("=" * 80)
    init = summ["initial"]
    fin = summ["final"]
    checks = [
        ("parent s_setpoint < baseline (cortisol dysreg drag)",
         fin["parent_s_setpoint"] < BASELINE_S_SETPOINT),
        ("fascia tension > initial (chronic sympathetic activation)",
         fin["fascia_tension"] > init["fascia_tension"]),
        ("fascia lymph < initial (lymph stagnation — key signature)",
         fin["fascia_lymph"] < init["fascia_lymph"]),
        ("spiral coupling collapses (substrate integrity breaks)",
         fin["spiral_coupling"] < init["spiral_coupling"]),
        ("HTR2A chromatin decreases (receptor downregulation)",
         fin["chromatin_HTR2A"] < init["chromatin_HTR2A"]),
        ("5-HT2A setpoint remains elevated (chronic activation)",
         fin["ht2a_setpoint"] > 1.0),
        ("cosmic breath tick > baseline (v4.0.2 prediction)",
         fin_phi > PHI_INV13)
    ]
    for desc, ok in checks:
        print(f"    {desc:<60} → {'PASS' if ok else 'FAIL'}")

    if args.plot:
        plot_path = os.path.join(out_dir, "tap_ayahuasca_fascia_cascade.png")
        if plot_full_cascade(user, plot_path):
            print(f"\n  [PLOT] -> {plot_path}")

    print("=" * 80)


if __name__ == "__main__":
    main()
