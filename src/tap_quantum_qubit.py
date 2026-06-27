# -*- coding: utf-8 -*-
"""
tap_quantum_qubit.py
====================
TAP Model -- Topological Qubit Coherence Simulator
Simulates a quantum qubit interacting with a thermal decohering environment.
Compares a standard unshielded qubit vs. a TAP 13D Fibonacci-shielded qubit,
tracking coherence decay (rho_12) and state purity Tr(rho^2).
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PHI_INV4, PI

def simulate_qubit():
    print("=" * 72)
    print("  TAP TOPOLOGICAL QUBIT COHERENCE SIMULATOR")
    print("=" * 72)
    
    # Time settings
    t_max = 500.0       # Time in femtoseconds (fs)
    dt = 0.5            # Time step
    steps = int(t_max / dt)
    time_grid = np.linspace(0, t_max, steps)
    
    # Decoherence rates
    gamma_decay = 0.02          # Longitudinal decay rate (T1 relaxation)
    gamma_dephase_std = 0.05    # Standard transverse dephasing rate (T2)
    
    # TAP Fibonacci shielding reduces dephasing by a factor related to phi^-8
    # Because high-dimensional projection restricts available noise modes
    phi_8_shield = PHI ** -8
    gamma_dephase_tap = gamma_dephase_std * phi_8_shield
    
    # Initial state (coherent superposition: |+> = (|0> + |1>)/sqrt(2))
    # State matrix: rho = [[rho_00, rho_01], [rho_10, rho_11]]
    rho_std = np.array([[0.5, 0.5], 
                        [0.5, 0.5]], dtype=complex)
    rho_tap = np.copy(rho_std)
    
    # Track metrics over time
    coherence_std = []
    coherence_tap = []
    purity_std = []
    purity_tap = []
    
    # Master equation solver (Euler integration of Lindblad equations)
    for step in range(steps):
        # Record metrics
        coherence_std.append(abs(rho_std[0, 1]))
        coherence_tap.append(abs(rho_tap[0, 1]))
        
        # Purity = Tr(rho^2)
        purity_std.append(np.real(np.trace(np.dot(rho_std, rho_std))))
        purity_tap.append(np.real(np.trace(np.dot(rho_tap, rho_tap))))
        
        # Derivatives for standard qubit
        d_rho_std = np.zeros((2, 2), dtype=complex)
        d_rho_std[0, 0] = gamma_decay * rho_std[1, 1]
        d_rho_std[1, 1] = -gamma_decay * rho_std[1, 1]
        d_rho_std[0, 1] = -(0.5 * gamma_decay + gamma_dephase_std) * rho_std[0, 1]
        d_rho_std[1, 0] = np.conj(d_rho_std[0, 1])
        
        # Derivatives for TAP shielded qubit
        d_rho_tap = np.zeros((2, 2), dtype=complex)
        d_rho_tap[0, 0] = gamma_decay * rho_tap[1, 1]
        d_rho_tap[1, 1] = -gamma_decay * rho_tap[1, 1]
        d_rho_tap[0, 1] = -(0.5 * gamma_decay + gamma_dephase_tap) * rho_tap[0, 1]
        d_rho_tap[1, 0] = np.conj(d_rho_tap[0, 1])
        
        # Update density matrices
        rho_std += d_rho_std * dt
        rho_tap += d_rho_tap * dt
        
    print("  Simulation completed.")
    print(f"    Final Coherence (Std): {coherence_std[-1]:.6f}")
    print(f"    Final Coherence (TAP): {coherence_tap[-1]:.6f}")
    
    # Save raw data
    data = {
        "time_grid": time_grid.tolist(),
        "coherence_std": coherence_std,
        "coherence_tap": coherence_tap,
        "purity_std": purity_std,
        "purity_tap": purity_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_quantum_qubit_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- Topological Qubit Coherence Simulator", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Coherence Decay
    ax = axes[0]
    ax.plot(time_grid, coherence_std, color=ORANGE, lw=2.0, label="Standard Qubit (Decohering)")
    ax.plot(time_grid, coherence_tap, color=GREEN, lw=2.0, label="TAP Shielded (Topological)")
    ax.set_xlabel("Time (femtoseconds)")
    ax.set_ylabel("Quantum Coherence |rho_12|")
    ax.set_title("Coherence Envelope Decay")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: State Purity
    ax = axes[1]
    ax.plot(time_grid, purity_std, color=ORANGE, lw=2.0, label="Standard Purity")
    ax.plot(time_grid, purity_tap, color=GREEN, lw=2.0, label="TAP Shielded Purity")
    ax.set_xlabel("Time (femtoseconds)")
    ax.set_ylabel("State Purity Tr(rho^2)")
    ax.set_title("Quantum State Purity Evolution")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_quantum_qubit.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Coherence visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_qubit()
