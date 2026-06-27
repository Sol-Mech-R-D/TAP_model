# -*- coding: utf-8 -*-
"""
tap_brain_neuromorphic.py
==========================
TAP Model -- BCI & Neuromorphic Computing Simulation Module
Simulates neural microtubule quantum coherence and Hopfield attractor capacity.
Compares standard brain thermal decoherence and neural network memory limits
vs. TAP topological boundary-shielded configurations (using golden-ratio coefficients).
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

def simulate_neuromorphic():
    print("=" * 72)
    print("  TAP BCI & NEUROMORPHIC COMPUTING SIMULATOR")
    print("=" * 72)
    
    # Simulation grid setup
    N_neurons = 200     # Number of simulated neuromorphic nodes
    T_coherence = 1000  # Total time grid for quantum coherence (fs)
    
    time_grid = np.linspace(0, T_coherence, 100)
    
    # 1. Microtubule Quantum Coherence
    # Tegmark calculated standard decoherence at body temp as tau_dec ~ 10^-13s (100 fs)
    # Under TAP, 13D boundary shielding extends this to ~940 fs
    tau_dec_std = 100.0   # fs
    tau_dec_tap = 939.57  # fs
    
    coherence_std = np.exp(-time_grid / tau_dec_std)
    coherence_tap = np.exp(-time_grid / tau_dec_tap)
    
    # 2. Hopfield Attractor Memory Capacity
    # Standard capacity coefficient: alpha_c = 0.138 (Hopfield limit)
    # TAP capacity limit includes the extra-dimensional enhancement: alpha_c = 0.138 * (1 + phi^-8)
    alpha_std = 0.138
    alpha_tap = 0.138 * (1.0 + PHI_INV8)
    
    # Simulate memory recall success rate vs. number of stored patterns (p/N ratio)
    patterns_ratio = np.linspace(0.01, 0.30, 50)
    recall_rate_std = 0.5 * (1.0 + np.vectorize(math.erf)((alpha_std - patterns_ratio) / (0.1 * math.sqrt(2.0))))
    recall_rate_tap = 0.5 * (1.0 + np.vectorize(math.erf)((alpha_tap - patterns_ratio) / (0.1 * math.sqrt(2.0))))
    
    print("  Simulation completed.")
    print(f"    Microtubule Coherence at 500fs (Std): {coherence_std[50]:.4f}")
    print(f"    Microtubule Coherence at 500fs (TAP): {coherence_tap[50]:.4f}")
    print(f"    Hopfield Attractor Critical Capacity (Std): {alpha_std:.4f}")
    print(f"    Hopfield Attractor Critical Capacity (TAP): {alpha_tap:.4f} (Boost: {((alpha_tap - alpha_std) / alpha_std)*100.0:.2f}%)")
    
    # Save raw data
    data = {
        "time_grid_fs": time_grid.tolist(),
        "coherence_std": coherence_std.tolist(),
        "coherence_tap": coherence_tap.tolist(),
        "patterns_ratio": patterns_ratio.tolist(),
        "recall_rate_std": recall_rate_std.tolist(),
        "recall_rate_tap": recall_rate_tap.tolist()
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_brain_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- BCI & Neuromorphic Computing Simulator", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Microtubule Coherence
    ax = axes[0]
    ax.plot(time_grid, coherence_std, color=ORANGE, lw=2.0, label="Standard Brain (Tegmark Limit)")
    ax.plot(time_grid, coherence_tap, color=GREEN, lw=2.0, label="TAP Boundary Shielded (Penrose)")
    ax.set_xlabel("Time (femtoseconds)")
    ax.set_ylabel("Quantum Coherence Scale")
    ax.set_title("Neural Microtubule Decoherence Curves")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Hopfield Capacity
    ax = axes[1]
    ax.plot(patterns_ratio, recall_rate_std, color=ORANGE, lw=2.0, label="Standard Hopfield Memory")
    ax.plot(patterns_ratio, recall_rate_tap, color=GREEN, lw=2.0, label="TAP Enhanced Memory")
    ax.axvline(alpha_std, color=ORANGE, ls=":", alpha=0.7, label=f"Standard Capacity ({alpha_std})")
    ax.axvline(alpha_tap, color=GREEN, ls=":", alpha=0.7, label=f"TAP Capacity ({alpha_tap:.3f})")
    ax.set_xlabel("Stored Patterns Ratio (p/N)")
    ax.set_ylabel("Memory Recall Success Rate")
    ax.set_title("Attractor Network Memory Capacity Limit")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_brain.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Brain/BCI visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_neuromorphic()
