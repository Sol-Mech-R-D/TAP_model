# -*- coding: utf-8 -*-
"""
tap_soliton_collision_stress.py
===============================
Simulates the collision of two solitons under CPU stress testing.
Uses multiprocessing to pin all CPU cores, generating heat to drive
the thermal decoherence (damping) of the wave packets in real-time.
"""

import os
import sys
import math
import time
import numpy as np
import multiprocessing

def stress_worker():
    """Heavy math-loop worker to max out a CPU core."""
    while True:
        # Endless multiplication to generate thermal dissipation
        _ = 12345.678 * 87654.321

def get_cpu_temp():
    """Reads CPU temperature in Celsius from common sysfs paths."""
    thermal_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp"
    ]
    for path in thermal_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    temp_raw = float(f.read().strip())
                    if temp_raw > 1000:
                        return temp_raw / 1000.0
                    return temp_raw
            except Exception:
                pass
    return 30.0  # Fallback baseline

def main():
    # ─────────────────────────────────────────────────────────────────────────
    # SIMULATION PARAMETERS
    # ─────────────────────────────────────────────────────────────────────────
    N_space = 80
    L = 15.0
    dx = (2.0 * L) / N_space
    x = np.linspace(-L, L, N_space, endpoint=False)
    
    dt = 0.005
    steps = 450
    visualize_every = 10
    
    # 1. Initialize two colliding solitons
    # Soliton A (Left, moving Right at v = 4.5)
    psi_A = 1.2 * (1.0 / np.cosh(1.2 * (x + 6.0))) * np.exp(1j * 4.5 * x)
    # Soliton B (Right, moving Left at v = -4.5)
    psi_B = 1.2 * (1.0 / np.cosh(1.2 * (x - 6.0))) * np.exp(1j * -4.5 * x)
    
    psi = psi_A + psi_B
    
    num_cores = multiprocessing.cpu_count()
    
    print("=" * 90)
    print("  TAP MULTI-CORE SOLITON COLLISION STRESS TEST")
    print(f"  Detected Cores: {num_cores} | Domain: [-{L}, {L}] | steps = {steps}")
    print("  Goal: Pin all cores, generate heat, and watch solitons bleed under thermal noise.")
    print("=" * 90)
    print("Press Enter to spawn the stress workers and begin...")
    input()

    # 2. Spawn CPU stress processes
    print(f"  [STRESS] Spawning {num_cores} background math workers...")
    workers = []
    for _ in range(num_cores):
        p = multiprocessing.Process(target=stress_worker)
        p.daemon = True
        p.start()
        workers.append(p)
        
    print("  [STRESS] Cores pinned. Running collision solver...")
    print("  -------------------------------------------------------------------------")
    time.sleep(1.0) # Let the cores heat up slightly before start

    def compute_derivatives(state, damping):
        """Calculates NLSE derivatives with variable thermal damping."""
        d2psi_dx2 = np.zeros_like(state)
        for j in range(N_space):
            jp = (j + 1) % N_space
            jm = (j - 1) % N_space
            d2psi_dx2[j] = (state[jp] - 2.0 * state[j] + state[jm]) / (dx ** 2)
            
        # Damping coefficient directly attenuates wave amplitude
        dpsi_dt = 1j * (0.5 * d2psi_dx2 + 1.2 * (np.abs(state)**2) * state) - damping * state
        return dpsi_dt

    try:
        for t_step in range(steps):
            # Read live temperature
            cpu_temp = get_cpu_temp()
            
            # Map thermal load to damping (higher temp = faster decay/bleeding)
            damping = max((cpu_temp - 28.0) * 0.008, 0.0)
            
            # temporal integration
            k1 = dt * compute_derivatives(psi, damping)
            k2 = dt * compute_derivatives(psi + 0.5 * k1, damping)
            k3 = dt * compute_derivatives(psi + 0.5 * k2, damping)
            k4 = dt * compute_derivatives(psi + k3, damping)
            
            psi += (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            
            # Print ASCII grid representation
            if t_step % visualize_every == 0:
                amp = np.abs(psi)
                phase = np.angle(psi)
                
                plot_chars = []
                for j in range(N_space):
                    val = amp[j]
                    height = min(int(val * 8), 8)
                    if height == 0:
                        char = "."
                    else:
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
                # Sum of total wave probability to monitor decay/bleeding
                mass_integral = np.sum(amp**2) * dx
                
                print(f"t={t_step*dt:5.3f}s | {cpu_temp:.1f}°C | Damping:{damping:.4f} | Mass:{mass_integral:5.2f} | {line}")
                time.sleep(0.05)
                
    finally:
        # 3. Clean up and terminate stress processes
        print("\n  [STRESS] Terminating background math processes...")
        for p in workers:
            p.terminate()
            p.join()
        print("  [STRESS] CPU cores released and cooled down.")
        print("=" * 90)

if __name__ == "__main__":
    main()
