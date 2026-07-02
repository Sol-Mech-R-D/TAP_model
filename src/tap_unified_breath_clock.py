# -*- coding: utf-8 -*-
"""
tap_unified_breath_clock.py
============================
TAP v5.3 — Unified Multi-Body Breath Clock.

The original framework has:
  - Master Breath Clock: N_B = 8 (chi² fit over 99 observables)
  - Per-Breath drift: ε = φ⁻¹³ = 0.001919
  - Sub-breath clock: 8.12133 days (Earth-Moon beat)
  - Meta-breath: N_MAX = 521

This sim adds OTHER BREATH-PRODUCING ENTITIES that the
TAP model implies but the previous work did not include:
  - Lunar synodic (29.53 days) — Moon phases
  - Solar Carrington rotation (27.27 days) — sunspots
  - Earth annual (365.25 days) — seasons
  - Lunar nodal (18.6 years) — eclipse cycle
  - Jupiter-Saturn conjunction (19.86 years) — great conjunction
  - Venus synodic (583.9 days) — Venus breath
  - Mars synodic (779.9 days) — Mars breath
  - Cosmic (Hubble time, 13.8 Gyr)

Each contributes a φ-rate-scaled modulation to the total
breath drift. The total drift is:

  ε_total(t) = ε_0 * product_i (1 + a_i * cos(2π*t/P_i + φ_i))

where:
  a_i = φ^-n_i (the φ-rate for body i)
  n_i = breath layer depth

This produces a UNIFIED time series that:
  - Drives the cosmic Kp prediction
  - Drives the weather modulation
  - Drives the seismic clustering
  - Drives the breath clock observable drift

All four sims now use the SAME drift function, ensuring
they're consistent with each other and with the cascade.
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

# Master TAP constants
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26

# Breath number
N_B = 8
GAMMA_NB = 1.0 + N_B * PHI_INV13

SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)

# Other breath-producing entities
# Each entry: name, period_days, phi_power (depth), coupling_amplitude
BREATH_PRODUCERS = [
    {
        "name": "Sub-breath (Earth-Moon beat)",
        "period_days": 8.12133,
        "phi_power": 4,        # φ⁻⁴
        "coupling": PHI_INV4,  # ≈ 0.146
        "description": "Primary 8.121-day sub-breath clock",
    },
    {
        "name": "Lunar synodic (Moon phases)",
        "period_days": 29.53059,
        "phi_power": 8,        # φ⁻⁸
        "coupling": PHI_INV8,  # ≈ 0.0213
        "description": "Full moon to full moon",
    },
    {
        "name": "Solar Carrington rotation",
        "period_days": 27.2753,
        "phi_power": 8,        # φ⁻⁸
        "coupling": PHI_INV8,
        "description": "Solar equatorial rotation (sunspot cycle)",
    },
    {
        "name": "Earth annual orbit",
        "period_days": 365.256,
        "phi_power": 13,        # φ⁻¹³
        "coupling": PHI_INV13,  # ≈ 0.00192
        "description": "Earth orbital period (perihelion to perihelion)",
    },
    {
        "name": "Lunar nodal (eclipse cycle)",
        "period_days": 18.6 * 365.25,
        "phi_power": 16,        # φ⁻¹⁶
        "coupling": PHI ** -16,
        "description": "Lunar orbital plane precession",
    },
    {
        "name": "Venus synodic",
        "period_days": 583.9,
        "phi_power": 16,        # φ⁻¹⁶
        "coupling": PHI ** -16,
        "description": "Venus-Earth conjunction cycle",
    },
    {
        "name": "Mars synodic",
        "period_days": 779.9,
        "phi_power": 18,        # φ⁻¹⁸
        "coupling": PHI ** -18,
        "description": "Mars-Earth conjunction cycle",
    },
    {
        "name": "Jupiter-Saturn conjunction",
        "period_days": 19.86 * 365.25,
        "phi_power": 20,        # φ⁻²⁰
        "coupling": PHI ** -20,
        "description": "Great conjunction (20-year cycle)",
    },
    {
        "name": "Cosmic (Hubble time)",
        "period_days": 13.8e9 * 365.25,
        "phi_power": 26,        # φ⁻²⁶
        "coupling": PHI_INV26,  # ≈ 3.68e-6
        "description": "Cosmic breath, age of universe",
    },
]


def get_producer_phase(producer: dict, date: datetime) -> float:
    """Get the phase for a specific breath producer at a given date."""
    # Anchor: 0 at SOLSTICE_2026 for all (arbitrary choice)
    days_since = (date - SOLSTICE_2026).total_seconds() / 86400.0
    phase = (days_since / producer["period_days"]) * 2.0 * math.pi
    return (phase + math.pi) % (2.0 * math.pi) - math.pi


def get_total_drift(date: datetime, include_producers: list = None) -> dict:
    """
    Compute the total breath drift at a given date, summing
    contributions from all (or selected) breath producers.

    Returns dict with:
      - total_modulation: product_i (1 + a_i * cos(phase_i))
      - eps_total: ε_0 * total_modulation
      - per_producer: dict of per-producer contributions
    """
    if include_producers is None:
        include_producers = BREATH_PRODUCERS

    per_producer = {}
    total_mod = 1.0
    for p in include_producers:
        phase = get_producer_phase(p, date)
        contribution = p["coupling"] * math.cos(phase)
        per_producer[p["name"]] = {
            "phase_deg": round(phase * 180 / math.pi, 2),
            "phase_rad": round(phase, 4),
            "coupling": p["coupling"],
            "contribution": round(contribution, 6),
            "phi_power": p["phi_power"],
        }
        total_mod *= (1.0 + contribution)

    eps_0 = PHI_INV13  # base drift
    eps_total = eps_0 * total_mod

    return {
        "total_modulation": total_mod,
        "eps_0": eps_0,
        "eps_total": eps_total,
        "per_producer": per_producer,
    }


def get_drift_at_full_resolution(date: datetime, hours: int = 24) -> dict:
    """Sample the drift at hour resolution for a day, to see variation."""
    samples = []
    for h in range(hours + 1):
        t = date + timedelta(hours=h)
        d = get_total_drift(t)
        samples.append({
            "time": t.strftime("%Y-%m-%d %H:%M"),
            "eps_total": d["eps_total"],
            "total_mod": d["total_mod"],
        })
    return samples


def main():
    print("=" * 80)
    print("  TAP UNIFIED MULTI-BODY BREATH CLOCK")
    print("  Wiring cosmic, weather, seismic to the master cascade")
    print("=" * 80)
    print()

    print("[1/3] Breath producers:")
    print(f"  {'Name':45s} | {'Period':>14s} | {'φ-power':>8s} | {'Coupling':>10s}")
    print("  " + "-" * 95)
    for p in BREATH_PRODUCERS:
        period_str = f"{p['period_days']:.4f} d" if p['period_days'] < 1000 else f"{p['period_days']/365.25:.2f} y"
        print(f"  {p['name']:45s} | {period_str:>14s} | φ⁻{p['phi_power']:>2d}    | {p['coupling']:.6f}")
    print()

    # 2. Today's drift
    print("[2/3] Today's total drift (July 2, 2026):")
    today = datetime(2026, 7, 2, 12, 0)
    drift = get_total_drift(today)
    print(f"  ε_0 (φ⁻¹³)            = {drift['eps_0']:.8f}")
    print(f"  Total modulation      = {drift['total_modulation']:.6f}")
    print(f"  ε_total               = {drift['eps_total']:.8f}")
    print(f"  Multiplicative factor = {drift['eps_total']/drift['eps_0']:.4f}")
    print()
    print("  Per-producer contributions:")
    for name, c in drift['per_producer'].items():
        sign = "+" if c['contribution'] >= 0 else ""
        print(f"    {name:45s}  phase={c['phase_deg']:+7.1f}°  contrib={sign}{c['contribution']:.6f}")
    print()

    # 3. Show what the unified drift looks like over the next 30 days
    print("[3/3] Forward 30-day drift prediction (key for cosmic/weather/seismic):")
    forward = []
    for d in range(30):
        date = today + timedelta(days=d)
        d_drift = get_total_drift(date)
        forward.append({
            "date": date.strftime("%Y-%m-%d"),
            "eps_total": d_drift['eps_total'],
            "total_mod": d_drift['total_modulation'],
        })
    eps_vals = [f['eps_total'] for f in forward]
    mod_vals = [f['total_mod'] for f in forward]
    print(f"  Min ε_total:  {min(eps_vals):.8f} on {[f['date'] for f in forward if f['eps_total'] == min(eps_vals)][0]}")
    print(f"  Max ε_total:  {max(eps_vals):.8f} on {[f['date'] for f in forward if f['eps_total'] == max(eps_vals)][0]}")
    print(f"  Mean ε_total: {statistics.mean(eps_vals):.8f}")
    print(f"  Std ε_total:  {statistics.stdev(eps_vals):.8f}")
    print()
    print(f"  Min mod: {min(mod_vals):.6f}  Max mod: {max(mod_vals):.6f}")
    print(f"  Modulation range: {max(mod_vals) - min(mod_vals):.6f}")
    print()
    print("  Daily forward drift:")
    for f in forward[::3]:  # every 3 days
        marker = "★" if abs(f['eps_total'] - statistics.mean(eps_vals)) > 1.5 * statistics.stdev(eps_vals) else " "
        print(f"    {marker} {f['date']}  ε_total={f['eps_total']:.8f}  mod={f['total_mod']:.6f}")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_unified_breath_clock_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "breath_producers": BREATH_PRODUCERS,
        "n_b": N_B,
        "gamma_n_b": GAMMA_NB,
        "today_drift": drift,
        "forward_30d": forward,
        "summary": {
            "min_eps_total": min(eps_vals),
            "max_eps_total": max(eps_vals),
            "mean_eps_total": statistics.mean(eps_vals),
            "std_eps_total": statistics.stdev(eps_vals),
            "modulation_range": max(mod_vals) - min(mod_vals),
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
