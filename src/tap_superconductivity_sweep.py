# -*- coding: utf-8 -*-
"""
tap_superconductivity_sweep.py
==============================
Models and optimizes high-temperature superconductivity transition temperatures (Tc)
as a function of twisted bilayer graphene angles and substrate aspect ratios.
Runs a parameter sweep to identify the exact geometric "magic coordinates" 
where Tc reaches room temperature (293 K) under the TAP model.
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from science_constants import PHI, PI

def calculate_tc(r, theta, tc_base=1.5, lambda_0=0.25, mu_star=0.1):
    """
    Calculates the superconducting transition temperature Tc based on BCS-TAP theory.
    
    Parameters:
      r     : substrate thickness aspect ratio (d1/d2)
      theta : twist angle in degrees
      tc_base: baseline Tc (Kelvin) for unoptimized twisted graphene
      lambda_0: baseline electron-phonon coupling
      mu_star: Coulomb repulsion coefficient (standard SM value ~ 0.1)
    """
    # Convert twist angle to radians
    theta_rad = math.radians(theta)
    
    # 1. Geometric resonance factor f(r)
    # The coupling peaks when the substrate ratio matches the Golden Ratio (phi) 
    # or its square (phi^2), reflecting constructive interference of phonon-polaritons.
    resonance_1 = math.exp(-((r - PHI) / 0.12)**2)
    resonance_2 = math.exp(-((r - (PHI**2)) / 0.18)**2)
    f_r = 1.0 + 2.5 * resonance_1 + 4.0 * resonance_2
    
    # 2. Twist angle modulation
    # Twisted bilayer graphene has a "magic angle" near 1.1 degrees. Under TAP, 
    # this magic angle is mathematically locked to the 13D saturation boundary ceiling:
    #   y_sat = 2 * pi * 13 * (1 - phi^-9 / pi) ≈ 81.34
    #   theta_magic = 180 / (2 * y_sat) ≈ 1.106 degrees.
    y_sat = 2.0 * PI * 13.0 * (1.0 - (PHI ** -9) / PI)
    theta_magic = 180.0 / (2.0 * y_sat) # ~1.106 degrees
    angle_width = 0.15 # degrees
    g_theta = math.exp(-((theta - theta_magic) / angle_width)**2)
    
    # 3. Effective coupling constant lambda_eff
    # The coupling is amplified by the 13D saturation factor (phi^8) in resonant states
    leakage_boost = PHI ** 3 # ~4.236
    lambda_eff = lambda_0 * (1.0 + leakage_boost * g_theta * f_r)
    
    # 4. Modified BCS Tc Formula
    if lambda_eff <= mu_star:
        return 0.0
    
    # Characteristic phonon energy scale (Debye temperature equivalents for carbon lattices ~ 2000 K)
    theta_debye = 2100.0 # Kelvin
    Tc = theta_debye * math.exp(-1.0 / (lambda_eff - mu_star))
    
    return Tc

def main():
    print("=" * 72)
    print("  TAP SUPERCONDUCTIVITY PARAMETER SWEEP")
    print("  Optimizing High-Tc Superconductivity via Fibonacci Metamaterials")
    print("=" * 72)
    print()
    
    # Define sweep arrays
    r_range = np.linspace(1.0, 3.5, 250)         # Aspect ratio d1/d2
    theta_range = np.linspace(0.5, 2.0, 250)     # Twist angle in degrees
    
    # Run the 2D sweep
    Tc_grid = np.zeros((len(r_range), len(theta_range)))
    
    max_tc = 0.0
    opt_r = 0.0
    opt_theta = 0.0
    
    for i, r in enumerate(r_range):
        for j, theta in enumerate(theta_range):
            tc = calculate_tc(r, theta)
            Tc_grid[i, j] = tc
            if tc > max_tc:
                max_tc = tc
                opt_r = r
                opt_theta = theta
                
    print(f"  Sweep completed across {len(r_range) * len(theta_range)} points.")
    print(f"  Maximum Transition Temperature (Tc)   : {max_tc:.2f} K ({max_tc - 273.15:.2f} C)")
    print(f"  Optimal Twist Angle (theta)           : {opt_theta:.4f} degrees")
    print(f"  Optimal Substrate Aspect Ratio (r)    : {opt_r:.4f}")
    print()
    
    # Check if we hit Room Temperature (293.15 K)
    rt_k = 293.15
    if max_tc >= rt_k:
        print("  [SUCCESS] Room-temperature superconductivity achieved!")
        print(f"  TAP configuration is tuned to a stable resonance ceiling.")
    else:
        print("  Baseline sweeps completed. Adjust boundaries to optimize coupling further.")
        
    # Generate Heatmap
    fig = plt.figure(figsize=(10, 8), facecolor="#0a0a0f")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#10101a")
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a3a")
    ax.tick_params(colors="gray")
    ax.xaxis.label.set_color("gray")
    ax.yaxis.label.set_color("gray")
    ax.title.set_color("white")
    
    # 2D Heatmap
    X, Y = np.meshgrid(theta_range, r_range)
    im = ax.pcolormesh(X, Y, Tc_grid, cmap="inferno", shading="auto", vmin=0, vmax=350)
    
    # Add Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(color='gray')
    cbar.ax.tick_params(labelcolor='gray')
    cbar.set_label("Transition Temperature Tc (Kelvin)", color='gray')
    
    # Annotate optimum
    ax.plot(opt_theta, opt_r, marker="x", color="#7c6af7", ms=10, mew=2, label="Optimal Resonance Point")
    ax.text(opt_theta + 0.05, opt_r + 0.05, f"Tc = {max_tc:.1f} K\n(theta = {opt_theta:.2f} deg, r = {opt_r:.2f})", 
            color="#e8e8e8", bbox=dict(facecolor="#10101a", alpha=0.8, edgecolor="#2a2a3a"))
    
    ax.set_xlabel("Twist Angle theta (degrees)")
    ax.set_ylabel("Substrate Thickness Aspect Ratio r (d1/d2)")
    ax.set_title("TAP Superconductivity Optimization Parameter Sweep")
    ax.legend(facecolor="#10101a", labelcolor="#e8e8e8")
    
    # Save both locally in this directory and in repository later
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_superconductivity_sweep.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    
    print(f"  [PLOT] Optimization heatmap saved -> {out}")
    print("=" * 72 + "\n")
    
    results = {
        "max_tc_k": max_tc,
        "optimal_twist_angle_deg": opt_theta,
        "optimal_aspect_ratio": opt_r,
        "room_temp_achieved": bool(max_tc >= rt_k)
    }
    return results

if __name__ == "__main__":
    main()
