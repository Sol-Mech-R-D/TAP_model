# -*- coding: utf-8 -*-
"""
tap_per_event_seismic.py
=========================
TAP v5.3 Per-Event Seismic Prediction.

The 1-year sim and 5-year sim predict M_max per crossing
but don't tell us WHICH specific earthquakes will occur.

This sim attempts per-event prediction by:
1. Computing a per-region "stress accumulation" function
   that integrates the sub-breath clock amplitude over time
2. Identifying "candidate events" — windows where the
   accumulated stress exceeds a threshold
3. Estimating the magnitude, location, and time of each
   candidate event

Validates against actual USGS M5+ events in the 5-year
back window (2021-2026).

Outputs:
  - Per-event predictions: time, place, magnitude, probability
  - Per-region accuracy: hit rate, false positive rate
  - Overall precision/recall
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

# TAP constants
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13
BASE_PERIOD = 8.12133
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

# Region definitions: name -> (lat_center, lon_center, roughness, base_mag)
REGIONS = {
    "California Strike-Slip":  {"lat": 35.5, "lon": -120.0, "roughness": 0.75, "base_mag": 5.8, "type": "strike-slip"},
    "Alaska Subduction":        {"lat": 60.0, "lon": -150.0, "roughness": 0.30, "base_mag": 6.5, "type": "subduction"},
    "Japan Trench":             {"lat": 38.0, "lon": 142.0,  "roughness": 0.20, "base_mag": 7.0, "type": "subduction"},
    "Philippines Subduction":   {"lat": 10.0, "lon": 125.0,  "roughness": 0.45, "base_mag": 6.3, "type": "subduction"},
    "Mediterranean Rift":       {"lat": 38.0, "lon": 25.0,   "roughness": 0.80, "base_mag": 5.7, "type": "rift"},
    "Indonesia Megathrust":     {"lat": 0.0,  "lon": 110.0,  "roughness": 0.55, "base_mag": 6.8, "type": "subduction"},
    "Chile Subduction":         {"lat": -35.0, "lon": -72.0,  "roughness": 0.40, "base_mag": 6.5, "type": "subduction"},
    "New Zealand":              {"lat": -42.0, "lon": 173.0,  "roughness": 0.50, "base_mag": 5.9, "type": "subduction"},
    "Mexico Subduction":        {"lat": 16.0, "lon": -98.0,  "roughness": 0.35, "base_mag": 6.2, "type": "subduction"},
    "Iran Fold Belt":           {"lat": 32.0, "lon": 53.0,   "roughness": 0.65, "base_mag": 5.8, "type": "collision"},
}

# Earth orbit
T_YEAR = 365.256
E = 0.0167
V_MEAN = 29.78


def get_earth_velocity(date: datetime) -> float:
    doy = (date - datetime(date.year, 1, 1)).days + 1
    mean_anomaly = (2.0 * math.pi * doy) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))


def get_phase(date: datetime) -> float:
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def stress_at_date(date: datetime, region: dict) -> float:
    """
    Compute the instantaneous stress on a region.
    Stress = phase_amplitude * roughness * velocity_anomaly
    """
    phase = get_phase(date)
    v = get_earth_velocity(date)
    v_anomaly = (v - V_MEAN) / V_MEAN

    # Stress is highest near phase = 0 (crossing) and at high velocity
    phase_stress = 0.5 + 0.5 * math.cos(phase)  # 0 to 1
    velocity_stress = 1.0 + 0.1 * v_anomaly

    return region["roughness"] * phase_stress * velocity_stress


def integrate_stress(start: datetime, end: datetime, region: dict, step_hours: int = 6) -> list:
    """Integrate stress over a time window for a region."""
    n_steps = int((end - start).total_seconds() / (step_hours * 3600))
    stress_series = []
    for i in range(n_steps + 1):
        t = start + timedelta(hours=i * step_hours)
        s = stress_at_date(t, region)
        stress_series.append({'time': t, 'stress': s})
    return stress_series


def predict_events(start: datetime, end: datetime, threshold: float = 0.5) -> list:
    """
    Predict per-event earthquakes in the time window.

    Algorithm:
    1. For each region, compute the stress time series
    2. Find local maxima above the threshold
    3. For each peak, predict:
       - Time: time of peak
       - Magnitude: region.base_mag + (stress - 0.5) * scaling
       - Location: region lat/lon
       - Probability: function of stress value
    """
    predictions = []
    for region_name, info in REGIONS.items():
        series = integrate_stress(start, end, info, step_hours=6)
        # Find local maxima
        for i in range(2, len(series) - 2):
            s = series[i]['stress']
            if s > threshold and s > series[i-1]['stress'] and s > series[i+1]['stress']:
                # Local maximum — predict an event
                # Magnitude scales with stress
                mag = round(info['base_mag'] + (s - 0.5) * 1.5, 2)
                # Probability: function of how much above threshold
                prob = min(1.0, (s - threshold) / (1.0 - threshold))
                predictions.append({
                    'time_utc': series[i]['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'region': region_name,
                    'lat': info['lat'],
                    'lon': info['lon'],
                    'region_type': info['type'],
                    'predicted_magnitude': mag,
                    'stress': round(s, 4),
                    'probability': round(prob, 4),
                })
    return predictions


def fetch_usgs_5year_quakes() -> list:
    """Fetch USGS M5.5+ from 2021-07-01 to 2026-07-02."""
    import urllib.request
    print("  [USGS API] Fetching 5-year catalog...")
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
                })
            except (KeyError, TypeError, ValueError):
                continue
        print(f"  [USGS API] Retrieved {len(quakes)} M5.5+ quakes")
        return quakes
    except Exception as e:
        print(f"  [USGS API ERROR] {e}")
        return []


def match_event(prediction: dict, actuals: list, time_window_h: int = 48, region_radius_deg: float = 15.0) -> bool:
    """Check if a prediction matches an actual event."""
    pred_time = datetime.strptime(prediction['time_utc'], '%Y-%m-%d %H:%M:%S')
    for q in actuals:
        if abs((q['time'] - pred_time).total_seconds()) > time_window_h * 3600:
            continue
        if abs(q['lat'] - prediction['lat']) > region_radius_deg:
            continue
        if abs(q['lon'] - prediction['lon']) > region_radius_deg:
            continue
        return True
    return False


def find_actual_region(quake: dict) -> str:
    """Find which region a quake is closest to."""
    min_dist = float('inf')
    closest = "Unknown"
    for region_name, info in REGIONS.items():
        # Simple lat/lon distance (not accounting for curvature, but good enough)
        d = math.sqrt((quake['lat'] - info['lat'])**2 + (quake['lon'] - info['lon'])**2)
        if d < min_dist:
            min_dist = d
            closest = region_name
    return closest


def main():
    print("=" * 80)
    print("  TAP PER-EVENT SEISMIC PREDICTION")
    print("  Predicting specific earthquakes (time, place, magnitude, probability)")
    print("=" * 80)
    print()

    # Back-window validation
    end_back = datetime(2026, 7, 2)
    start_back = datetime(2021, 7, 1)

    # Forward prediction
    start_forward = end_back
    end_forward = datetime(2026, 8, 2)  # 1 month forward

    # 1. Fetch actuals
    print("[1/5] Fetching 5-year USGS catalog...")
    actuals = fetch_usgs_5year_quakes()
    if not actuals:
        print("  ERROR: Could not fetch USGS data")
        return
    print(f"  Got {len(actuals)} M5.5+ quakes in 5-year back window")
    print()

    # 2. Per-region statistics
    print("[2/5] Per-region actuals (5 years)...")
    region_actuals = {}
    for q in actuals:
        region = find_actual_region(q)
        if region not in region_actuals:
            region_actuals[region] = []
        region_actuals[region].append(q)
    print(f"  {'Region':30s} | {'M5.5+ count':>12s} | {'Mean mag':>9s} | {'Max mag':>8s}")
    print("  " + "-" * 70)
    for region, qs in sorted(region_actuals.items(), key=lambda x: -len(x[1])):
        mags = [q['mag'] for q in qs if q['mag']]
        if mags:
            print(f"  {region:30s} | {len(qs):>12d} | {statistics.mean(mags):>9.2f} | {max(mags):>8.2f}")
    print()

    # 3. Per-event prediction on back window (5 years)
    print("[3/5] Predicting per-event earthquakes (5-year back window)...")
    # Use multiple thresholds
    for threshold in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
        predictions = predict_events(start_back, end_back, threshold=threshold)
        # Match against actuals
        hits = sum(1 for p in predictions if match_event(p, actuals, time_window_h=48, region_radius_deg=15.0))
        precision = hits / len(predictions) * 100 if predictions else 0
        recall = hits / len(actuals) * 100
        print(f"  Threshold {threshold:.2f}: {len(predictions):4d} predictions, {hits:3d} hits, precision={precision:.2f}%, recall={recall:.4f}%")
    print()

    # 4. Pick best threshold and run detailed
    print("[4/5] Detailed analysis at threshold 0.50...")
    predictions = predict_events(start_back, end_back, threshold=0.50)
    hits = [p for p in predictions if match_event(p, actuals, time_window_h=48, region_radius_deg=15.0)]
    misses = [p for p in predictions if not match_event(p, actuals, time_window_h=48, region_radius_deg=15.0)]
    precision = len(hits) / len(predictions) * 100 if predictions else 0
    recall = len(hits) / len(actuals) * 100
    print(f"  Total predictions: {len(predictions)}")
    print(f"  Hits (within 48h, 15°): {len(hits)}")
    print(f"  Misses: {len(misses)}")
    print(f"  Precision: {precision:.2f}%")
    print(f"  Recall:    {recall:.4f}%")
    print(f"  Total actuals: {len(actuals)}")
    print()

    # Per-region hit rate
    print("  Per-region hit rate:")
    print(f"    {'Region':30s} | {'Predictions':>11s} | {'Hits':>4s} | {'Actuals':>7s} | {'Precision':>9s}")
    print("    " + "-" * 75)
    for region in REGIONS.keys():
        preds = [p for p in predictions if p['region'] == region]
        h = sum(1 for p in preds if match_event(p, actuals))
        actual_count = len(region_actuals.get(region, []))
        prec = h / len(preds) * 100 if preds else 0
        print(f"    {region:30s} | {len(preds):>11d} | {h:>4d} | {actual_count:>7d} | {prec:>9.2f}%")
    print()

    # 5. Forward prediction (next 30 days)
    print("[5/5] Forward prediction (next 30 days)...")
    forward = predict_events(start_forward, end_forward, threshold=0.50)
    print(f"  Predicted events in next 30 days: {len(forward)}")
    for p in forward:
        prob_str = f"{p['probability']*100:.1f}%"
        print(f"    {p['time_utc']}  M{p['predicted_magnitude']}  {p['region']:30s}  prob={prob_str}")
    print()

    # Verdict
    print("=" * 80)
    print("  PER-EVENT PREDICTION VERDICT")
    print("=" * 80)
    print()
    p = precision
    r = recall
    if p > 30:
        print(f"  ✓ HIGH precision: {p:.1f}% of predicted events match actuals")
    elif p > 10:
        print(f"  ≈ Moderate precision: {p:.1f}%")
    else:
        print(f"  ✗ Low precision: {p:.1f}% (most predictions are false positives)")
    print(f"  Recall: {r:.2f}% of actual events are predicted")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_per_event_seismic_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "back_window": {
            "start": start_back.isoformat(),
            "end": end_back.isoformat(),
            "n_actuals": len(actuals),
            "n_predictions": len(predictions),
            "n_hits": len(hits),
            "precision_pct": round(precision, 4),
            "recall_pct": round(recall, 4),
        },
        "forward_window": {
            "start": start_forward.isoformat(),
            "end": end_forward.isoformat(),
            "predictions": forward,
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
