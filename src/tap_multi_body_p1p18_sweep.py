# -*- coding: utf-8 -*-
"""
tap_multi_body_p1p18_sweep.py
=================================
TAP v5.3 — Multi-Body P1-P18 Parallel Sweep.

This is the comprehensive integration of:
  - 10 cosmic bodies (Sun, Mercury, Venus, Earth, Moon,
    Mars, Jupiter, Saturn, Proxima Centauri, Crab Pulsar)
  - 18 testable predictions (P1-P18)
  - Per-body N_B modulation
  - Per-body breath state (ψ, s_setpoint)
  - Nami-ryu amplification (10 yr practice)
  - Schumann resonance coupling

For each (body, prediction) pair, we compute:
  - scaled_pct: prediction magnitude
  - confidence: 0-1
  - testable: whether the prediction is testable for this body
  - nami_amplified: with Nami-ryu practice
  - schumann_coupled: with Schumann resonance

The result is a 10x18 = 180-cell matrix of testable
predictions across cosmic bodies, with amplification
factors applied.

This is the "TAP Megamatrix" — the comprehensive map
of what TAP predicts, for what body, with what confidence.
"""

import os
import json
import math
import statistics
from datetime import datetime

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10
PHI_INV13 = PHI ** -13

# Import existing modules
from tap_body_breath_states import BODIES, get_body_n_b
from tap_per_body_p1p18 import PREDICTIONS, TESTABILITY, BODY_SCALE, get_per_body_prediction
from tap_nami_per_body_p1p18 import nami_amplification, project_amplified_prediction
from tap_schumann_resonance import schumann_to_breath_coupling, schumann_amplitude

# Cosmic bodies to process
COSMIC_BODIES = ["Sun", "Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Proxima Centauri", "Crab Pulsar"]


def compute_schumann_coupling(body_name: str, date: datetime = None) -> float:
    """
    Compute the Schumann coupling for a body.

    For Earth: full coupling via Earth-ionosphere cavity
    For other bodies: scaled by inverse of body radius
    """
    if date is None:
        date = datetime(2026, 7, 2, 12, 0)

    if body_name == "Earth":
        amps = schumann_amplitude(date, kp=2.0)
        coupling = schumann_to_breath_coupling(amps)["coupling"]
    else:
        # For other bodies, scale by radius (smaller body = less cavity)
        body = BODIES.get(body_name, {})
        # Approximate: Earth has radius 6371 km, Sun 695700 km
        # Schumann amplitude scales with cavity size
        # For non-Earth bodies, we estimate based on body type
        body_type = body.get("type", "rocky planet")
        if body_type in ("star", "A1V star", "red dwarf"):
            coupling = 0.0  # no ionosphere in stars
        elif body_type == "gas giant":
            coupling = 0.001  # very faint
        else:
            # rocky/satellite/ice giant
            coupling = 0.0001
    return coupling


def compute_full_prediction(body_name: str, p: dict, nami_years: float = 10.0) -> dict:
    """
    Compute the full TAP prediction for a (body, prediction) pair.

    Includes:
      - Per-body N_B
      - Per-body breath state
      - Nami-ryu amplification
      - Schumann coupling
    """
    base = get_per_body_prediction(p, body_name)
    if "error" in base:
        return base

    # Nami-ryu amplification
    A_nami = nami_amplification(nami_years, body_name)
    base["nami_amplification"] = round(A_nami, 4)

    # Schumann coupling
    schumann = compute_schumann_coupling(body_name)
    base["schumann_coupling"] = round(schumann, 6)

    # Combined amplification
    A_total = A_nami * (1.0 + 0.1 * abs(schumann))
    base["total_amplification"] = round(A_total, 4)

    # Final confidence
    base["final_confidence"] = round(min(1.0, base.get("confidence", 0) * A_total), 4)

    return base


