# -*- coding: utf-8 -*-
"""
tap_global_weather.py
=====================
Queries the Open-Meteo API for 5 major global operational hubs:
  1. Fresno, USA (Agriculture & West Coast Grid - Lat 36.75, Lon -119.77)
  2. Tokyo, Japan (Tech Manufacturing & East Asia Grid - Lat 35.68, Lon 139.69)
  3. London, UK (Finance & European ENTSO-E Grid - Lat 51.51, Lon -0.13)
  4. Singapore (Maritime Logistics & Choke Point - Lat 1.35, Lon 103.82)
  5. Sydney, Australia (Southern Hemisphere Logistics & Grid - Lat -33.87, Lon 151.21)

Applies latitude-dependent magnetospheric coupling to simulate global temperature
modulations and operations under the TAP model.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import math
import json
import urllib.request
from datetime import datetime, timedelta

from science_constants import PHI, GAMMA_BREATH

# ─── TAP Constants ──────────────────────────────────────────────────────────
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133 * GAMMA_BREATH  # Dynamic sub-breath period modulated by central Breath Clock

# ─── Earth Orbit Constants ───────────────────────────────────────────────────
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)
V_MEAN = 29.78
E = 0.0167
T_YEAR = 365.256

# ─── Global Hub Configurations ───────────────────────────────────────────────
HUBS = {
    "Fresno": {"lat": 36.7468, "lon": -119.7726, "clim_high": 36.9, "clim_low": 19.3, "notes": "Agriculture & West Grid"},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503, "clim_high": 29.4, "clim_low": 21.8, "notes": "Tech Manufacturing & East Asia Grid"},
    "London": {"lat": 51.5074, "lon": -0.1278, "clim_high": 22.3, "clim_low": 13.7, "notes": "Finance & ENTSO-E Grid"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "clim_high": 31.4, "clim_low": 25.1, "notes": "Maritime Shipping Choke Point"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "clim_high": 16.4, "clim_low": 8.1, "notes": "Southern Hemisphere / Winter Grid"}
}

def get_earth_velocity(days_since_perihelion):
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))

def get_crossing_times():
    """Generates crossings for July 2026."""
    current_date = SOLSTICE_2026
    days_from_peri = 169.0
    crossings = []
    
    # Run 15 steps forwards to cover July
    for step in range(15):
        v = get_earth_velocity(days_from_peri)
        interval = BASE_PERIOD * (V_MEAN / v)
        if current_date >= datetime(2026, 6, 20):
            crossings.append({
                "step": step,
                "date": current_date
            })
        current_date += timedelta(days=interval)
        days_from_peri += interval
    return crossings

def fetch_global_forecasts():
    """Queries Open-Meteo for all 5 operational hubs in a single API call."""
    lats = ",".join(str(info["lat"]) for info in HUBS.values())
    lons = ",".join(str(info["lon"]) for info in HUBS.values())
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lats}&longitude={lons}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto"
        f"&forecast_days=14"
    )
    print(f"  [Weather API] Fetching global forecasts for 5 hubs...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        return data
    except Exception as e:
        print(f"  [WARNING] Open-Meteo multi-city query failed: {e}. Using climatology fallbacks.")
        return None

def main():
    print("=" * 80)
    print("  TAP GLOBAL WEATHER ENGINE — 5 OPERATIONAL HUBS")
    print("=" * 80)
    
    raw_data = fetch_global_forecasts()
    crossings = get_crossing_times()
    start_date = datetime(2026, 7, 1)
    
    global_results = {}
    
    # Process each city
    for idx, (city_name, city_info) in enumerate(HUBS.items()):
        print(f"\n  [PROCESSING] {city_name} ({city_info['notes']})")
        
        # Open-Meteo multi-result indexing
        if isinstance(raw_data, list) and idx < len(raw_data):
            daily_data = raw_data[idx].get("daily", {})
        elif isinstance(raw_data, dict) and "daily" in raw_data:
            daily_data = raw_data.get("daily", {})
        else:
            daily_data = {}
            
        api_dates = daily_data.get("time", [])
        api_max = daily_data.get("temperature_2m_max", [])
        api_min = daily_data.get("temperature_2m_min", [])
        
        # Calculate magnetospheric sensitivity based on latitude
        lat_rad = math.radians(city_info["lat"])
        magneto_sensitivity = 0.015 * (1.0 + 0.5 * abs(math.sin(lat_rad)))
        print(f"    Latitude: {city_info['lat']}° | Magnetospheric Sensitivity: {magneto_sensitivity*100:.3f}%")
        
        july_days = []
        for i in range(31):
            day = start_date + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            
            # Base temp selection
            if day_str in api_dates:
                day_idx = api_dates.index(day_str)
                base_max = api_max[day_idx]
                base_min = api_min[day_idx]
                source = "API Forecast"
            else:
                # Summer progression (winter progression for Southern Hemisphere!)
                prog = (i / 31.0) * 1.5
                if city_info["lat"] < 0:
                    base_max = city_info["clim_high"] - prog
                    base_min = city_info["clim_low"] - (prog * 0.5)
                else:
                    base_max = city_info["clim_high"] + prog
                    base_min = city_info["clim_low"] + (prog * 0.5)
                source = "Climatology"
                
            # TAP phase modulation
            closest_crossing = min(crossings, key=lambda c: abs((day - c["date"]).total_seconds()))
            diff_days = (day - closest_crossing["date"]).total_seconds() / 86400.0
            phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
            
            # Apply coupling
            tap_max = base_max * (1.0 + magneto_sensitivity * math.cos(phase))
            tap_min = base_min * (1.0 + (magneto_sensitivity * 0.7) * math.cos(phase))
            
            # Convert to Fahrenheit for standard readability
            base_max_f = base_max * 9.0 / 5.0 + 32.0
            base_min_f = base_min * 9.0 / 5.0 + 32.0
            tap_max_f = tap_max * 9.0 / 5.0 + 32.0
            tap_min_f = tap_min * 9.0 / 5.0 + 32.0
            
            anomaly = "Normal"
            if abs(tap_max_f - base_max_f) > 1.2:
                if tap_max_f > base_max_f:
                    anomaly = "TAP Peak (High Pressure Lock) ☀️"
                else:
                    anomaly = "TAP Dip (Debye Screen Cool) 🌤️"
                    
            july_days.append({
                "date": day_str,
                "source": source,
                "base_max_f": round(base_max_f, 2),
                "base_min_f": round(base_min_f, 2),
                "tap_max_f": round(tap_max_f, 2),
                "tap_min_f": round(tap_min_f, 2),
                "diff_f": round(tap_max_f - base_max_f, 2),
                "anomaly": anomaly
            })
            
        global_results[city_name] = july_days
        
        # Display short summary
        print(f"    {'Date':10s} | {'Base Max (°F)':>14} | {'TAP Max (°F)':>12} | {'Anomaly'}")
        print(f"    {'-'*10}-+-{'-'*14}-+-{'-'*12}-+-{'-'*30}")
        for day in july_days[::6]:
            print(f"    {day['date']:10s} | {day['base_max_f']:14.1f} | {day['tap_max_f']:12.1f} | {day['anomaly']}")
            
    # Export results
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_global_weather_results.json")
    
    with open(out_path, "w") as f:
        json.dump(global_results, f, indent=2)
        
    print(f"\n  [EXPORT] Global weather results saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
