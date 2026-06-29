# -*- coding: utf-8 -*-
"""
tap_qubit_coherence_sweep.py
============================
Models and optimizes the classical wave coherence time (T2) in a room-temperature 
qubit emulator. Sweeps the number of Fibonacci spacer layers and the Floquet 
sub-harmonic pump frequency offset to find the exact configuration that maximizes 
coherence.
"""

import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from science_constants import PHI, PI

def calculate_coherence_time(n_layers, f_offset, t2_base_ms=10.0, f_qubit=4500.0):
    """
    Calculates the classical phase coherence time T2 (ms) of the soliton wave.
    
    Parameters:
      n_layers : number of Fibonacci spacer layers in the isolation stack
      f_offset : Floquet pump frequency ratio (f_pump / f_qubit)
      t2_base_ms: baseline coherence time with no shielding or active pumping
      f_qubit  : resonance frequency of the soliton wave (Hz)
    """
    # 1. Passive Shielding: Fibonacci Acoustic Bandgap
    # Each extra layer of Fibonacci-spaced sheets (Paper/Mylar/Copper) blocks 
    # more thermal phonon modes. The attenuation scales exponentially with n_layers
    # when aligned to the Golden Ratio.
    attenuation_factor = 1.0 - math.exp(-n_layers / PHI)
    passive_boost = 1.0 + 8.5 * attenuation_factor
    
    # 2. Active Shielding: Floquet Sub-Harmonic Pump Resonance
    # Coherence is maximized when the pump frequency is exactly at the sub-harmonic 
    # (f_pump / f_qubit = 0.5), which injects energy at the phase-stable nodes.
    # The width of this resonance is extremely narrow (0.02 frequency units).
    pump_resonance = math.exp(-((f_offset - 0.5) / 0.015)**2)
    active_boost = 1.0 + 15.0 * pump_resonance * (1.0 + 0.5 * n_layers)
    
    # 3. Overall T2 Coherence Time
    t2_opt = t2_base_ms * passive_boost * active_boost
    
    return t2_opt

def main():
    print("=" * 72)
    print("  TAP QUBIT COHERENCE PARAMETER SWEEP")
    print("  Optimizing Soliton Phase Coherence via Floquet Pumping")
    print("=" * 72)
    print()
    
    # Define sweep arrays
    layers_range = np.linspace(1, 12, 100)           # Number of layers
    pump_range = np.linspace(0.45, 0.55, 100)        # Floquet pump ratio (f_pump / f_qubit)
    
    # Run the 2D sweep
    t2_grid = np.zeros((len(layers_range), len(pump_range)))
    
    max_t2 = 0.0
    opt_layers = 0.0
    opt_pump = 0.0
    
    for i, layers in enumerate(layers_range):
        for j, pump in enumerate(pump_range):
            t2 = calculate_coherence_time(layers, pump)
            t2_grid[i, j] = t2
            if t2 > max_t2:
                max_t2 = t2
                opt_layers = layers
                opt_pump = pump
                
    print(f"  Sweep completed across {len(layers_range) * len(pump_range)} points.")
    print(f"  Maximum Coherence Time (T2)           : {max_t2:.2f} ms")
    print(f"  Optimal Number of Shielding Layers    : {opt_layers:.1f}")
    print(f"  Optimal Floquet Pump Ratio (f_offset) : {opt_pump:.4f}")
    print()
    
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
    X, Y = np.meshgrid(pump_range, layers_range)
    im = ax.pcolormesh(X, Y, t2_grid, cmap="viridis", shading="auto")
    
    # Add Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(color='gray')
    cbar.ax.tick_params(labelcolor='gray')
    cbar.set_label("Soliton Coherence Time T2 (ms)", color='gray')
    
    # Annotate optimum
    ax.plot(opt_pump, opt_layers, marker="x", color="#4ecdc4", ms=10, mew=2, label="Optimal Resonance Point")
    ax.text(opt_pump - 0.045, opt_layers + 0.4, f"T2 = {max_t2:.1f} ms\n(Layers = {opt_layers:.1f}, f_pump = {opt_pump:.3f})", 
            color="#e8e8e8", bbox=dict(facecolor="#10101a", alpha=0.8, edgecolor="#2a2a3a"))
    
    ax.set_xlabel("Floquet Pump Frequency Ratio (f_pump / f_qubit)")
    ax.set_ylabel("Number of Fibonacci Shielding Layers (N)")
    ax.set_title("TAP Qubit Soliton Coherence Optimization Sweep")
    ax.legend(facecolor="#10101a", labelcolor="#e8e8e8")
    
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_qubit_coherence_sweep.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    
    print("  [SUCCESS] Coherence optimization completed!")
    print("  [PLOT] Heatmap saved locally in artifact directory.")
    print("=" * 72 + "\n")
    
    results = {
        "max_t2_ms": max_t2,
        "optimal_layers": opt_layers,
        "optimal_pump_ratio": opt_pump
    }
    return results

if __name__ == "__main__":
    main()
