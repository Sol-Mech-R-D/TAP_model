# -*- coding: utf-8 -*-
"""
tap_breath_per_body.py
=========================
TAP v5.3 — Breath Number N_B per Cosmic Body.

The framework defines:
  - Master N_B = 8 (chi² fit, Earth current cycle)
  - Per-Breath drift ε = φ⁻¹³ ≈ 0.001919
  - 523 Breaths per Meta-Breath (Tier 2)
  - 523 Meta-Breaths per Meta²-Breath (Tier 3)
  - Γ(N, s) = 1 + s·N·φ⁻¹³ (universal correction)

But each cosmic body has its own N_B depending on:
  - Age of the body (older = more breaths completed)
  - Sub-breath period (shorter = more breaths in same time)
  - Substrate density (more braid pairs = faster breath count)
  - Cosmic phase alignment (where in Meta-cycle we are)

This file builds the lookup table for:
  - Sun, Mercury, Venus, Earth, Moon, Mars, Jupiter, Saturn
  - Uranus, Neptune, Pluto
  - Galactic center, local stellar group
  - Proxima Centauri, Sirius, etc.

For each body we compute:
  - Age (Gyr)
  - Sub-breath period (days, using φ-rate scaling)
  - N_B = round(age / sub-breath_in_years)
  - Γ(N_B) per body
  - Breath phase (where in current Exhale)
"""

import os
import json
import math
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26
N_B_EARTH = 8  # chi² fit from breath_clock.py

# Solar system body ages (Gyr, formation time)
# For solar system bodies, use the age of the solar system
SOLAR_SYSTEM_AGE_GYR = 4.567e-3 * 1000  # = 4.567 Gyr

# Universal sub-breath coupling: T_sub = T_rotation × φ^(-n) where n is
# the body's "depth" in the cosmic cascade (per tap_cosmic_quantum_neuro.py)

# Body definitions
# Each entry:
#   name, rotation_period_days (sidereal), phi_depth (φ-power to apply),
#   age_gyr, type
BODIES = [
    # Solar System
    {
        "name": "Sun",
        "rotation_days": 25.38,        # sidereal rotation (equator)
        "phi_depth": 3,                # T_sun = T_solar × φ⁻³
        "age_gyr": 4.6,
        "type": "star (G2V)",
        "notes": "Per tap_cosmic_quantum_neuro.py: T = 27.2753 × φ⁻³ ≈ 6.44d"
    },
    {
        "name": "Mercury",
        "rotation_days": 58.646,       # 3:2 spin-orbit resonance
        "phi_depth": 4,
        "age_gyr": 4.5,
        "type": "rocky planet",
        "notes": "3:2 resonance with orbital period (87.97d)"
    },
    {
        "name": "Venus",
        "rotation_days": -243.025,     # retrograde
        "phi_depth": 4,
        "age_gyr": 4.5,
        "type": "rocky planet",
        "notes": "Retrograde rotation, very slow"
    },
    {
        "name": "Earth",
        "rotation_days": 1.0,          # 1 day
        "phi_depth": 4,                # T_earth = 1 × φ⁻⁴ × T_solar... actually uses 8.12d sub-breath
        "age_gyr": 4.54,
        "type": "rocky planet",
        "notes": "Primary reference. T_sub-breath = 8.1213 days (Earth-Moon beat)"
    },
    {
        "name": "Moon",
        "rotation_days": 27.3217,      # sidereal
        "phi_depth": 4,                # T_moon = 27.3217 × φ⁻⁴ ≈ 3.99d
        "age_gyr": 4.51,
        "type": "natural satellite",
        "notes": "Per tap_cosmic_quantum_neuro.py: T = 27.3217 × φ⁻⁴ ≈ 3.99d"
    },
    {
        "name": "Mars",
        "rotation_days": 1.026,        # ~24h 37min
        "phi_depth": 4,
        "age_gyr": 4.6,
        "type": "rocky planet",
        "notes": "Similar to Earth"
    },
    {
        "name": "Jupiter",
        "rotation_days": 0.4135,       # ~9h 55min
        "phi_depth": 13,               # T_jupiter = 4332.59 × φ⁻¹³ ≈ 8.30d
        "age_gyr": 4.6,
        "type": "gas giant",
        "notes": "Per tap_cosmic_quantum_neuro.py: T = 4332.59 × φ⁻¹³ ≈ 8.30d"
    },
    {
        "name": "Saturn",
        "rotation_days": 0.444,
        "phi_depth": 13,
        "age_gyr": 4.5,
        "type": "gas giant",
        "notes": "Orbital period 10,759 days ≈ 29.46 years"
    },
    {
        "name": "Uranus",
        "rotation_days": -0.718,       # retrograde
        "phi_depth": 13,
        "age_gyr": 4.5,
        "type": "ice giant",
        "notes": "Tilted 98°, retrograde"
    },
    {
        "name": "Neptune",
        "rotation_days": 0.671,
        "phi_depth": 13,
        "age_gyr": 4.5,
        "type": "ice giant",
        "notes": ""
    },
    {
        "name": "Pluto",
        "rotation_days": -6.387,       # retrograde
        "phi_depth": 13,
        "age_gyr": 4.5,
        "type": "dwarf planet",
        "notes": "Orbital period 248 yr"
    },
    # Galactic
    {
        "name": "Milky Way (galactic rotation)",
        "rotation_days": 2.3e8,        # 230 million years (1 galactic year)
        "phi_depth": 26,               # cosmic scale
        "age_gyr": 13.6,
        "type": "spiral galaxy",
        "notes": "T_galactic = 2.3e8 × φ⁻²⁶ days = ?"
    },
    {
        "name": "Sgr A* (galactic center)",
        "rotation_days": 0.000166,      # S2 orbit ~16 yr
        "phi_depth": 26,
        "age_gyr": 13.6,
        "type": "supermassive black hole",
        "notes": "S2 star orbital period = 16 yr"
    },
    {
        "name": "Local stellar group",
        "rotation_days": 1e10,         # very long
        "phi_depth": 26,
        "age_gyr": 13.6,
        "type": "stellar association",
        "notes": ""
    },
    # Nearby stars
    {
        "name": "Proxima Centauri",
        "rotation_days": 31.0,         # ~31 days
        "phi_depth": 4,
        "age_gyr": 4.85,
        "type": "red dwarf (M5.5V)",
        "notes": ""
    },
    {
        "name": "Sirius A",
        "rotation_days": 5.4,          # ~5.4 days
        "phi_depth": 4,
        "age_gyr": 0.24,
        "type": "main sequence (A1V)",
        "notes": "Younger star"
    },
    {
        "name": "Betelgeuse",
        "rotation_days": 36.0,         # very slow rotator
        "phi_depth": 4,
        "age_gyr": 0.0085,             # 8.5 Myr
        "type": "red supergiant",
        "notes": "Near end of life"
    },
    {
        "name": "Crab Pulsar",
        "rotation_days": 0.0331,       # 33 ms
        "phi_depth": 2,                # very fast
        "age_gyr": 0.00097,            # 970 yr
        "type": "neutron star",
        "notes": "Remnant of SN 1054"
    },
]


