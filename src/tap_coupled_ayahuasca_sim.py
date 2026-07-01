# -*- coding: utf-8 -*-
"""
tap_coupled_ayahuasca_sim.py
=============================
TAP Model — Coupled 5-HT2A + Chromatin Simulator

Couples tap_5ht2a_ayahuasca_sim.py and tap_chromatin_state_sim.py
into a single end-to-end pipeline: DMT binding → 5-HT2A activation
→ receptor desensitization → chronic tolerance → setpoint shift →
chromatin remodeling → gene expression change.

THE φ-CASCADE COUPLING:
  The 5-HT2A sim's setpoint (chromatin remodeling level) is read
  by the chromatin sim as a "global chronic perturbation" that
  opens specific stress-responsive loci in proportion to (setpoint
  - 1.0). The chromatin sim's per-locus openness feeds back to the
  5-HT2A sim as a receptor-synthesis-rate modifier (more open
  chromatin = faster receptor turnover, accelerated recovery).

VALIDATION TARGETS:
  - Chronic ayahuasca use should produce measurable chromatin
    state shifts (openness changes at stress-responsive loci).
  - The shift should follow φ⁻¹⁰ kinetics, recoverable in ~15 days.
  - The recovery should be SLOWER than the receptor-level recovery
    (φ⁻⁸), because chromatin is the slow channel.
  - Cumulative dose should correlate with cumulative chromatin
    state shift, with diminishing returns at high setpoint (the
    system has a natural ceiling).

USAGE:
  python3 tap_coupled_ayahuasca_sim.py [--plot]
"""

import os
import json
import math
import argparse
import numpy as np
from science_constants import PHI

# Local imports — the two child sims
from tap_5ht2a_ayahuasca_sim import (
    HT2ABoundarySimulator, DMT_PLASMA_T_HALF_MIN, RIBA_2001_TOLERANCE_AT_4TH_DOSE,
    CALLAWAY_1994_SENSITIVITY_RECOVERY_DAYS
)
from tap_chromatin_state_sim import (
    ChromatinStateSimulator, BASELINE_OPEN_FRACTION, STRESS_RESPONSIVE_LOCI
)

# v4.0.2 — Optional parent-sim coupling
# Read the parent epigenetic sim's s_setpoint (serotonin epigenetic
# setpoint) from tap_epigenetic_flop_results.json. The parent sim's
# setpoint represents the 30-day hormonal trajectory's effect on the
# serotonin baseline. The coupled 5-HT2A sim reads this and uses it
# to compute a "neurochemical modifier" that biases both the
# receptor recovery and the chromatin stress.
try:
    from tap_epigenetic_flop_sim import EpigeneticFlopSimulator
    PARENT_SIM_AVAILABLE = True
except ImportError:
    PARENT_SIM_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# φ-CASCADE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
PHI_INV4 = PHI ** -4    # ≈ 0.146 — signaling
PHI_INV8 = PHI ** -8    # ≈ 0.0213 — receptor turnover
PHI_INV10 = PHI ** -10  # ≈ 0.00813 — chromatin remodeling
PHI_INV13 = PHI ** -13  # ≈ 0.001919 — cosmic breath


# ─────────────────────────────────────────────────────────────────────────────
# COUPLING MAPPINGS
# ─────────────────────────────────────────────────────────────────────────────

def setpoint_to_chromatin_stress(setpoint):
    """
    Map the 5-HT2A sim's sensitivity_setpoint (1.0 = baseline) to
    a chromatin "chronic stress" input in [0, 1].

    Linear mapping: setpoint 1.0 → 0 stress, setpoint 1.5 → 0.5 stress,
    setpoint 2.0 → 1.0 stress. The 2.0 saturation reflects the
    5-HT2A sim's hard clamp at setpoint ≤ 2.5.
    """
    return max(0.0, min(1.0, (setpoint - 1.0) / 1.0))


