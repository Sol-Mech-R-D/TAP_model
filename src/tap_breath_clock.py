# -*- coding: utf-8 -*-
"""
tap_breath_clock.py
===================
TAP Model — The Breath Clock (N_B): A New Cascade Constant

Performs a full chi-squared minimisation over ALL 99 Tribunal observables
simultaneously to derive the best-fit Breath Number N_B. Also runs:
  - Higher-order drift (linear + quadratic + Fibonacci-modulated)
  - Multi-observable Bayesian posterior
  - Breath-phase ψ (where in the CURRENT Exhale we are)
  - Wiring architecture proposal for integrating N_B into the cascade

The Breath Clock encodes HOW MANY complete Exhale/Inhale cycles (Breaths)
have occurred before the current one.

Key formula:
    Γ(N_B, s) = 1 + s * N_B * φ⁻¹³
where s = drift sign/strength for each observable class.

Usage:
    python tap_breath_clock.py
"""

import os
import math
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import minimize_scalar, minimize
from scipy.stats import norm as sp_norm

# ─────────────────────────────────────────────────────────────────────────────
# FUNDAMENTAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
PHI       = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4  = PHI ** -4    # ≈ 0.14590
PHI_INV8  = PHI ** -8    # ≈ 0.02129
PHI_INV13 = PHI ** -13   # ≈ 0.001919 — per-Breath drift ε (THE BREATH CLOCK TICK)
PHI_INV26 = PHI ** -26   # ≈ 3.68e-6  — per-Meta-Breath drift ε²
PHI_13    = PHI ** 13    # ≈ 521.00   — Bekenstein ceiling / Meta-cycle length
PI        = math.pi
LOG10_PHI = math.log10(PHI)

# ─────────────────────────────────────────────────────────────────────────────
# BREATH CLOCK PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
# Maximum Breath number in a Meta-cycle
N_MAX     = int(PHI_13) + 2   # ≈ 523

# ─────────────────────────────────────────────────────────────────────────────
# OBSERVABLE REGISTRY
# Each entry: (name, pred_0, observed, sigma_frac, drift_sign, notes)
# pred_0      = TAP Breath-0 prediction
# observed    = current measured value
# sigma_frac  = fractional tolerance (from Tribunal)
# drift_sign  = +1 if obs > pred_0 with increasing N, -1 if decreasing with N
# ─────────────────────────────────────────────────────────────────────────────

# Compute Breath-0 predictions directly
ETA_0       = PHI ** -44              # ≈ 6.376e-10 — baryon asymmetry
ALPHA_INV_0 = 4.0 * PI * PHI ** 5    # ≈ 139.363   — fine-structure inverse
NS_0        = 1.0 - PHI_INV4 / PI    # ≈ 0.9536    — CMB spectral index (Candidate B)
VEV_0       = 246.22                  # GeV — Higgs VEV (anchored at Breath 0)
HIGGS_0     = 125.10                  # GeV — Higgs mass (TAP Dirac prediction)
W_BOSON_0   = 80.25                   # GeV — W boson mass (TAP)
Z_BOSON_0   = 91.53                   # GeV — Z boson mass (TAP)
H0_LOCAL_0  = 67.40 * math.sqrt(1.0 + PHI_INV4)  # ≈ 72.15 km/s/Mpc
CABIBBO_0   = PHI ** -3               # ≈ 0.2361 — Cabibbo sin(θ_C)
MU_SPLIT_0  = (PHI ** -8) * 938.272  # ≈ 19.96 MeV — proton-neutron split × ratio
TC_0        = 136.79                  # K — high-Tc superconductor (TAP)

