# -*- coding: utf-8 -*-
"""
tap_cosmo_perturbations.py
===========================
TAP Model -- Cosmological Perturbation Spectra Simulator
Solves the modified Mukhanov-Sasaki perturbation mode equations under
extra-dimensional leakage. Computes the scalar and tensor power spectra,
spectral index running (alpha_s), and the tensor-to-scalar ratio.
Generates a 3-panel visualization: tap_cosmo_perturbations.png.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import math
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

# -----------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -----------------------------------------------------------------------------
PHI       = (1 + math.sqrt(5)) / 2   # Golden Ratio
PHI_INV4  = PHI ** -4                 # ~0.145898  (leakage rate)
PI        = math.pi

# Horizon scale / pivot scale
k_pivot = 0.05  # Mpc^-1
H_inf   = 1e-5  # Hubble rate during inflation (in Planck units)

# -----------------------------------------------------------------------------
# MODE EQUATION SOLVER
# -----------------------------------------------------------------------------
def solve_mode(k, is_tensor=False):
    """
    Solves the Mukhanov-Sasaki mode equation for a given wavenumber k.
    For tensors, the extra-dimensional leakage projects a damping term that is
    eliminated via a field transformation, shifting the effective index nu.
    """
    eta_start = -10.0 / k
    eta_end   = -1e-5  # Fixed final conformal time
    
    # Exponents for the mode equations:
    # Scalars: nu_s = 1.5 + phi^-4 / 2pi
    # Tensors: nu_t_eff = 1.5 - 0.5 * phi^-4
    if not is_tensor:
        nu = 1.5 + PHI_INV4 / (2.0 * PI)
    else:
        nu = 1.5 - 0.5 * PHI_INV4
        
    # Initial conditions (Bunch-Davies vacuum)
    v_real_0 = 1.0 / math.sqrt(2.0 * k)
    v_imag_0 = 0.0
    dv_real_0 = 0.0
    dv_imag_0 = -k * v_real_0
    
    # State: [v_r, v_i, dv_r, dv_i]
    y0 = [v_real_0, v_imag_0, dv_real_0, dv_imag_0]
    
    def derivatives(eta, y):
        v_r, v_i, dv_r, dv_i = y
        mass_term = (nu**2 - 0.25) / (eta**2)
        
        ddv_r = -(k**2 - mass_term) * v_r
        ddv_i = -(k**2 - mass_term) * v_i
        
        return [dv_r, dv_i, ddv_r, ddv_i]
    
    sol = solve_ivp(derivatives, [eta_start, eta_end], y0, t_eval=[eta_end], method='RK45', rtol=1e-6, atol=1e-9)
    
    v_r_end = sol.y[0, -1]
    v_i_end = sol.y[1, -1]
    
    return v_r_end**2 + v_i_end**2

# -----------------------------------------------------------------------------
# MAIN ANALYSIS
# -----------------------------------------------------------------------------
def analyze_perturbations():
    print("=" * 72)
    print("  TAP COSMOLOGICAL PERTURBATION SPECTRA ANALYSIS")
    print("=" * 72)
    
    # Generate range of wavenumbers (log space)
    k_modes = np.logspace(-3, -1, 40)
    
    scalar_amplitudes = []
    tensor_amplitudes = []
    
    print("  Solving mode equations across k space...")
    for k in k_modes:
        amp_s = solve_mode(k, is_tensor=False)
        amp_t = solve_mode(k, is_tensor=True)
        
        scalar_amplitudes.append(amp_s)
        tensor_amplitudes.append(amp_t)
        
    scalar_amplitudes = np.array(scalar_amplitudes)
    tensor_amplitudes = np.array(tensor_amplitudes)
    
    # Conformal scale factor at end of integration (fixed eta_end = -1e-5)
    eta_end = -1e-5
    a_end = -1.0 / (H_inf * eta_end)
    
    # Slow-roll parameters from boundary projection
    # Curvature perturbation is enhanced by 1 / (2*epsilon)
    epsilon_eff = PHI_INV4  # Exactly matches the leakage rate
    
    # Power spectra: P(k) = k^3 / (2 * pi^2) * |v_k / a|^2
    P_s = (k_modes**3 / (2.0 * PI**2)) * (scalar_amplitudes / (2.0 * epsilon_eff * a_end**2))
    P_t = (k_modes**3 / (2.0 * PI**2)) * (tensor_amplitudes / (a_end**2)) * 2.0
    
    # Normalize spectra to match Planck pivot A_s ~ 2.1e-9
    r_pivot_idx = np.argmin(np.abs(k_modes - k_pivot))
    normalization = 2.1e-9 / P_s[r_pivot_idx]
    P_s *= normalization
    P_t *= normalization
    
    # Fit spectral indices: ln P(k) = ln A + (n - 1) * ln(k/k_pivot) + 1/2 * alpha * ln(k/k_pivot)^2
    lnk = np.log(k_modes / k_pivot)
    lnPs = np.log(P_s)
    lnPt = np.log(P_t)
    
    poly_s = np.polyfit(lnk, lnPs, 2)
    alpha_s_pred = poly_s[0] * 2.0
    ns_pred = poly_s[1] + 1.0
    As_pred = math.exp(poly_s[2])
    
    poly_t = np.polyfit(lnk, lnPt, 1)
    nt_pred = poly_t[0]
    
    r_pred = P_t[r_pivot_idx] / P_s[r_pivot_idx]
    
    # TAP theoretical references
    ns_theory = 1.0 - PHI_INV4 / PI  # ~0.953559
    r_theory = (2.0 / 9.0) * PHI_INV4  # ~0.032422
    
    print()
    print("  Derived Perturbation Results:")
    print(f"    Scalar Amplitude A_s at pivot : {As_pred:.6e}")
    print(f"    Spectral Index n_s           : {ns_pred:.6f}  (Theoretical: {ns_theory:.6f}, Observed: 0.9649)")
    print(f"    Spectral Running alpha_s     : {alpha_s_pred:.6e}  (Planck Observed: -0.0045)")
    print(f"    Tensor Spectral Index n_t    : {nt_pred:.6f}")
    print(f"    Tensor-to-Scalar Ratio r     : {r_pred:.6f}  (Theoretical: {r_theory:.6f}, BICEP limit: <0.032)")
    
    # Modified Consistency Relation:
    # Standard: n_t = -r / 8
    # TAP: n_t = -r / 8 - 3 * phi^-4 (due to bulk damping)
    expected_nt_std = -r_pred / 8.0
    expected_nt_tap = -r_pred / 8.0 - 3.0 * PHI_INV4
    print(f"    Standard Consistency n_t     : {expected_nt_std:.6f}")
    print(f"    TAP Modified Consistency n_t : {expected_nt_tap:.6f}  (Actual: {nt_pred:.6f})")
    
    # Plots
    generate_plots(k_modes, P_s, P_t, lnk, lnPs, lnPt, ns_theory, r_theory)

# -----------------------------------------------------------------------------
# VISUALIZATION
# -----------------------------------------------------------------------------
def generate_plots(k_modes, P_s, P_t, lnk, lnPs, lnPt, ns_theory, r_theory):
    fig = plt.figure(figsize=(18, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- Cosmological Perturbation Spectra Analysis",
                 color="white", fontsize=15, fontweight="bold", y=1.05)
                 
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.3)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    
    BLUE   = "#7c6af7"
    GREEN  = "#4ecdc4"
    ORANGE = "#ff6b6b"
    WHITE  = "#e8e8e8"
    
    for ax in axes:
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray", labelsize=9)
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
    # Panel 1: Power Spectra P_s(k) and P_t(k)
    ax = axes[0]
    ax.loglog(k_modes, P_s, color=BLUE, lw=2.0, label="Scalar spectrum P_s(k)")
    ax.loglog(k_modes, P_t, color=ORANGE, lw=2.0, label="Tensor spectrum P_t(k)")
    ax.set_xlabel("Wavenumber k (Mpc^-1)")
    ax.set_ylabel("Power Amplitude P(k)")
    ax.set_title("Scalar and Tensor Power Spectra")
    ax.legend(facecolor="#10101a", labelcolor=WHITE, fontsize=9)
    ax.grid(True, which="both", color=(1, 1, 1, 0.05))
    
    # Panel 2: Tensor-to-Scalar Ratio Running
    ax = axes[1]
    r_modes = P_t / P_s
    ax.plot(k_modes, r_modes, color=GREEN, lw=2.0, label="r(k) = P_t / P_s")
    ax.axhline(r_theory, color=BLUE, ls="--", label=f"TAP r_theory = {r_theory:.4f}")
    ax.axhline(0.032, color=ORANGE, ls=":", label="BICEP/Keck 2018 limit")
    ax.set_xscale("log")
    ax.set_xlabel("Wavenumber k (Mpc^-1)")
    ax.set_ylabel("Ratio r")
    ax.set_title("Tensor-to-Scalar Ratio Running")
    ax.legend(facecolor="#10101a", labelcolor=WHITE, fontsize=9)
    ax.grid(True, color=(1, 1, 1, 0.05))
    
    # Panel 3: Spectral Index n_s Deviation
    ax = axes[2]
    # Local slope representing running
    n_s_modes = np.diff(lnPs) / np.diff(np.log(k_modes)) + 1.0
    ax.plot(k_modes[:-1], n_s_modes, color=BLUE, lw=2.0, label="Local n_s(k)")
    ax.axhline(ns_theory, color=GREEN, ls="--", label=f"Theoretical n_s = {ns_theory:.4f}")
    ax.axhline(0.9649, color=ORANGE, ls=":", label="Planck 2018 Observed")
    ax.set_xscale("log")
    ax.set_xlabel("Wavenumber k (Mpc^-1)")
    ax.set_ylabel("Spectral Index n_s")
    ax.set_title("Scalar Spectral Index Running")
    ax.legend(facecolor="#10101a", labelcolor=WHITE, fontsize=9)
    ax.grid(True, color=(1, 1, 1, 0.05))
    
    out = os.path.join(os.path.dirname(__file__), "tap_cosmo_perturbations.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"\n  [PLOT] Perturbations plot saved -> {out}\n")

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    analyze_perturbations()
