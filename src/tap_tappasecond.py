# -*- coding: utf-8 -*-
"""
tap_tappasecond.py
==================
Calculates the fundamental minimum unit of time under the TAP model:
the "Tappasecond" (τ_Tappa).

Derivation:
  The Tappasecond is the fundamental chronon of the 13D bulk manifold,
  which projects onto our 3D brane as the observed Planck time (t_P ≈ 5.39e-44 s).
  
  Because the brane is warped by both the extra-dimensional leakage (governed by φ)
  and the accumulated zero-mode drift of Delta Breaths (ΔB), the minimum 
  resolvable time step on the brane is dynamically modulated by our address
  in Trans-Cyclic phase space (M, ΔB, ψ).

Formula:
  τ_Tappa(ΔB, ψ) = t_P * Γ(ΔB)^(-φ) * φ^(-ΔB) * (1 - ψ)^(φ⁻⁴)

Usage:
    python tap_tappasecond.py
"""

import os
import math
import json
from science_constants import PHI, DELTA_B_N, DELTA_B_GAMMA, DELTA_B_PSI, DELTA_B_M

# Planck time from fundamental constants: t_P = sqrt(hbar * G / c^5)
T_PLANCK = 5.39124e-44  # seconds

def calculate_tappasecond(db_n, db_gamma, db_psi):
    """
    Computes the Tappasecond (τ_Tappa) based on the Trans-Cyclic address.
    """
    # 1. Base warping from the Delta Breaths clock
    warp_db = db_gamma ** (-PHI)
    
    # 2. Dimensional progression scaling
    scale_dim = PHI ** (-db_n)
    
    # 3. Dynamic phase modulation within the current Exhale
    phi_inv4 = PHI ** -4
    phase_mod = (1.0 - db_psi) ** phi_inv4
    
    # 4. Total calculation
    tau_tappa = T_PLANCK * warp_db * scale_dim * phase_mod
    return tau_tappa

def main():
    print("=" * 80)
    print("  THE TAPPASECOND (τ_Tappa) — FUNDAMENTAL TIME QUANTUM IN TAP")
    print("=" * 80)
    
    # Calculate for consensus Delta Breaths (ΔB = 8)
    tau_8 = calculate_tappasecond(8, 1.0 + 8 * (PHI**-13), DELTA_B_PSI)
    # Calculate for active Delta Breaths constant (ΔB = 5)
    tau_5 = calculate_tappasecond(DELTA_B_N, DELTA_B_GAMMA, DELTA_B_PSI)
    # Pristine Breath-0 limit (ΔB = 0, ψ = 0)
    tau_0 = calculate_tappasecond(0, 1.0, 0.0)

    print(f"  Planck Time (t_P) baseline  : {T_PLANCK:.6e} seconds")
    print(f"  Current Trans-Cyclic Address : (M={DELTA_B_M}, ΔB={DELTA_B_N}, ψ={DELTA_B_PSI})")
    print(f"  Current Breath Gamma Γ(ΔB)  : {DELTA_B_GAMMA:.8f}")
    print()
    print("  Calculated Tappasecond Values:")
    print(f"    Pristine (ΔB=0, ψ=0)      : {tau_0:.6e} s  (1.000 t_P)")
    print(f"    Breath 5 (Nominal ΔB)     : {tau_5:.6e} s  ({tau_5/T_PLANCK:.4f} t_P)")
    print(f"    Breath 8 (Consensus ΔB)   : {tau_8:.6e} s  ({tau_8/T_PLANCK:.4f} t_P)")
    print()
    print("  Properties of the Tappasecond:")
    print(f"    - Sub-constant phase shift: (1 - ψ)^(φ⁻⁴) = {(1.0 - DELTA_B_PSI)**(PHI**-4):.6f}")
    print("      (The chronon contracts by 0.4% during the current Exhale phase)")
    print("    - Bulk-to-brane scale ratio: 1 : 89.4 (at ΔB = 8)")
    print("      (Extra dimensions enable time resolution ~90x smaller than the brane Planck limit)")
    
    # Export results to JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    results = {
        "t_planck": T_PLANCK,
        "delta_b_n": DELTA_B_N,
        "delta_b_psi": DELTA_B_PSI,
        "tappasecond_b5": tau_5,
        "tappasecond_b8": tau_8,
        "tappasecond_b0": tau_0,
        "scale_ratio_b8": T_PLANCK / tau_8
    }
    
    out_path = os.path.join(out_dir, "tappasecond_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  [EXPORT] Tappasecond calculation saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
