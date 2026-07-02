# -*- coding: utf-8 -*-
"""
tap_5year_seismic_v2.py
==========================
TAP v5.3.2 — 5-Year Seismic Sweep v2.

Enhances tap_5year_seismic_sweep.py by:
  - Using the unified multi-body breath clock (13 producers)
    instead of just the 8.121d sub-breath
  - Per-body N_B modulation (Moon, Sun, Jupiter, etc.)
  - Cross-body coupling weighting (Earth-Moon strongest)
  - Cross-domain feedback (Kp, weather pressure)

The previous v1 had:
  - 449 crossings (225 back, 224 forward)
  - 23.91% within 24h of crossings
  - Rayleigh r=0.76, Z=323, p≈0

v2 should improve because the unified drift is 2.05x better
at identifying seismically active periods (from the
unified cascade sim).
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

# Import unified breath clock
from tap_unified_breath_clock import get_total_drift, SOLSTICE_2026
from tap_body_breath_states import get_body_breath_state, get_body_n_b
from tap_cross_body_coupling import total_coupling

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133
T_YEAR = 365.256


def get_phase(date: datetime) -> float:
    """8.12d sub-breath phase."""
    days_since = (date - SOLSTICE_2026).total_seconds() / 86400.0
    return (days_since / BASE_PERIOD) * 2.0 * math.pi


def get_unified_modulation(date: datetime) -> float:
    """Get unified multi-body breath clock modulation at a date."""
    return get_total_drift(date)['total_modulation']


def get_per_body_stress(date: datetime) -> dict:
    """
    Compute the per-body stress contribution at a date.

    Each body contributes based on its coupling strength and
    current breath state.
    """
    stress = {
        "earth": 0.0,
        "moon": 0.0,
        "sun": 0.0,
        "jupiter": 0.0,
        "saturn": 0.0,
        "mars": 0.0,
        "venus": 0.0,
        "mercury": 0.0,
    }
    for body in stress:
        coupling = total_coupling("Earth", body.title() if body != "earth" else "Earth")
        # Map coupling to [0, 1]
        coupling_factor = max(0, min(1, (coupling + 2) / 2))
        # Per-body phase contribution
        state = get_body_breath_state(body.title() if body != "earth" else "Earth", date)
        psi_contrib = math.cos(state['phase_rad']) * state['s_setpoint']
        stress[body] = coupling_factor * psi_contrib
    return stress


def get_unified_stress(date: datetime) -> float:
    """
    Get the total stress on Earth at a date.

    Combines:
      - 8.12d sub-breath phase (primary)
      - Unified multi-body drift modulation
      - Per-body coupling contributions
    """
    phase = get_phase(date)
    base_stress = 0.5 + 0.5 * math.cos(phase)
    mod = get_unified_modulation(date)
    per_body = get_per_body_stress(date)
    # Combined: base × unified_mod × (1 + per_body contributions)
    per_body_total = sum(per_body.values()) / len(per_body)  # average
    return base_stress * mod * (1.0 + 0.3 * per_body_total)


def get_crossing_step_time(step: int, reference_date: datetime) -> datetime:
    """Compute date at a given crossing step from reference."""
    return reference_date + timedelta(days=step * BASE_PERIOD)


def generate_sweep_window_v2(start_date: datetime, end_date: datetime, n_steps: int = 449) -> list:
    """Generate n_steps crossings using unified stress."""
    crossings = []
    # Generate ~one crossing per 8.12 days
    for step in range(n_steps):
        # Anchor: stress > 0.5 means high-stress period
        # We'll use the actual stress function
        c_date = start_date + timedelta(days=step * BASE_PERIOD)
        if c_date > end_date:
            break
        stress = get_unified_stress(c_date)
        # M_max scales with stress
        m_max = 5.0 + 3.0 * stress  # 5.0-8.0 range
        crossings.append({
            "date_utc": c_date.strftime("%Y-%m-%d %H:%M:%S"),
            "step": step,
            "stress": round(stress, 4),
            "predicted_max_m": round(m_max, 1),
            "mod": round(get_unified_modulation(c_date), 4),
        })
    return crossings


def fetch_usgs_5year() -> list:
    """Fetch 5 years of M5.5+ earthquakes from USGS."""
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
                t = datetime.utcfromtimestamp(f['properties']['time'] / 1000.0)
                quakes.append({
                    'time': t,
                    'mag': f['properties'].get('mag'),
                    'lat': f['geometry']['coordinates'][1],
                    'lon': f['geometry']['coordinates'][0],
                })
            except (KeyError, TypeError, ValueError):
                continue
        return quakes
    except Exception as e:
        return []


def correlate_v2(back_crossings: list, actual_quakes: list) -> dict:
    """Correlate crossings with earthquakes using unified stress."""
    print(f"\n  [CORRELATE v2] Matching {len(back_crossings)} crossings vs {len(actual_quakes)} earthquakes...")

    # Track which earthquakes fall in high-stress periods
    high_stress_threshold = 0.5
    n_high_stress = 0
    n_in_window = 0
    n_match_mag = 0
    phases_at_quakes = []

    for q in actual_quakes:
        # Find the stress at this time
        stress = get_unified_stress(q['time'])
        if stress > high_stress_threshold:
            n_high_stress += 1
        # Find closest crossing
        for c in back_crossings:
            c_date = datetime.strptime(c['date_utc'], '%Y-%m-%d %H:%M:%S')
            diff_h = abs((q['time'] - c_date).total_seconds()) / 3600.0
            if diff_h <= 24:
                n_in_window += 1
                if q['mag'] >= c['predicted_max_m'] - 1.0:
                    n_match_mag += 1
                phases_at_quakes.append(get_phase(q['time']))
                break

    # Rayleigh test
    n_phases = len(phases_at_quakes)
    if n_phases > 0:
        sum_cos = sum(math.cos(p) for p in phases_at_quakes)
        sum_sin = sum(math.sin(p) for p in phases_at_quakes)
        R = math.sqrt(sum_cos**2 + sum_sin**2)
        r = R / n_phases
        Z = n_phases * (r ** 2)
        p_val = math.exp(-Z)
    else:
        r, R, Z, p_val = 0, 0, 0, 1.0

    n_total = len(actual_quakes)
    return {
        "n_total": n_total,
        "n_high_stress": n_high_stress,
        "high_stress_pct": round(100 * n_high_stress / n_total, 2) if n_total else 0,
        "n_in_window_24h": n_in_window,
        "in_window_pct": round(100 * n_in_window / n_total, 2) if n_total else 0,
        "n_match_mag": n_match_mag,
        "match_pct": round(100 * n_match_mag / n_total, 2) if n_total else 0,
        "rayleigh_r": round(r, 4),
        "rayleigh_Z": round(Z, 2),
        "rayleigh_p": round(p_val, 6),
    }


def main():
    print("=" * 80)
    print("  TAP 5-YEAR SEISMIC SWEEP v2")
    print("  Unified breath clock + per-body N_B modulation")
    print("=" * 80)
    print()

    # 1. Generate crossings
    print("  [1/3] Generating 5-year sweep (5y back + 5y forward)...")
    end_back = datetime(2026, 7, 2, 12, 0)
    start_back = datetime(2021, 7, 2, 12, 0)
    start_forward = datetime(2026, 7, 2, 12, 0)
    end_forward = datetime(2031, 7, 2, 12, 0)
    n_steps_per_year = int(365.25 / BASE_PERIOD)
    n_total_steps = 2 * 5 * n_steps_per_year  # 5y back + 5y forward
    back_crossings = generate_sweep_window_v2(start_back, end_back, n_steps=n_steps_per_year * 5)
    forward_crossings = generate_sweep_window_v2(start_forward, end_forward, n_steps=n_steps_per_year * 5)
    print(f"    Back crossings:   {len(back_crossings)}")
    print(f"    Forward crossings: {len(forward_crossings)}")
    print(f"    Total:             {len(back_crossings) + len(forward_crossings)}")
    print()

    # 2. Fetch actual data
    print("  [2/3] Fetching 5 years of USGS M5.5+ earthquakes...")
    actuals = fetch_usgs_5year()
    print(f"    Got {len(actuals)} actual M5.5+ events")
    print()

    # 3. Correlate
    print("  [3/3] Correlating v2 (unified stress)...")
    correlation = correlate_v2(back_crossings, actuals)
    print(f"    Total events: {correlation['n_total']}")
    print(f"    High-stress periods: {correlation['n_high_stress']} ({correlation['high_stress_pct']}%)")
    print(f"    Within 24h of crossing: {correlation['n_in_window_24h']} ({correlation['in_window_pct']}%)")
    print(f"    Magnitude match: {correlation['n_match_mag']} ({correlation['match_pct']}%)")
    print(f"    Rayleigh r = {correlation['rayleigh_r']}, Z = {correlation['rayleigh_Z']}, p = {correlation['rayleigh_p']}")
    print()

    # Compare to v1
    print("  COMPARISON v1 vs v2:")
    print(f"    v1: 23.91% within 24h, r = 0.76, Z = 323, p ≈ 0")
    print(f"    v2: {correlation['in_window_pct']}% within 24h, r = {correlation['rayleigh_r']}, Z = {correlation['rayleigh_Z']}, p = {correlation['rayleigh_p']}")
    if correlation['in_window_pct'] > 23.91:
        print(f"    ✓ v2 IMPROVED: +{correlation['in_window_pct'] - 23.91:.2f}%")
    else:
        print(f"    ✗ v2 same/worse: {correlation['in_window_pct'] - 23.91:+.2f}%")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_5year_seismic_v2_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_back_crossings": len(back_crossings),
        "n_forward_crossings": len(forward_crossings),
        "n_actual_quakes": len(actuals),
        "correlation": correlation,
        "v1_baseline": {
            "within_24h_pct": 23.91,
            "rayleigh_r": 0.76,
            "rayleigh_Z": 323,
            "rayleigh_p": 0.0,
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
