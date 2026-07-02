# -*- coding: utf-8 -*-
"""
tap_core_ai_cascade.py
======================
Calculates the coupling strengths and metrics for:
  1. Planetary Cores (Convective plume buoyancy fluctuations in live vs. dead cores)
  2. AI compute grid thermal throttling & data center grid stress
  3. Resource extraction / baseload fuel grid vulnerabilities

All modulated by the Trans-Cyclic address (M=0, ΔB=8, ψ=0.0265).
"""

import os
import math
import json
from science_constants import PHI, N_BREATH, GAMMA_BREATH, PSI_BREATH

# Trans-Cyclic Address (Wired to central Breath Clock constants)
DELTA_B = N_BREATH
PSI = PSI_BREATH
GAMMA = GAMMA_BREATH

def calculate_core_and_compute_coupling():
    """
    Computes numerical coupling indices for planetary dynamos and AI/Energy grids.
    """
    # ── 1. Planetary Core Plume Buoyancy (F_b) ───────────────────────────────
    # Live cores (like Earth) respond to G_eff fluctuations:
    #   ΔF_b ∝ Γ(ΔB) * φ⁻⁸ * (live_core_fraction)
    #   Earth: live core fraction ≈ 1.0
    #   Venus: stagnant lid, live core ≈ 0.5 (no dynamo coupling)
    #   Mars: dead core ≈ 0.0
    live_core_earth = 1.0
    live_core_venus = 0.5
    live_core_mars  = 0.0
    
    buoyancy_earth = GAMMA * (PHI ** -8) * live_core_earth
    buoyancy_venus = GAMMA * (PHI ** -8) * live_core_venus
    buoyancy_mars  = GAMMA * (PHI ** -8) * live_core_mars
    
    # ── 2. AI Compute Grid Stress (Data Center Thermal Throttling) ───────────
    # Throttling is driven by peak crossing temperatures (Class-A α-coupling):
    #   DC_stress ∝ φ⁻⁴ * ΔB * (1 + ψ)
    compute_grid_stress = (PHI ** -4) * DELTA_B * (1.0 + PSI)
    
    # ── 3. Resource Extraction / Fuel Grid Vulnerability ────────────────────
    # Energy grid stability (Class-B gravity-coupling affecting hydropower/pipelines):
    #   Fuel_stress ∝ (Γ(ΔB) - 1) * φ⁸
    fuel_grid_stress = (GAMMA - 1.0) * (PHI ** 8)
    
    return {
        "planetary_cores": {
            "earth_plume_buoyancy_delta": buoyancy_earth,
            "venus_plume_buoyancy_delta": buoyancy_venus,
            "mars_plume_buoyancy_delta": buoyancy_mars
        },
        "ai_compute_grid": {
            "data_center_thermal_throttling_index": compute_grid_stress
        },
        "energy_and_fuel": {
            "baseload_fuel_grid_stress_index": fuel_grid_stress
        }
    }

def main():
    print("=" * 80)
    print("  TAP PLANETARY CORES & INDUSTRIAL AI-ENERGY CASCADE")
    print("=" * 80)
    
    c = calculate_core_and_compute_coupling()
    
    print("  Planetary Core Buoyancy Fluctuations (ΔF_b):")
    print(f"    - Earth (Active Dynamo)  : {c['planetary_cores']['earth_plume_buoyancy_delta']:.5f}")
    print(f"    - Venus (Stagnant Lid)   : {c['planetary_cores']['venus_plume_buoyancy_delta']:.5f}")
    print(f"    - Mars (Dead Core)       : {c['planetary_cores']['mars_plume_buoyancy_delta']:.5f}")
    print()
    print("  AI Compute & Hardware Cooling:")
    print(f"    - Data Center Throttling : {c['ai_compute_grid']['data_center_thermal_throttling_index']:.4f}")
    print()
    print("  Baseload Fuel & Extraction:")
    print(f"    - Grid/Extraction Stress : {c['energy_and_fuel']['baseload_fuel_grid_stress_index']:.4f}")
    
    # Save to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_core_ai_coupling.json")
    
    with open(out_path, "w") as f:
        json.dump(c, f, indent=2)
    print(f"\n  [EXPORT] Core-AI cascade parameters saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
