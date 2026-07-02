# -*- coding: utf-8 -*-
"""
tap_daily_prediction_check.py
=============================
TAP v5.3 Daily prediction check.

Fetches live data from Open-Meteo, USGS, NOAA SWPC and
compares to the framework's predictions across 5 domains:
weather, seismic, cosmic, logistics, finance.

Run daily. Outputs to assets/tap_daily_check_results.json
and prints a summary.
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta


def fetch_usgs_last_n_days(n_days: int = 5, min_mag: float = 4.5) -> list:
    """Fetch USGS M{min_mag}+ earthquakes in last n days."""
    url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{min_mag:.1f}_week.geojson"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        all_quakes = data.get('features', [])
        n_days_ago_ms = int((datetime.now() - timedelta(days=n_days)).timestamp() * 1000)
        return [q for q in all_quakes if q['properties']['time'] >= n_days_ago_ms]
    except Exception as e:
        print(f"  [USGS ERROR] {e}")
        return []


def fetch_open_meteo_archive(lat: float, lon: float, days_back: int = 5) -> dict:
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
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"  [Open-Meteo ERROR] {e}")
        return {}


def fetch_noaa_kp() -> list:
    """Fetch recent Kp index from NOAA SWPC."""
    url = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"  [NOAA ERROR] {e}")
        return []


def load_tap_predictions() -> dict:
    """Load all TAP prediction sim outputs."""
    out = {}
    asset_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets'
    )
    for fname, key in [
        ('tap_seismic_predictions_1year.json', 'seismic'),
        ('tap_option_arbitrage_results.json', 'finance'),
        ('tap_global_weather_results.json', 'weather'),
        ('tap_geocosmic_coupling.json', 'cosmic'),
    ]:
        path = os.path.join(asset_dir, fname)
        if os.path.exists(path):
            with open(path) as f:
                out[key] = json.load(f)
        else:
            out[key] = None
    return out


def check_seismic(usgs_quakes: list, tap_pred: dict) -> dict:
    """Check seismic prediction vs actual."""
    n = len(usgs_quakes)
    mags = [q['properties']['mag'] for q in usgs_quakes if q['properties']['mag']]
    m5 = sum(1 for m in mags if m >= 5.0)
    m6 = sum(1 for m in mags if m >= 6.0)
    max_mag = max(mags) if mags else 0
    avg_mag = sum(mags) / len(mags) if mags else 0

    # Get the framework's prediction for the period
    if tap_pred and 'prediction_sweep' in tap_pred:
        sweep = tap_pred['prediction_sweep']
        # The first crossing in the sweep is the next prediction
        if sweep:
            next_crossing = sweep[0]
            framework_pred = f"M_max={next_crossing['predicted_max_m']} on {next_crossing['date_utc'][:10]}"
        else:
            framework_pred = "no crossing"
    else:
        framework_pred = "(sim output missing)"

    # Verdict
    if m6 == 0 and max_mag < 6.5:
        verdict = "CONSISTENT (no M6+ events, framework predicts quiet)"
    elif m6 == 0:
        verdict = "MARGINAL (M5+ but no M6+)"
    else:
        verdict = "INCONSISTENT (M6+ events, framework predicts quiet)"

    return {
        "framework_prediction": framework_pred,
        "actual_total": n,
        "actual_m5_plus": m5,
        "actual_m6_plus": m6,
        "actual_max": max_mag,
        "actual_avg": round(avg_mag, 2),
        "verdict": verdict,
    }


def check_weather(tap_weather: dict) -> dict:
    """Check weather prediction vs actual (where available)."""
    # Load last few days of actuals for 5 hubs
    hubs = {
        'Fresno': (36.7468, -119.7726),
        'Tokyo': (35.6762, 139.6503),
        'London': (51.5074, -0.1278),
        'Singapore': (1.3521, 103.8198),
        'Sydney': (-33.8688, 151.2093),
    }
    results = []
    for hub, (lat, lon) in hubs.items():
        data = fetch_open_meteo_archive(lat, lon, days_back=3)
        if not data or 'daily' not in data:
            continue
        d = data['daily']
        # Find yesterday's date
        if d['time']:
            # Check the most recent actual date
            most_recent = d['time'][-1] if d['time'] else None
            if most_recent and tap_weather and hub in tap_weather:
                # Find matching TAP prediction
                for e in tap_weather[hub]:
                    if e['date'] == most_recent:
                        api_max = e['base_max_f']
                        tap_max = e['tap_max_f']
                        actual_max = d['temperature_2m_max'][-1] * 9/5 + 32
                        results.append({
                            "hub": hub,
                            "date": most_recent,
                            "api_max_f": round(api_max, 1),
                            "tap_max_f": round(tap_max, 1),
                            "actual_max_f": round(actual_max, 1),
                            "api_err": round(api_max - actual_max, 2),
                            "tap_err": round(tap_max - actual_max, 2),
                        })
                        break

    if not results:
        return {"error": "no data", "verdict": "unable to compare"}

    # Compare
    tap_wins = 0
    api_wins = 0
    for r in results:
        if abs(r['tap_err']) < abs(r['api_err']):
            tap_wins += 1
        else:
            api_wins += 1

    return {
        "results": results,
        "tap_wins": tap_wins,
        "api_wins": api_wins,
        "verdict": f"TAP wins {tap_wins}/{len(results)}, API wins {api_wins}/{len(results)}",
    }


def check_finance(tap_finance: list) -> dict:
    """Check option arbitrage sim — count actionable signals."""
    if not tap_finance:
        return {"error": "no data", "verdict": "unable to compare"}

    yields = [r['arbitrage_yield_pct'] for r in tap_finance]
    buy_signals = [r for r in tap_finance if r['arbitrage_yield_pct'] > 12]
    sell_signals = [r for r in tap_finance if r['arbitrage_yield_pct'] < -12]
    non_zero_phi = [r for r in tap_finance if abs(r['phi_sensitivity']) > 0.001]

    return {
        "total_contracts": len(tap_finance),
        "yield_mean": round(statistics.mean(yields), 3),
        "yield_max": round(max(yields), 2),
        "yield_min": round(min(yields), 2),
        "buy_signals": len(buy_signals),
        "sell_signals": len(sell_signals),
        "non_zero_phi": len(non_zero_phi),
        "verdict": (
            f"{len(buy_signals)} BUY + {len(sell_signals)} SELL signals at 12% threshold"
        ),
    }


def check_cosmic(tap_cosmic: dict, noaa_kp: list) -> dict:
    """Check cosmic/space weather."""
    if not noaa_kp:
        return {"verdict": "no NOAA data"}

    current_kp = noaa_kp[-1].get('kp_index', '?') if noaa_kp else '?'

    # Get coupling coefficients
    if tap_cosmic and 'tectonic' in tap_cosmic:
        couplings = {
            'california_strike_slip': tap_cosmic['tectonic'].get('california_strike_slip_coupling', 0),
            'tornado_vortex': tap_cosmic.get('atmospheric', {}).get('tornado_vortex_coupling', 0),
            'solar_reconnection': tap_cosmic.get('cosmic', {}).get('solar_reconnection_coupling', 0),
        }
    else:
        couplings = {}

    return {
        "current_kp": current_kp,
        "couplings": couplings,
        "verdict": f"Kp={current_kp} (no quantitative Kp prediction to compare)",
    }


def main():
    print("=" * 78)
    print("  TAP DAILY PREDICTION CHECK")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 78)
    print()

    # Load all TAP sim outputs
    print("[LOAD] TAP prediction sim outputs...")
    tap = load_tap_predictions()
    for k, v in tap.items():
        if v is None:
            print(f"  {k}: MISSING")
        else:
            print(f"  {k}: loaded")

    print()
    print("[FETCH] Live observations...")
    usgs_quakes = fetch_usgs_last_n_days(n_days=5, min_mag=4.5)
    print(f"  USGS M4.5+ in last 5 days: {len(usgs_quakes)}")
    noaa_kp = fetch_noaa_kp()
    print(f"  NOAA Kp records: {len(noaa_kp)}")

    print()
    print("[ANALYZE] Each domain...")

    results = {
        "timestamp": datetime.now().isoformat(),
        "seismic": check_seismic(usgs_quakes, tap.get('seismic')),
        "weather": check_weather(tap.get('weather')),
        "finance": check_finance(tap.get('finance')),
        "cosmic": check_cosmic(tap.get('cosmic'), noaa_kp),
    }

    # Print summary
    print()
    print("=" * 78)
    print("  DAILY CHECK SUMMARY")
    print("=" * 78)
    print()
    for domain, r in results.items():
        if domain == "timestamp":
            continue
        print(f"  [{domain.upper()}]")
        if isinstance(r, dict):
            for k, v in r.items():
                if k == 'results':
                    continue
                if isinstance(v, dict):
                    print(f"    {k}:")
                    for kk, vv in v.items():
                        print(f"      {kk}: {vv}")
                else:
                    print(f"    {k}: {v}")
        else:
            print(f"    {r}")
        print()

    # Export
    out_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'assets'
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_daily_check_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[EXPORT] -> {out_path}")
    print("=" * 78)


if __name__ == "__main__":
    main()
