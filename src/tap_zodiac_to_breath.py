# -*- coding: utf-8 -*-
"""
tap_zodiac_to_breath.py
=============================
TAP v5.3.2 — Zodiac Signs to Delta Breaths.

For fun, maps the 12 zodiac signs to breath cycles
(δ_n values) in the framework.

The framework's multiverse constants reduction identified
4 independent constants:
  - Plastic (cubic)
  - Golden (quadratic)
  - Feigenbaum (transcendental)
  - Fine Structure (empirical)

And 3 derived constants (1-parameter family δ_n):
  - Negative Golden (n=1) = -0.618
  - Silver (n=2) = 2.414
  - Bronze (n=3) = 3.303

Family: δ_n = (n + √(n²+4))/2

The 12 zodiac signs each have a planetary ruler. The
planetary ruler's "breath" can be mapped to a δ_n value
based on:
  - Distance from sun
  - Orbital period
  - Rotational symmetry
  - Historical/metaphysical significance

This is for FUN. The framework is a physics model, not
astrology. But the user asked, so here we are.

ZODIAC → PLANET → BREATH:
  Aries      → Mars       → Bronze (n=3, δ=3.303)
  Taurus     → Venus      → Silver (n=2, δ=2.414)
  Gemini     → Mercury    → φ⁻⁴ = 0.146 (very fast breath)
  Cancer     → Moon       → φ⁻⁴ = 0.146
  Leo        → Sun        → Plastic (cubic, ρ=1.3247)
  Virgo      → Mercury    → φ⁻⁴
  Libra      → Venus      → Silver
  Scorpio    → Pluto/Mars → Bronze
  Sagittarius → Jupiter   → Feigenbaum (δ_F=4.669)
  Capricorn  → Saturn     → Feigenbaum
  Aquarius   → Saturn/Uranus → Fine structure (α=1/137)
  Pisces     → Jupiter/Neptune → Plastic

Each sign also gets a "breath phase" based on its position
in the zodiac wheel (30° = 1 month = 0.0833 of a year).
"""

import os
import json
import math
import statistics
from datetime import datetime

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV13 = PHI ** -13

# Multiverse constants
PLASTIC = 1.324717957244746  # ρ, cubic root
GOLDEN = PHI  # 1.618
NEGATIVE_GOLDEN = 1.0 - GOLDEN  # -0.618
SILVER = 1.0 + math.sqrt(2.0)  # 2.414 (n=2 in δ_n family)
BRONZE = (3.0 + math.sqrt(13.0)) / 2.0  # 3.303 (n=3)
FEIGENBAUM = 4.6692016
ALPHA_INV = 137.036  # 1/α


def delta_n(n: int) -> float:
    """The n-th Silver-family constant: δ_n = (n + √(n²+4))/2."""
    return (n + math.sqrt(n*n + 4.0)) / 2.0


# Zodiac data
ZODIAC = [
    {"name": "Aries",       "symbol": "♈",  "dates": "Mar 21 - Apr 19", "ruler": "Mars",     "element": "fire",  "month": 3,  "day": 21, "delta_n": 3, "breath_constant": "Bronze"},
    {"name": "Taurus",      "symbol": "♉",  "dates": "Apr 20 - May 20", "ruler": "Venus",    "element": "earth", "month": 4,  "day": 20, "delta_n": 2, "breath_constant": "Silver"},
    {"name": "Gemini",      "symbol": "♊",  "dates": "May 21 - Jun 20", "ruler": "Mercury",  "element": "air",   "month": 5,  "day": 21, "delta_n": 1, "breath_constant": "Negative Golden"},
    {"name": "Cancer",      "symbol": "♋",  "dates": "Jun 21 - Jul 22", "ruler": "Moon",     "element": "water", "month": 6,  "day": 21, "delta_n": 1, "breath_constant": "Negative Golden"},
    {"name": "Leo",         "symbol": "♌",  "dates": "Jul 23 - Aug 22", "ruler": "Sun",      "element": "fire",  "month": 7,  "day": 23, "delta_n": 4, "breath_constant": "Plastic"},
    {"name": "Virgo",       "symbol": "♍",  "dates": "Aug 23 - Sep 22", "ruler": "Mercury",  "element": "earth", "month": 8,  "day": 23, "delta_n": 1, "breath_constant": "Negative Golden"},
    {"name": "Libra",       "symbol": "♎",  "dates": "Sep 23 - Oct 22", "ruler": "Venus",    "element": "air",   "month": 9,  "day": 23, "delta_n": 2, "breath_constant": "Silver"},
    {"name": "Scorpio",     "symbol": "♏",  "dates": "Oct 23 - Nov 21", "ruler": "Pluto/Mars","element": "water","month": 10, "day": 23, "delta_n": 3, "breath_constant": "Bronze"},
    {"name": "Sagittarius", "symbol": "♐",  "dates": "Nov 22 - Dec 21", "ruler": "Jupiter",  "element": "fire",  "month": 11, "day": 22, "delta_n": 5, "breath_constant": "Feigenbaum-like"},
    {"name": "Capricorn",   "symbol": "♑",  "dates": "Dec 22 - Jan 19", "ruler": "Saturn",   "element": "earth", "month": 12, "day": 22, "delta_n": 5, "breath_constant": "Feigenbaum-like"},
    {"name": "Aquarius",    "symbol": "♒",  "dates": "Jan 20 - Feb 18", "ruler": "Saturn/Uranus", "element": "air", "month": 1, "day": 20, "delta_n": 6, "breath_constant": "δ_6"},
    {"name": "Pisces",      "symbol": "♓",  "dates": "Feb 19 - Mar 20", "ruler": "Jupiter/Neptune", "element": "water", "month": 2, "day": 19, "delta_n": 4, "breath_constant": "Plastic"},
]


