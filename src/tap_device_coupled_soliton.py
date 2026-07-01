# -*- coding: utf-8 -*-
"""
tap_device_coupled_soliton.py
=============================
Solves the Nonlinear Schrödinger Equation (NLSE) dynamically coupled to
the phone's live CPU thermals and battery current draw.
"""

import os
import math
import time
import numpy as np

def get_cpu_temp():
    """Reads the primary CPU thermal zone temperature in Celsius."""
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
                    # Convert millidegrees to Celsius if needed
                    if temp_raw > 1000:
                        return temp_raw / 1000.0
                    return temp_raw
            except Exception:
                pass
    return 35.0  # Default baseline fallback

def get_battery_current():
    """Reads the live battery current draw in microamps (normalized)."""
    current_paths = [
        "/sys/class/power_supply/battery/current_now",
        "/sys/class/power_supply/battery/current_avg"
    ]
    for path in current_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    val = abs(float(f.read().strip()))
                    # Normalize to typical range [0.0, 1.0] assuming max 1A draw
                    if val > 1000:
                        val = val / 1e6
                    return min(val, 1.0)
            except Exception:
                pass
    return 0.2  # Default baseline fallback

def main():
    N_space = 80
    L = 15.0
    dx = (2.0 * L) / N_space
    x = np.linspace(-L, L, N_space, endpoint=False)
    
    dt = 0.005
    steps = 400
    visualize_every = 10
    
    # Initialize wave packet
    psi = 1.0 / np.cosh(x) * np.exp(1j * 3.0 * x)
    
    print("=" * 90)
    print("  TAP HARDWARE-COUPLED SOLITON SOLVER")
    print("  Coupling phone CPU thermals & battery current draw directly to NLSE wave parameters")
    print("=" * 90)
    print("  Initial Telemetry Reading:")
    print(f"  * CPU Temperature : {get_cpu_temp():.2f}°C")
    print(f"  * Battery Current : {get_battery_current():.4f} A")
    print("  -------------------------------------------------------------------------")
    print("Press Enter to begin the hardware-coupled propagation loop...")
    input()

    def compute_derivatives(state, damping, nonlinearity):
        """Calculates the NLSE derivative with thermal damping and battery nonlinearity."""
        d2psi_dx2 = np.zeros_like(state)
        for j in range(N_space):
            jp = (j + 1) % N_space
            jm = (j - 1) % N_space
            d2psi_dx2[j] = (state[jp] - 2.0 * state[j] + state[jm]) / (dx ** 2)
            
        # NLSE with thermal damping (-damping * state) and variable battery nonlinearity
        dpsi_dt = 1j * (0.5 * d2psi_dx2 + nonlinearity * (np.abs(state)**2) * state) - damping * state
        return dpsi_dt

    for t_step in range(steps):
        # 1. Read live phone sensor telemetry
        cpu_temp = get_cpu_temp()
        bat_curr = get_battery_current()
        
        # 2. Map sensor values to physical damping and nonlinearity coefficients
        # Damping increases by 0.001 per degree above 30°C (simulating thermal decoherence)
        damping = max((cpu_temp - 30.0) * 0.001, 0.0)
        
        # Nonlinearity scales with battery current draw (simulating current-driven pulse compression)
        nonlinearity = 1.0 + bat_curr * 0.5
        
        # 3. Step forward in time using RK4
        k1 = dt * compute_derivatives(psi, damping, nonlinearity)
        k2 = dt * compute_derivatives(psi + 0.5 * k1, damping, nonlinearity)
        k3 = dt * compute_derivatives(psi + 0.5 * k2, damping, nonlinearity)
        k4 = dt * compute_derivatives(psi + k3, damping, nonlinearity)
        
        psi += (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        
        # 4. Render the output
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
            peak_idx = np.argmax(amp)
            peak_val = amp[peak_idx]
            
            # Print status bar including live phone sensor telemetry
            print(f"t={t_step*dt:5.3f}s | {cpu_temp:.1f}°C (Damp:{damping:.4f}) | {bat_curr*1000:.1f}mA (Nonlin:{nonlinearity:.2f}) | Pk:{peak_val:.2f} | {line}")
            time.sleep(0.05)
            
    print("\nSimulation complete. Soliton successfully navigated the thermal field!")
    print("=" * 90)

if __name__ == "__main__":
    main()
