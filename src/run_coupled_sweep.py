# -*- coding: utf-8 -*-
"""
run_coupled_sweep.py
====================
Runs the physical Coupled Tetrahedron-Ratchet Phase Sweep.
Connects to COM5, triggers the Coupled Phase Sweep ('c'),
reads the accumulated DC voltage at Node 2, and plots the resulting
Phase-to-Voltage conversion curve to show constructive/destructive conversion.
"""

import sys
import os
import time
import serial
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    print("=" * 80)
    print("  TAP COUPLED WAVEGUIDE SWEEP CLIENT")
    print("  Interfacing with Arduino on COM5 @ 115200 baud")
    print("=" * 80)
    print()
    
    port = "COM5"
    baud = 115200
    
    try:
        ser = serial.Serial(port, baud, timeout=2.0)
        print(f"  [CONN] Connected to {port}.")
        
        # Reset Arduino
        print("  [RST] Rebooting Arduino...")
        ser.dtr = False
        time.sleep(0.1)
        ser.dtr = True
        time.sleep(2.0)
        
        # Trigger Coupled Sweep
        print("\n  [SWEEP] Starting Coupled Phase Sweep...")
        ser.reset_input_buffer()
        ser.write(b"c")
        
        delays = []
        voltages = []
        
        start_time = time.time()
        
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                if time.time() - start_time > 45.0:
                    print("  [TIMEOUT] Sweep timed out.")
                    break
                continue
                
            print(f"  [READ] {line}")
            
            if "END COUPLED WAVEGUIDE PHASE SWEEP" in line:
                print("  [STOP] Coupled phase sweep completed.")
                break
                
            if "PhaseDelay:" in line and "Voltage:" in line:
                try:
                    # Parse: PhaseDelay:15us | ADC:584 | Voltage:2.85V
                    parts = line.split("|")
                    delay_val = int(parts[0].replace("PhaseDelay:", "").replace("us", "").strip())
                    volt_val = float(parts[2].replace("Voltage:", "").replace("V", "").strip())
                    
                    delays.append(delay_val)
                    voltages.append(volt_val)
                except Exception as e:
                    print(f"  [PARSE ERROR] Failed to parse: {e}")
                    
        ser.close()
        
        # Plot results
        if voltages:
            v_max = max(voltages)
            v_min = min(voltages)
            ratio = v_max / v_min if v_min > 0 else 0
            
            p_max = delays[voltages.index(v_max)]
            p_min = delays[voltages.index(v_min)]
            
            fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#10101a")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2a3a")
            ax.tick_params(colors="gray")
            ax.xaxis.label.set_color("gray")
            ax.yaxis.label.set_color("gray")
            ax.title.set_color("white")
            
            ax.plot(delays, voltages, color="#39ff14", lw=3.0, marker="o", label="DC Voltage Output (V)")
            
            # Highlight max and min
            ax.axvline(p_max, color="#4ecdc4", linestyle="--", alpha=0.5, label=f"Constructive Phase ({p_max} us)")
            ax.axvline(p_min, color="#ff6b6b", linestyle="--", alpha=0.5, label=f"Destructive Phase ({p_min} us)")
            
            ax.set_xlabel("Phase Delay (us)")
            ax.set_ylabel("Accumulated DC Voltage (V)")
            ax.set_title("TAP Coupled Waveguide: Phase-to-Voltage Conversion Curve")
            ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
            ax.legend(facecolor="#10101a", labelcolor="#e8e8e8")
            
            out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_coupled_waveguide_sweep.png")
            plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
            plt.close()
            
            print(f"\n  [PLOT] Saved coupled waveguide curve to -> {out}")
            print(f"    Constructive Peak : {v_max:.2f} V at {p_max} us")
            print(f"    Destructive Null  : {v_min:.2f} V at {p_min} us")
            print(f"    Voltage Extinction: {ratio:.2f}x")
            print("=" * 80 + "\n")
        else:
            print("  [ERROR] Incomplete data. Could not plot curve.")
            
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

if __name__ == "__main__":
    main()