def compute_sub_breath(body: dict) -> float:
    """Compute the sub-breath period for a body."""
    T_rot = abs(body["rotation_days"])  # use absolute (some are retrograde)
    depth = body["phi_depth"]
    return T_rot * (PHI ** -depth)


def compute_n_b(body: dict) -> int:
    """
    Compute the breath number N_B for a body.

    N_B = age (years) / sub_breath (years)
    """
    age_yr = body["age_gyr"] * 1e9
    sub_breath_yr = compute_sub_breath(body) / 365.25
    if sub_breath_yr <= 0:
        return 0
    return round(age_yr / sub_breath_yr)


def compute_gamma(n_b: int, drift_sign: float = 1.0) -> float:
    """Breath correction factor Γ(N, s) = 1 + s·N·φ⁻¹³"""
    return 1.0 + drift_sign * n_b * PHI_INV13


def main():
    print("=" * 80)
    print("  TAP BREATH NUMBER N_B PER COSMIC BODY")
    print("  Universal lookup: which breath cycle is each body in?")
    print("=" * 80)
    print()

    print(f"  {'Body':28s} | {'Type':18s} | {'T_rot (d)':>10s} | {'T_sub (d)':>10s} | {'N_B':>4s} | {'Γ(N_B)':>10s}")
    print("  " + "-" * 100)

    body_data = []
    for body in BODIES:
        T_sub = compute_sub_breath(body)
        n_b = compute_n_b(body)
        gamma = compute_gamma(n_b)
        T_rot = abs(body["rotation_days"])
        print(f"  {body['name']:28s} | {body['type']:18s} | {T_rot:>10.4f} | {T_sub:>10.4f} | {n_b:>4d} | {gamma:>10.6f}")
        body_data.append({
            "name": body["name"],
            "type": body["type"],
            "rotation_days": T_rot,
            "sub_breath_days": round(T_sub, 4),
            "n_b": n_b,
            "gamma_n_b": round(gamma, 6),
            "age_gyr": body["age_gyr"],
            "phi_depth": body["phi_depth"],
            "notes": body["notes"],
        })

    # Comparison to Earth
    print()
    print(f"  Earth reference: N_B = {N_B_EARTH}, Γ = {compute_gamma(N_B_EARTH):.6f}")
    print(f"  (chi² fit, see tap_breath_clock.py)")
    print()

    # Earth vs other bodies
    earth_n_b = N_B_EARTH
    print("  N_B relative to Earth:")
    for d in body_data:
        if d['n_b'] > 0:
            ratio = d['n_b'] / earth_n_b
            print(f"    {d['name']:28s}: N_B / N_B_earth = {ratio:.2e}")
    print()

    # Meta-breath structure
    print("  Meta-breath structure (per tap_trans_cyclic_sweep.py):")
    print(f"    Breaths per Meta-Breath:  {int(PHI**13) + 2}")
    print(f"    Meta-Breaths per Meta²:  {int(PHI**13) + 2}")
    print(f"    Earth N_B = 8, Meta-Breath starts at N = {int(PHI**13) + 2}")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_breath_per_body_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "earth_n_b": N_B_EARTH,
        "phi_inv13": PHI_INV13,
        "n_b_per_meta_breath": int(PHI**13) + 2,
        "bodies": body_data,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