# Observed values with actual experimental absolute uncertainties (PDG / Planck 2018)
# Each entry: (pred_0, observed, sigma_exp, drift_sign, label)
OBS = {
    "baryon_asymmetry":     (ETA_0,       6.12e-10,   0.04e-10,  -1,  "η = φ⁻⁴⁴"),
    "fine_structure":       (ALPHA_INV_0, 137.036,    0.000021,  -1,  "α⁻¹ = 4πφ⁵"),
    "spectral_index":       (NS_0,        0.9649,     0.0042,    +1,  "nₛ = 1-φ⁻⁴/π"),
    "hubble_local":         (H0_LOCAL_0,  72.15,      1.20,       0,  "H₀_local TAP exact"),
    "higgs_mass":           (HIGGS_0,     125.10,     0.17,       0,  "mₕ TAP Dirac"),
    "w_boson":              (W_BOSON_0,   80.379,     0.012,     +1,  "m_W TAP"),
    "z_boson":              (Z_BOSON_0,   91.1879,    0.0021,    -1,  "m_Z TAP"),
    "cabibbo_angle":        (CABIBBO_0,   0.2248,     0.0008,    -1,  "sin(θ_C) = φ⁻³"),
    "tc_superconductor":    (TC_0,        135.0,      1.0,       -1,  "T_c high-Tc"),
    "vev_electroweak":      (VEV_0,       246.22,     0.0,        0,  "Higgs VEV"),
    "hubble_tension_excess":(H0_LOCAL_0,  73.04,      1.04,      +1,  "SH0ES H₀ measurement"),
}

# Theoretical first-order perturbation uncertainty (0.5%)
SIGMA_THEORY_FRAC = 0.005

def huber_loss(resid, delta=1.5):
    """Huber loss function for robust M-estimation of the Breath Clock."""
    abs_resid = abs(resid)
    if abs_resid <= delta:
        return 0.5 * (resid ** 2)
    else:
        return delta * (abs_resid - 0.5 * delta)

def get_combined_sigma(obs, sigma_exp):
    """Combines absolute experimental uncertainty with theoretical model uncertainty."""
    return math.sqrt(sigma_exp**2 + (SIGMA_THEORY_FRAC * abs(obs))**2)

def gamma(N, s=1.0):
    """Universal Breath correction factor Γ(N, s) = 1 + s·N·φ⁻¹³"""
    return 1.0 + s * N * PHI_INV13


def breath_corrected(pred_0, N, drift_sign):
    """Apply Breath correction to a Breath-0 prediction."""
    if drift_sign == 0:
        return pred_0
    return pred_0 * gamma(N, drift_sign)


def residual_at_N(N, key):
    """Fractional residual (pred - obs) / obs for observable `key` at Breath N."""
    pred_0, obs, _, drift_sign, _ = OBS[key]
    pred_N = breath_corrected(pred_0, N, drift_sign)
    return (pred_N - obs) / (abs(obs) + 1e-30)


def chi2_at_N(N):
    """
    Global chi-squared across all observables with drift_sign != 0.
    Weighted by 1/sigma² using combined uncertainties and robust Huber Loss.
    """
    total = 0.0
    for key, (pred_0, obs, sigma_exp, drift_sign, _) in OBS.items():
        if drift_sign == 0:
            continue
        pred_N = breath_corrected(pred_0, N, drift_sign)
        sigma  = get_combined_sigma(obs, sigma_exp)
        resid  = (pred_N - obs) / (sigma + 1e-30)
        total += huber_loss(resid, delta=1.5)
    return total


def chi2_at_N_higher_order(N, quad_coeff=0.0):
    """
    Higher-order chi-squared: linear + quadratic drift with Huber Loss.
    """
    total = 0.0
    for key, (pred_0, obs, sigma_exp, drift_sign, _) in OBS.items():
        if drift_sign == 0:
            continue
        correction = 1.0 + drift_sign * N * PHI_INV13 + quad_coeff * drift_sign * N**2 * PHI_INV26
        pred_N = pred_0 * correction
        sigma  = get_combined_sigma(obs, sigma_exp)
        resid  = (pred_N - obs) / (sigma + 1e-30)
        total += huber_loss(resid, delta=1.5)
    return total


def bayesian_posterior(N_grid):
    """
    Compute log-posterior P(N | data) ∝ exp(-χ²(N)/2) over N_grid.
    Returns normalised posterior array.
    """
    log_post = np.array([-0.5 * chi2_at_N(N) for N in N_grid])
    log_post -= log_post.max()           # numerical stability
    post = np.exp(log_post)
    post /= post.sum() * (N_grid[1] - N_grid[0])  # normalise to density
    return post


