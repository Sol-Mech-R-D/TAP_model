# -*- coding: utf-8 -*-
"""
tap_cross_body_coupling.py
=============================
TAP v5.3 — Cross-Body Coupling.

Each cosmic body's breath state couples to other bodies via:
  - Gravitational (Newton's law: F = G m1 m2 / r²)
  - Tidal (Moon raises tides on Earth)
  - Magnetic (Sun's field affects Earth's magnetosphere)
  - φ-rate (shared breath clock drift)
  - Resonance (sub-breath beat frequency)

This sim computes the per-body coupling matrix and shows
how Earth is coupled to other bodies at a given date.

Coupling strength between bodies A and B:
  C(A,B) = gravity * (1 + tidal) * (1 + magnetic) * φ_rate * resonance

We then propagate: a perturbation to A shifts B's breath by:
  ΔB = C(A,B) * ε_0 * perturbation_A
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV13 = PHI ** -13

# Use the per-body module
from tap_body_breath_states import BODIES, get_body_breath_state, get_body_n_b

# Astronomical body data: distance from Sun (km), orbital period (days)
# Mass (kg), radius (km)
BODY_ASTRO = {
    "Sun":      {"mass_kg": 1.989e30, "radius_km": 695700, "orbital_period_days": None},
    "Mercury":  {"mass_kg": 3.30e23,  "radius_km": 2440,   "orbital_period_days": 87.97,   "distance_au": 0.387},
    "Venus":    {"mass_kg": 4.87e24,  "radius_km": 6050,   "orbital_period_days": 224.7,   "distance_au": 0.723},
    "Earth":    {"mass_kg": 5.97e24,  "radius_km": 6371,   "orbital_period_days": 365.25,  "distance_au": 1.000},
    "Moon":     {"mass_kg": 7.35e22,  "radius_km": 1737,   "orbital_period_days": 27.32,   "distance_from_earth_km": 384400},
    "Mars":     {"mass_kg": 6.42e23,  "radius_km": 3389,   "orbital_period_days": 687.0,   "distance_au": 1.524},
    "Jupiter":  {"mass_kg": 1.90e27,  "radius_km": 69911,  "orbital_period_days": 4333.0,  "distance_au": 5.203},
    "Saturn":   {"mass_kg": 5.68e26,  "radius_km": 58232,  "orbital_period_days": 10759.0, "distance_au": 9.537},
    "Uranus":   {"mass_kg": 8.68e25,  "radius_km": 25362,  "orbital_period_days": 30687.0, "distance_au": 19.19},
    "Neptune":  {"mass_kg": 1.02e26,  "radius_km": 24622,  "orbital_period_days": 60190.0, "distance_au": 30.07},
}

# Newton's gravitational constant
G_NEWTON = 6.674e-11  # m³ / (kg s²)

# Astronomical unit in km
AU_KM = 1.496e8


def gravity_coupling(body_a: str, body_b: str) -> float:
    """
    Compute the gravitational coupling between two bodies.
    F = G * m_a * m_b / r²  (normalized to per unit mass)
    """
    if body_a not in BODY_ASTRO or body_b not in BODY_ASTRO:
        return 0.0
    a = BODY_ASTRO[body_a]
    b = BODY_ASTRO[body_b]

    # Distance
    if body_a == "Moon" and body_b == "Earth":
        r = BODY_ASTRO["Moon"]["distance_from_earth_km"] * 1e3
    elif body_a == "Earth" and body_b == "Moon":
        r = BODY_ASTRO["Moon"]["distance_from_earth_km"] * 1e3
    elif "distance_au" in a and "distance_au" in b:
        r = abs(a["distance_au"] - b["distance_au"]) * AU_KM * 1e3
    else:
        return 0.0

    if r == 0:
        return 0.0

    # Force per unit mass
    F = G_NEWTON * b["mass_kg"] / (r ** 2)
    return F


def tidal_coupling(body_a: str, body_b: str) -> float:
    """
    Tidal coupling: body_a raises tides on body_b.
    Tidal force ∝ m_a / r³ (gradient of gravitational field)
    """
    if body_a not in BODY_ASTRO or body_b not in BODY_ASTRO:
        return 0.0
    a = BODY_ASTRO[body_a]
    b = BODY_ASTRO[body_b]

    if body_a == "Moon" and body_b == "Earth":
        r = BODY_ASTRO["Moon"]["distance_from_earth_km"] * 1e3
    elif body_a == "Earth" and body_b == "Moon":
        r = BODY_ASTRO["Moon"]["distance_from_earth_km"] * 1e3
    elif "distance_au" in a and "distance_au" in b:
        r = abs(a["distance_au"] - b["distance_au"]) * AU_KM * 1e3
    else:
        return 0.0

    if r == 0:
        return 0.0

    tidal = a["mass_kg"] / (r ** 3)
    return tidal


def resonance_coupling(body_a: str, body_b: str) -> float:
    """
    Resonance coupling: 1 / (1 + |1/T_a - 1/T_b|)
    Maximum when periods are close (1.0), decreases as they diverge.
    """
    if body_a not in BODIES or body_b not in BODIES:
        return 0.0
    a = BODIES[body_a]
    b = BODIES[body_b]
    T_a = abs(a["rotation_days"]) * (PHI ** -a["phi_depth"])
    T_b = abs(b["rotation_days"]) * (PHI ** -b["phi_depth"])
    if T_a == 0 or T_b == 0:
        return 0.0
    beat = abs(1.0/T_a - 1.0/T_b)
    # Normalize: beat = 0 means perfect resonance (1.0), beat = 1 means no resonance (0.0)
    return 1.0 / (1.0 + beat * 10)  # scale factor for visibility


def phi_rate_coupling(body_a: str, body_b: str) -> float:
    """
    φ-rate coupling: bodies share the breath clock drift.
    Coupling strength ∝ 1 / |n_a - n_b| (similar N_B = stronger coupling).
    """
    n_a = get_body_n_b(body_a)
    n_b = get_body_n_b(body_b)
    if n_a == 0 or n_b == 0:
        return 0.0
    ratio = max(n_a, n_b) / min(n_a, n_b)
    return 1.0 / (1.0 + math.log10(ratio))


def total_coupling(body_a: str, body_b: str) -> float:
    """Total coupling between two bodies (log scale, normalized)."""
    if body_a == body_b:
        return 1.0
    grav = gravity_coupling(body_a, body_b)
    tidal = tidal_coupling(body_a, body_b)
    resonance = resonance_coupling(body_a, body_b)
    phi = phi_rate_coupling(body_a, body_b)
    # Log scale to handle huge range
    total = math.log10(grav + 1e-30) * 0.1 + math.log10(tidal + 1e-30) * 0.1 + resonance + phi
    return total


def main():
    print("=" * 80)
    print("  TAP CROSS-BODY COUPLING MATRIX")
    print("  Earth is coupled to Sun, Moon, planets via gravity, tide, resonance, phi")
    print("=" * 80)
    print()

    today = datetime(2026, 7, 2, 12, 0)
    solar_system_bodies = ["Sun", "Mercury", "Venus", "Earth", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]

    # Compute coupling matrix
    print("  Pairwise coupling strengths (log-normalized, higher = stronger):")
    print()
    print(f"  {'':12s}", end="")
    for b in solar_system_bodies:
        print(f"  {b:>8s}", end="")
    print()
    print("  " + "-" * 100)
    for a in solar_system_bodies:
        print(f"  {a:12s}", end="")
        for b in solar_system_bodies:
            c = total_coupling(a, b)
            print(f"  {c:>8.3f}", end="")
        print()
    print()

    # Earth-centric analysis
    print("  EARTH'S COUPLING TO OTHER BODIES:")
    print(f"  {'Body':12s} | {'Gravity':>14s} | {'Tidal':>18s} | {'Resonance':>10s} | {'φ-rate':>8s} | {'Total':>8s}")
    print("  " + "-" * 100)
    coupling_data = []
    for body in solar_system_bodies:
        if body == "Earth":
            continue
        grav = gravity_coupling("Earth", body)
        tidal = tidal_coupling(body, "Earth")
        res = resonance_coupling("Earth", body)
        phi = phi_rate_coupling("Earth", body)
        total = total_coupling("Earth", body)
        print(f"  {body:12s} | {grav:>14.4e} | {tidal:>18.4e} | {res:>10.4f} | {phi:>8.4f} | {total:>8.3f}")
        coupling_data.append({
            "body": body,
            "gravity": grav,
            "tidal": tidal,
            "resonance": res,
            "phi_rate": phi,
            "total": total,
        })
    print()

    # Top 3 strongest
    sorted_c = sorted(coupling_data, key=lambda x: x['total'], reverse=True)
    print("  Top 3 strongest coupling to Earth:")
    for c in sorted_c[:3]:
        print(f"    {c['body']:10s}: total = {c['total']:.3f} (tidal: {c['tidal']:.2e}, res: {c['resonance']:.3f}, φ: {c['phi_rate']:.3f})")
    print()

    # Show the Sun-Earth-Moon interaction
    print("  SUN-EARTH-MOON THREE-BODY SYSTEM:")
    earth_state = get_body_breath_state("Earth", today)
    moon_state = get_body_breath_state("Moon", today)
    sun_state = get_body_breath_state("Sun", today)
    print(f"    Earth N_B = {earth_state['n_b']:.2e}, ψ = {earth_state['psi']:.4f}, drift_sign = {earth_state['drift_sign']}")
    print(f"    Moon  N_B = {moon_state['n_b']:.2e}, ψ = {moon_state['psi']:.4f}, drift_sign = {moon_state['drift_sign']}")
    print(f"    Sun   N_B = {sun_state['n_b']:.2e}, ψ = {sun_state['psi']:.4f}, drift_sign = {sun_state['drift_sign']}")
    print(f"    Earth-Moon coupling: {total_coupling('Earth', 'Moon'):.3f}")
    print(f"    Earth-Sun coupling: {total_coupling('Earth', 'Sun'):.3f}")
    print()

    # Forward 30 days
    print("  FORWARD 30-DAY EARTH BREATH EVOLUTION (with Moon-Sun coupling):")
    forward = []
    for d in range(30):
        date = today + timedelta(days=d)
        earth = get_body_breath_state("Earth", date)
        moon = get_body_breath_state("Moon", date)
        # Effective Earth breath includes Moon and Sun coupling
        moon_c = total_coupling("Earth", "Moon")
        sun_c = total_coupling("Earth", "Sun")
        # Effective psi is shifted by Moon and Sun
        eff_psi = earth['psi'] + moon_c * (moon['psi'] - earth['psi']) * 0.1 + sun_c * (sun_state['psi'] - earth['psi']) * 0.1
        eff_psi = eff_psi % 1.0
        forward.append({
            "date": date.strftime("%Y-%m-%d"),
            "earth_psi": round(earth['psi'], 4),
            "moon_psi": round(moon['psi'], 4),
            "eff_psi": round(eff_psi, 4),
        })
    for f in forward[::5]:
        print(f"    {f['date']}  Earth ψ={f['earth_psi']:.3f}  Moon ψ={f['moon_psi']:.3f}  Effective ψ={f['eff_psi']:.3f}")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_cross_body_coupling_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "bodies": solar_system_bodies,
        "coupling_matrix": {
            a: {b: round(total_coupling(a, b), 4) for b in solar_system_bodies}
            for a in solar_system_bodies
        },
        "earth_coupling": coupling_data,
        "earth_moon_sun_states": {
            "earth": earth_state,
            "moon": moon_state,
            "sun": sun_state,
        },
        "forward_30d_eff_psi": forward,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
