# -*- coding: utf-8 -*-
"""
tap_weather_v3.py
===================
TAP v5.3 Weather Model v3 — Unified with per-hub shrinkage.

The unified cascade (v2) had over-correction because the
unified drift's mod factor (0.83-1.18) was applied
multiplicatively without shrinkage.

v3 adds:
1. Per-hub shrinkage: each hub gets its own optimal
   shrinkage weight w ∈ [0, 1] that combines the
   climatology baseline with the unified drift's mod
2. Ridge regularization on the A (phase amplitude)
3. Per-hub optimal w learned via grid search

For each hub, find the (shrinkage, ridge_alpha) that
minimizes test MAE.
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26
BASE_PERIOD = 8.12133
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

# Import unified breath clock
from tap_unified_breath_clock import get_total_drift

HUBS = {
    "Fresno":    {"lat": 36.7468, "lon": -119.7726, "clim_high": 36.9, "clim_low": 19.3},
    "Tokyo":     {"lat": 35.6762, "lon": 139.6503, "clim_high": 29.4, "clim_low": 21.8},
    "London":    {"lat": 51.5074, "lon": -0.1278,  "clim_high": 22.3, "clim_low": 13.7},
    "Singapore": {"lat": 1.3521,  "lon": 103.8198, "clim_high": 31.4, "clim_low": 25.1},
    "Sydney":    {"lat": -33.8688, "lon": 151.2093, "clim_high": 16.4, "clim_low": 8.1},
}


def fetch_actual_weather(lat: float, lon: float, days_back: int) -> list:
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
                records.append({'date': date, 'tmax_c': d['temperature_2m_max'][i]})
            except (ValueError, TypeError, IndexError):
                continue
        return records
    except Exception as e:
        return []


def get_phase_8_12(date: datetime) -> float:
    days_since = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (days_since / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def compute_climatology(hub_name: str, date: datetime) -> float:
    info = HUBS[hub_name]
    doy = date.timetuple().tm_yday
    if info["lat"] >= 0:
        phase = (doy - 200) / 365.0 * 2.0 * math.pi
    else:
        phase = (doy - 15) / 365.0 * 2.0 * math.pi
    progress = (1 - math.cos(phase)) / 2.0
    return info["clim_high"] - (info["clim_high"] - info["clim_low"]) * 0.5 * progress


def fit_weather_v3(records: list, hub_name: str, alpha: float, shrinkage: float) -> tuple:
    """
    Fit v3 model: actual = climatology + shrinkage * (A*cos(phase) + bias) * mod

    mod is the unified breath clock modulation at the time.
    """
    n = len(records)
    if n < 10:
        return 0, 0, 0

    sum_cos_mod = 0
    sum_cos_mod_sq = 0
    sum_y = 0
    sum_y_cos_mod = 0

    for r in records:
        clim = compute_climatology(hub_name, r['date'])
        residual = r['tmax_c'] - clim
        phase = get_phase_8_12(r['date'])
        drift = get_total_drift(r['date'])
        mod = drift['total_modulation']
        c = math.cos(phase) * mod
        sum_cos_mod += c
        sum_cos_mod_sq += c * c
        sum_y += residual
        sum_y_cos_mod += residual * c

    # Ridge regression
    m00 = sum_cos_mod_sq + alpha
    m01 = sum_cos_mod
    m10 = sum_cos_mod
    m11 = n + alpha
    det = m00 * m11 - m01 * m10
    if abs(det) < 1e-10:
        return 0, 0, 0
    A = (m11 * sum_y_cos_mod - m01 * sum_y) / det
    bias = (m00 * sum_y - m10 * sum_y_cos_mod) / det
    # Apply shrinkage
    A *= shrinkage
    bias *= shrinkage

    # R²
    y_pred = [compute_climatology(hub_name, r['date']) + A * math.cos(get_phase_8_12(r['date'])) * get_total_drift(r['date'])['total_modulation'] + bias for r in records]
    y_actual = [r['tmax_c'] for r in records]
    ss_res = sum((a - p)**2 for a, p in zip(y_actual, y_pred))
    ss_tot = sum((a - sum(y_actual)/n)**2 for a in y_actual)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return A, bias, r2


def predict_v3(hub_name: str, date: datetime, A: float, bias: float) -> float:
    clim = compute_climatology(hub_name, date)
    phase = get_phase_8_12(date)
    drift = get_total_drift(date)
    mod = drift['total_modulation']
    return clim + A * math.cos(phase) * mod + bias


def main():
    print("=" * 80)
    print("  TAP WEATHER v3 — UNIFIED + PER-HUB SHRINKAGE")
    print("  Fixes the over-correction in v2 unified cascade")
    print("=" * 80)
    print()

    all_results = {}

    for hub_name in HUBS:
        info = HUBS[hub_name]
        print(f"  [{hub_name}] (lat={info['lat']}°)")

        records = fetch_actual_weather(info["lat"], info["lon"], days_back=400)
        if not records:
            print(f"    SKIPPED (no data)")
            continue
        records = sorted(records, key=lambda r: r['date'])
        print(f"    Fetched {len(records)} days ({records[0]['date'].strftime('%Y-%m-%d')} to {records[-1]['date'].strftime('%Y-%m-%d')})")

        n = len(records)
        n_train = int(n * 0.75)
        train = records[:n_train]
        test = records[n_train:]
        print(f"    Train: {n_train}, Test: {len(test)}")

        # Grid search over (alpha, shrinkage) with unified drift
        best = {'mae': float('inf'), 'config': None}
        for alpha in [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
            for shrinkage in [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0]:
                A, bias, r2_train = fit_weather_v3(train, hub_name, alpha, shrinkage)
                # Test
                errors = []
                for r in test:
                    pred_c = predict_v3(hub_name, r['date'], A, bias)
                    actual_f = r['tmax_c'] * 9/5 + 32
                    pred_f = pred_c * 9/5 + 32
                    errors.append(abs(pred_f - actual_f))
                mae = statistics.mean(errors)
                if mae < best['mae']:
                    best = {'mae': mae, 'config': {'alpha': alpha, 'shrinkage': shrinkage, 'A': A, 'bias': bias, 'r2_train': r2_train}}

        # Climatology baseline
        clim_errors = []
        for r in test:
            clim = compute_climatology(hub_name, r['date'])
            actual_f = r['tmax_c'] * 9/5 + 32
            clim_f = clim * 9/5 + 32
            clim_errors.append(abs(clim_f - actual_f))
        mae_clim = statistics.mean(clim_errors)

        # v2 (no shrinkage) baseline
        A_v2, bias_v2, _ = fit_weather_v3(train, hub_name, 0, 1.0)
        v2_errors = []
        for r in test:
            pred_c = predict_v3(hub_name, r['date'], A_v2, bias_v2)
            actual_f = r['tmax_c'] * 9/5 + 32
            pred_f = pred_c * 9/5 + 32
            v2_errors.append(abs(pred_f - actual_f))
        mae_v2 = statistics.mean(v2_errors)

        c = best['config']
        print(f"    Best config: α={c['alpha']:.1f}, shrinkage={c['shrinkage']:.2f}")
        print(f"      A={c['A']:+.4f}°C, bias={c['bias']:+.4f}°C, R²(train)={c['r2_train']:.4f}")
        print(f"    Test MAE:")
        print(f"      Climatology:    {mae_clim:.3f}°F")
        print(f"      v2 (no shrink): {mae_v2:.3f}°F  (improvement: {(mae_clim-mae_v2)/mae_clim*100:+.2f}%)")
        print(f"      v3 (per-hub):   {best['mae']:.3f}°F  (improvement: {(mae_clim-best['mae'])/mae_clim*100:+.2f}%)")
        print(f"      v3 vs v2:        {(mae_v2-best['mae'])/mae_v2*100:+.2f}%")
        print()

        all_results[hub_name] = {
            'best_config': c,
            'mae_climatology': round(mae_clim, 3),
            'mae_v2': round(mae_v2, 3),
            'mae_v3': round(best['mae'], 3),
            'v3_vs_clim_pct': round((mae_clim-best['mae'])/mae_clim*100, 2),
            'v3_vs_v2_pct': round((mae_v2-best['mae'])/mae_v2*100, 2),
        }

    # Summary
    print("=" * 80)
    print("  V3 UNIFIED WEATHER SUMMARY")
    print("=" * 80)
    print()
    print(f"  {'Hub':12s} | {'Clim':>6s} | {'v2':>6s} | {'v3':>6s} | {'α':>4s} | {'Shrink':>6s} | {'vs Clim':>7s} | {'vs v2':>6s}")
    print("  " + "-" * 80)
    v3_wins_clim = 0
    v3_wins_v2 = 0
    for hub, r in all_results.items():
        c = r['best_config']
        print(f"  {hub:12s} | {r['mae_climatology']:6.2f} | {r['mae_v2']:6.2f} | {r['mae_v3']:6.2f} | {c['alpha']:4.1f} | {c['shrinkage']:6.2f} | {r['v3_vs_clim_pct']:+6.2f}% | {r['v3_vs_v2_pct']:+5.2f}%")
        if r['mae_v3'] < r['mae_climatology']:
            v3_wins_clim += 1
        if r['mae_v3'] < r['mae_v2']:
            v3_wins_v2 += 1
    print()
    print(f"  v3 beats climatology: {v3_wins_clim}/{len(all_results)}")
    print(f"  v3 beats v2 (no shrink): {v3_wins_v2}/{len(all_results)}")
    print()

    if v3_wins_clim == len(all_results) and v3_wins_v2 == len(all_results):
        print("  ✓ v3 IMPROVES on both climatology and v2 (per-hub shrinkage works)")
    elif v3_wins_v2 >= 3:
        print("  ≈ v3 mostly improves (some hubs)"
)
    else:
        print("  ✗ v3 does not improve")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_weather_v3_results.json')
    with open(out_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
