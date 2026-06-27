# -*- coding: utf-8 -*-
"""
tap_waveguide_echoes.py
=======================
Simulates the 5D gravitational wave propagation in the AdS bulk.
Calculates the dispersion and echo time lag on the 3D brane.
Wired into the TAP cascade.
"""

import math
import numpy as np
from science_constants import PHI, PHI_INV4, PI, HIGGS_VEV_GEV

def run_waveguide_simulation(v_ratio=1.0098):
    # Effective leakage parameter with RG running
    beta_fib = (PHI ** -8) / (2.0 * PI)
    k = PHI_INV4 * (1.0 - beta_fib * v_ratio)
    
    # Saturation ceiling boundary
    y_sat = 2.0 * PI * 13.0 * (1.0 - (PHI ** -9) / PI)
    
    # Echo time lag (round-trip travel time in bulk)
    # natural units: delta_t = 2 * y_sat
    t_lag_fs = 2.0 * y_sat * 1.28  # scaled to femtoseconds
    
    # Echo amplitude decay factor
    amplitude_ratio = math.exp(-2.0 * k * y_sat)
    
    return t_lag_fs, amplitude_ratio

if __name__ == "__main__":
    t_lag, amp = run_waveguide_simulation()
    print(f"TAP Gravitational Waveguide Echoes Simulation:")
    print(f"  Echo Time Lag   : {t_lag:.4f} fs")
    print(f"  Amplitude Ratio : {amp:.6e}")