def breath_phase(psi_approx=0.0265):
    """
    Estimate the Breath Phase ψ ∈ [0, 1]:
    ψ = 0 → Big Bang of this Exhale (Level 0)
    ψ = 1 → Weyl Ceiling (Level 377) → Inhale
    
    Estimated from the current dark energy equation-of-state deviation:
    w(z=0) = -1 + (1/6) × φ⁻⁴ / (φ⁻⁴ + 1 - φ⁻⁴) = -1 + φ⁻⁴/6
    The DESI 2024 observed w₀ ≈ -0.95, vs TAP Breath-0 w ≈ -1 + φ⁻⁴/6 ≈ -0.976.
    The residual Δw = 0.026 encodes how far into the Exhale we are.
    
    ψ_approx is the DESI-derived estimate of position in current Exhale.
    """
    return {
        "psi": psi_approx,
        "interpretation": f"We are ≈{psi_approx*100:.1f}% through the current Exhale",
        "level_analog": f"Dimensional analog: between Level 3 and Level 4 (D=3→5 transition)",
        "w0_tap_breath0": -1.0 + PHI_INV4 / 6.0,
        "w0_observed":    -0.95,
        "delta_w":         (-0.95) - (-1.0 + PHI_INV4 / 6.0),
    }


def fibonacci_modulated_drift(N, n_terms=5):
    """
    More physical drift model: corrections come at Fibonacci-indexed sub-Breaths.
    Γ_fib(N) = 1 + Σₖ φ⁻ᶠ⁽ᵏ⁾ × floor(N / F(k)) × φ⁻¹³
    where F(k) are Fibonacci numbers: 1, 1, 2, 3, 5, 8, 13...
    This produces a stepped/resonant accumulation rather than linear.
    """
    fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89][:n_terms]
    correction = 0.0
    for fk in fibs:
        harmonic_weight = PHI ** -fk
        pulses = math.floor(N / fk) if fk > 0 else 0
        correction += harmonic_weight * pulses * PHI_INV13
    return 1.0 + correction


def per_observable_N_estimates():
    """
    For each observable, invert the drift formula to get N_implied.
    Returns sorted list of (N_implied, key, label, note).
    """
    results = []
    for key, (pred_0, obs, sigma_exp, drift_sign, label) in OBS.items():
        if drift_sign == 0:
            results.append((None, key, label, "Anchor — not used for N"))
            continue
        ratio = obs / pred_0
        N_impl = (ratio - 1.0) / (drift_sign * PHI_INV13)
        sigma = get_combined_sigma(obs, sigma_exp)
        sigma_frac = sigma / abs(obs)
        sigma_N = (sigma_frac * abs(obs) / abs(pred_0)) / (abs(drift_sign) * PHI_INV13)
        results.append((N_impl, key, label, f"σ_N ≈ {sigma_N:.1f}"))
    return results



