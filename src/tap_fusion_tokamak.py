# -*- coding: utf-8 -*-
"""
tap_fusion_tokamak.py
======================
TAP Model -- Magnetohydrodynamic Tokamak Confinement Simulator
Simulates radial plasma pressure/density diffusion and boundary turbulence.
Compares standard MHD confinement (subject to Edge-Localized Modes / ELMs)
vs. TAP-stabilized confinement using the 5D boundary restoration term.
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PHI_INV4, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum
_, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV

def simulate_tokamak():
    print("=" * 72)
    print("  TAP TOKAMAK FUSION PLASMADYNAMICS SIMULATOR")
    print("=" * 72)
    
    # Confinement parameters (normalized units)
    R_minor = 1.0       # Minor radius (meters)
    N_grid = 30         # Spatial grid size (optimized for stability)
    dr = R_minor / (N_grid - 1)
    r = np.linspace(1e-5, R_minor, N_grid)  # Avoid division by zero at r=0
    
    # Time settings
    t_max = 1.0         # Total simulation time (seconds)
    dt = 0.0001         # Time step (satisfies CFL condition delta_t < delta_r^2 / 2D)
    steps = int(t_max / dt)
    
    # Diffusion coefficients
    D_core = 0.01       # Core diffusion coefficient
    D_edge_std = 0.20   # Standard turbulent edge diffusion
    D_edge_tap = 0.03   # TAP stabilized edge diffusion
    
    # Initial plasma density profile (normalized, parabolic core-peaked)
    n_std = 1.0 * (1.0 - (r / R_minor)**2) + 0.01
    n_tap = np.copy(n_std)
    
    # Source term (heating/fueling at center r < 0.2)
    source = np.zeros(N_grid)
    source[r < 0.2] = 2.0
    
    # Record history for diagnostics
    time_points = []
    energy_confinement_std = []
    energy_confinement_tap = []
    
    # Compute boundary profiles over time
    for step in range(steps):
        t = step * dt
        
        # Spatial diffusion updates using finite differences
        dn_std = np.zeros(N_grid)
        dn_tap = np.zeros(N_grid)
        
        for i in range(1, N_grid - 1):
            ri = r[i]
            
            # Diffusion coefficient profiles (turbulent edge leakage near boundary r > 0.7)
            if ri > 0.7:
                D_ri_std = D_core + (D_edge_std - D_core) * ((ri - 0.7) / 0.3)**2
                D_ri_tap = D_core + (D_edge_tap - D_core) * ((ri - 0.7) / 0.3)**2
            else:
                D_ri_std = D_core
                D_ri_tap = D_core
                
            # Centered spatial differences
            d2n_std = (n_std[i+1] - 2*n_std[i] + n_std[i-1]) / (dr**2)
            d1n_std = (n_std[i+1] - n_std[i-1]) / (2*dr)
            dn_std[i] = D_ri_std * (d2n_std + d1n_std / ri) + source[i]
            
            d2n_tap = (n_tap[i+1] - 2*n_tap[i] + n_tap[i-1]) / (dr**2)
            d1n_tap = (n_tap[i+1] - n_tap[i-1]) / (2*dr)
            
            # TAP stabilization includes the phi^-4 topological drag term
            restoration = PHI_INV4 * (n_tap[i] - n_std[i]) * v_ratio
            dn_tap[i] = D_ri_tap * (d2n_tap + d1n_tap / ri) + source[i] - restoration
            
        # Boundary conditions: dn/dr = 0 at center, n = 0 at wall
        n_std[0] = n_std[1]
        n_std[-1] = 0.01
        n_tap[0] = n_tap[1]
        n_tap[-1] = 0.01
        
        # Euler step
        n_std += dn_std * dt
        n_tap += dn_tap * dt
        
        # Enforce physical floor
        n_std = np.clip(n_std, 0.01, None)
        n_tap = np.clip(n_tap, 0.01, None)
        
        # Calculate approximate energy confinement metrics (integrated density volume)
        if step % 200 == 0:
            time_points.append(t)
            total_n_std = np.sum(n_std * r * dr)
            total_n_tap = np.sum(n_tap * r * dr)
            energy_confinement_std.append(total_n_std)
            energy_confinement_tap.append(total_n_tap)
            
    print("  Simulation completed.")
    print(f"    Final Core Density (Std): {n_std[0]:.6f}")
    print(f"    Final Core Density (TAP): {n_tap[0]:.6f}")
    
    # Save raw data
    data = {
        "radial_coordinates": r.tolist(),
        "final_profile_std": n_std.tolist(),
        "final_profile_tap": n_tap.tolist(),
        "time_history": time_points,
        "confinement_metric_std": energy_confinement_std,
        "confinement_metric_tap": energy_confinement_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_fusion_tokamak_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- MHD Tokamak Plasma Confinement Simulator", color="white", fontsize=14, fontweight="bold")
    
    for ax in axes:
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        ax.grid(True, color=(1, 1, 1, 0.05))
        
    BLUE = "#7c6af7"
    GREEN = "#4ecdc4"
    ORANGE = "#ff6b6b"
    
    # Panel 1: Radial Density Profile
    ax = axes[0]
    ax.plot(r, n_std, color=ORANGE, lw=2.0, label="Standard MHD (Turbulent)")
    ax.plot(r, n_tap, color=GREEN, lw=2.0, label="TAP Confinement (Stabilized)")
    ax.set_xlabel("Minor Radius r (meters)")
    ax.set_ylabel("Normalized Plasma Density")
    ax.set_title("Radial Plasma Density Profile")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Confinement Metric over Time
    ax = axes[1]
    ax.plot(time_points, energy_confinement_std, color=ORANGE, lw=2.0, label="Standard Confinement")
    ax.plot(time_points, energy_confinement_tap, color=GREEN, lw=2.0, label="TAP Stabilized Confinement")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Integrated Plasma Density")
    ax.set_title("Plasma Confinement Efficiency over Time")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_fusion_tokamak.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Confinement visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_tokamak()
