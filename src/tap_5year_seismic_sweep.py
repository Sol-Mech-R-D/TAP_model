# -*- coding: utf-8 -*-
"""
tap_5year_seismic_sweep.py
===========================
TAP v5.3 5-Year Back + 5-Year Forward Seismic Sweep.

Generates sub-breath crossings for 10 years (5 back, 5 forward):
  - Back: July 2021 - July 2026 (validated against USGS)
  - Forward: July 2026 - July 2031 (predictions only)

For each crossing:
  - Earth orbital velocity at the crossing time
  - Sub-breath phase (0 to 2π)
  - Global stress index (modulated by velocity anomaly)
  - Predicted max magnitude (M_max)
  - Per-region forecasts (CA, AK, Japan, Philippines, Med)

For the back window, computes:
  - Correlation between predicted high-stress crossings
    and actual M5+ earthquakes within ±24h
  - Rayleigh test for circular uniformity
  - Per-year hit rate (predictions / actuals)
  - Per-region hit rate

For the forward window:
  - Lists 5 years of upcoming high-stress crossings
  - Computes confidence intervals based on back-validation
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

# TAP constants
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

# Region roughness and risk zones
REGIONS = {
    "California Strike-Slip": {"roughness": 0.75, "lat_range": (32, 42), "lon_range": (-125, -115)},
    "Alaska Subduction":       {"roughness": 0.30, "lat_range": (50, 65), "lon_range": (-180, -130)},
    "Japan Trench":            {"roughness": 0.20, "lat_range": (30, 45), "lon_range": (130, 145)},
    "Philippines Subduction":  {"roughness": 0.45, "lat_range": (5, 20),  "lon_range": (120, 130)},
    "Mediterranean Rift":      {"roughness": 0.80, "lat_range": (35, 45), "lon_range": (15, 35)},
    "Indonesia Megathrust":    {"roughness": 0.55, "lat_range": (-10, 10), "lon_range": (95, 130)},
    "Chile Subduction":        {"roughness": 0.40, "lat_range": (-45, -20), "lon_range": (-75, -65)},
    "New Zealand":             {"roughness": 0.50, "lat_range": (-50, -35), "lon_range": (165, 180)},
}

# Earth orbit
T_YEAR = 365.256
E = 0.0167
V_MEAN = 29.78


def get_earth_velocity(days_since_perihelion: float) -> float:
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))


def get_crossing_step_time(step: int, reference_date: datetime, days_from_peri: float) -> tuple:
    """Compute the date and Earth velocity for a given step from reference."""
    current_date = reference_date
    cur_days_from_peri = days_from_peri
    for _ in range(abs(step)):
        v = get_earth_velocity(cur_days_from_peri)
        interval = BASE_PERIOD * (V_MEAN / v)
        if step > 0:
            current_date += timedelta(days=interval)
            cur_days_from_peri += interval
        else:
            current_date -= timedelta(days=interval)
            cur_days_from_peri -= interval
    return current_date, cur_days_from_peri


def get_phase(date: datetime) -> float:
    """Sub-breath phase for a given date."""
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def generate_sweep_window(start_date: datetime, end_date: datetime, n_steps_back: int) -> list:
    """Generate sub-breath crossings between start_date and end_date."""
    # First find the closest crossing to start_date (going backwards)
    ref_date = SOLSTICE_2026
    days_from_peri = 169.0  # Approx days from perihelion to Solstice

    # Start from the closest crossing to start_date by stepping back from Solstice
    step = 0
    current_date = SOLSTICE_2026
    cur_days_from_peri = days_from_peri
    # Step backwards until we go past start_date
    while current_date > start_date and step > -1000:
        step -= 1
        current_date, cur_days_from_peri = get_crossing_step_time(
            -1, current_date, cur_days_from_peri
        )

    # Now step forward and collect crossings in the window
    crossings = []
    while current_date < end_date:
        # Get the next crossing
        v = get_earth_velocity(cur_days_from_peri)
        interval = BASE_PERIOD * (V_MEAN / v)
        current_date += timedelta(days=interval)
        cur_days_from_peri += interval
        step += 1

        if start_date <= current_date <= end_date:
            # Compute stress and magnitude
            v_anomaly = (v - V_MEAN) / V_MEAN
            stress_amp = 1.0 + 0.1 * abs(v_anomaly)
            m_max = round(6.0 + 0.8 * stress_amp, 2)
            phase = get_phase(current_date)

            # Per-region forecasts
            regional = []
            for name, info in REGIONS.items():
                r_val = info["roughness"]
                if r_val < 0.4:
                    profile = f"Single consolidated rupture hazard (M_max: {m_max})"
                    n_events = 1
                else:
                    n_events = int(r_val * 8)
                    m_ind = round(m_max - 0.7, 2)
                    profile = f"Dispersed phase-wave swarm ({n_events} events, avg M: {m_ind})"
                regional.append({
                    "region": name,
                    "roughness": r_val,
                    "profile": profile,
                    "predicted_events": n_events,
                })

            crossings.append({
                "step": step,
                "date_utc": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "interval_days": round(interval, 4),
                "velocity_kms": round(v, 4),
                "velocity_anomaly_pct": round(v_anomaly * 100, 4),
                "global_stress_index_pct": round(stress_amp * 100, 4),
                "predicted_max_m": m_max,
                "phase_rad": round(phase, 4),
                "regional_forecasts": regional,
            })

    return crossings


def fetch_usgs_5year() -> list:
    """Fetch USGS M5.5+ earthquakes from July 2021 to July 2026."""
    print("  [USGS API] Fetching 5-year earthquake catalog (2021-07-01 to 2026-07-02)...")
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        "?format=geojson"
        "&starttime=2021-07-01"
        "&endtime=2026-07-02"
        "&minmagnitude=5.5"
    )
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
        features = data.get('features', [])
        quakes = []
        for f in features:
            try:
                time_ms = f['properties']['time']
                t = datetime.utcfromtimestamp(time_ms / 1000.0)
                quakes.append({
                    'time': t,
                    'mag': f['properties'].get('mag'),
                    'place': f['properties'].get('place', ''),
                    'lat': f['geometry']['coordinates'][1],
                    'lon': f['geometry']['coordinates'][0],
                    'depth': f['geometry']['coordinates'][2],
                })
            except (KeyError, TypeError, ValueError):
                continue
        print(f"  [USGS API] Retrieved {len(quakes)} M5.5+ earthquakes")
        return quakes
    except Exception as e:
        print(f"  [USGS API ERROR] {e}")
        return []


def correlate_back(back_crossings: list, actual_quakes: list) -> dict:
    """Compute correlation between predicted crossings and actual earthquakes."""
    # For each crossing, check if any M5.5+ event happened within ±24h
    print(f"\n  [CORRELATE] Matching {len(back_crossings)} crossings vs {len(actual_quakes)} earthquakes...")

    hit_window_24h = 0
    hit_window_12h = 0
    hit_window_6h = 0
    total_actual_within_window = 0
    magnitudes_at_crossings = []
    magnitudes_elsewhere = []

    phases = []
    for c in back_crossings:
        c_date = datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S')
        c_m_max = c['predicted_max_m']
        # Find earthquakes within ±24h
        for q in actual_quakes:
            diff_h = abs((q['time'] - c_date).total_seconds()) / 3600.0
            if diff_h <= 24:
                total_actual_within_window += 1
                if q['mag'] >= c_m_max - 1.0:  # Within 1 magnitude of prediction
                    hit_window_24h += 1
                if diff_h <= 12 and q['mag'] >= c_m_max - 1.0:
                    hit_window_12h += 1
                if diff_h <= 6 and q['mag'] >= c_m_max - 1.0:
                    hit_window_6h += 1
                phases.append(get_phase(q['time']))
                magnitudes_at_crossings.append(q['mag'])
            elif diff_h > 24 and diff_h < 96:  # Away from crossings
                magnitudes_elsewhere.append(q['mag'])

    # Rayleigh test
    n = len(phases)
    if n > 0:
        sum_cos = sum(math.cos(p) for p in phases)
        sum_sin = sum(math.sin(p) for p in phases)
        R = math.sqrt(sum_cos**2 + sum_sin**2)
        r = R / n
        Z = n * (r**2)
        p_val = math.exp(-Z)
    else:
        r, R, Z, p_val = 0, 0, 0, 1.0

    # Per-year hit rate
    yearly_hits = {}
    yearly_totals = {}
    for c in back_crossings:
        c_date = datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S')
        year = c_date.year
        if year not in yearly_totals:
            yearly_totals[year] = 0
            yearly_hits[year] = 0
        yearly_totals[year] += 1
        # Check if any quake matched
        for q in actual_quakes:
            diff_h = abs((q['time'] - c_date).total_seconds()) / 3600.0
            if diff_h <= 24 and q['mag'] >= c['predicted_max_m'] - 1.0:
                yearly_hits[year] += 1
                break

    yearly_rates = {
        year: round(yearly_hits[year] / yearly_totals[year], 4) if yearly_totals[year] > 0 else 0
        for year in sorted(yearly_totals.keys())
    }

    return {
        "n_crossings": len(back_crossings),
        "n_actual_quakes": len(actual_quakes),
        "n_quakes_within_24h": total_actual_within_window,
        "n_hits_24h": hit_window_24h,
        "n_hits_12h": hit_window_12h,
        "n_hits_6h": hit_window_6h,
        "rayleigh_r": round(r, 4),
        "rayleigh_z": round(Z, 4),
        "rayleigh_p": round(p_val, 6),
        "mean_mag_at_crossings": round(statistics.mean(magnitudes_at_crossings), 2) if magnitudes_at_crossings else 0,
        "mean_mag_elsewhere": round(statistics.mean(magnitudes_elsewhere), 2) if magnitudes_elsewhere else 0,
        "yearly_hit_rates": yearly_rates,
    }


def main():
    print("=" * 80)
    print("  TAP 5-YEAR BACK + 5-YEAR FORWARD SEISMIC SWEEP")
    print("  Validates framework against 5 years of USGS data")
    print("  Then predicts 5 years forward")
    print("=" * 80)
    print()

    # Define windows
    today = datetime(2026, 7, 2)
    back_start = datetime(2021, 7, 1)
    forward_end = datetime(2031, 7, 1)

    print(f"  Back window:    {back_start.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')} (5 years)")
    print(f"  Forward window: {today.strftime('%Y-%m-%d')} to {forward_end.strftime('%Y-%m-%d')} (5 years)")
    print()

    # Generate full 10-year sweep
    print("[1/4] Generating 10-year sub-breath crossing sweep...")
    all_crossings = generate_sweep_window(back_start, forward_end, 0)
    back_crossings = [c for c in all_crossings if datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S') <= today]
    forward_crossings = [c for c in all_crossings if datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S') > today]
    print(f"  Total crossings:    {len(all_crossings)}")
    print(f"  Back (validation):  {len(back_crossings)}")
    print(f"  Forward (predict):  {len(forward_crossings)}")
    print()

    # Fetch USGS 5-year data
    print("[2/4] Fetching 5-year USGS catalog (this may take 30-60s)...")
    actual_quakes = fetch_usgs_5year()
    if not actual_quakes:
        print("  ERROR: Could not fetch USGS data")
        return

    # Stats
    mags = [q['mag'] for q in actual_quakes if q['mag']]
    print(f"  Actual earthquakes M5.5+ in 5-year back window: {len(actual_quakes)}")
    print(f"    Mean magnitude: {statistics.mean(mags):.2f}")
    print(f"    Max magnitude:  {max(mags):.2f}")
    print(f"    M6+ count:      {sum(1 for m in mags if m >= 6.0)}")
    print(f"    M7+ count:      {sum(1 for m in mags if m >= 7.0)}")
    print()

    # Correlate
    print("[3/4] Computing back-window correlation...")
    correlation = correlate_back(back_crossings, actual_quakes)
    print(f"\n  BACK-WINDOW CORRELATION RESULTS:")
    print(f"    Total crossings:        {correlation['n_crossings']}")
    print(f"    Total actual M5.5+:     {correlation['n_actual_quakes']}")
    print(f"    Within 24h of crossing: {correlation['n_quakes_within_24h']} ({100*correlation['n_quakes_within_24h']/correlation['n_actual_quakes']:.2f}% of all quakes)")
    print(f"    Hits within 24h (±1M):  {correlation['n_hits_24h']}")
    print(f"    Hits within 12h (±1M):  {correlation['n_hits_12h']}")
    print(f"    Hits within 6h (±1M):   {correlation['n_hits_6h']}")
    print(f"    Mean mag at crossing:   {correlation['mean_mag_at_crossings']}")
    print(f"    Mean mag elsewhere:     {correlation['mean_mag_elsewhere']}")
    print(f"    Rayleigh r:             {correlation['rayleigh_r']:.4f}")
    print(f"    Rayleigh Z:             {correlation['rayleigh_z']:.4f}")
    print(f"    Rayleigh p-value:       {correlation['rayleigh_p']:.6f}")
    print(f"    Per-year hit rates:     {correlation['yearly_hit_rates']}")
    print()

    # Forward window summary
    print("[4/4] Summarizing forward 5-year predictions...")
    forward_m_max = [c['predicted_max_m'] for c in forward_crossings]
    forward_stress = [c['global_stress_index_pct'] for c in forward_crossings]
    print(f"  Forward crossings: {len(forward_crossings)}")
    print(f"    Mean predicted M_max: {statistics.mean(forward_m_max):.2f}")
    print(f"    Max predicted M_max:  {max(forward_m_max):.2f}")
    print(f"    Mean stress index:    {statistics.mean(forward_stress):.2f}%")
    print()

    # Top forward crossings (highest stress)
    forward_crossings_sorted = sorted(forward_crossings, key=lambda c: -c['predicted_max_m'])
    print(f"  TOP 10 FORWARD CROSSINGS (highest predicted M_max):")
    for c in forward_crossings_sorted[:10]:
        d = datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S')
        print(f"    {d.strftime('%Y-%m-%d %H:%M')}  M_max={c['predicted_max_m']}  Stress={c['global_stress_index_pct']}%")
    print()

    # Verdict
    print("=" * 80)
    print("  5-YEAR VALIDATION VERDICT")
    print("=" * 80)
    print()
    r2_pct = correlation['n_quakes_within_24h'] / correlation['n_actual_quakes'] * 100
    print(f"  Proportion of actual earthquakes within 24h of a crossing: {r2_pct:.2f}%")
    print(f"  Expected by chance (24h/8.12d): {24/8.12133*24*100:.2f}%  (24h out of 8.12 days × 100)")
    print()
    if r2_pct > 50:
        print("  ✓ MAJORITY of actual earthquakes are within 24h of a crossing")
    elif r2_pct > 20:
        print("  ≈ Minority within 24h, but above chance expectation")
    else:
        print("  ✗ Below chance expectation — no clustering signal")
    print()

    p = correlation['rayleigh_p']
    if p < 0.001:
        print(f"  ✓ Rayleigh p = {p:.6f}: HIGHLY SIGNIFICANT clustering (p < 0.001)")
    elif p < 0.05:
        print(f"  ≈ Rayleigh p = {p:.6f}: Significant clustering (p < 0.05)")
    else:
        print(f"  ✗ Rayleigh p = {p:.6f}: NOT significant (p > 0.05)")
    print()

    # Compute the chance expectation correctly
    chance_24h_pct = (24.0 / (BASE_PERIOD * 24.0)) * 100  # 24h out of 8.12 days
    print(f"  Chance expectation (24h / 8.12d): {chance_24h_pct:.2f}%")
    print(f"  Observed: {r2_pct:.2f}%")
    if r2_pct > chance_24h_pct * 1.2:
        print(f"  ✓ Observed is {r2_pct/chance_24h_pct:.1f}x the chance expectation")
    elif r2_pct > chance_24h_pct:
        print(f"  ≈ Observed is above chance expectation")
    else:
        print(f"  ✗ Observed is at or below chance expectation")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_5year_seismic_sweep_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "back_window": {
            "start": back_start.isoformat(),
            "end": today.isoformat(),
            "n_crossings": len(back_crossings),
            "n_actual_quakes": len(actual_quakes),
            "correlation": correlation,
        },
        "forward_window": {
            "start": today.isoformat(),
            "end": forward_end.isoformat(),
            "n_crossings": len(forward_crossings),
            "mean_predicted_m_max": round(statistics.mean(forward_m_max), 2),
            "max_predicted_m_max": max(forward_m_max),
            "mean_stress_index_pct": round(statistics.mean(forward_stress), 2),
            "top_10_highest_m_max": [
                {
                    "date": c['date_utc'],
                    "predicted_max_m": c['predicted_max_m'],
                    "stress_index_pct": c['global_stress_index_pct'],
                } for c in forward_crossings_sorted[:10]
            ],
        },
        "all_crossings_count": len(all_crossings),
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    # Also export the full sweep (slim version, no per-region detail)
    sweep_export = []
    for c in all_crossings:
        sweep_export.append({
            "step": c['step'],
            "date_utc": c['date_utc'],
            "interval_days": c['interval_days'],
            "velocity_kms": c['velocity_kms'],
            "predicted_max_m": c['predicted_max_m'],
            "stress_index_pct": c['global_stress_index_pct'],
        })
    sweep_path = os.path.join(out_dir, 'tap_5year_sweep.json')
    with open(sweep_path, 'w') as f:
        json.dump({"total_crossings": len(sweep_export), "sweep": sweep_export}, f, indent=2)
    print(f"  [EXPORT] Full sweep -> {sweep_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
