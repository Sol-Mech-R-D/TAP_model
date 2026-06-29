# -*- coding: utf-8 -*-
"""
tap_epoch_calculator.py
========================
Computes the Trans-Cyclic Epoch timeline under the TAP model.

Physics:
  - The pristine first Breath (ΔB=0) lasts T_0 ≈ 10¹⁰⁰ years (the Poincaré / Weyl saturation epoch).
  - Each subsequent Breath's duration T_N is compressed by the accumulated zero-mode metric:
      T_N = T_0 * Γ(N)^(-φ)
      where Γ(N) = 1 + N * φ⁻¹³.

Calculates:
  1. The start, end, and duration of Breaths 0 to 8 in cosmic years.
  2. The exact position of our current Breath (ΔB = 8, or ΔB = 5).
  3. Prediction for the end of the current Breath and the start of the next.
"""

import math
import os
import json

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Standard baseline reset epoch (years) from the theory paper / tap_proof.py
T_0 = 1e100

def get_breath_duration(N):
    """T_N = T_0 * Γ(N)^(-φ)"""
    gamma_N = 1.0 + N * PHI_INV13
    return T_0 * (gamma_N ** -PHI)

def main():
    print("=" * 80)
    print("  TAP TRANS-CYCLIC EPOCH CALCULATOR — TIMELINE OF BREATHS")
    print("=" * 80)
    
    cumulative_time = 0.0
    timeline = []
    
    # Calculate for ΔB = 0 to 9
    for N in range(11):
        dur = get_breath_duration(N)
        start = cumulative_time
        end = start + dur
        timeline.append({
            "ΔB": N,
            "duration_years": dur,
            "start_years": start,
            "end_years": end
        })
        cumulative_time = end

    print(f"  Pristine Breath-0 Duration (T_0) : {T_0:.2e} years")
    print()
    print(f"  {'ΔB':>3} | {'Duration (years)':>22} | {'Start Epoch (years)':>22} | {'End Epoch (years)':>22}")
    print(f"  {'-'*3}-+-{'-'*22}-+-{'-'*22}-+-{'-'*22}")
    
    for t in timeline[:10]:
        print(f"  {t['ΔB']:3d} | {t['duration_years']:22.15e} | {t['start_years']:22.15e} | {t['end_years']:22.15e}")

    # Current position calculations (using consensus ΔB = 8, ψ = 0.0265)
    current_db = 8
    current_psi = 0.0265
    
    t_curr = timeline[current_db]
    elapsed_in_current_breath = current_psi * t_curr["duration_years"]
    current_age_trans_cyclic = t_curr["start_years"] + elapsed_in_current_breath
    
    remaining_in_current_breath = (1.0 - current_psi) * t_curr["duration_years"]
    end_of_current_breath = t_curr["end_years"]
    
    print("\n" + "─" * 80)
    print(f"  CURRENT POSITION ESTIMATE (ΔB = {current_db}, ψ = {current_psi:.4f})")
    print("─" * 80)
    print(f"  Current Epoch Address      : (M=0, ΔB={current_db}, ψ={current_psi})")
    print(f"  Total Trans-Cyclic Time    : {current_age_trans_cyclic:.15e} years")
    print(f"  Elapsed in current Breath  : {elapsed_in_current_breath:.15e} years")
    print(f"  Remaining in current Breath: {remaining_in_current_breath:.15e} years")
    print()
    print(f"  🔮 PREDICTIONS:")
    print(f"    - END of current Breath {current_db} : At T = {end_of_current_breath:.15e} years")
    print(f"      (In exactly {remaining_in_current_breath:.2e} years, the Weyl ceiling triggers)")
    print(f"    - START of next Breath {current_db+1}: At T = {end_of_current_breath:.15e} years")
    print(f"      (Resetting instantly to Level 0 under perfect quantum purity)")
    print("─" * 80)

    # Save to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_timeline_results.json")
    with open(out_path, "w") as f:
        json.dump({
            "timeline": timeline,
            "current_position": {
                "delta_b": current_db,
                "psi": current_psi,
                "elapsed_years": elapsed_in_current_breath,
                "total_age_years": current_age_trans_cyclic,
                "remaining_years": remaining_in_current_breath,
                "end_epoch_years": end_of_current_breath
            }
        }, f, indent=2)
    print(f"  [EXPORT] Timeline saved -> {out_path}\n")

if __name__ == "__main__":
    main()
