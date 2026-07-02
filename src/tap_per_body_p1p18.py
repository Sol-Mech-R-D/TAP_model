# -*- coding: utf-8 -*-
"""
tap_per_body_p1p18.py
========================
TAP v5.3 — Per-Body P1-P18 Predictions.

Each cosmic body (Sun, Mercury, Earth, Moon, Mars, etc.)
gets its own version of the 18 testable predictions. The
predictions are parameterized by the body's:

  - N_B (which breath cycle it's in)
  - sub_breath period
  - type (rocky, gas, star, etc.)
  - body breath state (ψ, s_setpoint, t_setpoint)

This extends the Earth-only P1-P18 catalog. For each
prediction, the per-body version:
  - Adjusts the predicted value by the body's N_B factor
  - Re-scales the prediction magnitude based on body type
  - Shows which predictions are testable for which body

For example:
  - P1 (signatures ayahuasca vs tensegrity): Earth-only
    (biology doesn't exist on Jupiter)
  - P8 (L-excess correlates Γ(N_B)): testable for any
    body with chiral chemistry
  - P15 (soot): testable for bodies with carbon chemistry
    (not gas giants)
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
PHI_INV26 = PHI ** -26

from tap_body_breath_states import BODIES, get_body_n_b, get_body_breath_state
from tap_p1p18_re_evaluation import PREDICTIONS

# Testable per body type
# type -> which predictions are testable
TESTABILITY = {
    "rocky planet":   ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18"],
    "satellite":      ["P7", "P8", "P11", "P12", "P14", "P15", "P16", "P17"],
    "gas giant":      ["P7", "P8", "P11", "P12", "P14", "P15", "P17"],
    "ice giant":      ["P7", "P8", "P11", "P12", "P14", "P15", "P17"],
    "star":           ["P7", "P8", "P11", "P12", "P14", "P17"],
    "red dwarf":      ["P7", "P8", "P11", "P12", "P14", "P17"],
    "A1V star":       ["P7", "P8", "P11", "P12", "P14", "P17"],
    "neutron star":   ["P7", "P11", "P14", "P17"],
    "dwarf planet":   ["P7", "P8", "P11", "P12", "P15", "P16", "P17"],
}

# Re-scaling factor: how body type scales the prediction
BODY_SCALE = {
    "rocky planet":  1.0,
    "satellite":     0.3,  # smaller body, weaker effects
    "gas giant":     5.0,  # much larger, stronger effects
    "ice giant":     3.0,
    "star":          100.0,  # stellar-scale
    "red dwarf":     50.0,
    "A1V star":      100.0,
    "neutron star":  1000.0,  # extreme
    "dwarf planet":  0.1,
}


def get_per_body_prediction(p: dict, body_name: str) -> dict:
    """
    Get the per-body version of a prediction.

    Returns the prediction with:
      - body: which body
      - n_b: per-body N_B
      - testable: whether this prediction can be tested for this body
      - scaled_pct: prediction magnitude scaled for body type
      - confidence: 0-1 confidence
    """
    body = BODIES.get(body_name)
    if not body:
        return {"error": f"Body {body_name} not in registry"}

    body_type = body["type"]
    n_b = get_body_n_b(body_name)
    testable_list = TESTABILITY.get(body_type, [])
    testable = p["id"] in testable_list
    scale = BODY_SCALE.get(body_type, 1.0)

    # The "core" prediction is from Earth
    earth_baseline = p["baseline_pct"]
    # Per-body N_B modulation
    gamma = 1.0 + 1.0 * n_b * PHI_INV13
    # Body breath state (today)
    state = get_body_breath_state(body_name, datetime(2026, 7, 2, 12, 0))

    # Scaled prediction (in %): baseline × scale × (1 + small N_B effect)
    n_b_factor = 1.0 + (math.log10(max(n_b, 1)) / 20)  # small modulation
    scaled_pct = earth_baseline * scale * n_b_factor
    scaled_pct = min(99.0, max(0.0, scaled_pct))  # clamp

    # Confidence: high if testable + sims run + N_B reasonable
    has_sim = p.get("sim_result") is not None
    confidence = (0.5 if testable else 0.0) + (0.3 if has_sim else 0.0) + (0.2 if n_b > 0 else 0.0)

    return {
        "id": p["id"],
        "body": body_name,
        "body_type": body_type,
        "n_b": n_b,
        "gamma": gamma,
        "psi": state["psi"],
        "testable": testable,
        "scaled_pct": round(scaled_pct, 2),
        "baseline_pct": earth_baseline,
        "scale_factor": scale,
        "confidence": round(confidence, 2),
        "description": p["desc"],
        "sim_result": p.get("sim_result", None),
    }


def main():
    print("=" * 80)
    print("  TAP PER-BODY P1-P18 PREDICTIONS")
    print("  Each body gets its own P1-P18 catalog")
    print("=" * 80)
    print()

    # Process each body
    bodies_to_process = ["Sun", "Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Proxima Centauri", "Crab Pulsar"]
    body_results = {}
    for body_name in bodies_to_process:
        per_body_preds = []
        for p in PREDICTIONS:
            result = get_per_body_prediction(p, body_name)
            per_body_preds.append(result)
        body_results[body_name] = per_body_preds

    # Summary per body
    print("  PER-BODY SUMMARY:")
    print(f"  {'Body':18s} | {'Testable':>9s} | {'Avg conf':>9s} | {'Best P':6s} | {'Worst P':6s}")
    print("  " + "-" * 80)
    for body_name in bodies_to_process:
        preds = body_results[body_name]
        testable = sum(1 for p in preds if p.get("testable"))
        if testable > 0:
            avg_conf = statistics.mean([p.get("confidence", 0) for p in preds if p.get("testable")])
            confident_preds = [p for p in preds if p.get("testable")]
            best = max(confident_preds, key=lambda p: p.get("confidence", 0))
            worst = min(confident_preds, key=lambda p: p.get("confidence", 0))
            print(f"  {body_name:18s} | {testable:>4d}/18  | {avg_conf:>8.2f} | {best['id']:>5s} | {worst['id']:>5s}")
        else:
            print(f"  {body_name:18s} |   0/18    |    0.00   |   -    |   -    ")
    print()

    # Per-body detail for Earth (most predictions testable)
    print("  EARTH PER-BODY P1-P18:")
    print(f"  {'ID':4s} | {'Test':>4s} | {'Conf':>4s} | {'Earth%':>7s} | {'Scaled%':>8s} | Description")
    print("  " + "-" * 90)
    for p in body_results["Earth"]:
        test_str = "✓" if p.get("testable") else "✗"
        conf = p.get("confidence", 0)
        baseline = p.get("baseline_pct", 0)
        scaled = p.get("scaled_pct", 0)
        desc = p.get("description", "")[:50]
        print(f"  {p['id']:4s} | {test_str:>4s} | {conf:>4.2f} | {baseline:>6.1f}% | {scaled:>7.2f}% | {desc}")
    print()

    # Sun
    print("  SUN PER-BODY P1-P18 (star, only cosmic predictions):")
    print(f"  {'ID':4s} | {'Test':>4s} | {'Conf':>4s} | {'Earth%':>7s} | {'Scaled%':>8s} | Description")
    print("  " + "-" * 90)
    for p in body_results["Sun"]:
        test_str = "✓" if p.get("testable") else "✗"
        conf = p.get("confidence", 0)
        baseline = p.get("baseline_pct", 0)
        scaled = p.get("scaled_pct", 0)
        desc = p.get("description", "")[:50]
        print(f"  {p['id']:4s} | {test_str:>4s} | {conf:>4.2f} | {baseline:>6.1f}% | {scaled:>7.2f}% | {desc}")
    print()

    # Crab Pulsar
    print("  CRAB PULSAR PER-BODY P1-P18 (neutron star, only P7/P11/P14/P17):")
    for p in body_results["Crab Pulsar"]:
        if p.get("testable"):
            print(f"    {p['id']:4s}: {p['description']}  (scaled: {p['scaled_pct']:.1f}%, conf: {p['confidence']:.2f})")
    print()

    # Total coverage stats
    print("  TOTAL PREDICTIONS TESTABLE ACROSS ALL BODIES:")
    p_id_coverage = {}
    for body_name, preds in body_results.items():
        for p in preds:
            pid = p["id"]
            if pid not in p_id_coverage:
                p_id_coverage[pid] = 0
            if p.get("testable"):
                p_id_coverage[pid] += 1
    for pid in sorted(p_id_coverage.keys()):
        n = p_id_coverage[pid]
        print(f"    {pid}: testable for {n}/{len(bodies_to_process)} bodies")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_per_body_p1p18_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "bodies_processed": bodies_to_process,
        "testability_matrix": TESTABILITY,
        "body_scale": BODY_SCALE,
        "body_results": body_results,
        "p_id_coverage": p_id_coverage,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
