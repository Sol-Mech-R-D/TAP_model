# -*- coding: utf-8 -*-
"""
tap_planetary_dynamos.py
========================
Predicts planetary core temperatures and geodynamo status (active magnetic field)
across solar system planets and exoplanets using the TAP volume-to-surface heat cascade.
Uses astropy and scipy constants for physical parameters.
"""

import math
import numpy as np
from scipy import constants as const
from astropy import constants as ac
from science_constants import PHI, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum

def predict_dynamos():
    # Solve cascade VEV ratio
    _, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
    v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV
    PHI_INV4 = PHI ** -4
    
    # Standard constants
    G = const.G
    
    # Planetary catalog: (Name, Radius relative to Earth, Mass relative to Earth, Atmosphere/Lid)
    planets = [
        ("Earth", 1.0, 1.0, "active_tectonics"),
        ("Mars", 0.53, 0.107, "stagnant_dead"),
        ("Venus", 0.95, 0.815, "stagnant_lid"),
        ("Super-Earth Kepler-186f", 1.17, 1.44, "active_tectonics"),
        ("Sub-Earth Proxima b", 1.03, 1.07, "active_tectonics"),
        ("Mars-sized Exoplanet", 0.60, 0.15, "stagnant_dead")
    ]
    
    results = {}
    for name, r_rel, m_rel, lid in planets:
        # Volume-to-surface ratio scales with radius
        # Vol ~ R^3 (heat generation), Surface ~ R^2 (heat loss)
        # Net cooling rate is proportional to 1/R
        cooling_factor = 0.3 / r_rel
        
        # TAP core heat generation scales with core volume (R^3) and VEV ratio
        Q_tap = 450.0 * PHI_INV4 * v_ratio * (r_rel ** 1.5)
        
        # Initial core temp T0 = 6000 K, solve cooling over t = 4.5 Gyr
        # dT/dt = - cooling_factor * (T - 3000.0) + Q_tap
        # Steady state T_final = 3000.0 + Q_tap / cooling_factor
        T_final = 3000.0 + (Q_tap / cooling_factor) * (1.0 - math.exp(-cooling_factor * 4.5))
        
        # Geodynamo active if T_final > 4200 K and tectonics allow convection
        if T_final >= 4200.0 and lid != "stagnant_lid":
            status = "ACTIVE DYNAMO (Shielded)"
        elif T_final >= 4200.0 and lid == "stagnant_lid":
            status = "ACTIVE CORE / NO DYNAMO (Stagnant Lid)"
        else:
            status = "DEAD CORE (Frozen / Exposed)"
            
        results[name] = {
            "radius_m": r_rel * ac.R_earth.si.value,
            "final_core_temp_k": T_final,
            "status": status
        }
        
    return results

if __name__ == "__main__":
    res = predict_dynamos()
    print("TAP Planetary Dynamo & Core Temperature Predictions:")
    for name, data in res.items():
        print(f"  {name:<25}: {data['final_core_temp_k']:.1f} K | {data['status']}")
