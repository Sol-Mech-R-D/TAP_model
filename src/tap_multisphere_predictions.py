# -*- coding: utf-8 -*-
"""
tap_multisphere_predictions.py
==============================
Computes the regional coupling strengths and predictions for the 
Tectonic, Atmospheric, and Cosmic spheres under the TAP model.

Models:
  1. Tectonic (California strike-slip vs. Japan subduction)
  2. Weather (Tornado Alley vs. Western Pacific Typhoons)
  3. Cosmic (Solar Tachocline reconnection rate & Cosmic Ray flux)
"""

import os
import math
import json

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Current address: (M=0, ΔB=8, ψ=0.0265)
DELTA_B = 8
PSI = 0.0265
GAMMA = 1.0 + DELTA_B * PHI_INV13

def calculate_regional_coupling():
    """
    Computes regional coupling factors (scaling with local dimensional warp).
    """
    # ── Tectonic Coupling ────────────────────────────────────────────────────
    # Strike-slip faults (shear-sensitive, like San Andreas) scale with horizontal metric strain:
    #   K_shear ∝ φ⁻⁴ * ΔB * (1 - ψ)
    k_shear = (PHI ** -4) * DELTA_B * (1.0 - PSI)
    
    # Subduction zones (vertical pressure sensitive, like Japan/Chile) scale with G_eff:
    #   K_normal ∝ Γ(ΔB) * φ⁻⁸
    k_normal = GAMMA * (PHI ** -8)
    
    # ── Atmospheric Coupling ─────────────────────────────────────────────────
    # Convective storm electrification (lightning/Debye) scales with α drift:
    #   K_debye ∝ (Γ(ΔB) - 1) * φ⁵
    k_debye = (GAMMA - 1.0) * (PHI ** 5)
    
    # Vortex/Tornado stability scales with 3:1 partition ratio variance:
    #   K_vortex ∝ (1 - ψ)^(φ⁻⁴)
    k_vortex = (1.0 - PSI) ** (PHI ** -4)
    
    # ── Cosmic Coupling ──────────────────────────────────────────────────────
    # Solar magnetic reconnection trigger rate (Tachocline stress):
    #   K_solar ∝ φ⁻¹³ * ΔB * (1 + PSI)
    k_solar = PHI_INV13 * DELTA_B * (1.0 + PSI)
    
    return {
        "tectonic": {
            "california_strike_slip_coupling": k_shear,
            "japan_subduction_coupling": k_normal
        },
        "atmospheric": {
            "lightning_debye_coupling": k_debye,
            "tornado_vortex_coupling": k_vortex
        },
        "cosmic": {
            "solar_reconnection_coupling": k_solar
        }
    }

def main():
    print("=" * 80)
    print("  TAP MULTI-SPHERE REGIONAL COUPLING CALCULATOR")
    print("=" * 80)
    
    c = calculate_regional_coupling()
    
    print("  Tectonic Coupling Factors:")
    print(f"    - California Strike-Slip (Shear) : {c['tectonic']['california_strike_slip_coupling']:.4f}")
    print(f"    - Japan Megathrust (Normal)      : {c['tectonic']['japan_subduction_coupling']:.4f}")
    print()
    print("  Atmospheric Coupling Factors:")
    print(f"    - Storm Debye Electrification    : {c['atmospheric']['lightning_debye_coupling']:.4f}")
    print(f"    - Tornado Soliton Vortex         : {c['atmospheric']['tornado_vortex_coupling']:.4f}")
    print()
    print("  Cosmic Coupling Factors:")
    print(f"    - Solar Flare Reconnection       : {c['cosmic']['solar_reconnection_coupling']:.4f}")
    
    # Save to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_geocosmic_coupling.json")
    
    with open(out_path, "w") as f:
        json.dump(c, f, indent=2)
    print(f"\n  [EXPORT] Regional coupling saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
