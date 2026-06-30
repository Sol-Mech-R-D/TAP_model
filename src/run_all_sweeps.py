# -*- coding: utf-8 -*-
"""
run_all_sweeps.py
=================
Sequentially executes the four advanced characterization sweeps for the coupled 
Tetrahedron-Schottky Ratchet circuit:
  1. Resonant Spectral Sweep (Frequency Sweep, cmd 's')
  2. T1 Energy Relaxation Sweep (Decay Sweep, cmd 'd')
  3. Two-Tone Floquet Drive Sweep (Modulation Sweep, cmd 'w')
  4. Combined 2D Heatmap Sweep (2D sweep, cmd 'm')
Generates plots for each sweep and outputs performance metrics.
"""

import sys
import os
import time
import serial
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def init_serial():
    port = "COM5"
    baud = 115200
    ser = serial.Serial(port, baud, timeout=2.0)
    print(f"  [CONN] Connected to {port}.")
    
    # Reset Arduino
    print("  [RST] Rebooting Arduino...")
    ser.dtr = False
    time.sleep(0.1)
    ser.dtr = True
    time.sleep(2.0)
    ser.reset_input_buffer()
    return ser

def run_frequency_sweep(ser):
    print("\n" + "="*60)
    print("  [RUN 1] RESONANT SPECTRAL SWEEP (FREQUENCY SWEEP)")
    print("="*60)
    
    ser.write(b"s")
    freqs = []
    voltages = []
    start_time = time.time()
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            if time.time() - start_time > 60.0:
                print("  [TIMEOUT] Sweep timed out.")
                break
            continue
            
        print(f"  [READ] {line}")
        
        if "END RESONANT SPECTRAL SWEEP" in line:
            break
            
        if "Freq:" in line and "Voltage:" in line:
            try:
                parts = line.split("|")
                f_val = int(parts[0].replace("Freq:", "").replace("Hz", "").strip())
                v_val = float(parts[2].replace("Voltage:", "").replace("V", "").strip())
                freqs.append(f_val)
                voltages.append(v_val)
            except Exception as e:
                pass
                
    if freqs:
        fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
        ax.plot(freqs, voltages, color="#39ff14", lw=2.5, marker="o", markersize=4)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Accumulated DC Voltage (V)")
        ax.set_title("Coupled Waveguide: Resonant Spectral Response")
        ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
        
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_coupled_frequency_sweep.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  [PLOT] Saved frequency sweep -> {out}")
        print(f"    Peak Resonance: {max(voltages):.2f} V at {freqs[voltages.index(max(voltages))]} Hz")

def run_decay_sweep(ser):
    print("\n" + "="*60)
    print("  [RUN 2] T1 ENERGY RELAXATION SWEEP (DECAY SWEEP)")
    print("="*60)
    
    ser.write(b"d")
    times = []
    voltages = []
    start_time = time.time()
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            if time.time() - start_time > 90.0:
                break
            continue
            
        print(f"  [READ] {line}")
        
        if "END T1 RELAXATION SWEEP" in line:
            break
            
        if "DecayTime:" in line and "Voltage:" in line:
            try:
                parts = line.split("|")
                t_val = int(parts[0].replace("DecayTime:", "").replace("ms", "").strip())
                v_val = float(parts[2].replace("Voltage:", "").replace("V", "").strip())
                times.append(t_val)
                voltages.append(v_val)
            except Exception as e:
                pass
                
    if times:
        fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
        ax.plot(times, voltages, color="#ff007f", lw=3.0, marker="s", markersize=4)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Stored DC Voltage (V)")
        ax.set_title("Coupled Waveguide: T1 Energy Relaxation (Decay)")
        ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
        
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_coupled_decay_sweep.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  [PLOT] Saved decay sweep -> {out}")
        
        # Calculate T1 (time to decay to 1/e ~ 36.8% of starting voltage above floor)
        v_start = voltages[0]
        v_min = min(voltages)
        target = v_min + (v_start - v_min) * 0.368
        t1_val = 0
        for t, v in zip(times, voltages):
            if v <= target:
                t1_val = t
                break
        print(f"    T1 Relaxation Time Constant: {t1_val} ms (decline to {target:.2f} V)")

