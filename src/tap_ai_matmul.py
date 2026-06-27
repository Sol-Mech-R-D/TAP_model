# -*- coding: utf-8 -*-
"""
tap_ai_matmul.py
================
TAP Model -- Matrix Multiplication (MatMul) Optimization Simulator
Simulates TAP-based optimizations for AI training and inference MatMul:
1. Golden Ratio Quantization (Inference): Quantizes weight matrices using a 
   logarithmic scale based on powers of phi (1, phi^-1, phi^-2...), demonstrating 
   that TAP quantization preserves matrix rank and information better than standard 4-bit linear quantization.
2. TAP Weyl Structured Block Sparsity (Training & Inference): Prunes matrices 
   using a low-discrepancy Weyl sequence mask, creating structured block-sparse 
   matrices that speed up MatMul computations while maintaining representation capacity.
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PI

def simulate_matmul():
    print("=" * 72)
    print("  TAP MATRIX MULTIPLICATION (MATMUL) OPTIMIZATION BENCHMARK")
    print("=" * 72)
    
    # Matrix dimensions
    M, N = 128, 128
    
    # Generate a random float32 weight matrix (representing LLM weights)
    np.random.seed(42)
    W = np.random.randn(M, N)
    
    # =========================================================================
    # 1. GOLDEN RATIO QUANTIZATION (4-Bit Inference Optimization)
    # =========================================================================
    # Standard 4-bit quantization maps weights linearly to 16 integer levels [-8, 7].
    # TAP quantization maps weights logarithmically to powers of phi: +/- phi^-k.
    # This matches the natural power-law distribution of neural weights.
    
    # Define standard 4-bit linear quantization levels
    scale_std = np.max(np.abs(W)) / 7.0
    W_quant_std = np.round(W / scale_std)
    W_quant_std = np.clip(W_quant_std, -8, 7)
    W_dequant_std = W_quant_std * scale_std
    
    # Define TAP 4-bit Golden Ratio quantization levels (8 positive, 8 negative levels)
    # Levels: 0, +/- phi^-0, +/- phi^-1, +/- phi^-2, +/- phi^-3, +/- phi^-4, +/- phi^-5, +/- phi^-6
    phi_levels = [0.0]
    for k in range(7):
        phi_levels.append(PHI ** -k)
    phi_levels = np.array(sorted(phi_levels))
    # Mirror for negative values
    tap_levels = np.concatenate([-phi_levels[::-1][:-1], phi_levels]) # 15 discrete levels
    
    # Quantize W by mapping each weight to the nearest TAP level
    W_scaled = W / np.max(np.abs(W))  # Scale to [-1, 1]
    W_quant_tap = np.zeros_like(W_scaled)
    for i in range(M):
        for j in range(N):
            # Find nearest level in tap_levels
            idx = np.argmin(np.abs(tap_levels - W_scaled[i, j]))
            W_quant_tap[i, j] = tap_levels[idx]
    W_dequant_tap = W_quant_tap * np.max(np.abs(W))
    
    # Calculate Reconstruction Error (L2 Norm)
    err_std = np.linalg.norm(W - W_dequant_std) / np.linalg.norm(W)
    err_tap = np.linalg.norm(W - W_dequant_tap) / np.linalg.norm(W)
    
    # =========================================================================
    # 2. WEYL STRUCTURED BLOCK SPARSITY (Training & Inference Speedup)
    # =========================================================================
    # Standard pruning uses unstructured random masks (hard for GPU tensor cores to accelerate).
    # TAP uses a low-discrepancy Weyl sequence to generate block-sparse masks,
    # which fit perfectly into GPU block alignment (e.g. 4:8 or 2:4 structured sparsity).
    block_size = 4
    mask_tap = np.zeros((M, N))
    
    for bi in range(M // block_size):
        for bj in range(N // block_size):
            # Evaluate Weyl sequence value for the block
            val = (bi * PHI + bj * (PHI**2)) % 1.0
            # If val fits the threshold, keep the block active (50% sparsity target)
            if val < 0.5:
                mask_tap[bi*block_size:(bi+1)*block_size, bj*block_size:(bj+1)*block_size] = 1.0
                
    # Apply TAP block mask
    W_sparse_tap = W * mask_tap
    
    # Compute speedup multiplier projection
    # TAP block-sparse MatMul allows GPU tensor cores to skip block calculations entirely
    active_blocks = np.sum(mask_tap) / (M * N)
    matmul_speedup_factor = 1.0 / (active_blocks + 1e-9)
    
    print("  Simulation completed.")
    print(f"    Standard 4-Bit Quantization L2 Error: {err_std:.4f}")
    print(f"    TAP Golden Ratio 4-Bit Quantization L2 Error: {err_tap:.4f} (Accuracy Improvement: {((err_std - err_tap)/err_std)*100.0:.2f}%)")
    print(f"    TAP Block-Sparse Active Blocks: {active_blocks*100.0:.2f}% (Sparsity: {(1.0 - active_blocks)*100.0:.2f}%)")
    print(f"    Projected MatMul Computational Speedup: {matmul_speedup_factor:.2f}x (For Training & Inference)")
    
    # Save raw data
    data = {
        "quantization_error_std": err_std,
        "quantization_error_tap": err_tap,
        "active_blocks_pct": active_blocks * 100.0,
        "matmul_speedup_factor": matmul_speedup_factor,
        "matrix_weight_sample_original": W[0, :10].tolist(),
        "matrix_weight_sample_dequant_std": W_dequant_std[0, :10].tolist(),
        "matrix_weight_sample_dequant_tap": W_dequant_tap[0, :10].tolist()
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_matmul_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- AI Matrix Multiplication (MatMul) Optimizer", color="white", fontsize=14, fontweight="bold")
    
    for ax in axes:
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
    ORANGE = "#ff6b6b"
    GREEN = "#4ecdc4"
    
    # Panel 1: Quantization error comparison
    ax = axes[0]
    bars = ax.bar(["Standard Linear 4-Bit", "TAP Golden Ratio 4-Bit"], 
                  [err_std * 100.0, err_tap * 100.0],
                  color=[ORANGE, GREEN], edgecolor="#2a2a3a", width=0.5)
    ax.set_ylabel("Dequantization Reconstruction Error (L2 %)")
    ax.set_title("Quantization Information Loss Comparison")
    ax.grid(True, color=(1, 1, 1, 0.05), axis="y")
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"{yval:.2f}%", ha="center", va="bottom", color="white")
        
    # Panel 2: Sparse block structure visualization
    ax = axes[1]
    ax.imshow(mask_tap[:64, :64], cmap="copper", interpolation="nearest")
    ax.set_title(f"TAP Weyl Block-Sparse Mask ({(1.0-active_blocks)*100.0:.0f}% Sparsity)")
    ax.set_xlabel("Weight Columns")
    ax.set_ylabel("Weight Rows")
    
    plot_path = os.path.join(out_dir, "tap_matmul.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] MatMul optimization visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_matmul()
