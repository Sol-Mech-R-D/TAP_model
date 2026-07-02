# -*- coding: utf-8 -*-
"""
tap_weather_backfill.py
=========================
TAP v5.3 Weather Backfill — 6-month out-of-sample test.

The original tap_weather_recalibration.py learned on
60 days of data and validated on the most recent day.
This is a proper backfill test:

1. Fetch 6 months of historical ACTUAL data per hub
2. Use months 1-5 as TRAINING
3. Predict on month 6 (out-of-sample)
4. Compare to:
   - Climatology baseline
   - Old TAP model (constant 0.015 sensitivity)
   - Recalibrated TAP (per-hub amplitude + bias)
5. Report win/loss statistics

This is a real out-of-sample test, not in-sample fitting.
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

# Constants
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

# Hubs
HUBS = {
    "Fresno":    {"lat": 36.7468, "lon": -119.7726, "clim_high": 36.9, "clim_low": 19.3},
    "Tokyo":     {"lat": 35.6762, "lon": 139.6503, "clim_high": 29.4, "clim_low": 21.8},
    "London":    {"lat": 51.5074, "lon": -0.1278,  "clim_high": 22.3, "clim_low": 13.7},
    "Singapore": {"lat": 1.3521,  "lon": 103.8198, "clim_high": 31.4, "clim_low": 25.1},
    "Sydney":    {"lat": -33.8688, "lon": 151.2093, "clim_high": 16.4, "clim_low": 8.1},
}


def fetch_actual_weather(lat: float, lon: float, days_back: int = 200) -> list:
    """Fetch actual weather from Open-Meteo archive."""
    end = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    url = (f'https://archive-api.open-meteo.com/v1/archive'
           f'?latitude={lat}&longitude={lon}'
           f'&start_date={start}&end_date={end}'
           f'&daily=temperature_2m_max,temperature_2m_min'
           f'&timezone=auto')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        d = data['daily']
        records = []
        for i, date_str in enumerate(d['time']):
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                records.append({
                    'date': date,
                    'tmax_c': d['temperature_2m_max'][i],
                    'tmin_c': d['temperature_2m_min'][i],
                    'tmax_f': d['temperature_2m_max'][i] * 9/5 + 32,
                    'tmin_f': d['temperature_2m_min'][i] * 9/5 + 32,
                })
            except (ValueError, TypeError, IndexError):
                continue
        return records
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []


def get_phase(date: datetime) -> float:
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def compute_climatology(hub_name: str, date: datetime) -> float:
    """Compute climatology baseline max temp for a hub on a given date (Celsius)."""
    info = HUBS[hub_name]
    doy = date.timetuple().tm_yday
    if info["lat"] >= 0:
        phase = (doy - 200) / 365.0 * 2.0 * math.pi
    else:
        phase = (doy - 15) / 365.0 * 2.0 * math.pi
    progress = (1 - math.cos(phase)) / 2.0
    base = info["clim_high"] - (info["clim_high"] - info["clim_low"]) * 0.5 * progress
    return base


def predict_climatology(hub_name: str, date: datetime) -> float:
    """Climatology baseline (Celsius)."""
    return compute_climatology(hub_name, date)


def predict_old_tap(hub_name: str, date: datetime) -> float:
    """Old TAP model: climatology * (1 + 0.015 * cos(phase))."""
    info = HUBS[hub_name]
    lat = info["lat"]
    clim = compute_climatology(hub_name, date)
    magneto = 0.015 * (1.0 + 0.5 * abs(math.sin(math.radians(lat))))
    phase = get_phase(date)
    return clim * (1.0 + magneto * math.cos(phase))


def predict_recalibrated(hub_name: str, date: datetime, params: dict) -> float:
    """Recalibrated TAP: climatology + A*cos(phase) + bias."""
    clim = compute_climatology(hub_name, date)
    phase = get_phase(date)
    A = params["A"]
    bias = params["bias"]
    return clim + A * math.cos(phase) + bias


def learn_params(records: list, hub_name: str) -> dict:
    """Learn TAP modulation parameters via least-squares."""
    n = len(records)
    sum_cos = 0
    sum_cos_sq = 0
    sum_y = 0
    sum_y_cos = 0
    for r in records:
        clim = compute_climatology(hub_name, r['date'])
        actual = r['tmax_c']
        residual = actual - clim
        c = math.cos(get_phase(r['date']))
        sum_cos += c
        sum_cos_sq += c**2
        sum_y += residual
        sum_y_cos += residual * c

    det = sum_cos_sq * n - sum_cos**2
    if abs(det) < 1e-10:
        return {"A": 0, "bias": 0, "r_squared": 0}
    A = (n * sum_y_cos - sum_cos * sum_y) / det
    bias = (sum_cos_sq * sum_y - sum_cos * sum_y_cos) / det

    # R²
    y_pred = [A * math.cos(get_phase(r['date'])) + bias + compute_climatology(hub_name, r['date']) for r in records]
    y_actual = [r['tmax_c'] for r in records]
    ss_res = sum((a - p)**2 for a, p in zip(y_actual, y_pred))
    ss_tot = sum((a - sum(y_actual)/n)**2 for a in y_actual)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return {"A": A, "bias": bias, "r_squared": r_squared, "n": n}


def run_backfill():
    print("=" * 80)
    print("  TAP WEATHER BACKFILL — 6-month out-of-sample test")
    print("  Train on months 1-5, test on month 6")
    print("=" * 80)
    print()

    all_results = {}
    for hub_name in HUBS:
        info = HUBS[hub_name]
        print(f"  [{hub_name}] (lat={info['lat']}°)")

        # Fetch ~200 days (~6.5 months)
        records = fetch_actual_weather(info["lat"], info["lon"], days_back=200)
        if not records:
            print(f"    SKIPPED (no data)")
            continue
        records = sorted(records, key=lambda r: r['date'])
        print(f"    Fetched {len(records)} days ({records[0]['date'].strftime('%Y-%m-%d')} to {records[-1]['date'].strftime('%Y-%m-%d')})")

        # Split: 80% train, 20% test (about 5 months train, 1 month test)
        n = len(records)
        n_train = int(n * 0.80)
        train = records[:n_train]
        test = records[n_train:]
        print(f"    Train: {n_train} days, Test: {len(test)} days ({test[0]['date'].strftime('%Y-%m-%d')} to {test[-1]['date'].strftime('%Y-%m-%d')})")

        # Learn params on train
        params = learn_params(train, hub_name)
        print(f"    Learned: A={params['A']:+.4f}°C, bias={params['bias']:+.4f}°C, R²(train)={params['r_squared']:.4f}")

        # Test on test set
        clim_errors = []
        old_tap_errors = []
        recal_errors = []
        for r in test:
            actual_f = r['tmax_f']
            clim_c = predict_climatology(hub_name, r['date'])
            old_tap_c = predict_old_tap(hub_name, r['date'])
            recal_c = predict_recalibrated(hub_name, r['date'], params)
            clim_f = clim_c * 9/5 + 32
            old_tap_f = old_tap_c * 9/5 + 32
            recal_f = recal_c * 9/5 + 32
            clim_errors.append(abs(clim_f - actual_f))
            old_tap_errors.append(abs(old_tap_f - actual_f))
            recal_errors.append(abs(recal_f - actual_f))

        mae_clim = statistics.mean(clim_errors)
        mae_old = statistics.mean(old_tap_errors)
        mae_recal = statistics.mean(recal_errors)
        print(f"    MAE on test set:")
        print(f"      Climatology:    {mae_clim:.3f}°F")
        print(f"      Old TAP:        {mae_old:.3f}°F")
        print(f"      Recalibrated:   {mae_recal:.3f}°F")
        improvement_old = (mae_old - mae_recal) / mae_old * 100
        improvement_clim = (mae_clim - mae_recal) / mae_clim * 100
        print(f"      Recal vs Old:    {improvement_old:+.2f}%")
        print(f"      Recal vs Clim:   {improvement_clim:+.2f}%")
        print()

        all_results[hub_name] = {
            "params": params,
            "n_train": n_train,
            "n_test": len(test),
            "test_mae_climatology": round(mae_clim, 3),
            "test_mae_old_tap": round(mae_old, 3),
            "test_mae_recal": round(mae_recal, 3),
            "improvement_vs_old_pct": round(improvement_old, 2),
            "improvement_vs_climatology_pct": round(improvement_clim, 2),
        }

    # Summary
    print("=" * 80)
    print("  6-MONTH BACKFILL SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Hub':12s} | {'Clim MAE':>10s} | {'Old MAE':>9s} | {'Recal MAE':>10s} | {'vs Old':>7s} | {'vs Clim':>7s}")
    print("  " + "-" * 75)
    recal_wins_old = 0
    recal_wins_clim = 0
    for hub, r in all_results.items():
        print(f"  {hub:12s} | {r['test_mae_climatology']:>10.3f} | {r['test_mae_old_tap']:>9.3f} | {r['test_mae_recal']:>10.3f} | {r['improvement_vs_old_pct']:>+6.2f}% | {r['improvement_vs_climatology_pct']:>+6.2f}%")
        if r['test_mae_recal'] < r['test_mae_old_tap']:
            recal_wins_old += 1
        if r['test_mae_recal'] < r['test_mae_climatology']:
            recal_wins_clim += 1
    print()
    print(f"  Recalibrated beats Old TAP: {recal_wins_old}/{len(all_results)} hubs")
    print(f"  Recalibrated beats Climatology: {recal_wins_clim}/{len(all_results)} hubs")
    print()

    # Verdict
    if recal_wins_clim >= 3 and recal_wins_old >= 3:
        print("  ✓ Recalibration is robust on 6-month out-of-sample test")
    elif recal_wins_clim > recal_wins_old:
        print("  ≈ Recalibration shows weak improvement")
    else:
        print("  ✗ Recalibration is not robust on 6-month out-of-sample test")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_weather_backfill_results.json')
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    run_backfill()
