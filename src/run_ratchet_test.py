# -*- coding: utf-8 -*-
"""
run_ratchet_test.py
===================
Runs the physical Diode-Capacitor Temporal Ratchet test.
Connects to COM5, triggers the Forward ('f') and Reversed ('b') phase sequences,
parses the voltage accumulation at Node 2, and plots the resulting curves
to show the temporal asymmetry (one-way charge flow).
"""

import sys
import os
import time
import serial
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def run_sequence(ser, command, expected_end):
    steps = []
    voltages = []
    
    # Flush input
    ser.reset_input_buffer()
    
    # Send command
    print(f"  [CMD] Sending '{command}' command...")
    ser.write(command.encode('utf-8'))
    
    start_time = time.time()
    
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            if time.time() - start_time > 15.0:
                print("  [TIMEOUT] No response from Arduino.")
                break
            continue
            
        print(f"  [READ] {line}")
        
        if expected_end in line:
            print(f"  [STOP] {command} sequence completed.")
            break
            
        if "Step:" in line and "Voltage:" in line:
            try:
                # Parse: Step:5 | ADC:210 | Voltage:1.03V
                parts = line.split("|")
                step_val = int(parts[0].replace("Step:", "").strip())
                volt_val = float(parts[2].replace("Voltage:", "").replace("V", "").strip())
                
                steps.append(step_val)
                voltages.append(volt_val)
            except Exception as e:
                print(f"  [PARSE ERROR] Failed to parse: {e}")
                
    return steps, voltages

def main():
    print("=" * 80)
    print("  TAP DIODE-CAPACITOR RATCHET TEST CLIENT")
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
        
        # 1. Run Forward Test
        print("\n  [TEST 1] Running Forward Ratchet Sequence...")
        f_steps, f_volts = run_sequence(ser, "f", "END RATCHET SEQUENCE: FORWARD")
        
        print("\n" + "-"*60)
        print("  [DISCHARGE REQUIRED] RATCHET DISCHARGE REQUIRED:")
        print("  Please temporarily connect Node 2 (Pin A1) to GND to drain the stored charge.")
        print("  Once discharged, press ENTER in the terminal to start the Reversed test.")
        print("-"*60)
        
        # Wait for user input
        input("  Press ENTER to continue...")
        
        # 2. Run Reversed Test
        print("\n  [TEST 2] Running Reversed Ratchet Sequence...")
        b_steps, b_volts = run_sequence(ser, "b", "END RATCHET SEQUENCE: REVERSED")
        
        ser.close()
        
        # Plot results
        if f_volts and b_volts:
            fig = plt.figure(figsize=(10, 6), facecolor="#0a0a0f")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#10101a")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2a3a")
            ax.tick_params(colors="gray")
            ax.xaxis.label.set_color("gray")
            ax.yaxis.label.set_color("gray")
            ax.title.set_color("white")
            
            ax.plot(f_steps, f_volts, color="#4ecdc4", lw=2.5, marker="o", label="Forward Sequence (t1->t2->t3->t4)")
            ax.plot(b_steps, b_volts, color="#ff6b6b", lw=2.5, marker="s", label="Reversed Sequence (t1->t3->t2->t4)")
            
            ax.set_xlabel("Time Steps")
            ax.set_ylabel("Accumulated Voltage (V)")
            ax.set_title("TAP Diode-Capacitor Ratchet: Temporal Asymmetry Verification")
            ax.grid(color="#1a1a2e", linestyle="--", linewidth=0.5)
            ax.legend(facecolor="#10101a", labelcolor="#e8e8e8")
            
            out = os.path.join(os.path.dirname(__file__), "..", "assets", "tap_ratchet_sweep_results.png")
            plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
            plt.close()
            
            print(f"\n  [PLOT] Saved ratchet curves to -> {out}")
            print(f"    Peak Forward Voltage : {max(f_volts):.2f} V")
            print(f"    Peak Reversed Voltage: {max(b_volts):.2f} V")
            print("=" * 80 + "\n")
        else:
            print("  [ERROR] Incomplete data. Could not plot curves.")
            
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

if __name__ == "__main__":
    main()
