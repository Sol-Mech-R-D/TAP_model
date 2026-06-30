# -*- coding: utf-8 -*-
"""
run_tetrahedral_sweep.py
========================
Triggers and monitors the physical 6-capacitor tetrahedral phase sweep.
Connects to the Arduino on COM5, sends the 't' command, parses the real-time 
interference telemetry, and plots the resulting phase-cancellation curve.
"""

import sys
import os
import time
import serial
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    print("=" * 80)
    print("  TAP TETRAHEDRAL PHASE-MIXING SWEEP CLIENT")
    print("  Interfacing with Arduino on COM5 @ 115200 baud")
    print("=" * 80)
    print()
    
    port = "COM5"
    baud = 115200
    
    try:
        # Open serial port
        ser = serial.Serial(port, baud, timeout=3.0)
        print(f"  [CONN] Connected to {port} successfully.")
        
        # Reset Arduino to ensure clean slate
        print("  [RST] Rebooting Arduino...")
        ser.dtr = False
        time.sleep(0.1)
        ser.dtr = True
        time.sleep(2.0)
        
        # Flush buffer
        ser.reset_input_buffer()
        
        # Send 't' command to trigger tetrahedral sweep
        print("  [CMD] Sending 't' command to start phase-mixing sweep...")
        ser.write(b't')
        
        phase_delays = []
        amplitudes = []
        
        active_reading = False
        start_time = time.time()
        
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                # Keep alive check
                if time.time() - start_time > 30.0:
                    print("  [TIMEOUT] No response received from Arduino.")
                    break
                continue
                
            print(f"  [READ] {line}")
            
            if "START TETRAHEDRAL PHASE SWEEP" in line:
                active_reading = True
                continue
                
            if "END TETRAHEDRAL PHASE SWEEP" in line:
                print("\n  [STOP] Sweep complete.")
                break
                
            if active_reading and "PhaseDelay:" in line:
                try:
                    # Parse: PhaseDelay:5us | Amplitude:412 [Min: 211, Max: 623]
                    parts = line.split("|")
                    delay_part = parts[0].strip().replace("PhaseDelay:", "").replace("us", "")
                    amp_part = parts[1].strip().split(" ")[0].replace("Amplitude:", "")
                    
                    delay = int(delay_part)
                    amp = int(amp_part)
                    
                    phase_delays.append(delay)
                    amplitudes.append(amp)
                except Exception as e:
                    print(f"  [PARSE ERROR] Failed to parse line: {e}")
                    
        ser.close()
        
        if not phase_delays:
            print("  [ERROR] No data points collected. Check connections and try again.")
            return
            
        print(f"\n  [ANALYSIS] Collected {len(phase_delays)} data points.")
        max_amp = max(amplitudes)
        min_amp = min(amplitudes)
        extinction_ratio = max_amp / max(1.0, float(min_amp))
        
        print(f"    Peak Amplitude (Constructive) : {max_amp} ADC counts")
        print(f"    Null Amplitude (Destructive)  : {min_amp} ADC counts")
        print(f"    Extinction Ratio              : {extinction_ratio:.2f}x")
        print()
        
        # Generate plot
        fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        
        ax.plot(phase_delays, amplitudes, marker="o", color="#4ecdc4", lw=2, label="Measured Node C Output")
        
        # Label constructive/destructive points
        opt_constructive = phase_delays[np.argmax(amplitudes)]
        opt_destructive = phase_delays[np.argmin(amplitudes)]
        
        ax.plot(opt_constructive, max_amp, marker="o", color="#7c6af7", ms=8)
        ax.plot(opt_destructive, min_amp, marker="o", color="#ff6b6b", ms=8)
        
        ax.text(opt_constructive - 10, max_amp + 15, "Constructive", color="#7c6af7")
        ax.text(opt_destructive - 10, min_amp - 25, "Destructive Null", color="#ff6b6b")
        
        ax.set_xlabel("Phase Delay Dt (us)")
        ax.set_ylabel("Interference Amplitude (ADC units)")
        ax.set_title("TAP Tetrahedral Qubit Bridge: Wave Phase Interference Curve")
        ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
        ax.legend(facecolor="#10101a", labelcolor="#e8e8e8")
        
        out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_tetrahedral_sweep_results.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        
        print(f"  [PLOT] Phase interference curve saved -> {out}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"  [ERROR] Serial connection error: {e}")
        print("  Ensure no other terminal is monitoring COM5 and the USB cable is secure.")

if __name__ == "__main__":
    main()
