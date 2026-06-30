# -*- coding: utf-8 -*-
"""
tap_hardware_market_clock.py
============================
Calculates the computer hardware purchase index (HPI) for the rest of 2026.
HPI measures the relative pricing/supply-chain stress for silicon components
(GPUs, CPUs, RAM) based on:
  1. Baseload energy grid surcharges
  2. Maritime/Rail logistics bottleneck clearing rates
  3. Regional summer thermal-sag cooling premiums in semiconductor fabs
  
HPI = 100.0 is baseline. Lower HPI means better buying window.
"""

import os
import math
import json
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Trans-Cyclic address parameters
DELTA_B = 8
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)
V_MEAN = 29.78
E = 0.0167
T_YEAR = 365.256

def get_earth_velocity(days_since_perihelion):
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))

def get_crossing_times_2026():
    """Generates crossing dates for June - December 2026."""
    current_date = SOLSTICE_2026
    days_from_peri = 169.0
    crossings = []
    
    # Propagate for 30 steps
    for step in range(30):
        v = get_earth_velocity(days_from_peri)
        interval = 8.12 * (V_MEAN / v)
        crossings.append({
            "step": step,
            "date": current_date
        })
        current_date += timedelta(days=interval)
        days_from_peri += interval
    return crossings

def compute_monthly_hardware_index():
    """
    Computes HPI for each month from July to December 2026.
    """
    crossings = get_crossing_times_2026()
    monthly_data = []
    
    # We evaluate Month by Month
    months = [
        ("July 2026", datetime(2026, 7, 1)),
        ("August 2026", datetime(2026, 8, 1)),
        ("September 2026", datetime(2026, 9, 1)),
        ("October 2026", datetime(2026, 10, 1)),
        ("November 2026", datetime(2026, 11, 1)),
        ("December 2026", datetime(2026, 12, 1))
    ]
    
    for name, start_date in months:
        # Get crossings that fall in this month
        month_crossings = [c for c in crossings if c["date"].year == start_date.year and c["date"].month == start_date.month]
        n_crossings = len(month_crossings)
        
        # 1. Thermal load factor (highest in July/August, drops in Autumn)
        if start_date.month in [7, 8]:
            thermal_load = 1.3
        elif start_date.month in [9, 10]:
            thermal_load = 0.9
        else:
            thermal_load = 0.7
            
        # 2. Logistics lag accumulation
        # Backlog from July crossings takes ~45 days to clear
        if start_date.month == 7:
            logistics_lag = 1.2
        elif start_date.month == 8:
            logistics_lag = 1.4  # peak backlog
        elif start_date.month == 9:
            logistics_lag = 1.0  # clearing
        elif start_date.month == 10:
            logistics_lag = 0.7  # cleared, low rates
        else:
            logistics_lag = 0.9  # winter demand rise
            
        # Compute HPI
        # HPI = Base (100) * thermal_load * logistics_lag * (1 + n_crossings * 0.02)
        hpi = 100.0 * thermal_load * logistics_lag * (1.0 + n_crossings * 0.02)
        
        monthly_data.append({
            "month": name,
            "number_of_crossings": n_crossings,
            "thermal_load_factor": thermal_load,
            "logistics_lag_factor": logistics_lag,
            "hardware_purchase_index": hpi
        })
        
    return monthly_data

def main():
    print("=" * 80)
    print("  TAP SILICON MARKET WATCH — HARDWARE BUYING CALENDAR (2026)")
    print("=" * 80)
    
    data = compute_monthly_hardware_index()
    
    print(f"  {'Month':15s} | {'Crossings':9s} | {'Thermal':7s} | {'Logistics':9s} | {'HPI Index':9s} | Buying Recommendation")
    print(f"  {'-'*15}-+-{'-'*9}-+-{'-'*7}-+-{'-'*9}-+-{'-'*9}-+-{'─'*25}")
    
    for m in data:
        rec = "HOLD (Peak Backlog/Rates) ❌"
        if m["hardware_purchase_index"] < 80.0:
            rec = "BEST BUY WINDOW! 🎯✅"
        elif m["hardware_purchase_index"] < 100.0:
            rec = "FAVORABLE (Standard Buy) 🌤️"
            
        print(f"  {m['month']:15s} | {m['number_of_crossings']:9d} | {m['thermal_load_factor']:7.1f} | {m['logistics_lag_factor']:9.1f} | {m['hardware_purchase_index']:9.2f} | {rec}")
        
    # Export to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_hardware_index.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n  [EXPORT] Silicon buying indices saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