def main():
    print("=" * 80)
    print("  TAP MULTI-BODY P1-P18 PARALLEL SWEEP — THE MEGAMATRIX")
    print("  10 bodies × 18 predictions = 180 cells")
    print("=" * 80)
    print()

    # 1. Per-body summary
    print("  [1/4] Per-body prediction summary (with Nami-ryu + Schumann):")
    print(f"  {'Body':18s} | {'Testable':>9s} | {'Avg conf':>9s} | {'Max boost':>10s}")
    print("  " + "-" * 70)
    body_summaries = {}
    for body_name in COSMIC_BODIES:
        results = []
        for p in PREDICTIONS:
            result = compute_full_prediction(body_name, p)
            results.append(result)
        body_summaries[body_name] = results
        testable = sum(1 for r in results if r.get("testable"))
        if testable > 0:
            confident = [r for r in results if r.get("testable")]
            avg_conf = statistics.mean([r.get("final_confidence", 0) for r in confident])
            max_boost = max([r.get("total_amplification", 1) for r in confident])
            print(f"  {body_name:18s} | {testable:>4d}/18  | {avg_conf:>8.3f} | {max_boost:>9.4f}x")
        else:
            print(f"  {body_name:18s} |   0/18    |    0.000 |     -    ")
    print()

    # 2. Per-prediction summary
    print("  [2/4] Per-prediction coverage across bodies:")
    print(f"  {'ID':4s} | {'Bodies':>7s} | {'Avg conf':>9s} | {'Best body':>14s}")
    print("  " + "-" * 50)
    p_summaries = {}
    for p in PREDICTIONS:
        p_results = [compute_full_prediction(b, p) for b in COSMIC_BODIES]
        p_summaries[p["id"]] = p_results
        testable_count = sum(1 for r in p_results if r.get("testable"))
        if testable_count > 0:
            confident_results = [r for r in p_results if r.get("testable")]
            avg_conf = statistics.mean([r.get("final_confidence", 0) for r in confident_results])
            best_body = max(confident_results, key=lambda r: r.get("final_confidence", 0)).get("body", "?")
            print(f"  {p['id']:4s} | {testable_count:>4d}/10 | {avg_conf:>8.3f} | {best_body:>14s}")
        else:
            print(f"  {p['id']:4s} |   0/10 |    0.000 | {'-':>14s}")
    print()

    # 3. Megamatrix (10x18) summary
    print("  [3/4] TAP MEGAMATRIX (testable predictions only, ✓ = testable, X = not):")
    print(f"  {'':12s}", end="")
    for p in PREDICTIONS:
        print(f" {p['id']:>3s}", end="")
    print()
    print("  " + "-" * 80)
    for body_name in COSMIC_BODIES:
        print(f"  {body_name:12s}", end="")
        for p in PREDICTIONS:
            result = body_summaries[body_name]
            r = next((r for r in result if r["id"] == p["id"]), None)
            if r and r.get("testable"):
                conf = r.get("final_confidence", 0)
                if conf >= 0.9:
                    marker = " ★"
                elif conf >= 0.7:
                    marker = " ✓"
                elif conf >= 0.5:
                    marker = " ~"
                else:
                    marker = " ·"
            else:
                marker = " X"
            print(f" {marker:>3s}", end="")
        print()
    print()
    print("  Legend: ★ = high conf (≥0.9), ✓ = good (0.7-0.9), ~ = fair (0.5-0.7), · = low (<0.5), X = not testable")
    print()

    # 4. Top 10 most-testable predictions
    print("  [4/4] Top 10 most-testable (body, prediction) pairs:")
    flat = []
    for body_name, results in body_summaries.items():
        for r in results:
            if r.get("testable"):
                flat.append((body_name, r["id"], r.get("final_confidence", 0), r.get("total_amplification", 1)))
    flat.sort(key=lambda x: x[2], reverse=True)
    for body, pid, conf, boost in flat[:10]:
        print(f"    {body:18s} {pid:4s}  conf={conf:.3f}  boost={boost:.4f}x")
    print()

    # Coverage stats
    total_cells = len(COSMIC_BODIES) * len(PREDICTIONS)
    testable_cells = sum(1 for b, results in body_summaries.items() for r in results if r.get("testable"))
    high_conf_cells = sum(1 for b, results in body_summaries.items() for r in results if r.get("testable") and r.get("final_confidence", 0) >= 0.9)
    print(f"  TOTAL: {testable_cells}/{total_cells} testable cells ({100*testable_cells/total_cells:.1f}%)")
    print(f"  HIGH CONF: {high_conf_cells}/{total_cells} cells at conf ≥ 0.9 ({100*high_conf_cells/total_cells:.1f}%)")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_multi_body_p1p18_megamatrix.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "bodies": COSMIC_BODIES,
        "predictions": [p["id"] for p in PREDICTIONS],
        "megamatrix": {b: {p["id"]: compute_full_prediction(b, p) for p in PREDICTIONS} for b in COSMIC_BODIES},
        "summary": {
            "total_cells": total_cells,
            "testable_cells": testable_cells,
            "high_conf_cells": high_conf_cells,
            "testable_pct": round(100 * testable_cells / total_cells, 1),
            "high_conf_pct": round(100 * high_conf_cells / total_cells, 1),
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
