# -*- coding: utf-8 -*-
"""
tap_planetary_dynamos.py
========================
Predicts planetary core temperatures and geodynamo status (active magnetic field)
across solar system planets and exoplanets using the TAP volume-to-surface heat cascade.
Uses scipy.integrate.solve_ivp to solve the cooling differential equations.
"""

import math
import numpy as np
from scipy import constants as const
from scipy.integrate import solve_ivp
from astropy import constants as ac
from science_constants import PHI, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum

def predict_dynamos():
    # Solve cascade VEV ratio
    _, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
    v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV
    PHI_INV4 = PHI ** -4
    
    # Planetary catalog: (Name, Radius relative to Earth, Mass relative to Earth, Atmosphere/Lid)
    planets = [
        ("Earth", 1.0, 1.0, "active_tectonics"),
        ("Mars", 0.53, 0.107, "stagnant_dead"),
        ("Venus", 0.95, 0.815, "stagnant_lid"),
        ("Super-Earth Kepler-186f", 1.17, 1.44, "active_tectonics")
    ]
    
    results = {}
    for name, r_rel, m_rel, lid in planets:
        # Vol-to-surface ratio scales with radius: cooling coeff = 0.3 / r_rel
        cooling_coeff = 0.3 / r_rel
        T_mantle = 3000.0
        
        # TAP heat generation scales with core volume (r_rel^2) and VEV ratio
        Q_tap = 450.0 * PHI_INV4 * v_ratio * (r_rel ** 2)
        
        def cooling_ode(t, T):
            # Radioactive heat decays over time (half life ~ 1.5 Gyr)
            Q_rad = 600.0 * np.exp(-t / 1.5)
            dT = -cooling_coeff * (T - T_mantle) + Q_rad + Q_tap
            return [dT]
            
        sol = solve_ivp(cooling_ode, (0.0, 4.5), [6000.0], t_eval=[4.5])
        T_final = sol.y[0][0]
        
        # Geodynamo active if T_final > 4150 K and tectonics allow convection
        if T_final >= 4150.0 and lid != "stagnant_lid":
            status = "ACTIVE DYNAMO (Shielded)"
        elif T_final >= 4150.0 and lid == "stagnant_lid":
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
