# -*- coding: utf-8 -*-
"""
tap_bullet_cluster.py
=====================
Simulates the collision of gas and Weyl soliton dark matter in colliding galaxy clusters.
Calculates the spatial separation of the lensing peak relative to the gas.
"""

import math
import numpy as np
from science_constants import PHI, PHI_INV4, PI

def run_bullet_simulation(v_ratio=1.0098):
    # Soliton bulk propagation velocity
    v_soliton = math.sqrt(1.0 - PHI_INV4) # in units of c
    
    # Gas drag coefficient slowing the baryonic core
    gas_drag = 0.45 * (1.0 + (PHI ** -8) * v_ratio)
    
    # Lensing peak separation after t = 100 Myr collision time
    # delta_x = (v_soliton - (v_soliton * e^-drag)) * t
    delta_x_kpc = 150.0 * (v_soliton - v_soliton * math.exp(-gas_drag))
    
    return v_soliton, delta_x_kpc

if __name__ == "__main__":
    v_sol, dx = run_bullet_simulation()
    print(f"TAP Bullet Cluster Crossover Simulation:")
    print(f"  Soliton Velocity: {v_sol:.4f} c")
    print(f"  Lensing Offset  : {dx:.4f} kpc")
