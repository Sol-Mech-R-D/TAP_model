# -*- coding: utf-8 -*-
"""
tap_parameter_sweep.py
======================
TAP Model Parameter Sensitivity Sweep Analysis.
Sweeps the topological dimension D and golden ratio phi parameters of the 
compactified 13D manifold to plot the Higgs mass prediction error landscape.
Saves plot to assets/tap_parameter_sweep.png.
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from science_constants import PHI, PI, HIGGS_MASS_GEV
from tap_dirac_modes import solve_dirac_spectrum

def main():
    print("=" * 80)
    print("  TAP MODEL -- PARAMETER SENSITIVITY SWEEP")
    print("  Testing predicted Higgs mass error minimization over phi and D")
    print("=" * 80)

    # 1. Sweep Golden Ratio (phi) from 1.55 to 1.68 (D=13.0)
    phi_grid = np.linspace(1.55, 1.68, 60)
    phi_errors = []
    phi_masses = []
    
    print("  Sweeping golden ratio phi (at D=13.0)...")
    for p in phi_grid:
        _, _, _, _, m_pred, _ = solve_dirac_spectrum(n_grid=500, phi=p, D=13.0)
        err = abs(m_pred - HIGGS_MASS_GEV) / HIGGS_MASS_GEV
        phi_errors.append(err * 100.0)
        phi_masses.append(m_pred)

    # 2. Sweep Bulk Dimension (D) from 11.5 to 14.5 (phi=PHI)
    d_grid = np.linspace(11.5, 14.5, 60)
    d_errors = []
    d_masses = []

    print("  Sweeping bulk dimension D (at phi=1.61803)...")
    for d in d_grid:
        _, _, _, _, m_pred, _ = solve_dirac_spectrum(n_grid=500, phi=PHI, D=d)
        err = abs(m_pred - HIGGS_MASS_GEV) / HIGGS_MASS_GEV
        d_errors.append(err * 100.0)
        d_masses.append(m_pred)

    # Find optimal values
    opt_phi_idx = np.argmin(phi_errors)
    opt_d_idx = np.argmin(d_errors)
    
    print()
    print(f"  Minimum error over phi grid           : {phi_errors[opt_phi_idx]:.4f}% at phi = {phi_grid[opt_phi_idx]:.5f}")
    print(f"  Minimum error over D grid             : {d_errors[opt_d_idx]:.4f}% at D = {d_grid[opt_d_idx]:.5f}")
    print()

    # Generate Sensitivity Plots
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 6), facecolor="#030308")
    gs = gridspec.GridSpec(1, 2, wspace=0.3)
    
    # Color scheme
    teal = "#4ecdc4"
    purple = "#7c6af7"
    gold = "#ffd93d"
    dark_blue = "#0d0d1e"

    # Panel 1: phi sweep
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(dark_blue)
    ax1.plot(phi_grid, phi_errors, color=purple, lw=2.5, label="Predicted Higgs Mass Error")
    ax1.axvline(PHI, color=gold, linestyle="--", alpha=0.8, label=f"Mathematical Golden Ratio ({PHI:.5f})")
    ax1.scatter([phi_grid[opt_phi_idx]], [phi_errors[opt_phi_idx]], color=gold, s=100, zorder=5)
    
    ax1.set_title("Higgs Mass Error vs. Golden Ratio (phi)", fontsize=12, fontweight='bold', pad=12)
    ax1.set_xlabel("Golden Ratio parameter (phi)", fontsize=10)
    ax1.set_ylabel("Higgs Mass Relative Error (%)", fontsize=10)
    ax1.grid(color='#202040', linestyle=':', alpha=0.5)
    ax1.legend(loc="upper right", framealpha=0.9, facecolor="#06060f", edgecolor=purple)
    ax1.set_yscale('log')

    # Panel 2: D sweep
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(dark_blue)
    ax2.plot(d_grid, d_errors, color=teal, lw=2.5, label="Predicted Higgs Mass Error")
    ax2.axvline(13.0, color=gold, linestyle="--", alpha=0.8, label="Topological Saturation D=13")
    ax2.scatter([d_grid[opt_d_idx]], [d_errors[opt_d_idx]], color=gold, s=100, zorder=5)

    ax2.set_title("Higgs Mass Error vs. Bulk Dimension (D)", fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel("Topological Bulk Dimension parameter (D)", fontsize=10)
    ax2.set_ylabel("Higgs Mass Relative Error (%)", fontsize=10)
    ax2.grid(color='#202040', linestyle=':', alpha=0.5)
    ax2.legend(loc="upper right", framealpha=0.9, facecolor="#06060f", edgecolor=teal)
    ax2.set_yscale('log')

    # Overall formatting
    plt.suptitle("TAP MODEL PARAMETER SENSITIVITY SWEEP ANALYSIS", 
                 color='#ffffff', fontsize=14, fontweight='black', y=0.98)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "..", "assets", "tap_parameter_sweep.png")
    
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [EXPORT] Parameter sweep diagram saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
