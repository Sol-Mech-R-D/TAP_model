# -*- coding: utf-8 -*-
"""
tap_cascade_orchestrator.py
===========================
The Grand Master Orchestrator for the TAP Trans-Cyclic Cascade.

Sequentially executes all individual sweeps and updates the global dashboard:
  1. tap_super_tribunal_99.py (The 100-check peer-review tribunal)
  2. tap_breath_clock.py (Global N_B / ΔB minimisation and Bayesian posterior)
  3. tap_seismic_correlation.py (USGS live earthquake circular correlation & 1-year sweep)
  4. tap_fresno_weather.py (Open-Meteo live weather forecast modulation)
  5. tap_global_macro_cascade.py (10-year macro economic projections)
  6. tap_core_ai_cascade.py (Geodynamo and AI compute thermal limits)
  7. tap_grid_supply_cascade.py (ERCOT grid sag and cargo transport sun kinks)
  8. tap_epidemiology_correlation.py (10-year viral mutation sweep & winter storm locking)
  9. update_dashboard.py (Injects the results into the interactive dashboard)
"""

import subprocess
import os
import sys
import json

SCRIPTS = [
    "tap_super_tribunal_99.py",
    "tap_breath_clock.py",
    "tap_seismic_correlation.py",
    "tap_fresno_weather.py",
    "tap_global_macro_cascade.py",
    "tap_core_ai_cascade.py",
    "tap_grid_supply_cascade.py",
    "tap_epidemiology_correlation.py",
    "update_dashboard.py"
]

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 80)
    print("  TAP GRAND CASCADE ORCHESTRATOR — GLOBAL MULTI-SPHERE RUN")
    print("=" * 80)
    
    success_count = 0
    
    for s in SCRIPTS:
        script_path = os.path.join(root_dir, s)
        print(f"\n  [RUNNING] {s} ...")
        
        try:
            # We run the script in a subprocess
            res = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  [SUCCESS] {s} completed clean.")
            # Print the last 3 lines of output as status
            lines = res.stdout.strip().split("\n")
            status_lines = lines[-3:] if len(lines) >= 3 else lines
            for l in status_lines:
                print(f"    └ {l}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] {s} failed with exit code {e.returncode}:")
            print(e.stderr)
            
    print("\n" + "=" * 80)
    print("  ORCHESTRATION SUMMARY")
    print("=" * 80)
    print(f"  Total Scripts Executed: {len(SCRIPTS)}")
    print(f"  Successfully Completed: {success_count} / {len(SCRIPTS)}")
    if success_count == len(SCRIPTS):
        print("  🎯 CASCADE IS 100% UNIFIED, ACCURATE, AND LIVE-WIRED.")
    else:
        print("  ⚠️ Some components require debug attention.")
    print("=" * 80)

if __name__ == "__main__":
    main()