def chromatin_openness_to_receptor_synthesis(mean_openness):
    """
    Map the chromatin sim's mean openness (around 0.25 baseline)
    to a receptor-synthesis-rate multiplier. More open chromatin
    = more transcriptional activity = faster receptor turnover.

    Returns a multiplier in [0.5, 2.0]. At baseline (0.25) the
    multiplier is 1.0. High openness accelerates φ⁻⁸ recovery;
    low openness slows it.
    """
    if mean_openness <= 0:
        return 0.5
    ratio = mean_openness / BASELINE_OPEN_FRACTION
    # Soft scaling: clamp to [0.5, 2.0]
    return max(0.5, min(2.0, ratio))


# ─────────────────────────────────────────────────────────────────────────────
# COUPLED SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

class CoupledAyahuascaSimulator:
    """
    End-to-end ayahuasca pipeline simulator. Couples 5-HT2A receptor
    dynamics (fast, τ_hr) with chromatin state (slow, τ_days).

    v4.0.2: optionally also couples to the parent epigenetic sim's
    s_setpoint (serotonin epigenetic setpoint). When parent_sim_path
    is given, the 5-HT2A sim's recovery is biased by the parent
    sim's s_setpoint: ayahuasca use should DECREASE s_setpoint
    (cortisol dysregulation), tensegrity should INCREASE it.
    """

    def __init__(self,
                 chromatin_n_beads=233,
                 chromatin_tad_size=13,
                 chromatin_seed=42,
                 dt_hr=0.25,
                 parent_sim_path=None):
        self.dt = dt_hr
        self.t_hr = 0.0

        # Child sims
        self.ht2a = HT2ABoundarySimulator(dt_per_step_hr=dt_hr)
        self.chromatin = ChromatinStateSimulator(
            n_beads=chromatin_n_beads,
            tad_size=chromatin_tad_size,
            dt_hr=dt_hr,
            seed=chromatin_seed
        )

        # v4.0.2: optional parent-sim coupling
        self.parent_sim_path = parent_sim_path
        self.parent_s_setpoint = 0.5  # default to baseline
        self.parent_s_setpoint_history = []  # track parent sim's setpoint
        self._load_parent_sim()

        # Track coupling
        self.history = []
        self.dose_log = []  # list of (t_hr, dose_mg) for each dose

    def _load_parent_sim(self):
        """Load the parent sim's s_setpoint from JSON if available."""
        if not self.parent_sim_path:
            return
        if not os.path.exists(self.parent_sim_path):
            return
        try:
            with open(self.parent_sim_path, "r") as f:
                epi_data = json.load(f)
            if epi_data and len(epi_data) > 0:
                self.parent_s_setpoint = epi_data[-1].get("s_setpoint", 0.5)
        except (json.JSONDecodeError, KeyError):
            pass

    def set_parent_s_setpoint(self, value):
        """Set the parent sim's s_setpoint externally (for live updates)."""
        self.parent_s_setpoint = max(0.30, min(0.70, value))

    def administer_ayahuasca(self, dose_mg_dmt=40.0, dose_mg_harmine=200.0):
        """One ayahuasca dose — propagates to both child sims."""
        self.ht2a.administer_ayahuasca(
            dose_mg_dmt=dose_mg_dmt,
            dose_mg_harmine=dose_mg_harmine
        )
        # NOTE: We do NOT directly push the chromatin sim here. The
        # chromatin sim sees the setpoint shift as a chronic stress
        # input in step(), via the coupling mapping. The dose is
        # recorded for the timeline.
        self.dose_log.append((self.t_hr, dose_mg_dmt))

    def step(self):
        """
        Advance one coupled step (dt hours).
        Order:
          1. 5-HT2A sim advances one step (PK, receptor, setpoint)
          2. Map setpoint → chromatin stress
          3. Chromatin sim advances one step with that stress
          4. Map chromatin openness → receptor-synthesis modifier
          5. Apply modifier to ht2a.sensitivity_setpoint recovery rate
          6. v4.0.2: Apply parent-sim s_setpoint bias to recovery
          7. Record coupled state
        """
        # 1. 5-HT2A step
        self.ht2a.step()
        self.t_hr += self.dt

        # 2. Map setpoint → chromatin stress
        chromatin_stress = setpoint_to_chromatin_stress(
            self.ht2a.sensitivity_setpoint
        )

        # 3. Chromatin step
        self._chromatin_step_with_stress(chromatin_stress)

        # 4. Map chromatin openness → receptor-synthesis modifier
        synth_modifier = chromatin_openness_to_receptor_synthesis(
            float(self.chromatin.openness.mean())
        )

        # 5. Apply modifier to 5-HT2A sensitivity recovery
        if self.ht2a.dmt_plasma_nm < 1.0 and self.ht2a.sensitivity_setpoint > 1.0:
            extra_recovery = (synth_modifier - 1.0) * PHI_INV10 * \
                             (self.ht2a.sensitivity_setpoint - 1.0) * self.dt
            self.ht2a.sensitivity_setpoint -= extra_recovery
            self.ht2a.sensitivity_setpoint = max(1.0, self.ht2a.sensitivity_setpoint)

        # 6. v4.0.2: Apply parent-sim s_setpoint bias
        # The parent sim's s_setpoint represents the systemic serotonin
        # epigenetic baseline. When parent_s_setpoint < 0.5 (ayahuasca
        # user with chronic dysregulation, or in chronic stress), the
        # 5-HT2A recovery from setpoint is SLOWED (extra stickiness).
        # When parent_s_setpoint > 0.5 (tensegrity-trained), recovery
        # is ACCELERATED.
        if self.ht2a.dmt_plasma_nm < 1.0 and self.ht2a.sensitivity_setpoint > 1.0:
            parent_bias = (self.parent_s_setpoint - 0.5) * 0.3  # ±15% modifier
            bias_recovery = parent_bias * PHI_INV10 * \
                            (self.ht2a.sensitivity_setpoint - 1.0) * self.dt
            self.ht2a.sensitivity_setpoint -= bias_recovery
            self.ht2a.sensitivity_setpoint = max(1.0, self.ht2a.sensitivity_setpoint)

        # Track parent sim's setpoint evolution
        self.parent_s_setpoint_history.append(self.parent_s_setpoint)

        # 7. Record coupled state
        self._record_state(chromatin_stress, synth_modifier)

    def _chromatin_step_with_stress(self, stress_level):
        """
        Single step of the chromatin sim with a specified stress level.
        Mirrors the logic in tap_chromatin_state_sim.py's step() but
        inlined here so we can call it from the coupled sim without
        rewriting the dynamics.
        """
        # We need to call the chromatin sim's step with the right
        # stress. The simplest way: temporarily set the chromatin sim's
        # behavior. But the chromatin sim's step() takes stress_level
        # as a parameter, so we can just call it directly.
        # However, the chromatin sim's step() advances time by self.dt
        # and tracks its own history. We don't want to advance its
        # time separately — we want it to advance by self.dt.
        # The chromatin sim's dt should match ours.
        # Just call it.
        self.chromatin.step(stress_level=stress_level, dt=self.dt)

    def _record_state(self, chromatin_stress, synth_modifier):
        """Append current coupled state to history."""
        record = {
            "t_hr": round(self.t_hr, 3),
            "t_day": round(self.t_hr / 24.0, 3),
            # 5-HT2A state
            "ht2a_dmt_nm": round(self.ht2a.dmt_plasma_nm, 3),
            "ht2a_occupancy": round(self.ht2a.occupancy, 4),
            "ht2a_open_fraction": round(self.ht2a.open_fraction, 4),
            "ht2a_sensitivity": round(self.ht2a.sensitivity, 4),
            "ht2a_setpoint": round(self.ht2a.sensitivity_setpoint, 4),
            "ht2a_chronic_tol": round(self.ht2a.chronic_tolerance, 4),
            "ht2a_acute_desens": round(self.ht2a.acute_desens, 4),
            # Coupling
            "chromatin_stress": round(chromatin_stress, 4),
            "synth_modifier": round(synth_modifier, 4),
            "parent_s_setpoint": round(self.parent_s_setpoint, 4),
            # Chromatin state
            "chromatin_mean_open": round(float(self.chromatin.openness.mean()), 4),
            "chromatin_FOS": round(float(self.chromatin.openness[self.chromatin.loci["FOS"]["pos"]]), 4),
            "chromatin_HSP70": round(float(self.chromatin.openness[self.chromatin.loci["HSP70"]["pos"]]), 4),
            "chromatin_NR3C1": round(float(self.chromatin.openness[self.chromatin.loci["NR3C1"]["pos"]]), 4),
            "chromatin_FKBP5": round(float(self.chromatin.openness[self.chromatin.loci["FKBP5"]["pos"]]), 4),
            "chromatin_BDNF": round(float(self.chromatin.openness[self.chromatin.loci["BDNF"]["pos"]]), 4),
            "dose_count": self.ht2a.cumulative_dose_count
        }
        self.history.append(record)


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION PROTOCOLS
# ─────────────────────────────────────────────────────────────────────────────

