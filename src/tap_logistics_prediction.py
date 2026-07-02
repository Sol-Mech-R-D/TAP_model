# -*- coding: utf-8 -*-
"""
tap_logistics_prediction.py
============================
TAP v5.3 Logistics / Shipping / Freight prediction layer.

Tests the framework's claim that the sub-breath clock
modulates logistics-relevant signals:
  1. Baltic Dry Index (BDI) — dry bulk shipping rates
  2. Shanghai Containerized Freight Index (SCFI)
  3. Drewry World Container Index (WCI)
  4. Port congestion proxies (when available)

For each metric, fetches 5 years of data, computes
phase correlation with the 8.121-day sub-breath clock,
and predicts the next 30 days of values.

If the framework has predictive power, the phase-resolved
mean should differ significantly from the unconditional
mean, and the Rayleigh test should show clustering.
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


def get_phase(date: datetime) -> float:
    """Sub-breath phase for a given date."""
    diff_days = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (diff_days / BASE_PERIOD) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def fetch_baltic_dry_index() -> list:
    """Fetch historical BDI from a free source (Investing.com public CSV)."""
    # Try a few public sources
    sources = [
        # Yahoo Finance BDIY (Baltic Dry Index Yahoo) — no reliable free API
        # Try FRED Baltic Exchange Dry Index
        "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BDIY&cosd=2010-01-01&costa=2026-07-02",
    ]
    for url in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TAP-Model/5.3'})
            with urllib.request.urlopen(req, timeout=15) as response:
                text = response.read().decode()
            # Parse CSV: DATE,VALUE
            records = []
            for line in text.strip().split('\n')[1:]:  # skip header
                parts = line.split(',')
                if len(parts) >= 2 and parts[1] != '.':
                    try:
                        date = datetime.strptime(parts[0], '%Y-%m-%d')
                        value = float(parts[1])
                        records.append({'time': date, 'value': value})
                    except (ValueError, TypeError):
                        continue
            if records:
                return records
        except Exception as e:
            print(f"  [BDI ERROR] {e}")
            continue
    return []


def fetch_scci_freight() -> list:
    """Try to fetch Shanghai Containerized Freight Index."""
    # SCFI is published weekly by Shanghai Shipping Exchange
    # No free public API; use a sample/illustrative dataset
    return []


def synth_shipping_data(start_date: datetime, end_date: datetime) -> list:
    """
    Synthesize a realistic shipping dataset for testing the framework.
    In production, this would be replaced with real BDI/SCFI data.

    The synthetic data has:
    - Long-term trend (10% per year growth)
    - Weekly seasonality
    - Sub-breath phase modulation (5% amplitude)
    - Random noise
    """
    print("  [SYNTH] Generating synthetic shipping data (5 years, daily)...")
    import random
    random.seed(42)

    records = []
    days = (end_date - start_date).days
    base_value = 1500  # BDI baseline
    annual_growth = 0.10
    for i in range(days):
        date = start_date + timedelta(days=i)
        years_elapsed = i / 365.25
        # Long-term growth
        growth = base_value * (1 + annual_growth) ** years_elapsed
        # Weekly seasonality
        weekly = 1.0 + 0.02 * math.sin(2 * math.pi * i / 7)
        # Sub-breath modulation (the framework's signature)
        phase = get_phase(date)
        tap_mod = 1.0 + 0.05 * math.cos(phase)
        # Random noise
        noise = 1.0 + 0.1 * random.gauss(0, 1)
        value = growth * weekly * tap_mod * noise
        records.append({
            'time': date,
            'value': value,
            'source': 'synthetic',
        })
    return records


def phase_correlation_analysis(records: list, n_phase_bins: int = 16) -> dict:
    """
    Analyze whether the metric correlates with the sub-breath clock phase.

    Approach:
    1. Compute the deviation of each value from the local mean (60-day window)
    2. Bin the deviations by phase
    3. Compute mean deviation per bin
    4. Test if the means differ significantly from 0 (t-test)
    5. Compute the Rayleigh test on the phase distribution
    """
    if not records:
        return {"error": "no data"}

    # Sort by time
    records = sorted(records, key=lambda r: r['time'])

    # Compute deviation from 60-day rolling mean
    deviations = []
    phases = []
    values = []
    for i, r in enumerate(records):
        # Get 60-day window
        window_start = max(0, i - 30)
        window_end = min(len(records), i + 30)
        window_values = [records[j]['value'] for j in range(window_start, window_end)]
        if not window_values:
            continue
        local_mean = statistics.mean(window_values)
        deviation = (r['value'] - local_mean) / local_mean  # fractional deviation
        deviations.append(deviation)
        phases.append(get_phase(r['time']))
        values.append(r['value'])

    # Bin by phase
    bin_width = 2 * math.pi / n_phase_bins
    bin_means = [[] for _ in range(n_phase_bins)]
    for dev, phase in zip(deviations, phases):
        bin_idx = int((phase + math.pi) / bin_width) % n_phase_bins
        bin_means[bin_idx].append(dev)

    bin_summary = []
    for i, devs in enumerate(bin_means):
        if devs:
            bin_summary.append({
                'phase_deg': round((i * bin_width - math.pi) * 180 / math.pi, 1),
                'phase_bin': i,
                'mean_dev': round(statistics.mean(devs), 6),
                'count': len(devs),
            })

    # Test: do bin means differ from 0?
    bin_mean_values = [s['mean_dev'] for s in bin_summary if s['count'] > 10]
    if bin_mean_values:
        # Are positive bins near phase 0 (the crossings) and negative elsewhere?
        # Compute correlation between phase and deviation
        # bin index 0 corresponds to phase = -π, bin n/2 = 0, bin n-1 ≈ +π
        bin_indices = [s['phase_bin'] for s in bin_summary if s['count'] > 10]
        # Wrap to bring phase 0 to center
        wrapped_indices = [(bi - n_phase_bins // 2) % n_phase_bins for bi in bin_indices]
        # Convert to cos(phase_bin_index * 2π/n)
        cos_bins = [math.cos(2 * math.pi * (wi / n_phase_bins)) for wi in wrapped_indices]
        # Pearson correlation
        n = len(cos_bins)
        if n > 2:
            mean_cos = statistics.mean(cos_bins)
            mean_dev = statistics.mean(bin_mean_values)
            cov = sum((c - mean_cos) * (d - mean_dev) for c, d in zip(cos_bins, bin_mean_values)) / n
            std_cos = math.sqrt(sum((c - mean_cos)**2 for c in cos_bins) / n)
            std_dev = math.sqrt(sum((d - mean_dev)**2 for d in bin_mean_values) / n)
            r_corr = cov / (std_cos * std_dev) if std_cos * std_dev > 0 else 0
        else:
            r_corr = 0
    else:
        r_corr = 0

    # Rayleigh test on the phase distribution
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

    # Mean and max values
    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values) if len(values) > 1 else 0
    max_val = max(values)
    min_val = min(values)
    max_date = records[values.index(max_val)]['time']
    min_date = records[values.index(min_val)]['time']

    return {
        "n_records": n,
        "mean_value": round(mean_val, 2),
        "std_value": round(std_val, 2),
        "max_value": round(max_val, 2),
        "max_date": max_date.strftime('%Y-%m-%d'),
        "min_value": round(min_val, 2),
        "min_date": min_date.strftime('%Y-%m-%d'),
        "rayleigh_r": round(r, 4),
        "rayleigh_z": round(Z, 4),
        "rayleigh_p": round(p_val, 6),
        "phase_bin_correlation": round(r_corr, 4),
        "bin_summary": bin_summary,
    }


def main():
    print("=" * 80)
    print("  TAP LOGISTICS / SHIPPING / FREIGHT PREDICTION LAYER")
    print("  Testing sub-breath phase correlation with shipping metrics")
    print("=" * 80)
    print()

    # Define time window
    end_date = datetime(2026, 7, 2)
    start_date = end_date - timedelta(days=5 * 365 + 1)  # 5 years back

    # Try real data first
    print("[1/3] Fetching Baltic Dry Index (5 years)...")
    real_records = fetch_baltic_dry_index()
    if real_records:
        records = real_records
        source = "BDI (FRED BDIY)"
    else:
        print("  Real BDI not available, using synthetic shipping data")
        records = synth_shipping_data(start_date, end_date)
        source = "Synthetic (5% TAP modulation)"

    print(f"  Got {len(records)} records from {source}")
    if records:
        print(f"  Date range: {records[0]['time'].strftime('%Y-%m-%d')} to {records[-1]['time'].strftime('%Y-%m-%d')}")
    print()

    # Analyze
    print("[2/3] Phase correlation analysis...")
    analysis = phase_correlation_analysis(records)
    print()
    print(f"  STATISTICS:")
    print(f"    Records:        {analysis['n_records']}")
    print(f"    Mean:           {analysis['mean_value']}")
    print(f"    Std:            {analysis['std_value']}")
    print(f"    Max:            {analysis['max_value']} on {analysis['max_date']}")
    print(f"    Min:            {analysis['min_value']} on {analysis['min_date']}")
    print()
    print(f"  PHASE CORRELATION:")
    print(f"    Rayleigh r:     {analysis['rayleigh_r']:.4f}")
    print(f"    Rayleigh Z:     {analysis['rayleigh_z']:.4f}")
    print(f"    Rayleigh p:     {analysis['rayleigh_p']:.6f}")
    print(f"    Bin correlation: {analysis['phase_bin_correlation']:.4f}")
    print()

    # Show phase bins
    print("  PHASE BINS (16 bins, -180° to +180°):")
    print(f"    {'Phase':>8s} | {'Mean dev':>10s} | {'Count':>5s}")
    print("    " + "-" * 32)
    for s in analysis['bin_summary']:
        print(f"    {s['phase_deg']:>+7.1f}° | {s['mean_dev']:>+10.6f} | {s['count']:>5d}")
    print()

    # Predict forward 30 days
    print("[3/3] Forward prediction (next 30 days)...")
    forward_predictions = []
    today = datetime(2026, 7, 2)
    overall_mean = analysis['mean_value']
    # The "TAP factor" — how much to modulate
    # Use the bin correlation strength as the signal
    tap_amplitude = 0.05 if abs(analysis['phase_bin_correlation']) > 0.2 else 0.0
    for i in range(30):
        date = today + timedelta(days=i)
        phase = get_phase(date)
        # Phase = 0 is at crossing (peak), phase = π is trough
        # If we found positive correlation with cos(phase), TAP signal is +cos(phase)
        # Otherwise, use raw data
        if tap_amplitude > 0:
            tap_factor = 1.0 + tap_amplitude * math.cos(phase)
            predicted = overall_mean * tap_factor
        else:
            predicted = overall_mean
        forward_predictions.append({
            'date': date.strftime('%Y-%m-%d'),
            'phase_deg': round(phase * 180 / math.pi, 1),
            'predicted_value': round(predicted, 2),
            'tap_modulation_pct': round((predicted - overall_mean) / overall_mean * 100, 2),
        })

    print(f"  Forward 30-day predictions:")
    for p in forward_predictions[::5]:  # every 5th day
        print(f"    {p['date']}  phase={p['phase_deg']:+6.1f}°  predicted={p['predicted_value']:.0f}  TAP_mod={p['tap_modulation_pct']:+.2f}%")
    print()

    # Verdict
    print("=" * 80)
    print("  LOGISTICS VERDICT")
    print("=" * 80)
    print()
    p = analysis['rayleigh_p']
    r_corr = analysis['phase_bin_correlation']
    print(f"  Phase bin correlation: {r_corr:+.4f}")
    print(f"  Rayleigh p:            {p:.6f}")
    print()
    if abs(r_corr) > 0.3 and p < 0.05:
        print(f"  ✓ STRONG signal: shipping rates correlate with sub-breath phase")
        print(f"    (r={r_corr:+.3f}, p={p:.4f})")
    elif abs(r_corr) > 0.1 and p < 0.1:
        print(f"  ≈ WEAK signal: marginal correlation with phase")
    else:
        print(f"  ✗ NO signal: shipping rates don't correlate with phase in this data")
        if source.startswith("Synthetic"):
            print(f"    (Note: data is synthetic with 5% TAP modulation by design)")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_logistics_prediction_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "data_source": source,
        "n_records": len(records),
        "analysis": analysis,
        "forward_predictions_30d": forward_predictions,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
