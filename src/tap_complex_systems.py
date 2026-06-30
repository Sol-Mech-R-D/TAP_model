# -*- coding: utf-8 -*-
"""
tap_complex_systems.py
======================
Simulates three advanced complex systems:
1. Quantitative Finance: Weyl-discrepancy tail risk options pricing.
2. Epidemiology: Fibonacci percolation threshold in contact networks.
3. Aerospace Propulsion: Asymmetric Casimir vacuum thrust limits.
All models are dynamically coupled to the master VEV cascade.
"""

import math
import numpy as np
from scipy import constants as const
from science_constants import PHI, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum

def run_complex_systems():
    # Solve VEV ratio from Sturm-Liouville Dirac solver
    _, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
    v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV
    
    PHI_INV4 = PHI ** -4
    PHI_INV8 = PHI ** -8
    
    # -------------------------------------------------------------------------
    # 1. QUANTITATIVE FINANCE: TAIL RISK BLACK SWAN ESTIMATOR
    # -------------------------------------------------------------------------
    # Options pricing: Asset price S=100, Strike K=100, Time T=1 yr, Vol=20%
    # Compare standard Black-Scholes (Gaussian) tail risk to TAP Weyl distribution
    spot = 100.0
    strike = 120.0  # Deep out-of-the-money
    vol = 0.20
    
    # Black-Scholes probability of exercise (Gaussian tail)
    d2_bs = (math.log(spot / strike) - 0.5 * (vol ** 2)) / vol
    p_exercise_bs = 0.5 * (1.0 + math.erf(d2_bs / math.sqrt(2.0)))
    
    # TAP tail risk scales with the power-law tail exponent beta = phi - 1
    # Weyl distribution has heavier tails due to low-discrepancy fluctuations
    beta = (PHI - 1.0) * (1.0 - PHI_INV8 * v_ratio)
    p_exercise_tap = p_exercise_bs * (1.0 + PHI_INV4 * v_ratio * (strike / spot) ** beta)
    
    # -------------------------------------------------------------------------
    # 2. EPIDEMIOLOGY: PANDEMIC NETWORK PERCOLATION
    # -------------------------------------------------------------------------
    # Percolation threshold on scale-free contact networks
    p_critical_std = 0.50  # Standard random network threshold
    p_critical_tap = 1.0 - (PHI ** -1)  # Topologically protected threshold = 0.38196
    
    # Effective herd immunity threshold (HIT) required
    hit_std = 1.0 - (1.0 / 2.0)  # 50%
    hit_tap = 1.0 - p_critical_tap  # 61.8%
    
    # -------------------------------------------------------------------------
    # 3. AEROSPACE PROPULSION: ASYMMETRIC CASIMIR THRUST
    # -------------------------------------------------------------------------
    # We query scipy constants for h_bar and c
    hbar = const.hbar
    c = const.c
    
    # Cavity geometry: Length L = 0.1 m, small radius r1 = 0.01 m, large radius r2 = 0.05 m
    L = 0.1
    r1 = 0.01
    r2 = 0.05
    
    # Vacuum zero point energy gradient: F = h_bar * c * A * (1/r1^4 - 1/r2^4) / 240
    # Modulated by extra-dimensional leakage phi^-4 and VEV ratio
    area_avg = PI * ((r1 + r2) / 2.0) ** 2
    f_casimir_std = (hbar * c * PI * area_avg) * (1.0 / (r1 ** 4) - 1.0 / (r2 ** 4)) / 240.0
    f_casimir_tap = f_casimir_std * PHI_INV4 * v_ratio
    
    return {
        "v_ratio": v_ratio,
        "option_strike": strike,
        "option_bs_prob_pct": p_exercise_bs * 100.0,
        "option_tap_prob_pct": p_exercise_tap * 100.0,
        "percolation_threshold_std": p_critical_std,
        "percolation_threshold_tap": p_critical_tap,
        "casimir_thrust_n": f_casimir_tap
    }

if __name__ == "__main__":
    res = run_complex_systems()
    print("TAP Complex Systems Simulations:")
    for k, v in res.items():
        if "thrust" in k:
            print(f"  {k:<30}: {v:.6e} N")
        else:
            print(f"  {k:<30}: {v:.6f}")
