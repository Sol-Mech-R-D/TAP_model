# -*- coding: utf-8 -*-
"""
tap_fresno_weather.py
======================
Queries the Open-Meteo API for Fresno, California forecast data.
Applies the TAP model's geocosmic weather coupling to simulate Fresno's
temperature and anomaly spikes for July 2026 based on the sub-breath crossings.

Fresno, CA Coordinates: Lat 36.7468, Lon -119.7726
"""

import os
import math
import json
import urllib.request
from datetime import datetime, timedelta

# ─── TAP Constants ──────────────────────────────────────────────────────────
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# ─── Crossing Calendar 2026 ──────────────────────────────────────────────────
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)
V_MEAN = 29.78
E = 0.0167
T_YEAR = 365.256

def get_earth_velocity(days_since_perihelion):
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))

def get_crossing_times():
    """Generates crossings for July 2026."""
    current_date = SOLSTICE_2026
    days_from_peri = 169.0
    crossings = []
    
    # We run 15 steps forwards to cover July
    for step in range(15):
        v = get_earth_velocity(days_from_peri)
        interval = 8.12 * (V_MEAN / v)
        if current_date >= datetime(2026, 6, 20):
            crossings.append({
                "step": step,
                "date": current_date
            })
        current_date += timedelta(days=interval)
        days_from_peri += interval
    return crossings

def get_fresno_forecast():
    """Fetches the 14-day forecast for Fresno from Open-Meteo."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=36.7468&longitude=-119.7726"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=America/Los_Angeles"
        "&forecast_days=14"
    )
    print("  [Weather API] Fetching Fresno 14-day forecast from Open-Meteo...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        daily = data.get("daily", {})
        return daily
    except Exception as e:
        print(f"  [WARNING] Open-Meteo failed: {e}. Using climatology fallback.")
        return None

def main():
    print("=" * 80)
    print("  TAP WEATHER ENGINE — FRESNO, CALIFORNIA (JULY 2026)")
    print("=" * 80)
    
    # 1. Get real weather forecast
    daily = get_fresno_forecast()
    
    # Climatology averages for July in Fresno (typical highs/lows)
    # July is the hottest month in Fresno: average high 98.5 F, average low 66.8 F
    # Convert to Celsius: High 36.9 C, Low 19.3 C
    clim_high = 36.9
    clim_low = 19.3
    
    # 2. Get the crossings list
    crossings = get_crossing_times()
    
    # 3. Simulate July 2026 day-by-day
    start_date = datetime(2026, 7, 1)
    july_days = []
    
    # Fresno API daily data mapping if available
    api_dates = daily.get("time", []) if daily else []
    api_max = daily.get("temperature_2m_max", []) if daily else []
    api_min = daily.get("temperature_2m_min", []) if daily else []
    
    for i in range(31):
        day = start_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        
        # Determine baseline temp
        # Use forecast if within 14 days, otherwise use climatology
        if day_str in api_dates:
            idx = api_dates.index(day_str)
            base_max = api_max[idx]
            base_min = api_min[idx]
            source = "API Forecast"
        else:
            # Add a slight summer heating progression throughout July
            progression = (i / 31.0) * 1.5  # July heats up towards late July
            base_max = clim_high + progression
            base_min = clim_low + (progression * 0.5)
            source = "Climatology"
            
        # 4. Calculate TAP modulation
        # Find closest crossing node
        closest_crossing = min(crossings, key=lambda c: abs((day - c["date"]).total_seconds()))
        diff_days = (day - closest_crossing["date"]).total_seconds() / 86400.0
        
        # Phase angle (8.12 days period)
        phase = (diff_days / 8.12) * 2.0 * math.pi
        
        # Convective temperature coupling
        # Node crossings (phase = 0) trigger minor air subsidence / high-pressure locks in the valley:
        #   T_mod = T_base * (1 + A * cos(phase))
        #   where A ≈ 0.015 (1.5% thermal modulation)
        #   In Fahrenheit this translates to a 2 to 3 degree F shift.
        coupling_max = 0.015
        coupling_min = 0.010
        
        tap_max = base_max * (1.0 + coupling_max * math.cos(phase))
        tap_min = base_min * (1.0 + coupling_min * math.cos(phase))
        
        # Convert to Fahrenheit for user readability
        base_max_f = base_max * 9.0 / 5.0 + 32.0
        base_min_f = base_min * 9.0 / 5.0 + 32.0
        tap_max_f = tap_max * 9.0 / 5.0 + 32.0
        tap_min_f = tap_min * 9.0 / 5.0 + 32.0
        
        # Determine anomaly flags
        anomaly = "Normal"
        if abs(tap_max_f - base_max_f) > 1.2:
            if tap_max_f > base_max_f:
                anomaly = "TAP Peak (High Pressure Lock) ☀️"
            else:
                anomaly = "TAP Dip (Debye Screen Cool) 🌤️"
                
        july_days.append({
            "date": day_str,
            "source": source,
            "base_max_f": base_max_f,
            "base_min_f": base_min_f,
            "tap_max_f": tap_max_f,
            "tap_min_f": tap_min_f,
            "diff_f": tap_max_f - base_max_f,
            "anomaly": anomaly
        })
        
    # Print results summary
    print(f"  Fresno July 2026 Weather Sweep:")
    print(f"  {'Date':10s} | {'Source':12s} | {'Base Max (°F)':>14} | {'TAP Max (°F)':>12} | {'Shift (°F)':>10} | {'Anomaly'}")
    print(f"  {'-'*10}-+-{'-'*12}-+-{'-'*14}-+-{'-'*12}-+-{'-'*10}-+-{'-'*30}")
    
    # Print a selection of July days (every 3rd day to save output space)
    for day in july_days[::3]:
        print(f"  {day['date']:10s} | {day['source']:12s} | {day['base_max_f']:14.1f} | {day['tap_max_f']:12.1f} | {day['diff_f']:+10.1f} | {day['anomaly']}")

    # Export to assets
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_fresno_july2026.json")
    with open(out_path, "w") as f:
        json.dump(july_days, f, indent=2)
    print(f"\n  [EXPORT] Fresno July weather forecast saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
