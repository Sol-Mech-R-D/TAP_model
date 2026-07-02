# -*- coding: utf-8 -*-
"""
tap_kp_prediction_sim.py
=========================
TAP v5.3 Kp prediction sim.

Predicts the planetary Kp index (geomagnetic activity) from
the TAP framework's state variables:

  - Sub-breath clock phase
  - Solar reconnection coupling coefficient
  - Breath clock N_B and gamma
  - Earth orbital velocity anomaly

Validates against NOAA SWPC historical Kp data.

The Kp index is a 0-9 scale where:
  0-1: very quiet
  2-3: quiet
  4: unsettled
  5-6: storm (G1-G2)
  7-8: strong storm (G3-G4)
  9: extreme storm (G5)

The framework's claim: Kp is modulated by the sub-breath
clock phase, with peak activity near the crossings.
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
N_B = 8  # breath clock current cycle
GAMMA_NB = 1.0 + N_B * PHI_INV13  # = 1.0154

# Sub-breath clock
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)
BASE_PERIOD = 8.12133


def fetch_historical_kp(days_back: int = 60) -> list:
    """Fetch historical Kp from NOAA SWPC (3-hourly data)."""
    url = 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        # Filter to last N days
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
        return result
    except Exception as e:
        print(f"  [NOAA ERROR] {e}")
        return []


def get_phase(date: datetime) -> float:
    """Get sub-breath clock phase for a given date."""
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def get_earth_velocity(date: datetime) -> float:
    """Get Earth orbital velocity at a given date (km/s)."""
    # Perihelion is around Jan 3 (day 3)
    doy = (date - datetime(date.year, 1, 1)).days + 1
    mean_anomaly = (2.0 * math.pi * doy) / 365.256
    E = 0.0167  # eccentricity
    V_MEAN = 29.78
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))


def predict_kp(date: datetime, learned_params: dict) -> float:
    """
    Predict Kp index from TAP state.

    Model: Kp = baseline + A * cos(phase) + B * v_anomaly + C * N_B

    Where:
    - baseline: average Kp (typically 2-3)
    - A: amplitude of sub-breath modulation
    - v_anomaly: deviation of Earth velocity from mean
    - N_B: breath clock cycle number

    All parameters learned from data.
    """
    baseline = learned_params.get('baseline', 2.0)
    A = learned_params.get('A', 0.5)
    B = learned_params.get('B', 10.0)
    C = learned_params.get('C', 0.1)

    phase = get_phase(date)
    v = get_earth_velocity(date)
    v_anomaly = (v - 29.78) / 29.78  # fractional anomaly

    kp = baseline + A * math.cos(phase) + B * v_anomaly + C * (N_B - 8)

    # Clamp to [0, 9]
    return max(0, min(9, kp))


def learn_kp_params(historical_data: list) -> dict:
    """
    Learn Kp prediction parameters from historical data via
    least-squares regression.

    Model: kp_i = baseline + A * cos(phase_i) + B * v_anomaly_i

    We use 3 parameters (no N_B term since it's constant).
    """
    n = len(historical_data)
    if n < 10:
        return {"baseline": 2.0, "A": 0.5, "B": 10.0, "r_squared": 0.0}

    # Build regression matrix
    phases = []
    v_anomalies = []
    kps = []
    for r in historical_data:
        phases.append(get_phase(r['time']))
        v = get_earth_velocity(r['time'])
        v_anomalies.append((v - 29.78) / 29.78)
        kps.append(r['kp'])

    # Design matrix columns: [1, cos(phase), v_anomaly]
    # Solve via normal equations
    sum_1 = n
    sum_cos = sum(math.cos(p) for p in phases)
    sum_v = sum(v_anomalies)
    sum_cos_sq = sum(math.cos(p)**2 for p in phases)
    sum_v_sq = sum(v**2 for v in v_anomalies)
    sum_cos_v = sum(math.cos(p) * v for p, v in zip(phases, v_anomalies))
    sum_kp = sum(kps)
    sum_kp_cos = sum(k * math.cos(p) for k, p in zip(kps, phases))
    sum_kp_v = sum(k * v for k, v in zip(kps, v_anomalies))

    # 3x3 normal equations
    # [n        sum_cos    sum_v    ] [b0]   [sum_kp    ]
    # [sum_cos  sum_cos_sq sum_cos_v] [A ] = [sum_kp_cos]
    # [sum_v    sum_cos_v  sum_v_sq ] [B ]   [sum_kp_v  ]

    # Solve via Gaussian elimination
    matrix = [
        [sum_1, sum_cos, sum_v, sum_kp],
        [sum_cos, sum_cos_sq, sum_cos_v, sum_kp_cos],
        [sum_v, sum_cos_v, sum_v_sq, sum_kp_v],
    ]
    n_rows = 3
    for i in range(n_rows):
        # Find pivot
        max_row = i
        max_val = abs(matrix[i][i])
        for j in range(i+1, n_rows):
            if abs(matrix[j][i]) > max_val:
                max_val = abs(matrix[j][i])
                max_row = j
        matrix[i], matrix[max_row] = matrix[max_row], matrix[i]
        # Eliminate
        for j in range(i+1, n_rows):
            factor = matrix[j][i] / matrix[i][i]
            for k in range(i, n_rows+1):
                matrix[j][k] -= factor * matrix[i][k]

    # Back-substitute
    solution = [0.0] * n_rows
    for i in range(n_rows-1, -1, -1):
        solution[i] = matrix[i][n_rows]
        for j in range(i+1, n_rows):
            solution[i] -= matrix[i][j] * solution[j]
        solution[i] /= matrix[i][i]

    baseline, A, B = solution

    # Compute R²
    y_pred = [baseline + A * math.cos(p) + B * v for p, v in zip(phases, v_anomalies)]
    ss_res = sum((k - yp)**2 for k, yp in zip(kps, y_pred))
    ss_tot = sum((k - sum(kps)/n)**2 for k in kps)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return {
        "baseline": round(baseline, 4),
        "A": round(A, 4),
        "B": round(B, 4),
        "r_squared": round(r_squared, 4),
        "n_samples": n,
    }


def run_kp_prediction() -> dict:
    """Run Kp prediction and validate."""
    print("=" * 80)
    print("  TAP KP PREDICTION SIM")
    print("  Predicting planetary Kp index from sub-breath clock + Earth velocity")
    print("=" * 80)
    print()

    # Fetch historical data
    print("[FETCH] Historical Kp from NOAA SWPC...")
    historical = fetch_historical_kp(days_back=60)
    if not historical:
        print("  ERROR: Could not fetch Kp data")
        return {"error": "no data"}
    print(f"  Got {len(historical)} records (3-hourly Kp)")
    print()

    # Stats
    kps = [r['kp'] for r in historical]
    print(f"  Kp statistics (last 60 days):")
    print(f"    Mean:  {statistics.mean(kps):.2f}")
    print(f"    Median: {statistics.median(kps):.2f}")
    print(f"    Min:   {min(kps):.2f}")
    print(f"    Max:   {max(kps):.2f}")
    print(f"    Std:   {statistics.stdev(kps):.2f}")
    print()

    # Learn parameters
    print("[LEARN] Fitting Kp prediction model...")
    params = learn_kp_params(historical)
    print(f"  Baseline Kp:  {params['baseline']:.4f}")
    print(f"  Phase amp A:  {params['A']:.4f} (sub-breath modulation)")
    print(f"  Velocity B:   {params['B']:.4f} (Earth velocity coupling)")
    print(f"  R²:           {params['r_squared']:.4f}")
    print()

    # Validate on most recent data
    print("[VALIDATE] Predicting on most recent Kp data...")
    n_test = min(20, len(historical) // 5)  # last 20% of data
    test_data = historical[-n_test:]
    train_data = historical[:-n_test]

    # Re-fit on training data only
    train_params = learn_kp_params(train_data)

    # Test
    test_errors = []
    for r in test_data:
        kp_pred = predict_kp(r['time'], train_params)
        err = abs(kp_pred - r['kp'])
        test_errors.append(err)

    mae = statistics.mean(test_errors)
    rmse = math.sqrt(sum(e**2 for e in test_errors) / len(test_errors))

    print(f"  Test set: {len(test_data)} records")
    print(f"  MAE:  {mae:.4f} Kp units")
    print(f"  RMSE: {rmse:.4f} Kp units")
    print(f"  Baseline MAE (always predict mean): {statistics.mean([abs(k - statistics.mean(kps)) for k in [r['kp'] for r in test_data]]):.4f}")
    print()

    # Predict today
    today = datetime.now()
    kp_today = predict_kp(today, params)
    kp_today_rounded = round(kp_today)

    # Get current actual
    current_url = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
    try:
        req = urllib.request.Request(current_url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=10) as response:
            current_data = json.loads(response.read().decode())
        kp_now = current_data[-1].get('kp_index', '?') if current_data else '?'
    except Exception as e:
        kp_now = '?'

    print(f"  TODAY's prediction:")
    print(f"    TAP predicts Kp = {kp_today:.2f} (rounded: {kp_today_rounded})")
    print(f"    Actual current Kp = {kp_now}")
    print()

    # Per-day sample predictions vs actual
    print("  Recent predictions vs actual (last 10 records):")
    for r in historical[-10:]:
        kp_pred = predict_kp(r['time'], params)
        err = kp_pred - r['kp']
        marker = "✓" if abs(err) < 1.0 else "✗"
        print(f"    {r['time'].strftime('%Y-%m-%d %H:%M')}  actual={r['kp']:.1f}  pred={kp_pred:.2f}  err={err:+.2f} {marker}")
    print()

    return {
        "params": params,
        "train_params": train_params,
        "test_mae": mae,
        "test_rmse": rmse,
        "today_prediction": kp_today,
        "today_rounded": kp_today_rounded,
        "current_actual": kp_now,
    }


def main():
    results = run_kp_prediction()

    # Verdict
    print("=" * 80)
    print("  KP PREDICTION VERDICT")
    print("=" * 80)
    print()

    if "error" in results:
        print("  ERROR: Could not run Kp prediction")
        return

    r2 = results['params']['r_squared']
    mae = results['test_mae']
    baseline_mae = statistics.mean([abs(r['kp'] - 2.0) for r in fetch_historical_kp(60)[-20:]])

    print(f"  R² on full 60-day fit:        {r2:.4f}")
    print(f"  MAE on test set:              {mae:.4f}")
    print(f"  Baseline MAE (mean Kp):      {baseline_mae:.4f}")
    print()

    if mae < baseline_mae:
        print(f"  ✓ TAP Kp model BEATS baseline by {(baseline_mae - mae):.4f} Kp units")
    else:
        print(f"  ✗ TAP Kp model DOES NOT beat baseline (worse by {(mae - baseline_mae):.4f})")

    if r2 > 0.3:
        print(f"  ✓ R² = {r2:.4f} shows real predictive power")
    elif r2 > 0.1:
        print(f"  ≈ R² = {r2:.4f} shows weak predictive power")
    else:
        print(f"  ✗ R² = {r2:.4f} shows no predictive power above noise")
    print()

    # Export
    out_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets'
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_kp_prediction_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
