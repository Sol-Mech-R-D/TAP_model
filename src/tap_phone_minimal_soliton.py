# -*- coding: utf-8 -*-
"""
tap_phone_minimal_soliton.py
============================
Simulates the "Minimal Soliton of the Phone" by dynamically coupling
five real-time hardware metrics (CPU temp, battery current, battery voltage,
load average, and Wi-Fi signal) to the NLSE wave solver.
"""

import os
import sys
import math
import time
import numpy as np

# Adjust encoding for Termux console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------------------------------------------------------
# TELEMETRY READERS
# -----------------------------------------------------------------------------
def get_cpu_temp():
    thermal_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/devices/virtual/thermal/thermal_zone0/temp"
    ]
    for path in thermal_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    temp_raw = float(f.read().strip())
                    return temp_raw / 1000.0 if temp_raw > 1000 else temp_raw
            except Exception:
                pass
    return 35.0

def get_battery_current():
    current_paths = [
        "/sys/class/power_supply/battery/current_now",
        "/sys/class/power_supply/battery/current_avg"
    ]
    for path in current_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    val = abs(float(f.read().strip()))
                    return val / 1e6 if val > 1000 else val
            except Exception:
                pass
    return 0.15

def get_battery_voltage():
    voltage_paths = [
        "/sys/class/power_supply/battery/voltage_now",
        "/sys/class/power_supply/battery/voltage_avg"
    ]
    for path in voltage_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    val = float(f.read().strip())
                    return val / 1e6 if val > 1000 else val
            except Exception:
                pass
    return 4.0  # standard Li-ion voltage baseline

def get_cpu_load():
    """Reads 1-minute CPU load average."""
    load_path = "/proc/loadavg"
    if os.path.exists(load_path):
        try:
            with open(load_path, "r") as f:
                parts = f.read().split()
                return float(parts[0])
        except Exception:
            pass
    return 0.5

def get_wifi_quality():
    """Reads Wi-Fi link quality from /proc/net/wireless (0.0 to 1.0)."""
    wireless_path = "/proc/net/wireless"
    if os.path.exists(wireless_path):
        try:
            with open(wireless_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "wlan0" in line or "wld0" in line:
                        parts = line.split()
                        # Link quality is typically the 3rd column
                        quality = float(parts[2].replace(".", ""))
                        return min(quality / 70.0, 1.0)  # normalized
        except Exception:
            pass
    return 0.8  # Default baseline (strong link)

# -----------------------------------------------------------------------------
# MAIN SOLVER
# -----------------------------------------------------------------------------
def main():
    N_space = 80
    L = 15.0
    dx = (2.0 * L) / N_space
    x = np.linspace(-L, L, N_space, endpoint=False)
    
    dt = 0.005
    steps = 400
    visualize_every = 10
    
    # Initialize colliding solitons (explicitly cast to complex128)
    psi_A = 1.0 / np.cosh(x + 5.0)
    psi_B = 1.0 / np.cosh(x - 5.0)
    psi = (psi_A + psi_B).astype(np.complex128)
    
    print("=" * 90)
    print("  SIMULATING THE MINIMAL SOLITON OF THE PHONE")
    print("  Wiring CPU temp, Load, Battery Current/Voltage, and Wi-Fi to NLSE solver")
    print("=" * 90)
    print("  Initial Hardware State:")
    print(f"  * CPU Temp    : {get_cpu_temp():.2f}°C")
    print(f"  * CPU Load    : {get_cpu_load():.2f}")
    print(f"  * Battery V/I : {get_battery_voltage():.3f}V / {get_battery_current()*1000:.1f}mA")
    print(f"  * Wi-Fi Link  : {get_wifi_quality()*100.0:.1f}%")
    print("  -------------------------------------------------------------------------")
    print("Press Enter to start the unified hardware-coupled wave solver...")
    input()

    def compute_derivatives(state, damping, nonlinearity, phase_noise, grid_wrinkles):
        """Calculates NLSE derivatives perturbed by multi-variable hardware noise."""
        d2psi_dx2 = np.zeros_like(state)
        for j in range(N_space):
            jp = (j + 1) % N_space
            jm = (j - 1) % N_space
            # Grid wrinkles add minor spatial fluctuations to the derivative
            d2psi_dx2[j] = (state[jp] - 2.0 * state[j] + state[jm]) / ((dx * (1.0 + grid_wrinkles[j])) ** 2)
            
        # Add random phase noise (jitter) to the state
        noisy_state = state * np.exp(1j * phase_noise)
        
        # d(psi)/dt = i * (0.5 * d^2(psi)/dx^2 + nonlinearity * |psi|^2 * psi) - damping * psi
        dpsi_dt = 1j * (0.5 * d2psi_dx2 + nonlinearity * (np.abs(noisy_state)**2) * noisy_state) - damping * state
        return dpsi_dt

    for t_step in range(steps):
        # 1. Read live phone sensor telemetry
        temp = get_cpu_temp()
        current = get_battery_current()
        voltage = get_battery_voltage()
        load = get_cpu_load()
        wifi = get_wifi_quality()
        
        # 2. Map telemetry to wave physics coefficients
        damping = max((temp - 28.0) * 0.005, 0.0)
        nonlinearity = 1.0 + current * 0.8
        
        # Wi-Fi signal loss maps to phase noise jitter
        wifi_loss = max(1.0 - wifi, 0.0)
        phase_noise = np.random.normal(0, wifi_loss * 0.05, N_space)
        
        # CPU load maps to physical grid wrinkles (spatial noise)
        grid_wrinkles = np.random.normal(0, load * 0.01, N_space)
        
        # Battery voltage scales the propagation speed (time step scale)
        voltage_scale = min(voltage / 4.0, 1.2)
        local_dt = dt * voltage_scale
        
        # 3. Step forward using RK4
        k1 = local_dt * compute_derivatives(psi, damping, nonlinearity, phase_noise, grid_wrinkles)
        k2 = local_dt * compute_derivatives(psi + 0.5 * k1, damping, nonlinearity, phase_noise, grid_wrinkles)
        k3 = local_dt * compute_derivatives(psi + 0.5 * k2, damping, nonlinearity, phase_noise, grid_wrinkles)
        k4 = local_dt * compute_derivatives(psi + k3, damping, nonlinearity, phase_noise, grid_wrinkles)
        
        psi += (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
        
        # 4. Render ASCII graph with status updates
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
            
            print(f"t={t_step*dt:5.3f}s | {temp:.1f}°C | {current*1000:5.1f}mA | {voltage:.2f}V | Load:{load:.2f} | WiFi:{wifi*100:.0f}% | {line}")
            time.sleep(0.05)
            
    print("\nSimulation complete. Soliton successfully navigated the phone's field!")
    print("=" * 90)

if __name__ == "__main__":
    main()