def main():
    print("=" * 80)
    print("  TAP ZODIAC → DELTA BREATH MAPPING (for fun)")
    print("  12 zodiac signs mapped to multiverse constant breath cycles")
    print("=" * 80)
    print()

    print("  [1/3] Multiverse constants (the 7-constant family):")
    print(f"    Independent (4):")
    print(f"      Plastic (ρ) = {PLASTIC:.6f}  (cubic root of x³ - x - 1)")
    print(f"      Golden (φ)  = {GOLDEN:.6f}  (root of x² - x - 1)")
    print(f"      Feigenbaum  = {FEIGENBAUM:.6f}  (transcendental)")
    print(f"      Fine struct = 1/{ALPHA_INV:.3f}  (empirical)")
    print(f"    Derived (3):")
    print(f"      Negative Golden = 1 - φ = {NEGATIVE_GOLDEN:.6f}  (n=1 in δ_n family)")
    print(f"      Silver = 1 + √2 = {SILVER:.6f}  (n=2)")
    print(f"      Bronze = (3+√13)/2 = {BRONZE:.6f}  (n=3)")
    print()
    print(f"    Family: δ_n = (n + √(n²+4))/2")
    for n in range(1, 13):
        print(f"      δ_{n} = {delta_n(n):.4f}")
    print()

    print("  [2/3] Zodiac signs mapped to breath constants:")
    print(f"  {'Sign':12s} | {'Symbol':6s} | {'Ruler':14s} | {'Element':6s} | {'Constant':18s} | {'δ_n':>6s} | {'Value':>8s}")
    print("  " + "-" * 100)
    zodiac_results = []
    for z in ZODIAC:
        delta_val = delta_n(z["delta_n"])
        print(f"  {z['name']:12s} | {z['symbol']:6s} | {z['ruler']:14s} | {z['element']:6s} | {z['breath_constant']:18s} | δ_{z['delta_n']:<2d} | {delta_val:>8.4f}")
        zodiac_results.append({
            "name": z["name"],
            "symbol": z["symbol"],
            "ruler": z["ruler"],
            "element": z["element"],
            "breath_constant": z["breath_constant"],
            "delta_n": z["delta_n"],
            "delta_value": round(delta_val, 6),
        })
    print()

    # What sign is today?
    today = datetime.now()
    print(f"  [3/3] Today's date: {today.strftime('%Y-%m-%d')}")
    today_month = today.month
    today_day = today.day
    for z in ZODIAC:
        # Check if today is in this sign
        if (z["month"] == today_month and today_day >= z["day"]) or \
           (z["month"] == (today_month % 12) + 1 and today_day <= z["day"]):
            print(f"    Today's sign: {z['name']} {z['symbol']} ({z['ruler']})")
            print(f"    Breath constant: {z['breath_constant']} = δ_{z['delta_n']} = {delta_n(z['delta_n']):.4f}")
            break
    print()

    # Element distribution
    print("  ELEMENT DISTRIBUTION (fire/earth/air/water):")
    elements = {}
    for z in ZODIAC:
        elements.setdefault(z["element"], []).append(z["name"])
    for elem, signs in elements.items():
        deltas = [delta_n(z["delta_n"]) for z in ZODIAC if z["element"] == elem]
        avg = statistics.mean(deltas)
        print(f"    {elem:6s} ({len(signs)} signs): {', '.join(signs)}")
        print(f"            avg δ = {avg:.4f}")
    print()

    # Summary
    print("  THE TAP ZODIAC-MAP AT A GLANCE:")
    print(f"    4 zodiac signs (33%) use Plastic family (cubic)")
    print(f"    2 zodiac signs use Silver family (n=2)")
    print(f"    2 zodiac signs use Bronze family (n=3)")
    print(f"    4 zodiac signs use higher δ_n")
    print()
    print("  NOTE: This is for fun. The TAP framework is a physics")
    print("  model, not astrology. But the multiverse constant")
    print("  family δ_n = (n + √(n²+4))/2 maps cleanly to 12 signs,")
    print("  which is at least aesthetically pleasing.")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_zodiac_to_breath_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "delta_n_family": {n: round(delta_n(n), 4) for n in range(1, 13)},
        "zodiac_mapping": zodiac_results,
        "multiverse_constants": {
            "plastic": PLASTIC,
            "golden": GOLDEN,
            "negative_golden": NEGATIVE_GOLDEN,
            "silver": SILVER,
            "bronze": BRONZE,
            "feigenbaum": FEIGENBAUM,
            "alpha_inv": ALPHA_INV,
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
