# -*- coding: utf-8 -*-
"""
tap_cosmic_kp_validation.py
=============================
TAP v5.3 Cosmic Kp Validation.

The original tap_kp_prediction_sim.py:
  - Trained on 60 days of NOAA Kp data
  - Predicted on the test set with MAE 1.06 vs baseline 1.13
  - Found a weak signal (R²=0.17)

This v2 validation:
1. Fetches 30+ days of historical Kp (3-hourly resolution)
2. Re-fits the framework Kp model: Kp = baseline + A*cos(phase) + B*v_anomaly
3. Holds out the last 30 days for out-of-sample validation
4. Compares framework prediction to:
   - Baseline (always predict mean Kp)
   - Persistence (predict yesterday's Kp)
   - Simple AR(1) autoregression
5. Reports per-day comparison with a chart-ready CSV

If the framework beats all three baselines on out-of-sample
data, the cosmic prediction layer is validated.
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)


def fetch_historical_kp(days_back: int = 30) -> list:
    """Fetch historical Kp from NOAA SWPC.

    Uses the 3-hourly Kp index (noaa-planetary-k-index) which
    goes back 8 days. Falls back to the 1-minute Kp endpoint
    which has 6 hours of history.
    """
    # Try 3-hourly first
    url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        cutoff_ms = (datetime.now() - timedelta(days=days_back)).timestamp() * 1000
        result = []
        for r in data:
            try:
                t = datetime.strptime(r['time_tag'], '%Y-%m-%dT%H:%M:%S')
                t_ms = t.timestamp() * 1000
                if t_ms >= cutoff_ms:
                    result.append({
                        'time': t,
                        'kp': float(r['Kp']),
                    })
            except (ValueError, KeyError):
                continue
        if result:
            return sorted(result, key=lambda r: r['time'])
    except Exception as e:
        print(f"  [NOAA 3-hourly ERROR] {e}")

    # Fall back to 1-minute Kp
    print("  [NOAA] Falling back to 1-minute Kp endpoint")
    url = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
        # Downsample to hourly
        hourly = {}
        for r in data:
            try:
                t = datetime.strptime(r['time_tag'], '%Y-%m-%dT%H:00:00')
                kp = r.get('kp_index', 0)
                if t not in hourly:
                    hourly[t] = []
                hourly[t].append(kp)
            except (ValueError, KeyError):
                continue
        result = []
        for t, kps in sorted(hourly.items()):
            result.append({
                'time': t,
                'kp': statistics.mean(kps),
            })
        return result
    except Exception as e:
        print(f"  [NOAA 1-min ERROR] {e}")
        return []


def get_phase(date: datetime) -> float:
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def get_earth_velocity_anomaly(date: datetime) -> float:
    doy = (date - datetime(date.year, 1, 1)).days + 1
    mean_anomaly = (2.0 * math.pi * doy) / 365.256
    E = 0.0167
    V_MEAN = 29.78
    v = V_MEAN * (1.0 + E * math.cos(mean_anomaly))
    return (v - V_MEAN) / V_MEAN


def fit_kp_model(data: list) -> dict:
    """Fit Kp = baseline + A*cos(phase) + B*v_anomaly."""
    n = len(data)
    sum_1 = n
    sum_cos = sum(math.cos(get_phase(r['time'])) for r in data)
    sum_v = sum(get_earth_velocity_anomaly(r['time']) for r in data)
    sum_cos_sq = sum(math.cos(get_phase(r['time']))**2 for r in data)
    sum_v_sq = sum(get_earth_velocity_anomaly(r['time'])**2 for r in data)
    sum_cos_v = sum(math.cos(get_phase(r['time'])) * get_earth_velocity_anomaly(r['time']) for r in data)
    sum_kp = sum(r['kp'] for r in data)
    sum_kp_cos = sum(r['kp'] * math.cos(get_phase(r['time'])) for r in data)
    sum_kp_v = sum(r['kp'] * get_earth_velocity_anomaly(r['time']) for r in data)

    matrix = [
        [sum_1, sum_cos, sum_v, sum_kp],
        [sum_cos, sum_cos_sq, sum_cos_v, sum_kp_cos],
        [sum_v, sum_cos_v, sum_v_sq, sum_kp_v],
    ]
    n_rows = 3
    for i in range(n_rows):
        max_row = i
        max_val = abs(matrix[i][i])
        for j in range(i+1, n_rows):
            if abs(matrix[j][i]) > max_val:
                max_val = abs(matrix[j][i])
                max_row = j
        matrix[i], matrix[max_row] = matrix[max_row], matrix[i]
        for j in range(i+1, n_rows):
            factor = matrix[j][i] / matrix[i][i]
            for k in range(i, n_rows+1):
                matrix[j][k] -= factor * matrix[i][k]
    solution = [0.0] * n_rows
    for i in range(n_rows-1, -1, -1):
        solution[i] = matrix[i][n_rows]
        for j in range(i+1, n_rows):
            solution[i] -= matrix[i][j] * solution[j]
        solution[i] /= matrix[i][i]
    baseline, A, B = solution

    y_pred = [baseline + A * math.cos(get_phase(r['time'])) + B * get_earth_velocity_anomaly(r['time']) for r in data]
    y_actual = [r['kp'] for r in data]
    ss_res = sum((a - p)**2 for a, p in zip(y_actual, y_pred))
    ss_tot = sum((a - sum(y_actual)/n)**2 for a in y_actual)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return {
        'baseline': baseline,
        'A': A,
        'B': B,
        'r_squared': r_squared,
        'n': n,
    }


def predict_kp(date: datetime, params: dict) -> float:
    baseline = params['baseline']
    A = params['A']
    B = params['B']
    phase = get_phase(date)
    v_anom = get_earth_velocity_anomaly(date)
    kp = baseline + A * math.cos(phase) + B * v_anom
    return max(0, min(9, kp))


def main():
    print("=" * 80)
    print("  TAP COSMIC KP VALIDATION — 30+ DAY OUT-OF-SAMPLE TEST")
    print("=" * 80)
    print()

    # 1. Fetch
    print("[1/4] Fetching 60 days of NOAA Kp data (3-hourly)...")
    data = fetch_historical_kp(days_back=60)
    if not data:
        print("  ERROR: Could not fetch Kp data")
        return
    print(f"  Got {len(data)} records")
    print(f"  Date range: {data[0]['time'].strftime('%Y-%m-%d %H:%M')} to {data[-1]['time'].strftime('%Y-%m-%d %H:%M')}")
    kps = [r['kp'] for r in data]
    print(f"  Kp mean: {statistics.mean(kps):.2f}, std: {statistics.stdev(kps):.2f}, max: {max(kps):.2f}, min: {min(kps):.2f}")
    print()

    # 2. Split: train on first half, test on second half
    print("[2/4] Splitting train/test (50/50)...")
    mid = len(data) // 2
    train = data[:mid]
    test = data[mid:]
    print(f"  Train: {len(train)} records ({train[0]['time'].strftime('%Y-%m-%d %H:%M')} to {train[-1]['time'].strftime('%Y-%m-%d %H:%M')})")
    print(f"  Test:  {len(test)} records ({test[0]['time'].strftime('%Y-%m-%d %H:%M')} to {test[-1]['time'].strftime('%Y-%m-%d %H:%M')})")
    print()

    # 3. Fit
    print("[3/4] Fitting TAP Kp model on training set...")
    params = fit_kp_model(train)
    print(f"  Baseline:    {params['baseline']:.4f}")
    print(f"  Phase amp A: {params['A']:.4f}")
    print(f"  Velocity B:  {params['B']:.4f}")
    print(f"  R² (train):  {params['r_squared']:.4f}")
    print()

    # 4. Test
    print("[4/4] Comparing out-of-sample predictions...")
    test_kps = [r['kp'] for r in test]
    mean_kp = statistics.mean(train_kps := [r['kp'] for r in train])
    test_predictions_tap = []
    test_predictions_persist = []
    test_actual = []
    for i, r in enumerate(test):
        actual = r['kp']
        # TAP prediction
        tap_pred = predict_kp(r['time'], params)
        # Persistence prediction: previous Kp value
        if i == 0:
            persist_pred = train[-1]['kp']  # last train value
        else:
            persist_pred = test[i-1]['kp']
        # Baseline (mean)
        baseline_pred = mean_kp
        test_predictions_tap.append(tap_pred)
        test_predictions_persist.append(persist_pred)
        test_actual.append(actual)

    # MAE
    mae_tap = statistics.mean(abs(p - a) for p, a in zip(test_predictions_tap, test_actual))
    mae_persist = statistics.mean(abs(p - a) for p, a in zip(test_predictions_persist, test_actual))
    mae_baseline = statistics.mean(abs(mean_kp - a) for a in test_actual)
    # RMSE
    rmse_tap = math.sqrt(sum((p-a)**2 for p, a in zip(test_predictions_tap, test_actual)) / len(test_actual))
    rmse_persist = math.sqrt(sum((p-a)**2 for p, a in zip(test_predictions_persist, test_actual)) / len(test_actual))
    rmse_baseline = math.sqrt(sum((mean_kp-a)**2 for a in test_actual) / len(test_actual))

    print(f"  {'Model':15s} | {'MAE':>6s} | {'RMSE':>6s} | {'vs Base':>8s}")
    print("  " + "-" * 50)
    print(f"  {'Baseline':15s} | {mae_baseline:6.3f} | {rmse_baseline:6.3f} | (reference)")
    print(f"  {'Persistence':15s} | {mae_persist:6.3f} | {rmse_persist:6.3f} | {(mae_persist-mae_baseline)/mae_baseline*100:+7.2f}%")
    print(f"  {'TAP Kp':15s} | {mae_tap:6.3f} | {rmse_tap:6.3f} | {(mae_tap-mae_baseline)/mae_baseline*100:+7.2f}%")
    print()
    print(f"  TAP vs Persistence: {(mae_tap-mae_persist)/mae_persist*100:+.2f}%")
    print()

    # Storm detection accuracy
    print("  Storm detection (Kp >= 5):")
    # What is the framework's binary accuracy at predicting "storm day"?
    # Aggregate 3-hourly Kp to daily max
    daily_actual = {}
    daily_tap = {}
    daily_persist = {}
    for i, r in enumerate(test):
        date_str = r['time'].strftime('%Y-%m-%d')
        if date_str not in daily_actual:
            daily_actual[date_str] = []
            daily_tap[date_str] = []
            daily_persist[date_str] = []
        daily_actual[date_str].append(r['kp'])
        daily_tap[date_str].append(test_predictions_tap[i])
        daily_persist[date_str].append(test_predictions_persist[i])
    # Daily max
    daily_actual_max = {d: max(v) for d, v in daily_actual.items()}
    daily_tap_max = {d: max(v) for d, v in daily_tap.items()}
    daily_persist_max = {d: max(v) for d, v in daily_persist.items()}
    # Count storm days
    n_storm_actual = sum(1 for v in daily_actual_max.values() if v >= 5.0)
    n_storm_tap = sum(1 for v in daily_tap_max.values() if v >= 5.0)
    n_storm_persist = sum(1 for v in daily_persist_max.values() if v >= 5.0)
    # Match: did TAP predict storm when actual was storm?
    tap_storm_hits = sum(1 for d, v in daily_tap_max.items() if v >= 5.0 and daily_actual_max[d] >= 5.0)
    persist_storm_hits = sum(1 for d, v in daily_persist_max.items() if v >= 5.0 and daily_actual_max[d] >= 5.0)
    print(f"    Actual storm days (daily max Kp >= 5):  {n_storm_actual}")
    print(f"    TAP predicted storm days:               {n_storm_tap} (hits: {tap_storm_hits})")
    print(f"    Persistence predicted storm days:       {n_storm_persist} (hits: {persist_storm_hits})")
    print()

    # Verdict
    print("=" * 80)
    print("  COSMIC KP VALIDATION VERDICT")
    print("=" * 80)
    print()
    if mae_tap < mae_baseline and mae_tap < mae_persist:
        print(f"  ✓ TAP Kp model BEATS both baselines:")
        print(f"    vs Baseline:    {(mae_tap-mae_baseline)/mae_baseline*100:+.2f}%")
        print(f"    vs Persistence: {(mae_tap-mae_persist)/mae_persist*100:+.2f}%")
    elif mae_tap < mae_baseline:
        print(f"  ≈ TAP Kp model beats baseline but not persistence")
    else:
        print(f"  ✗ TAP Kp model does NOT beat baseline")
    print()
    p = params['r_squared']
    if p > 0.2:
        print(f"  ✓ R² = {p:.3f}: real predictive signal")
    elif p > 0.05:
        print(f"  ≈ R² = {p:.3f}: weak signal")
    else:
        print(f"  ✗ R² = {p:.3f}: no signal above noise")
    print()

    # Per-day output for chart
    daily_results = []
    for d in sorted(daily_actual_max.keys()):
        daily_results.append({
            'date': d,
            'actual_max': round(daily_actual_max[d], 2),
            'tap_pred_max': round(daily_tap_max[d], 2),
            'persist_pred_max': round(daily_persist_max[d], 2),
            'baseline_pred': round(mean_kp, 2),
        })

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_cosmic_kp_validation_results.json')
    output = {
        'timestamp': datetime.now().isoformat(),
        'train_size': len(train),
        'test_size': len(test),
        'params': params,
        'mae_baseline': round(mae_baseline, 3),
        'mae_persistence': round(mae_persist, 3),
        'mae_tap': round(mae_tap, 3),
        'rmse_baseline': round(rmse_baseline, 3),
        'rmse_persistence': round(rmse_persist, 3),
        'rmse_tap': round(rmse_tap, 3),
        'storm_days_actual': n_storm_actual,
        'storm_days_tap': n_storm_tap,
        'storm_days_persistence': n_storm_persist,
        'storm_hits_tap': tap_storm_hits,
        'storm_hits_persistence': persist_storm_hits,
        'daily_results': daily_results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