def run_chronic_ceremonial(sim, days=84, doses_per_week=2):
    """
    Long-term ceremonial ayahuasca use: 12 weeks @ 2 doses/week.
    This is the chronic-use scenario the v3.0 review predicts should
    produce detectable chromatin-level changes.
    """
    dose_interval_hr = 24.0 * 7.0 / doses_per_week
    next_dose_hr = 0.0
    total_hr = days * 24.0
    steps = int(total_hr / sim.dt)
    for step in range(steps):
        if sim.t_hr >= next_dose_hr:
            sim.administer_ayahuasca()
            next_dose_hr += dose_interval_hr
        sim.step()
    return sim.history


def run_chronic_4x_protocol(sim):
    """
    Riba 2001 protocol (4 doses at 4-hr intervals) in the coupled sim.
    Should produce the same Riba-fit result as the standalone 5-HT2A sim
    (since the chromatin coupling is slow, doesn't affect fast dynamics).
    """
    for _ in range(4):
        sim.administer_ayahuasca()
        for _ in range(int(4.0 / sim.dt)):
            sim.step()
    return sim.history


def run_single_dose_recovery(sim, follow_days=30):
    """
    Single dose, then 30 days of recovery. Tests the long-term
    chromatin response to a single ayahuasca exposure.
    """
    sim.administer_ayahuasca()
    total_hr = (1 + follow_days) * 24.0
    steps = int(total_hr / sim.dt)
    for step in range(steps):
        sim.step()
    return sim.history


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_coupled_sim():
    """
    Run the three protocols and check that the coupled sim produces
    consistent results with the standalone sims.
    """
    results = {}

    # 1. Riba 2001 protocol: coupled sim should match standalone
    sim1 = CoupledAyahuascaSimulator()
    hist1 = run_chronic_4x_protocol(sim1)
    peaks = []
    # Track peaks per dose
    dose_boundaries = [i for i, h in enumerate(hist1) if h["dose_count"] > 0 and (i == 0 or h["dose_count"] > hist1[i-1]["dose_count"])]
    for i, start in enumerate(dose_boundaries):
        end = dose_boundaries[i+1] if i+1 < len(dose_boundaries) else len(hist1)
        peaks.append(max(h["ht2a_open_fraction"] for h in hist1[start:end]))
    if peaks[0] > 0:
        riba_ratio = peaks[-1] / peaks[0]
        results["riba_2001_tolerance_coupled"] = {
            "predicted_peak_open_per_dose": [round(p, 4) for p in peaks],
            "predicted_ratio_4th_to_1st": round(riba_ratio, 4),
            "observed_ratio_4th_to_1st": round(RIBA_2001_TOLERANCE_AT_4TH_DOSE, 4),
            "error_pct": round(abs(riba_ratio - RIBA_2001_TOLERANCE_AT_4TH_DOSE) / RIBA_2001_TOLERANCE_AT_4TH_DOSE * 100.0, 2)
        }

    # 2. Chronic ceremonial: chromatin should show cumulative shift
    sim2 = CoupledAyahuascaSimulator()
    initial_chromatin = float(sim2.chromatin.openness.mean())
    hist2 = run_chronic_ceremonial(sim2, days=84, doses_per_week=2)
    final_chromatin = float(sim2.chromatin.openness.mean())
    final_setpoint = sim2.ht2a.sensitivity_setpoint
    final_FOS = float(sim2.chromatin.openness[sim2.chromatin.loci["FOS"]["pos"]])
    final_HSP70 = float(sim2.chromatin.openness[sim2.chromatin.loci["HSP70"]["pos"]])
    results["chronic_ceremonial_84d"] = {
        "duration_days": 84,
        "doses_per_week": 2,
        "total_doses": sim2.ht2a.cumulative_dose_count,
        "initial_chromatin_mean": round(initial_chromatin, 4),
        "final_chromatin_mean": round(final_chromatin, 4),
        "chromatin_shift": round(final_chromatin - initial_chromatin, 4),
        "final_setpoint": round(final_setpoint, 4),
        "final_FOS_openness": round(final_FOS, 4),
        "final_HSP70_openness": round(final_HSP70, 4),
        "tap_prediction": "Chromatin mean should rise above 0.25 baseline; FOS/HSP70 should show sustained openness above their resting baselines (0.10/0.20)."
    }

    # 3. Single dose + recovery
    sim3 = CoupledAyahuascaSimulator()
    hist3 = run_single_dose_recovery(sim3, follow_days=30)
    # Find peak setpoint and recovery
    peak_setpoint = max(h["ht2a_setpoint"] for h in hist3)
    peak_day = next(h["t_day"] for h in hist3 if h["ht2a_setpoint"] == peak_setpoint)
    # Recovery: day at which setpoint returns to within 5% of 1.0
    recovery_day = None
    for h in hist3:
        if h["ht2a_setpoint"] <= 1.005:
            recovery_day = h["t_day"]
            break
    results["single_dose_recovery_30d"] = {
        "peak_setpoint": round(peak_setpoint, 4),
        "peak_day": round(peak_day, 2),
        "setpoint_recovery_day": round(recovery_day, 2) if recovery_day else ">30",
        "tap_expected_setpoint_recovery_day": "≈15 days (φ⁻¹⁰ timescale)"
    }

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING
# ─────────────────────────────────────────────────────────────────────────────

