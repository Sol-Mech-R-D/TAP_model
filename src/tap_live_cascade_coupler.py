# -*- coding: utf-8 -*-
"""
tap_live_cascade_coupler.py
===========================
Bridges the physical breadboard hardware with the TAP mathematical simulation.
Monitors live_qubit_data.log in real-time, extracts voltage/amplitude, 
and drives the global multisphere cascade parameters (N_B, psi) dynamically.
"""

import os
import sys
import time
import json
import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13

LOG_PATH = "/data/data/com.termux/files/home/TAP_model/assets/live_qubit_data.log"
STATE_PATH = "/data/data/com.termux/files/home/TAP_model/assets/tap_live_state.json"
GEO_PATH = "/data/data/com.termux/files/home/TAP_model/assets/tap_geocosmic_coupling.json"
GRID_PATH = "/data/data/com.termux/files/home/TAP_model/assets/tap_grid_supply_coupling.json"

def compute_couplings(N_B, psi):
    """Recalculates all multisphere coupling coefficients using live variables."""
    gamma_val = 1.0 + N_B * PHI_INV13
    
    # Tectonic (California Strike-Slip & Japan Subduction)
    k_shear = (PHI ** -4) * N_B * (1.0 - psi)
    k_normal = gamma_val * (PHI ** -8)
    
    # Atmospheric
    k_debye = (gamma_val - 1.0) * (PHI ** 5)
    k_vortex = (1.0 - psi) ** (PHI ** -4)
    
    # Cosmic (Solar Reconnection)
    k_solar = PHI_INV13 * N_B * (1.0 + psi)
    
    # Grid (ERCOT with 0.35 active battery/wire buffer)
    base_thermal_stress = (PHI ** -4) * N_B * (1.0 + psi)
    ercot_stress = base_thermal_stress * (1.2 - 0.35)
    entsoe_stress = base_thermal_stress * 0.4
    
    # Supply lines
    rail_buckle = (PHI ** -4) * N_B * (1.0 - psi)
    panama_draft = gamma_val * (PHI ** -8)
    
    return {
        "constants": {
            "N_B": N_B,
            "psi": round(psi, 4),
            "gamma": round(gamma_val, 6)
        },
        "tectonic": {
            "california_strike_slip_coupling": k_shear,
            "japan_subduction_coupling": k_normal
        },
        "atmospheric": {
            "lightning_debye_coupling": k_debye,
            "tornado_vortex_coupling": k_vortex
        },
        "cosmic": {
            "solar_reconnection_coupling": k_solar
        },
        "power_grids": {
            "texas_ercot_sag_stress": ercot_stress,
            "europe_entsoe_sag_stress": entsoe_stress
        },
        "supply_lines": {
            "rail_sun_kink_buckling_risk": rail_buckle,
            "panama_canal_draft_restriction": panama_draft
        }
    }

def main():
    print("=" * 80)
    print("  TAP LIVE HARDWARE-TO-SOFTWARE CASCADE COUPLER")
    print("  Listening to breadboard telemetry...")
    print("=" * 80)
    
    if not os.path.exists(LOG_PATH):
        # Create empty log if missing
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "w") as f:
            f.write("=== LOG CREATED BY COUPLER ===\n")
            
    # Initialize variables
    N_B = 34  # Start with best-fit Breath Number
    prev_voltage = 0.0
    max_observed_v = 4.05
    
    # File pointer tracking
    file_size = os.path.getsize(LOG_PATH)
    log_file = open(LOG_PATH, "r", errors="ignore")
    log_file.seek(file_size)  # Go to end of file to read only new lines
    
    print(f"  [INIT] Base Breath Number: N_B = {N_B}")
    print(f"  [INIT] Clamping V_max = {max_observed_v}V")
    print("  [LIVE] Awaiting serial entries. Press Ctrl+C to halt.\n")
    
    try:
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            # Process lines containing telemetry
            # Expected format: "Voltage:2.35V" or "Voltage: 2.35V" or "ADC:480"
            line_str = line.strip()
            
            # Check for standard step readings
            if "Voltage:" in line_str:
                try:
                    parts = line_str.split("Voltage:")
                    v_part = parts[1].split("V")[0].strip()
                    voltage = float(v_part)
                    
                    # Calculate live psi (normalized voltage)
                    psi = min(1.0, max(0.0, voltage / max_observed_v))
                    
                    # Detect avalanche collapse (drop of > 2.0V)
                    if prev_voltage - voltage > 2.0 and prev_voltage > 2.5:
                        N_B += 1
                        print(f"\n  🚨 [COLLAPSE DETECTED] Physical avalanche discharge! Cosmic Inhale.")
                        print(f"  🔄 [CYCLE RESET] Incrementing Breath Number: N_B -> {N_B}\n")
                        
                    prev_voltage = voltage
                    
                    # Compute updated coupling indices
                    data = compute_couplings(N_B, psi)
                    
                    # Print status line
                    sys.stdout.write(
                        f"\r  [TELEMETRY] V_A0: {voltage:.2f}V | ψ_live: {psi:.4f} | "
                        f"N_B: {N_B} | ERCOT Sag: {data['power_grids']['texas_ercot_sag_stress']:.4f} "
                    )
                    sys.stdout.flush()
                    
                    # Export outputs
                    with open(STATE_PATH, "w") as f:
                        json.dump(data, f, indent=2)
                        
                    # Maintain individual geocosmic and grid supply assets
                    with open(GEO_PATH, "w") as f:
                        json.dump({
                            "tectonic": data["tectonic"],
                            "atmospheric": data["atmospheric"],
                            "cosmic": data["cosmic"]
                        }, f, indent=2)
                        
                    with open(GRID_PATH, "w") as f:
                        json.dump({
                            "power_grids": data["power_grids"],
                            "supply_lines": data["supply_lines"]
                        }, f, indent=2)
                        
                except Exception as parse_err:
                    # Ignore parsing errors from incomplete serial lines
                    pass
                    
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\n  [STOP] Live coupling stopped.")
    finally:
        log_file.close()
        print("=" * 80)

if __name__ == "__main__":
    main()
