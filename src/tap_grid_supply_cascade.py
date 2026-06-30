# -*- coding: utf-8 -*-
"""
tap_grid_supply_cascade.py
==========================
Calculates the coupling strengths and metrics for:
  1. Power Grids (Texas ERCOT sag/resistivity stress vs. European ENTSO-E)
  2. Supply Lines (Rail line sun kink buckling & Panama Canal draft restrictions)

All modulated by the Trans-Cyclic address (M=0, ΔB=8, ψ=0.0265).
"""

import os
import math
import json

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Trans-Cyclic Address
DELTA_B = 8
PSI = 0.0265
GAMMA = 1.0 + DELTA_B * PHI_INV13

def calculate_grid_and_supply_coupling():
    """
    Computes numerical coupling indices for power grids and global supply lines.
    """
    # ── 1. Power Grid Sag & Resistivity Stress (e.g. Texas ERCOT) ───────────
    # Isolated grids with high thermal load have maximum vulnerability:
    #   Grid_Sag ∝ φ⁻⁴ * ΔB * (1 + ψ) * grid_isolation_factor
    #   Texas ERCOT isolation factor ≈ 1.2 (due to lack of interstate ties)
    #   Europe ENTSO-E isolation factor ≈ 0.4 (highly interconnected)
    base_thermal_stress = (PHI ** -4) * DELTA_B * (1.0 + PSI)
    
    ercot_stress = base_thermal_stress * 1.2
    entsoe_stress = base_thermal_stress * 0.4
    
    # ── 2. Rail Line Buckling Risk (Sun Kinks) ───────────────────────────────
    # Metal rail tracks buckle under thermal expansion during crossing heat locks:
    #   Rail_Buckle ∝ φ⁻⁴ * ΔB * (1 - ψ)
    rail_buckle_risk = (PHI ** -4) * DELTA_B * (1.0 - PSI)
    
    # ── 3. Panama Canal Hydrological Draft Restrictions ──────────────────────
    # Droughts affecting lock water supply scale with vertical pressure locks (Class-B):
    #   Panama_Draft ∝ Γ(ΔB) * φ⁻⁸
    panama_draft_stress = GAMMA * (PHI ** -8)
    
    return {
        "power_grids": {
            "texas_ercot_sag_stress": ercot_stress,
            "europe_entsoe_sag_stress": entsoe_stress
        },
        "supply_lines": {
            "rail_sun_kink_buckling_risk": rail_buckle_risk,
            "panama_canal_draft_restriction": panama_draft_stress
        }
    }

def main():
    print("=" * 80)
    print("  TAP POWER GRIDS & GLOBAL SUPPLY LINE CASCADE")
    print("=" * 80)
    
    c = calculate_grid_and_supply_coupling()
    
    print("  Power Grid Stress Indices:")
    print(f"    - Texas ERCOT (Isolated Grid)   : {c['power_grids']['texas_ercot_sag_stress']:.4f}")
    print(f"    - Europe ENTSO-E (Connected)    : {c['power_grids']['europe_entsoe_sag_stress']:.4f}")
    print()
    print("  Supply Line Risk Indices:")
    print(f"    - Rail Track Sun Kink Buckling  : {c['supply_lines']['rail_sun_kink_buckling_risk']:.4f}")
    print(f"    - Panama Canal Draft Constraint : {c['supply_lines']['panama_canal_draft_restriction']:.4f}")
    
    # Save to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_grid_supply_coupling.json")
    
    with open(out_path, "w") as f:
        json.dump(c, f, indent=2)
    print(f"\n  [EXPORT] Grid-Supply cascade parameters saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
