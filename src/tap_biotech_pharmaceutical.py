# -*- coding: utf-8 -*-
"""
tap_biotech_pharmaceutical.py
==============================
TAP Model -- Biotechnology & Pharmaceutical Simulation Module
Simulates peptide chain polymerization and DNA hydration layer stabilization.
Compares standard aqueous hydrolysis degradation vs. TAP-stabilized dehydration
and extra-dimensional hydration layer shielding (using phi^-8 boundary controls).
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PI
PHI_INV8 = PHI ** -8

def simulate_biotech():
    print("=" * 72)
    print("  TAP BIOTECHNOLOGY & PHARMACEUTICAL SIMULATOR")
    print("=" * 72)
    
    # Time settings
    t_max = 100.0       # Time steps (arbitrary units)
    dt = 1.0
    steps = int(t_max / dt)
    time_grid = np.linspace(0, t_max, steps)
    
    # Peptide polymerization rate constants
    k_synth = 0.5       # Synthesis rate
    k_hydrolysis_std = 0.4   # Standard hydrolysis rate in water (fast degradation)
    
    # TAP mineral boundary layer suppresses hydrolysis by phi^-8
    k_hydrolysis_tap = k_hydrolysis_std * PHI_INV8
    
    # Simulate peptide average length over time (monomer-polymer equilibrium)
    length_std = np.zeros(steps)
    length_tap = np.zeros(steps)
    
    current_std = 1.0
    current_tap = 1.0
    
    # DNA Hydration shell degradation simulation
    # DNA requires a hydration shell of ~2.8 Angstroms. Dehydration leads to damage.
    # Shielding factor protects against thermal disruption
    hydration_std = []
    hydration_tap = []
    
    hyd_shell_std = 2.80
    hyd_shell_tap = 2.80
    
    for step in range(steps):
        # 1. Peptide Polymerization
        # dL/dt = k_synth - k_hydrolysis * L
        dL_std = k_synth - k_hydrolysis_std * current_std
        dL_tap = k_synth - k_hydrolysis_tap * current_tap
        
        current_std += dL_std * dt
        current_tap += dL_tap * dt
        
        length_std[step] = current_std
        length_tap[step] = current_tap
        
        # 2. DNA Hydration Stability (Thermal noise decay)
        # Standard shell decays under high thermal fluctuations
        decay_std = 0.05 * np.random.randn()
        # TAP boundary interface acts as a stabilizer, dampening fluctuations
        decay_tap = 0.05 * np.random.randn() * PHI_INV8
        
        hyd_shell_std += decay_std - 0.01 * (hyd_shell_std - 2.80)
        hyd_shell_tap += decay_tap - 0.01 * (hyd_shell_tap - 2.80)
        
        hydration_std.append(hyd_shell_std)
        hydration_tap.append(hyd_shell_tap)
        
    print("  Simulation completed.")
    print(f"    Final Peptide Length (Std): {length_std[-1]:.4f} monomers")
    print(f"    Final Peptide Length (TAP): {length_tap[-1]:.4f} monomers")
    
    # Save raw data
    data = {
        "time_grid": time_grid.tolist(),
        "peptide_length_std": length_std.tolist(),
        "peptide_length_tap": length_tap.tolist(),
        "dna_hydration_std": hydration_std,
        "dna_hydration_tap": hydration_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_biotech_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- Biotechnology & Pharmaceutical Simulator", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Peptide Polymerization
    ax = axes[0]
    ax.plot(time_grid, length_std, color=ORANGE, lw=2.0, label="Standard Aqueous (Hydrolysis Dominated)")
    ax.plot(time_grid, length_tap, color=GREEN, lw=2.0, label="TAP Shielded Boundary (Polymer-Stabilized)")
    ax.set_xlabel("Reaction Steps")
    ax.set_ylabel("Average Peptide Length (Monomers)")
    ax.set_title("Peptide Polymerization Chain Growth")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: DNA Hydration shell stability
    ax = axes[1]
    ax.plot(time_grid, hydration_std, color=ORANGE, lw=1.5, label="Standard DNA Hydration shell")
    ax.plot(time_grid, hydration_tap, color=GREEN, lw=1.5, label="TAP Shielded Hydration shell")
    ax.axhline(2.8, color=BLUE, ls=":", label="Optimal Hydration Width (2.8 A)")
    ax.set_xlabel("Time steps")
    ax.set_ylabel("Hydration layer thickness (Angstroms)")
    ax.set_title("DNA Hydration Layer Shell Stability")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_biotech.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Biotech visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_biotech()
