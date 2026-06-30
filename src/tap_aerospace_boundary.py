# -*- coding: utf-8 -*-
"""
tap_aerospace_boundary.py
=========================
TAP Model -- Aerospace Boundary Layer & Drag Reduction Simulator
Simulates fluid velocity profiles over a solid surface boundary layer.
Compares standard boundary layer velocity gradients (high skin-friction drag)
vs. TAP soliton boundary layer control (using phi^-4 wave perturbations),
demonstrating drag reduction and boundary-layer laminar stabilization.
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

def simulate_boundary():
    print("=" * 72)
    print("  TAP AEROSPACE BOUNDARY LAYER DRAG SIMULATOR")
    print("=" * 72)
    
    # Boundary layer grid setup
    N_y = 100            # Vertical grid resolution (distance from surface)
    y_max = 0.05        # Boundary layer height boundary (meters)
    y = np.linspace(0, y_max, N_y)
    dy = y_max / (N_y - 1)
    
    # Flow properties
    U_inf = 50.0        # Free-stream velocity (m/s)
    nu = 1.5e-5         # Kinematic viscosity of air (m^2/s)
    x = 1.0             # Downstream distance (meters)
    
    # Classical Blasius velocity profile approximation for laminar boundary layer
    # u(y) = U_inf * erf(y * sqrt(U_inf / (4 * nu * x)))
    eta = y * math.sqrt(U_inf / (4.0 * nu * x))
    u_laminar = U_inf * np.vectorize(math.erf)(eta)
    
    # Standard turbulent transition profile (high gradient near wall)
    # Approximated by 1/7th power law: u(y) = U_inf * (y/delta)^(1/7)
    delta_std = 0.035
    u_turbulent_std = U_inf * (y / delta_std) ** (1.0 / 7.0)
    u_turbulent_std[y > delta_std] = U_inf
    u_turbulent_std[0] = 0.0 # No-slip condition
    
    # TAP soliton boundary layer control:
    # Demonstrates fractional laminarization of the boundary layer
    # The stabilized boundary layer profile is modeled as a linear combination of the
    # turbulent state and the clean laminar state, scaled by the TAP leakage rate (phi^-4)
    u_tap = u_turbulent_std + PHI_INV4 * (u_laminar - u_turbulent_std) * v_ratio
    u_tap[0] = 0.0 # No-slip
    
    # Calculate skin friction coefficients (Cf) from velocity gradient at the wall (y=0)
    # Cf = 2 * tau_w / (rho * U_inf^2) where tau_w = mu * (du/dy)|_wall
    # Proportional to (u[1] - u[0]) / dy
    grad_laminar = u_laminar[1] / dy
    grad_std = u_turbulent_std[1] / dy
    grad_tap = u_tap[1] / dy
    
    # Normalize drag force values
    drag_laminar = grad_laminar * 1e-5
    drag_std = grad_std * 1e-5
    drag_tap = grad_tap * 1e-5
    
    print("  Simulation completed.")
    print(f"    Skin friction gradient at wall (Std): {grad_std:.4f} s^-1")
    print(f"    Skin friction gradient at wall (TAP): {grad_tap:.4f} s^-1 (Reduction: {((grad_std - grad_tap) / grad_std) * 100.0:.2f}%)")
    
    # Save raw data
    data = {
        "height_coordinates_y": y.tolist(),
        "velocity_profile_laminar": u_laminar.tolist(),
        "velocity_profile_std": u_turbulent_std.tolist(),
        "velocity_profile_tap": u_tap.tolist(),
        "skin_friction_laminar": drag_laminar,
        "skin_friction_std": drag_std,
        "skin_friction_tap": drag_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_aerospace_boundary_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- Aerospace Boundary Layer Drag Simulator", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Boundary Layer Velocity Profiles
    ax = axes[0]
    ax.plot(u_laminar, y * 1000, color=BLUE, ls="--", lw=1.5, label="Laminar Boundary (Ideal)")
    ax.plot(u_turbulent_std, y * 1000, color=ORANGE, lw=2.0, label="Standard Boundary (Turbulent)")
    ax.plot(u_tap, y * 1000, color=GREEN, lw=2.0, label="TAP Conformal Control (Laminarized)")
    ax.set_ylabel("Height y (mm)")
    ax.set_xlabel("Fluid Velocity u(y) (m/s)")
    ax.set_title("Boundary Layer Velocity Profile")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Skin Friction Drag
    ax = axes[1]
    bars = ax.bar(["Laminar", "Standard", "TAP Control"], 
                  [drag_laminar, drag_std, drag_tap],
                  color=[BLUE, ORANGE, GREEN], edgecolor="#2a2a3a", width=0.5)
    ax.set_ylabel("Skin Friction Drag Force (N)")
    ax.set_title("Aerodynamic Skin-Friction Drag")
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.4f} N", ha="center", va="bottom", color="white", fontsize=9)
        
    plot_path = os.path.join(out_dir, "tap_aerospace_boundary.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Aerodynamics visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_boundary()
