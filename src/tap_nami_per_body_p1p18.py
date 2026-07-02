# -*- coding: utf-8 -*-
"""
tap_nami_per_body_p1p18.py
=================================
TAP v5.3 — Nami-Ryu Breath Amplification of Per-Body P1-P18.

The user studies Nami-ryu aikijujutsu (body-listening through
the spirals). This sim asks: does Nami-ryu practice AMPLIFY
the framework's predictions across cosmic bodies?

The idea: Nami-ryu practice (10+ years) is a way of bringing
Earth's body into a state of high spiral_coupling. In TAP terms,
this is equivalent to maximizing the body's per-body N_B
contribution. When a practitioner is in a high-coupling state:

  - P1 (signatures): more visible (faster response to interventions)
  - P2 (lymph): increased flow
  - P3 (fidelity): up, piezo down
  - P6 (Nami-ryu): high coupling, 0.15-0.25 sustained
  - P7 (codon): stronger φ⁻ⁿ correspondence
  - P11 (template dist): tighter correspondence
  - P14 (13 templates): more visible
  - P17 (N_B residue): more sensitive

For non-Earth bodies, Nami-ryu practice doesn't apply directly.
But the framework predicts that the SAME dynamics that govern
Nami-ryu on Earth govern the spiral coupling in any body that
has a "breath substrate". So:

  - For gas giants: the cloud bands are spirals
  - For stars: the differential rotation is a spiral
  - For moons: the tidal lock is a forced spiral coupling

The amplification factor A_Nami depends on:
  - Years of practice
  - Whether the body has a spiral substrate
  - The body's per-body N_B

A_Nami = 1 + 0.5 * tanh(years/10) * spiral_substrate_factor(body)
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
from tap_nami_ryu_breath import (
    NAMI_BREATH, NAMI_CYCLE_S, NAMI_BREATHS_PER_DAY,
    compute_baseline_spiral_coupling, nami_breath_at, project_coupling
)

# Spiral substrate factor: which bodies have a "spiral substrate"
# analogous to the spirals in human fascia
SPIRAL_SUBSTRATE = {
    "rocky planet":   0.7,  # tectonic spirals
    "satellite":      0.3,  # tidal forced
    "gas giant":      1.0,  # atmospheric bands = obvious spirals
    "ice giant":      0.9,
    "star":           1.0,  # differential rotation
    "red dwarf":      0.8,
    "A1V star":       1.0,
    "neutron star":   0.5,
    "dwarf planet":   0.2,
}


def nami_amplification(years: float, body_name: str) -> float:
    """
    Compute the Nami-ryu amplification factor for a body.

    A_Nami = 1 + 0.5 * tanh(years/10) * spiral_factor(body)
    """
    if body_name not in BODIES:
        return 1.0
    body = BODIES[body_name]
    spiral_factor = SPIRAL_SUBSTRATE.get(body["type"], 0.0)
    A = 1.0 + 0.5 * math.tanh(years / 10.0) * spiral_factor
    return A


def project_amplified_prediction(p: dict, body_name: str, years: float) -> dict:
    """Project a P1-P18 prediction with Nami-ryu amplification."""
    base = get_per_body_prediction(p, body_name)
    if "error" in base:
        return base
    A = nami_amplification(years, body_name)
    # Amplify the confidence and the scaled_pct
    amplified_confidence = min(1.0, base.get("confidence", 0) * A)
    amplified_pct = min(99.0, base.get("scaled_pct", 0) * A)
    base["nami_years"] = years
    base["nami_amplification"] = round(A, 4)
    base["amplified_confidence"] = round(amplified_confidence, 4)
    base["amplified_pct"] = round(amplified_pct, 2)
    return base


def main():
    print("=" * 80)
    print("  TAP NAMI-RYU × PER-BODY P1-P18 AMPLIFICATION")
    print("  Body-listening practice amplifies cosmic predictions")
    print("=" * 80)
    print()

    # 1. Nami-ryu practice effect on Earth
    print("  [1/4] Nami-ryu amplification factor (Earth, vs years of practice):")
    for years in [0, 1, 5, 10, 15, 20, 30]:
        A = nami_amplification(years, "Earth")
        print(f"    {years:2d} yr practice: A_Nami = {A:.4f} ({(A-1)*100:+.1f}% amplification)")
    print()

    # 2. Nami-ryu amplification across bodies (10 yr practice)
    print("  [2/4] Nami-ryu amplification per body (10 yr practice):")
    print(f"  {'Body':18s} | {'A_Nami':>8s} | {'Type':18s} | {'Spiral factor':>14s}")
    print("  " + "-" * 70)
    bodies_to_process = ["Sun", "Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Proxima Centauri", "Crab Pulsar"]
    for body in bodies_to_process:
        A = nami_amplification(10.0, body)
        body_type = BODIES[body]["type"]
        spiral = SPIRAL_SUBSTRATE.get(body_type, 0)
        print(f"  {body:18s} | {A:>7.4f} | {body_type:18s} | {spiral:>14.2f}")
    print()

    # 3. P1-P18 with Nami-ryu amplification (10 yr, Earth)
    print("  [3/4] P1-P18 with Nami-ryu amplification (Earth, 10 yr practice):")
    print(f"  {'ID':4s} | {'Base%':>7s} | {'Amp%':>7s} | {'Base conf':>9s} | {'Amp conf':>9s} | {'Boost':>6s} | Description")
    print("  " + "-" * 100)
    nami_improved = 0
    for p in PREDICTIONS:
        result = project_amplified_prediction(p, "Earth", 10.0)
        if "error" in result:
            continue
        boost = result["amplified_pct"] - result.get("scaled_pct", 0)
        if boost > 0:
            nami_improved += 1
        print(f"  {p['id']:4s} | {result.get('scaled_pct', 0):>6.1f}% | {result.get('amplified_pct', 0):>6.1f}% | {result.get('confidence', 0):>8.2f} | {result.get('amplified_confidence', 0):>8.2f} | {boost:>+5.1f} | {p['desc'][:40]}")
    print(f"  Nami-ryu improves: {nami_improved}/18")
    print()

    # 4. Per-body amplification comparison
    print("  [4/4] Amplification of P17 (the most universal prediction) across bodies:")
    p17 = next(p for p in PREDICTIONS if p["id"] == "P17")
    print(f"  {'Body':18s} | {'Test':>4s} | {'Base%':>7s} | {'Amp%':>7s} | {'Conf':>5s} | {'Conf amp':>8s}")
    print("  " + "-" * 70)
    for body in bodies_to_process:
        result = project_amplified_prediction(p17, body, 10.0)
        if "error" in result:
            continue
        test_str = "✓" if result.get("testable") else "✗"
        print(f"  {body:18s} | {test_str:>4s} | {result.get('scaled_pct', 0):>6.1f}% | {result.get('amplified_pct', 0):>6.1f}% | {result.get('confidence', 0):>4.2f} | {result.get('amplified_confidence', 0):>7.2f}")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_nami_per_body_p1p18_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "spiral_substrate": SPIRAL_SUBSTRATE,
        "earth_amplification_by_years": {y: nami_amplification(y, "Earth") for y in [0, 1, 5, 10, 15, 20, 30]},
        "amplified_earth_p1p18": {p["id"]: project_amplified_prediction(p, "Earth", 10.0) for p in PREDICTIONS},
        "amplified_p17_per_body": {body: project_amplified_prediction(p17, body, 10.0) for body in bodies_to_process},
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