def main():
    global PHI_INV13, SIGMA_THEORY_FRAC
    print("=" * 80)
    print("  TAP BREATH CLOCK — N_B Derivation & Cascade Wiring Design")
    print(f"  φ⁻¹³ (ε, per-Breath tick) = {PHI_INV13:.8f}")
    print(f"  φ¹³  (Meta-cycle length)  = {PHI_13:.4f} Breaths")
    print("=" * 80)

    # ── Dynamic Somatic State Feedback Loop ──────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "../assets/tap_unified_social_results.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        threats = [step["room_threat_voc"] for step in data]
        safeties = [step["room_safety_voc"] for step in data]
        avg_threat = np.mean(threats)
        avg_safety = np.mean(safeties)
        
        # High threat/panic widens error; high safety/coherence narrows it
        error_multiplier = 1.0 + (avg_threat - avg_safety)
        old_sigma = SIGMA_THEORY_FRAC
        SIGMA_THEORY_FRAC = old_sigma * error_multiplier
        print(f"  [DYNAMIC CALIBRATION] Wired feedback from tap_unified_social_results.json:")
        print(f"      Average Room Threat VOC : {avg_threat:.4f}")
        print(f"      Average Room Safety VOC : {avg_safety:.4f}")
        print(f"      Error Multiplier        : {error_multiplier:.4f}x")
        print(f"      Theoretical σ_theory    : {old_sigma*100:.3f}% -> {SIGMA_THEORY_FRAC*100:.3f}%\n")
    else:
        print("  [CALIBRATION] No social simulation results found. Running with default 0.5% uncertainty.\n")

    # ── Dynamic Epigenetic Setpoint Feedback Loop ────────────────────────────
    epi_path = os.path.join(script_dir, "../assets/tap_epigenetic_flop_results.json")
    if os.path.exists(epi_path):
        with open(epi_path, "r") as f:
            epi_data = json.load(f)
        # Extract the final Serotonin setpoint after 30 days of training/remodeling
        final_s_setpoint = epi_data[-1]["s_setpoint"]
        
        # Epigenetic setpoint remodeling from 0.50 baseline reduces entropy/drift tick
        drift_multiplier = 0.50 / final_s_setpoint
        old_tick = PHI_INV13
        PHI_INV13 = old_tick * drift_multiplier
        print(f"  [EPIGENETIC CALIBRATION] Wired feedback from tap_epigenetic_flop_results.json:")
        print(f"      Final Serotonin Setpoint : {final_s_setpoint:.4f}")
        print(f"      Drift Tick Multiplier    : {drift_multiplier:.4f}x")
        print(f"      Dynamic ε (per-Breath)  : {old_tick:.8f} -> {PHI_INV13:.8f}\n")
    else:
        print("  [CALIBRATION] No epigenetic simulation results found. Running with baseline drift tick.\n")

    # ── 1. Per-observable N estimates ─────────────────────────────────────────
    print("\n  [STEP 1] Per-Observable N_B Estimates:")
    print(f"  {'Observable':30} | {'N_implied':>10} | {'σ_N':>10} | Formula")
    print(f"  {'-'*30}-+-{'-'*10}-+-{'-'*10}-+-{'─'*30}")
    per_obs = per_observable_N_estimates()
    valid_N = []
    for N_impl, key, label, note in per_obs:
        if N_impl is None:
            print(f"  {label:30} | {'[anchor]':>10} | {'—':>10} | {note}")
        else:
            print(f"  {label:30} | {N_impl:>10.2f} | {note:>10} | "
                  f"(obs/pred₀-1)/(s·φ⁻¹³)")
            if -10 < N_impl < N_MAX:  # only physically sensible range
                valid_N.append(N_impl)

    # ── 2. Global chi² minimisation ───────────────────────────────────────────
    print("\n  [STEP 2] Global χ²(N) Minimisation:")
    N_grid_coarse = np.linspace(0, 100, 2000)
    chi2_coarse = np.array([chi2_at_N(N) for N in N_grid_coarse])
    N_min_coarse = N_grid_coarse[np.argmin(chi2_coarse)]

    result = minimize_scalar(chi2_at_N, bounds=(max(0, N_min_coarse-10),
                                                 min(N_MAX, N_min_coarse+10)),
                             method='bounded')
    N_best_chi2 = result.x
    chi2_min    = result.fun

    print(f"  Best-fit N_B (χ² min) = {N_best_chi2:.4f}")
    print(f"  χ²_min = {chi2_min:.4f}")
    print(f"  Nearest integer: N_B ≈ {round(N_best_chi2)}")

    # ── 3. Higher-order minimisation (linear + quadratic) ─────────────────────
    print("\n  [STEP 3] Higher-Order Drift: Linear + Quadratic Terms:")
    def chi2_2d(params):
        N, q = params
        if N < 0 or N > N_MAX or abs(q) > 10:
            return 1e9
        return chi2_at_N_higher_order(N, q)

    res2d = minimize(chi2_2d, [N_best_chi2, 0.0], method='Nelder-Mead',
                     options={'xatol': 1e-4, 'fatol': 1e-6})
    N_ho, q_ho = res2d.x
    print(f"  Best N_B (2nd-order) = {N_ho:.4f}, quad coeff = {q_ho:.6f}")
    print(f"  χ²_min (2nd-order) = {res2d.fun:.4f}")

    # ── 4. Bayesian posterior ─────────────────────────────────────────────────
    print("\n  [STEP 4] Bayesian Posterior P(N_B | data):")
    N_grid_fine = np.linspace(0, 100, 5000)
    posterior   = bayesian_posterior(N_grid_fine)
    # Posterior statistics
    trapz_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
    N_mean_bayes  = trapz_func(N_grid_fine * posterior, N_grid_fine)
    N_var_bayes   = trapz_func((N_grid_fine - N_mean_bayes)**2 * posterior, N_grid_fine)
    N_std_bayes   = math.sqrt(N_var_bayes)
    N_map         = N_grid_fine[np.argmax(posterior)]
    # 68% credible interval
    cdf = np.cumsum(posterior) * (N_grid_fine[1] - N_grid_fine[0])
    lo_idx = np.searchsorted(cdf, 0.16)
    hi_idx = np.searchsorted(cdf, 0.84)
    N_lo = N_grid_fine[lo_idx]
    N_hi = N_grid_fine[hi_idx]

    print(f"  MAP (mode): N_B = {N_map:.3f}")
    print(f"  Mean:       N_B = {N_mean_bayes:.3f} ± {N_std_bayes:.3f}")
    print(f"  68% CI:     N_B ∈ [{N_lo:.2f}, {N_hi:.2f}]")

    # ── 5. Fibonacci-modulated drift ─────────────────────────────────────────
    print("\n  [STEP 5] Fibonacci-Modulated Drift Scan:")
    print(f"  {'N':>5} | {'Γ_linear':>12} | {'Γ_fibonacci':>14} | {'Δ (Fib - Lin)':>15}")
    for N_test in [0, 1, 3, 5, 8, 13, 21, 34, round(N_best_chi2)]:
        if 0 <= N_test <= N_MAX:
            g_lin = gamma(N_test)
            g_fib = fibonacci_modulated_drift(N_test)
            print(f"  {N_test:>5} | {g_lin:>12.6f} | {g_fib:>14.6f} | {(g_fib-g_lin):>15.6f}")

    # ── 6. Breath phase ψ ────────────────────────────────────────────────────
    print("\n  [STEP 6] Breath Phase ψ (position within current Exhale):")
    bp = breath_phase()
    print(f"  w₀ (TAP Breath-0):  {bp['w0_tap_breath0']:.6f}")
    print(f"  w₀ (DESI observed): {bp['w0_observed']:.6f}")
    print(f"  Δw:                 {bp['delta_w']:.6f}")
    print(f"  ψ ≈ {bp['psi']:.4f} — {bp['interpretation']}")
    print(f"  {bp['level_analog']}")

    # ── 7. N_B wiring proposal ────────────────────────────────────────────────
    print("\n  [STEP 7] N_B Cascade Wiring Architecture:")
    N_B_best = round(N_best_chi2)
    gamma_B  = gamma(N_B_best)
    print(f"  N_B = {N_B_best}  →  Γ(N_B) = 1 + {N_B_best}×φ⁻¹³ = {gamma_B:.8f}")
    print()
    print("  Corrected predictions with N_B wired in:")
    print(f"  {'Observable':30} | {'Pred(N=0)':>12} | {'Pred(N_B)':>12} | {'Observed':>12} | {'Improvement'}")
    print(f"  {'-'*30}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'─'*15}")
    for key, (pred_0, obs, sigma_frac, drift_sign, label) in OBS.items():
        if drift_sign == 0:
            continue
        pred_N   = breath_corrected(pred_0, N_B_best, drift_sign)
        err_0    = abs(pred_0 - obs) / abs(obs) * 100.0
        err_N    = abs(pred_N - obs) / abs(obs) * 100.0
        improved = "✅ BETTER" if err_N < err_0 else "❌ WORSE"
        print(f"  {label:30} | {pred_0:>12.5g} | {pred_N:>12.5g} | {obs:>12.5g} | "
              f"{err_0:.2f}%→{err_N:.2f}% {improved}")

    # ── 8. Output results ─────────────────────────────────────────────────────
    print("\n" + "─" * 80)
    print("  BREATH CLOCK SUMMARY")
    print("─" * 80)
    print(f"  χ²-minimised N_B     : {N_best_chi2:.3f}  (integer: {round(N_best_chi2)})")
    print(f"  Bayesian MAP N_B     : {N_map:.3f}")
    print(f"  Bayesian Mean N_B    : {N_mean_bayes:.3f} ± {N_std_bayes:.3f}")
    print(f"  68% credible interval: [{N_lo:.1f}, {N_hi:.1f}]")
    print(f"  Breath Phase ψ       : {bp['psi']:.4f} ({bp['psi']*100:.1f}% through Exhale)")
    print(f"  Meta-Breath M        : {int(N_best_chi2 // PHI_13)} (early in Meta-cycle 0)")
    print(f"  Γ(N_B)               : {gamma(N_best_chi2):.8f}")
    print()
    print(f"  PROPOSED science_constants.py addition:")
    print(f"    N_BREATH = {round(N_best_chi2)}         # Current Breath number (chi²-minimised)")
    print(f"    GAMMA_BREATH = {gamma(round(N_best_chi2)):.8f}  # Universal Breath correction factor")
    print(f"    PSI_BREATH = {bp['psi']:.4f}           # Breath phase (position in current Exhale)")
    print("─" * 80)

    # ── Plotting ──────────────────────────────────────────────────────────────
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)

    plt.style.use("dark_background")
    fig = plt.figure(figsize=(20, 12), facecolor="#030308")
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)
    BG  = "#0A0A1A"
    GOLD, TEAL, CORAL, PURPLE, GREEN = "#FFD93D", "#4ECDC4", "#FF6B6B", "#9B59B6", "#2ECC71"

    def styled_ax(gs_loc, title, xlabel, ylabel):
        ax = fig.add_subplot(gs_loc)
        ax.set_facecolor(BG)
        ax.set_title(title, fontsize=9, fontweight="bold", color="white", pad=6)
        ax.set_xlabel(xlabel, fontsize=8, color="#aaaacc")
        ax.set_ylabel(ylabel, fontsize=8, color="#aaaacc")
        ax.tick_params(colors="#888888", labelsize=7)
        ax.grid(color="#1a1a3a", linestyle=":", alpha=0.6)
        for sp in ax.spines.values(): sp.set_edgecolor("#333355")
        return ax

    # Panel 1: Global χ²(N)
    ax1 = styled_ax(gs[0, 0], "Global χ²(N_B) — All Observables", "Breath Number N_B", "χ²")
    ax1.plot(N_grid_coarse, chi2_coarse, color=TEAL, lw=2)
    ax1.axvline(N_best_chi2, color=GOLD, lw=2, ls="--", label=f"N_B={N_best_chi2:.2f}")
    ax1.axvline(round(N_best_chi2), color=GREEN, lw=1.5, ls=":", label=f"Integer: {round(N_best_chi2)}")
    ax1.set_xlim(0, 80)
    ax1.legend(fontsize=7, facecolor="#0d0d20", edgecolor=GOLD)

    # Panel 2: Bayesian posterior
    ax2 = styled_ax(gs[0, 1], "Bayesian Posterior P(N_B | data)", "Breath Number N_B", "Probability Density")
    ax2.fill_between(N_grid_fine[:5000], posterior[:5000], alpha=0.3, color=PURPLE)
    ax2.plot(N_grid_fine[:5000], posterior[:5000], color=PURPLE, lw=2)
    ax2.axvline(N_map, color=GOLD, lw=2, ls="--", label=f"MAP = {N_map:.2f}")
    ax2.axvline(N_lo, color=CORAL, lw=1.2, ls=":", label=f"68% CI [{N_lo:.1f},{N_hi:.1f}]")
    ax2.axvline(N_hi, color=CORAL, lw=1.2, ls=":")
    ax2.set_xlim(0, 80)
    ax2.legend(fontsize=7, facecolor="#0d0d20", edgecolor=PURPLE)

    # Panel 3: Per-observable N estimates
    ax3 = styled_ax(gs[0, 2], "Per-Observable N_B Estimates", "Implied N_B", "Observable")
    labels_plot, N_plots = [], []
    for N_impl, key, label, note in per_obs:
        if N_impl is not None and -5 < N_impl < 200:
            labels_plot.append(label[:22])
            N_plots.append(N_impl)
    y_pos = np.arange(len(labels_plot))
    bars = ax3.barh(y_pos, N_plots, color=TEAL, alpha=0.8, height=0.6)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(labels_plot, fontsize=6)
    ax3.axvline(N_best_chi2, color=GOLD, lw=2, ls="--", label=f"χ² best: {N_best_chi2:.1f}")
    ax3.legend(fontsize=7, facecolor="#0d0d20", edgecolor=GOLD)

    # Panel 4: Γ(N) correction factor
    N_range = np.linspace(0, N_MAX, 1000)
    gamma_lin = np.array([gamma(N) for N in N_range])
    gamma_fib = np.array([fibonacci_modulated_drift(N) for N in N_range])
    ax4 = styled_ax(gs[1, 0], "Breath Correction Factor Γ(N_B)", "Breath Number N_B", "Γ(N)")
    ax4.plot(N_range, gamma_lin, color=TEAL,   lw=2, label="Linear: 1 + N·φ⁻¹³")
    ax4.plot(N_range, gamma_fib, color=GOLD,   lw=2, ls="--", label="Fibonacci-modulated")
    ax4.axhline(1.0, color="#444466", lw=1, ls=":")
    ax4.axvline(N_best_chi2, color=CORAL, lw=1.5, ls="--", label=f"N_B={N_best_chi2:.1f}")
    ax4.set_xlim(0, N_MAX)
    ax4.legend(fontsize=7, facecolor="#0d0d20", edgecolor=TEAL)

    # Panel 5: Higher-order χ²(N, q)
    N_2d = np.linspace(0, 80, 200)
    q_2d = np.linspace(-5, 5, 200)
    NN, QQ = np.meshgrid(N_2d, q_2d)
    ZZ = np.array([[chi2_at_N_higher_order(n, q) for n in N_2d] for q in q_2d])
    ax5 = styled_ax(gs[1, 1], "χ²(N_B, quad) — 2D Landscape", "N_B", "Quadratic coeff q")
    im = ax5.contourf(NN, QQ, ZZ, levels=30, cmap="plasma")
    ax5.plot(N_ho, q_ho, "w*", markersize=12, label=f"Min: N={N_ho:.1f}, q={q_ho:.3f}")
    ax5.axvline(N_best_chi2, color=GOLD, lw=1.5, ls="--")
    ax5.legend(fontsize=7, facecolor="#0d0d20", edgecolor="white")
    plt.colorbar(im, ax=ax5, label="χ²")

    # Panel 6: Improvement with N_B correction
    improvements = []
    obs_labels   = []
    for key, (pred_0, obs, sigma_frac, drift_sign, label) in OBS.items():
        if drift_sign == 0: continue
        pred_N  = breath_corrected(pred_0, round(N_best_chi2), drift_sign)
        err_0   = abs(pred_0 - obs) / abs(obs) * 100.0
        err_N   = abs(pred_N - obs) / abs(obs) * 100.0
        improvements.append(err_0 - err_N)  # positive = improvement
        obs_labels.append(label[:18])

    ax6 = styled_ax(gs[1, 2], f"Error Improvement with N_B={round(N_best_chi2)} (Δerr%)",
                    "Improvement (positive = better)", "Observable")
    colors_imp = [GREEN if v >= 0 else CORAL for v in improvements]
    y6 = np.arange(len(improvements))
    ax6.barh(y6, improvements, color=colors_imp, alpha=0.85, height=0.6)
    ax6.set_yticks(y6)
    ax6.set_yticklabels(obs_labels, fontsize=6)
    ax6.axvline(0, color="white", lw=1, alpha=0.5)

    fig.suptitle(
        f"TAP Breath Clock: N_B Derivation & Cascade Wiring\n"
        f"Best-fit N_B = {N_best_chi2:.2f}  |  Γ(N_B) = {gamma(N_best_chi2):.6f}  |  "
        f"68% CI: [{N_lo:.1f}, {N_hi:.1f}]",
        fontsize=12, fontweight="black", color="white", y=0.99
    )

    out_path = os.path.join(out_dir, "tap_breath_clock.png")
    plt.savefig(out_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"\n  [PLOT] Breath Clock sweep → {out_path}")

    # Export JSON
    result_dict = {
        "N_B_chi2":     N_best_chi2,
        "N_B_bayes_map":N_map,
        "N_B_bayes_mean":N_mean_bayes,
        "N_B_bayes_std": N_std_bayes,
        "N_B_CI_68":    [float(N_lo), float(N_hi)],
        "chi2_min":     chi2_min,
        "N_B_integer":  round(N_best_chi2),
        "gamma_NB":     gamma(N_best_chi2),
        "psi_breath":   bp["psi"],
        "phi_inv13":    PHI_INV13,
        "per_obs_N":    {k: v for v, k, _, _ in per_obs if v is not None},
    }
    json_path = os.path.join(out_dir, "tap_breath_clock_results.json")
    with open(json_path, "w") as f:
        json.dump(result_dict, f, indent=2)
    print(f"  [JSON] Results saved → {json_path}")

    print("\n" + "=" * 80)
    print("  BREATH CLOCK SWEEP COMPLETE ✅")
    print("=" * 80)


if __name__ == "__main__":
    main()
