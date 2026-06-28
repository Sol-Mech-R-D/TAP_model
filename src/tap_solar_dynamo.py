# -*- coding: utf-8 -*-
"""
tap_solar_dynamo.py
===================
Solar core dynamo model under the TAP lens.
Computes CME probability and geomagnetically induced current (GICs) stress indices
using the solar sub-breath resonance clock (T_solar ≈ 27.27 days).
"""

import os
import json
import math
from science_constants import PHI, PHI_INV4

def main():
    print("=" * 80)
    print("  TAP SOLAR CORE DYNAMO & CME PREDICTION MODEL")
    print("=" * 80)
    
    # Solar rotation period (synodic) as driving cycle
    T_solar_days = 27.2753
    # Solar sub-breath period scaling: T_solar * φ^-3 ≈ 6.438 days
    T_sub_solar = T_solar_days * (PHI ** -3) 
    
    print(f"  Solar Rotation Period  : {T_solar_days:.4f} days")
    print(f"  Solar Sub-Breath Period : {T_sub_solar:.4f} days")
    
    # Generate 1-year prediction sweep for solar flare activity index (F_idx)
    predictions = []
    
    # Anchor to solstice epoch: June 21, 2026
    start_time_days = 0.0 # days from solstice
    
    for day in range(365):
        t_elapsed = start_time_days + day
        # Calculate three-coordinate resonance phase
        phase_rot = (t_elapsed % T_solar_days) / T_solar_days
        phase_sub = (t_elapsed % T_sub_solar) / T_sub_solar
        
        # Double attractor resonance coupling
        coupling = 0.5 * (math.sin(2 * math.pi * phase_rot) + math.sin(2 * math.pi * phase_sub))
        
        # Calculate CME trigger stress index (0 to 100%)
        # Base activity is modulated by Golden ratio scaling
        cme_stress_idx = (coupling + 1.0) / 2.0 * 100.0 * (1.0 + PHI_INV4 * math.sin(t_elapsed / 365.25 * 2 * math.pi))
        
        # Limit to 100%
        cme_stress_idx = min(100.0, max(0.0, cme_stress_idx))
        
        # Grid sag hazard potential (GIC index)
        gic_hazard = cme_stress_idx * 1.45 * (1.0 + 0.1 * math.sin(phase_rot * 2 * math.pi))
        
        predictions.append({
            "day_from_solstice": day,
            "cme_stress_idx": round(cme_stress_idx, 2),
            "gic_hazard_idx": round(gic_hazard, 2)
        })
        
        # Highlight first few days
        if day < 5:
            print(f"    Day {day:2d} | CME Stress Index: {cme_stress_idx:6.2f}% | GIC Sag Hazard: {gic_hazard:6.2f}")
            
    out_data = {
        "solar_rotation_days": T_solar_days,
        "solar_sub_breath_days": T_sub_solar,
        "predictions_365d": predictions
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "../assets/tap_solar_dynamo_results.json")
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"\n  [EXPORT] Solar dynamo results saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