def plot_coupled_results(sim, history, out_path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    days = [h["t_day"] for h in history]
    ht2a_open = [h["ht2a_open_fraction"] for h in history]
    ht2a_setpoint = [h["ht2a_setpoint"] for h in history]
    ht2a_chronic = [h["ht2a_chronic_tol"] for h in history]
    chrom_stress = [h["chromatin_stress"] for h in history]
    chrom_mean = [h["chromatin_mean_open"] for h in history]
    chrom_FOS = [h["chromatin_FOS"] for h in history]
    chrom_HSP70 = [h["chromatin_HSP70"] for h in history]
    chrom_FKBP5 = [h["chromatin_FKBP5"] for h in history]
    doses = [h["dose_count"] for h in history]

    # Dose times
    dose_times = [h["t_day"] for h in history
                  if h["dose_count"] > 0 and
                  (history.index(h) == 0 or
                   h["dose_count"] > history[history.index(h)-1]["dose_count"])]

    fig, axes = plt.subplots(5, 1, figsize=(14, 16), sharex=True)

    # Panel 1: 5-HT2A open fraction + dose markers
    axes[0].plot(days, ht2a_open, color="#ff006e", lw=1)
    axes[0].set_ylabel("5-HT2A\nopen fraction")
    axes[0].set_ylim(0, 1)
    axes[0].set_title("Coupled Ayahuasca Sim — 84-day Ceremonial Schedule (2 doses/wk)")
    for d in dose_times:
        axes[0].axvline(d, color="red", alpha=0.3, lw=0.5, ls=":")

    # Panel 2: 5-HT2A setpoint + chronic tolerance
    axes[1].plot(days, ht2a_setpoint, color="#ffd166", lw=1.5, label="setpoint")
    axes[1].plot(days, ht2a_chronic, color="#fb5607", lw=1, label="chronic tolerance")
    axes[1].axhline(1.0, color="grey", ls="--", lw=0.8)
    axes[1].set_ylabel("5-HT2A state")
    axes[1].legend(loc="best", fontsize=9)

    # Panel 3: Chromatin stress (coupling signal)
    axes[2].plot(days, chrom_stress, color="#8338ec", lw=1.2)
    axes[2].set_ylabel("chromatin\nstress input")
    axes[2].set_ylim(0, 1.1)

    # Panel 4: Chromatin mean openness
    axes[3].plot(days, chrom_mean, color="#3a86ff", lw=1.5, label="mean")
    axes[3].axhline(BASELINE_OPEN_FRACTION, color="grey", ls="--", lw=0.8,
                    label=f"baseline ({BASELINE_OPEN_FRACTION})")
    axes[3].set_ylabel("chromatin mean\nopenness")
    axes[3].legend(loc="best", fontsize=9)

    # Panel 5: Per-locus openness (FOS, HSP70, FKBP5)
    axes[4].plot(days, chrom_FOS, color="#06d6a0", lw=1, label="FOS")
    axes[4].plot(days, chrom_HSP70, color="#118ab2", lw=1, label="HSP70")
    axes[4].plot(days, chrom_FKBP5, color="#ef476f", lw=1, label="FKBP5")
    axes[4].axhline(BASELINE_OPEN_FRACTION, color="grey", ls="--", lw=0.5)
    axes[4].set_ylabel("locus openness")
    axes[4].set_xlabel("day")
    axes[4].legend(loc="best", fontsize=9, ncol=3)

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
    print("  TAP COUPLED AYAHUASCA SIMULATOR — 5-HT2A + Chromatin pipeline")
    print(f"  φ-cascade: φ⁻⁴ (signaling) → φ⁻⁸ (receptor) → φ⁻¹⁰ (chromatin) → φ⁻¹³ (cosmic)")
    print("=" * 80)

    print("\n  [VALIDATION]")
    val = validate_coupled_sim()
    for k, v in val.items():
        print(f"\n    {k}:")
        for kk, vv in v.items():
            print(f"      {kk}: {vv}")

    # Run the 84-day chronic ceremonial for the plot
    print(f"\n  [CHRONIC CEREMONIAL 84 days, 2 doses/wk]")
    sim = CoupledAyahuascaSimulator()
    history = run_chronic_ceremonial(sim, days=84, doses_per_week=2)
    print(f"    Total doses: {sim.ht2a.cumulative_dose_count}")
    print(f"    Final 5-HT2A setpoint: {sim.ht2a.sensitivity_setpoint:.4f}")
    print(f"    Final chromatin mean openness: {sim.chromatin.openness.mean():.4f}")
    print(f"    Final FOS openness: {sim.chromatin.openness[sim.chromatin.loci['FOS']['pos']]:.4f}")
    print(f"    Final HSP70 openness: {sim.chromatin.openness[sim.chromatin.loci['HSP70']['pos']]:.4f}")

    if args.plot:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
        os.makedirs(out_dir, exist_ok=True)
        plot_path = os.path.join(out_dir, "tap_coupled_ceremonial_84d.png")
        if plot_coupled_results(sim, history, plot_path):
            print(f"    Plot saved -> {plot_path}")

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_coupled_ayahuasca_results.json")
    # Sample every 6 hours of history
    sampled = history[::6]
    export = {
        "config": {
            "phi_constants": {
                "PHI_INV4": round(PHI_INV4, 6),
                "PHI_INV8": round(PHI_INV8, 6),
                "PHI_INV10": round(PHI_INV10, 6),
                "PHI_INV13": round(PHI_INV13, 6)
            },
            "coupling_mappings": {
                "setpoint_to_chromatin_stress": "linear: (setpoint-1.0)/1.0, clamped [0,1]",
                "chromatin_to_synth_modifier": "soft scaling: openness/0.25, clamped [0.5, 2.0]"
            }
        },
        "validation": val,
        "chronic_ceremonial_84d": {
            "duration_days": 84,
            "history_sampled_every_6h": sampled,
            "final_state": {
                "ht2a_setpoint": sim.ht2a.sensitivity_setpoint,
                "chromatin_mean": float(sim.chromatin.openness.mean()),
                "FOS": float(sim.chromatin.openness[sim.chromatin.loci["FOS"]["pos"]]),
                "HSP70": float(sim.chromatin.openness[sim.chromatin.loci["HSP70"]["pos"]])
            }
        }
    }
    with open(out_path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"\n  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
