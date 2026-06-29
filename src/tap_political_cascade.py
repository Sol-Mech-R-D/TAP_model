# -*- coding: utf-8 -*-
"""
tap_political_cascade.py
========================
Calculates the coupling strengths and metrics for:
  1. Cognitive Polarization Index (CPI) based on brain critical phase coherence.
  2. Anti-Incumbent Sentiment (AIS) driven by thermal/grid sag discomfort.
  3. Campaign Spending Soliton Index (CSSI) of PAC/lobby allocations.

Correlates with major historical elections (2024) and projects forward
to upcoming elections (e.g. US Midterms, November 3, 2026).
"""

import os
import math
import json
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Earth Orbit Constants
T_YEAR = 365.256
E = 0.0167
V_MEAN = 29.78
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

def get_earth_velocity(days_since_perihelion):
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))

def get_crossing_times_range(start_year, end_year):
    current_date = SOLSTICE_2026
    days_from_peri = 169.0
    crossings = []
    
    # Step backwards
    while current_date > datetime(start_year, 1, 1):
        v = get_earth_velocity(days_from_peri)
        interval = 8.12 * (V_MEAN / v)
        current_date -= timedelta(days=interval)
        days_from_peri -= interval
        
    # Step forwards
    step = 0
    while current_date < datetime(end_year, 12, 31):
        v = get_earth_velocity(days_from_peri)
        interval = 8.12 * (V_MEAN / v)
        crossings.append({
            "step": step,
            "date": current_date
        })
        current_date += timedelta(days=interval)
        days_from_peri += interval
        step += 1
        
    return crossings

def get_closest_crossing(target_date, crossings):
    closest = min(crossings, key=lambda c: abs((target_date - c["date"]).total_seconds()))
    diff_days = (target_date - closest["date"]).total_seconds() / 86400.0
    phase = (diff_days / 8.12) * 2.0 * math.pi
    alignment = math.cos(phase)
    return closest, diff_days, alignment

def process_historical_elections(crossings):
    """
    Correlates major 2024 elections with TAP crossings.
    """
    elections = [
        ("US Presidential Election", datetime(2024, 11, 5)),
        ("UK General Election", datetime(2024, 7, 4)),
        ("French Legislative Runoff", datetime(2024, 7, 7)),
        ("European Parliament Elections", datetime(2024, 6, 9)),
        ("Taiwan Presidential Election", datetime(2024, 1, 13))
    ]
    
    results = []
    for name, date in elections:
        closest, diff_days, alignment = get_closest_crossing(date, crossings)
        
        # Calculate indices
        cpi = 1.0 + 0.15 * alignment  # polarization
        ais = 1.0 + 0.20 * abs(alignment)  # anti-incumbent
        cssi = 100.0 * (1.0 + 0.10 * alignment)  # spending surge
        
        results.append({
            "election": name,
            "date": date.strftime("%Y-%m-%d"),
            "closest_crossing": closest["date"].strftime("%Y-%m-%d %H:%M"),
            "days_diff": diff_days,
            "alignment": alignment,
            "cognitive_polarization_index": cpi,
            "anti_incumbent_sentiment": ais,
            "spending_soliton_index": cssi
        })
    return results

def project_future_elections(crossings):
    """
    Projects future election risk corridors (2026-2030).
    Specifically looks at the US Midterms on November 3, 2026.
    """
    future_elections = [
        ("US Midterm Elections", datetime(2026, 11, 3)),
        ("French Presidential Election", datetime(2027, 4, 18)),
        ("German Federal Election", datetime(2027, 10, 24)),
        ("US Presidential Election", datetime(2028, 11, 7))
    ]
    
    projections = []
    for name, date in future_elections:
        closest, diff_days, alignment = get_closest_crossing(date, crossings)
        
        # Calculate indices
        cpi = 1.0 + 0.15 * alignment
        ais = 1.0 + 0.20 * abs(alignment)
        cssi = 100.0 * (1.0 + 0.10 * alignment)
        
        projections.append({
            "election": name,
            "date": date.strftime("%Y-%m-%d"),
            "closest_crossing": closest["date"].strftime("%Y-%m-%d %H:%M"),
            "days_diff": diff_days,
            "alignment": alignment,
            "cognitive_polarization_index": cpi,
            "anti_incumbent_sentiment": ais,
            "spending_soliton_index": cssi
        })
    return projections

def main():
    print("=" * 80)
    print("  TAP POLITICAL CASCADE & VOTER TRANS-CYCLIC ALIGNMENT")
    print("=" * 80)
    
    crossings = get_crossing_times_range(2024, 2030)
    
    # 1. Process 2024 Historical Elections
    hist = process_historical_elections(crossings)
    print("  [HISTORICAL 2024 ELECTIONS] Alignment Results:")
    print(f"    {'Election':30s} | {'Date':10s} | {'TAP Align':9s} | {'Polarization':12s} | {'Anti-Incumb'}")
    print(f"    {'-'*30}-+-{'-'*10}-+-{'-'*9}-+-{'-'*12}-+-{'-'*11}")
    for h in hist:
        print(f"    {h['election']:30s} | {h['date']:10s} | {h['alignment']:9.4f} | {h['cognitive_polarization_index']:12.2f} | {h['anti_incumbent_sentiment']:11.2f}")
        
    # 2. Project Future Elections
    proj = project_future_elections(crossings)
    print("\n  [FUTURE PROJECTIONS (2026-2028)] Risk Corridor Analysis:")
    print(f"    {'Election':30s} | {'Date':10s} | {'TAP Align':9s} | {'Polarization':12s} | {'Anti-Incumb'}")
    print(f"    {'-'*30}-+-{'-'*10}-+-{'-'*9}-+-{'-'*12}-+-{'-'*11}")
    for p in proj:
        print(f"    {p['election']:30s} | {p['date']:10s} | {p['alignment']:9.4f} | {p['cognitive_polarization_index']:12.2f} | {p['anti_incumbent_sentiment']:11.2f}")
        
    # Export to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_political_predictions.json")
    with open(out_path, "w") as f:
        json.dump({
            "historical_2024": hist,
            "future_projections": proj
        }, f, indent=2)
    print(f"\n  [EXPORT] Political cascade predictions saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
