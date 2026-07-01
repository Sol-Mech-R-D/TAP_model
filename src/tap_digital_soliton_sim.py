# -*- coding: utf-8 -*-
"""
tap_digital_soliton_sim.py
===========================
Numerical solver for the Nonlinear Schrödinger Equation (NLSE) in 1D.
Uses central finite differences in space and RK4 integration in time.
Displays a live ASCII terminal visualization of the moving soliton.
"""

import math
import time
import numpy as np

def sech(x):
    return 1.0 / np.cosh(x)

def main():
    # ─────────────────────────────────────────────────────────────────────────
    # SIMULATION PARAMETERS
    # ─────────────────────────────────────────────────────────────────────────
    N_space = 80             # Number of spatial grid points (suited for terminal width)
    L = 15.0                 # Spatial domain length (-L to L)
    dx = (2.0 * L) / N_space
    x = np.linspace(-L, L, N_space, endpoint=False)
    
    dt = 0.005               # Time step size (must be small for RK4 stability)
    steps = 400              # Total simulation steps
    visualize_every = 10     # Frame update interval
    
    # Soliton parameters
    amplitude = 1.0
    velocity = 3.0           # Initial travel speed
    phase_freq = 0.5         # Phase rotation rate
    
    # 1. Initialize soliton wave packet: psi(x, 0) = A * sech(A * x) * exp(i * v * x)
    psi = amplitude * sech(amplitude * x) * np.exp(1j * velocity * x)
    
    print("=" * 80)
    print("  DIGITAL SOLITON PDE WAVE SOLVER (NLSE)")
    print(f"  Domain: x in [-{L:.1f}, {L:.1f}] | steps = {steps} | dx = {dx:.4f} | dt = {dt:.4f}")
    print("  Solving: i*d(psi)/dt + 0.5*d^2(psi)/dx^2 + |psi|^2*psi = 0")
    print("=" * 80)
    print("Press Enter to begin the real-time propagation...")
    input()

    def compute_derivatives(state):
        """Calculates the time derivative d(psi)/dt using central finite differences."""
        d2psi_dx2 = np.zeros_like(state)
        # Apply periodic boundary conditions for the second derivative
        for j in range(N_space):
            jp = (j + 1) % N_space
            jm = (j - 1) % N_space
            d2psi_dx2[j] = (state[jp] - 2.0 * state[j] + state[jm]) / (dx ** 2)
            
        # NLSE formula: d(psi)/dt = i * (0.5 * d^2(psi)/dx^2 + |psi|^2 * psi)
        dpsi_dt = 1j * (0.5 * d2psi_dx2 + (np.abs(state)**2) * state)
        return dpsi_dt

    # ─────────────────────────────────────────────────────────────────────────
    # RUN RK4 TEMPORAL INTEGRATION LOOP
    # ─────────────────────────────────────────────────────────────────────────
    for t_step in range(steps):
        # RK4 step calculation
        k1 = dt * compute_derivatives(psi)
        k2 = dt * compute_derivatives(psi + 0.5 * k1)
        k3 = dt * compute_derivatives(psi + 0.5 * k2)
        k4 = dt * compute_derivatives(psi + k3)
        
        psi += (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        
        # ─────────────────────────────────────────────────────────────────────
        # ASCII TERMINAL VISUALIZATION
        # ─────────────────────────────────────────────────────────────────────
        if t_step % visualize_every == 0:
            amp = np.abs(psi)
            phase = np.angle(psi)
            
            # Create a text-based amplitude plot
            plot_chars = []
            for j in range(N_space):
                val = amp[j]
                # Scale amplitude to integer height [0, 8]
                height = min(int(val * 8), 8)
                if height == 0:
                    char = "."
                else:
                    # Show phase angle dynamically using arrows pointing in phase direction
                    ph = phase[j]
                    if -math.pi/4 <= ph < math.pi/4:
                        char = "→"
                    elif math.pi/4 <= ph < 3*math.pi/4:
                        char = "↑"
                    elif -3*math.pi/4 <= ph < -math.pi/4:
                        char = "↓"
                    else:
                        char = "←"
                plot_chars.append(char)
                
            line = "".join(plot_chars)
            # Find current peak index
            peak_idx = np.argmax(amp)
            peak_pos = x[peak_idx]
            
            print(f"t = {t_step*dt:5.3f}s | Peak Pos: {peak_pos:6.2f} | {line}")
            time.sleep(0.05)
            
    print("\nSimulation complete. Soliton successfully navigated the boundary!")
    print("=" * 80)

if __name__ == "__main__":
    main()
