# -*- coding: utf-8 -*-
"""
tap_multidiscipline_sweep.py
============================
Unified diagnostics sweep across:
1. Phinary ALU Emulator (analog arithmetic)
2. Planetary Dynamos (convective core thermodynamics)
3. Waveguide Echoes (acoustic resonance & phase lag)
"""

import sys
import os

# Dynamically add src/ to the Python search path to load the compiled modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tap_kernel_hardware_emulator import run_emulator
from tap_planetary_dynamos import predict_dynamos
from tap_waveguide_echoes import run_waveguide_simulation

def main():
    print("=" * 90)
    print("  TAP MULTI-DISCIPLINE SWEEP DIAGNOSTICS")
    print("  Running sweeps across Phinary ALU, Planetary Dynamos, and Waveguide Echoes")
    print("=" * 90)
    
    vev_ratios = [0.95, 1.00, 1.05]
    
    # ─────────────────────────────────────────────────────────────────────────
    # 1. PHINARY ALU EMULATOR RESULTS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[1/3] PHINARY ALU EMULATOR DIAGNOSTICS:")
    print("-" * 60)
    try:
        em_res = run_emulator()
        print(f"  * Phinary Addition Sum (2 + 3 = 5) : {em_res['phinary_sum_5']}")
        print(f"  * RT Scheduler Allocation Share     : {em_res['scheduler_rt_pct']:.2f}% (Target: 61.80%)")
        print(f"  * Brane Pointer Protection Status   : Locked = {em_res['invalid_ptr_blocked']}")
        print(f"  * Valid Pointer Base Potential      : {em_res['valid_ptr_potential']:.5f}")
    except Exception as e:
        print(f"  [ERROR] Failed to run Phinary ALU: {e}")
    print("-" * 60)

    # ─────────────────────────────────────────────────────────────────────────
    # 2. PLANETARY DYNAMOS THERMAL SWEEP
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[2/3] PLANETARY DYNAMOS THERMAL SWEEP (VEV Coupling):")
    print("-" * 80)
    print(f"  {'Planet / Body':30} | {'v_ratio = 0.95':14} | {'v_ratio = 1.00':14} | {'v_ratio = 1.05':14}")
    print("-" * 80)
    
    planet_temps = {}
    
    for vr in vev_ratios:
        # We manually inject the v_ratio by temporarily patching or scaling
        # In tap_planetary_dynamos, the output scales with the global v_ratio variable
        # We can dynamically pass/overwrite it if supported, or read the predictions
        try:
            # Let's import the module and patch the global v_ratio if present
            import tap_planetary_dynamos
            tap_planetary_dynamos.v_ratio = vr
            dyn_res = predict_dynamos()
            for planet, data in dyn_res.items():
                if planet not in planet_temps:
                    planet_temps[planet] = []
                planet_temps[planet].append(f"{data['final_core_temp_k']:.1f} K ({data['status'].split()[0]})")
        except Exception as e:
            print(f"  [ERROR] Failed to compile planet {vr}: {e}")
            
    for planet, temps in planet_temps.items():
        if len(temps) == 3:
            print(f"  {planet:30} | {temps[0]:14} | {temps[1]:14} | {temps[2]:14}")
    print("-" * 80)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. WAVEGUIDE ACOUSTIC ECHO SWEEP
    # ─────────────────────────────────────────────────────────────────────────
    print("\n[3/3] WAVEGUIDE ACOUSTIC ECHO SWEEP (Phase Lag & Amplitude):")
    print("-" * 70)
    print(f"  {'VEV Ratio':12} | {'Acoustic Echo Lag (t_echo)':28} | {'Reflection Amplitude Ratio':24}")
    print("-" * 70)
    for vr in vev_ratios:
        try:
            t_lag, amp = run_waveguide_simulation(vr)
            print(f"  {vr:12.2f} | {t_lag:24.4f} fs | {amp:.4e}")
        except Exception as e:
            print(f"  [ERROR] Failed to run waveguide sweep for {vr}: {e}")
    print("-" * 70)
    print("=" * 90)

if __name__ == "__main__":
    main()
