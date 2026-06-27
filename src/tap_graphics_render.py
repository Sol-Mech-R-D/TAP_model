# -*- coding: utf-8 -*-
"""
tap_graphics_render.py
=======================
TAP Model -- 3D Ray Tracing & Game Engine Renderer Simulator
Simulates light ray direction sampling for path tracing and ambient occlusion.
Compares standard random Monte Carlo sampling (high discrepancy, noisy)
vs. TAP-based Golden Ratio Fibonacci Lattice sampling (low discrepancy, uniform),
demonstrating rendering noise reduction and sampling efficiency.
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PI

def simulate_graphics():
    print("=" * 72)
    print("  TAP 3D RENDERING & GAME ENGINE GRAPHICS SIMULATOR")
    print("=" * 72)
    
    # Sampling parameters
    N_samples = 150     # Number of rays/samples per pixel
    
    # 1. Standard Random Monte Carlo Sampling
    # Rays are generated using standard random coordinates
    theta_std = 2.0 * PI * np.random.rand(N_samples)
    r_std = np.sqrt(np.random.rand(N_samples))  # Uniform area distribution
    x_std = r_std * np.cos(theta_std)
    y_std = r_std * np.sin(theta_std)
    
    # 2. TAP Golden Ratio (Fibonacci) Lattice Sampling
    # Rays are distributed uniformly using the Golden Ratio
    indices = np.arange(N_samples) + 0.5
    r_tap = np.sqrt(indices / N_samples)
    theta_tap = 2.0 * PI * indices * PHI  # Multiplied by golden ratio
    x_tap = r_tap * np.cos(theta_tap)
    y_tap = r_tap * np.sin(theta_tap)
    
    # Calculate Discrepancy (measure of sampling quality)
    # Lower discrepancy means more uniform distribution and less visual noise
    # We estimate discrepancy by counting samples in grid sectors
    grid_size = 5
    bounds = np.linspace(-1.0, 1.0, grid_size + 1)
    
    counts_std = []
    counts_tap = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Check standard
            in_sector_std = np.sum((x_std >= bounds[i]) & (x_std < bounds[i+1]) &
                                   (y_std >= bounds[j]) & (y_std < bounds[j+1]))
            counts_std.append(in_sector_std)
            
            # Check TAP
            in_sector_tap = np.sum((x_tap >= bounds[i]) & (x_tap < bounds[i+1]) &
                                   (y_tap >= bounds[j]) & (y_tap < bounds[j+1]))
            counts_tap.append(in_sector_tap)
            
    # Discrepancy is estimated as the variance of sample counts across sectors
    discrepancy_std = np.var(counts_std)
    discrepancy_tap = np.var(counts_tap)
    
    # Visual noise is proportional to the discrepancy
    noise_std = np.sqrt(discrepancy_std) / N_samples * 100.0
    noise_tap = np.sqrt(discrepancy_tap) / N_samples * 100.0
    
    print("  Simulation completed.")
    print(f"    Sampling Discrepancy (Std): {discrepancy_std:.4f}")
    print(f"    Sampling Discrepancy (TAP): {discrepancy_tap:.4f} (Reduction: {((discrepancy_std - discrepancy_tap) / discrepancy_std)*100.0:.2f}%)")
    print(f"    Estimated Rendering Noise (Std): {noise_std:.2f}%")
    print(f"    Estimated Rendering Noise (TAP): {noise_tap:.2f}%")
    
    # Save raw data
    data = {
        "samples_std": {"x": x_std.tolist(), "y": y_std.tolist()},
        "samples_tap": {"x": x_tap.tolist(), "y": y_tap.tolist()},
        "discrepancy_std": discrepancy_std,
        "discrepancy_tap": discrepancy_tap,
        "noise_std": noise_std,
        "noise_tap": noise_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_graphics_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- 3D Ray Tracing Graphics Sampling Simulator", color="white", fontsize=14, fontweight="bold")
    
    for ax in axes:
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        ax.grid(True, color=(1, 1, 1, 0.05))
        
    ORANGE = "#ff6b6b"
    GREEN = "#4ecdc4"
    
    # Panel 1: Standard Random Monte Carlo
    ax = axes[0]
    ax.scatter(x_std, y_std, color=ORANGE, alpha=0.8, edgecolor="none", s=25, label="Random (Monte Carlo)")
    circle = plt.Circle((0,0), 1.0, color="gray", fill=False, ls=":", alpha=0.5)
    ax.add_patch(circle)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.set_title(f"Standard Sampling (Noise: {noise_std:.2f}%)")
    ax.legend(facecolor="#10101a", labelcolor="white", loc="upper right")
    
    # Panel 2: TAP Golden Ratio Weyl Sequence
    ax = axes[1]
    ax.scatter(x_tap, y_tap, color=GREEN, alpha=0.8, edgecolor="none", s=25, label="TAP Fibonacci Lattice")
    circle = plt.Circle((0,0), 1.0, color="gray", fill=False, ls=":", alpha=0.5)
    ax.add_patch(circle)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.set_title(f"TAP Conformal Sampling (Noise: {noise_tap:.2f}%)")
    ax.legend(facecolor="#10101a", labelcolor="white", loc="upper right")
    
    plot_path = os.path.join(out_dir, "tap_graphics.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Rendering visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_graphics()