def run_floquet_sweep(ser):
    print("\n" + "="*60)
    print("  [RUN 3] TWO-TONE FLOQUET SWEEP")
    print("="*60)
    
    ser.write(b"w")
    carriers = []
    voltages = []
    start_time = time.time()
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            if time.time() - start_time > 60.0:
                break
            continue
            
        print(f"  [READ] {line}")
        
        if "END TWO-TONE FLOQUET SWEEP" in line:
            break
            
        if "CarrierFreq:" in line and "Voltage:" in line:
            try:
                parts = line.split("|")
                c_val = int(parts[0].replace("CarrierFreq:", "").replace("Hz", "").strip())
                v_val = float(parts[2].replace("Voltage:", "").replace("V", "").strip())
                carriers.append(c_val)
                voltages.append(v_val)
            except Exception as e:
                pass
                
    if carriers:
        fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
        ax.plot(carriers, voltages, color="#00ffff", lw=2.5, marker="^", markersize=4)
        ax.set_xlabel("Carrier Frequency (Hz)")
        ax.set_ylabel("Accumulated DC Voltage (V)")
        ax.set_title("Coupled Waveguide: Two-Tone Floquet Sweep (Carrier at 2x Pump)")
        ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
        
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_coupled_floquet_sweep.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  [PLOT] Saved Floquet sweep -> {out}")
        print(f"    Max Floquet Coupling: {max(voltages):.2f} V at {carriers[voltages.index(max(voltages))]} Hz")

def run_2d_sweep(ser):
    print("\n" + "="*60)
    print("  [RUN 4] COMBINED 2D SPATIO-TEMPORAL SWEEP")
    print("="*60)
    
    ser.write(b"m")
    freqs = []
    phases = []
    voltages = []
    start_time = time.time()
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            if time.time() - start_time > 120.0:
                print("  [TIMEOUT] 2D Sweep timed out.")
                break
            continue
            
        print(f"  [READ] {line}")
        
        if "END COMBINED 2D SWEEP" in line:
            break
            
        if "2D | Freq:" in line:
            try:
                # 2D | Freq:2000Hz | Phase:10us | ADC:102 | Voltage:0.50V
                parts = line.split("|")
                f_val = int(parts[1].replace("Freq:", "").replace("Hz", "").strip())
                p_val = int(parts[2].replace("Phase:", "").replace("us", "").strip())
                v_val = float(parts[4].replace("Voltage:", "").replace("V", "").strip())
                
                freqs.append(f_val)
                phases.append(p_val)
                voltages.append(v_val)
            except Exception as e:
                pass
                
    if freqs:
        # Convert lists to unique sorted arrays
        unique_freqs = sorted(list(set(freqs)))
        unique_phases = sorted(list(set(phases)))
        
        # Initialize grid
        Z = np.zeros((len(unique_phases), len(unique_freqs)))
        
        # Populate grid
        for f, p, v in zip(freqs, phases, voltages):
            f_idx = unique_freqs.index(f)
            p_idx = unique_phases.index(p)
            Z[p_idx, f_idx] = v
            
        fig = plt.figure(figsize=(11, 7), facecolor="#0a0a0f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#10101a")
        
        X, Y = np.meshgrid(unique_freqs, unique_phases)
        cp = ax.contourf(X, Y, Z, cmap="plasma", levels=50)
        cbar = fig.colorbar(cp, ax=ax)
        cbar.set_label("DC Stored Voltage (V)", color="gray")
        cbar.ax.yaxis.set_tick_params(color="gray")
        cbar.ax.tick_params(labelcolor="gray")
        
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Phase Delay (us)")
        ax.set_title("Coupled Waveguide: Spatio-Temporal Resonance Heatmap")
        
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_coupled_2d_heatmap.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        
        print(f"  [PLOT] Saved 2D Heatmap -> {out}")
        print(f"    Peak Coordinates: {np.max(Z):.2f} V at Freq {unique_freqs[np.unravel_index(np.argmax(Z), Z.shape)[1]]} Hz, Phase {unique_phases[np.unravel_index(np.argmax(Z), Z.shape)[0]]} us")

def main():
    try:
        ser = init_serial()
        
        # Run sweeps
        run_frequency_sweep(ser)
        time.sleep(1.0)
        
        run_decay_sweep(ser)
        time.sleep(1.0)
        
        run_floquet_sweep(ser)
        time.sleep(1.0)
        
        run_2d_sweep(ser)
        
        ser.close()
        print("\n  [SUCCESS] All sweeps executed successfully!")
        
    except Exception as e:
        print(f"  [ERROR] Main execution failed: {e}")

if __name__ == "__main__":
    main()
