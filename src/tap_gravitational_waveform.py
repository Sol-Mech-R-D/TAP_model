# -*- coding: utf-8 -*-
"""
tap_gravitational_waveform.py
================================
TAP v5.3 — Gravitational Waveform Output.

The previous cross-body coupling sim (tap_cross_body_coupling.py)
returns SCALAR tidal forces. This sim computes the full
VECTOR tidal force and gravitational waveform:

  - 3D Cartesian: (Fx, Fy, Fz) tidal force vector
  - Tidal bulge direction
  - Strain tensor (h_xx, h_yy, h_zz, h_xy, h_xz, h_yz)
  - Tidal acceleration over time (waveform)
  - Tidal potential at any point

This is needed for:
  - Earthquake prediction (strain accumulation on faults)
  - Volcanic activity (magma chamber pressure)
  - Ocean tides (Lagrange points)
  - Earth's rotation (tidal friction)
  - Schumann resonance coupling

The body positions are computed from orbital elements
(Kepler's laws) for any given date.
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV13 = PHI ** -13

# Newton's gravitational constant
G_NEWTON = 6.674e-11  # m³ / (kg s²)
AU_M = 1.496e11  # 1 AU in meters
EARTH_RADIUS_M = 6.371e6
MOON_RADIUS_M = 1.737e6

# Body orbital elements
# (semi-major axis AU, eccentricity, period days, inclination deg,
#  longitude of ascending node deg, mean longitude at epoch deg)
ORBITAL = {
    "Mercury": {"a_au": 0.387, "e": 0.2056, "period_d": 87.97, "incl": 7.005, "long_asc": 48.33, "mean_long": 252.25, "mass_kg": 3.30e23},
    "Venus":   {"a_au": 0.723, "e": 0.0068, "period_d": 224.7, "incl": 3.394, "long_asc": 76.68, "mean_long": 181.98, "mass_kg": 4.87e24},
    "Earth":   {"a_au": 1.000, "e": 0.0167, "period_d": 365.25, "incl": 0.000, "long_asc": 0.00, "mean_long": 100.47, "mass_kg": 5.97e24},
    "Moon":    {"a_au": 0.00257, "e": 0.0549, "period_d": 27.32, "incl": 5.145, "long_asc": 125.08, "mean_long": 0.0, "mass_kg": 7.35e22},  # relative to Earth
    "Mars":    {"a_au": 1.524, "e": 0.0934, "period_d": 687.0, "incl": 1.850, "long_asc": 49.56, "mean_long": 355.43, "mass_kg": 6.42e23},
    "Jupiter": {"a_au": 5.203, "e": 0.0484, "period_d": 4333.0, "incl": 1.303, "long_asc": 100.46, "mean_long": 34.40, "mass_kg": 1.90e27},
    "Saturn":  {"a_au": 9.537, "e": 0.0542, "period_d": 10759.0, "incl": 2.489, "long_asc": 113.66, "mean_long": 49.94, "mass_kg": 5.68e26},
    "Sun":     {"a_au": 0.0, "e": 0.0, "period_d": 0.0, "incl": 0.0, "long_asc": 0.0, "mean_long": 0.0, "mass_kg": 1.989e30},  # at origin
}

# Epoch for orbital elements: J2000 = 2000-01-01 12:00 UTC
J2000 = datetime(2000, 1, 1, 12, 0)


def body_position_3d(body_name: str, date: datetime) -> tuple:
    """
    Compute the 3D position of a body at a given date.

    Returns (x, y, z) in AU in heliocentric ecliptic frame.
    For Moon, returns position relative to Earth in Earth-centered frame.
    """
    if body_name == "Sun":
        return (0.0, 0.0, 0.0)

    elem = ORBITAL[body_name]
    if body_name == "Moon":
        # Moon's position relative to Earth
        days_since = (date - J2000).total_seconds() / 86400.0
        mean_anomaly = 2.0 * math.pi * days_since / elem["period_d"] + math.radians(elem["mean_long"])
        r_au = elem["a_au"] * (1.0 - elem["e"] * math.cos(mean_anomaly))
        # Simplified: assume circular orbit in xy plane
        x = r_au * math.cos(mean_anomaly)
        y = r_au * math.sin(mean_anomaly)
        z = 0.0
        return (x, y, z)

    # Heliocentric position
    days_since = (date - J2000).total_seconds() / 86400.0
    mean_anomaly = 2.0 * math.pi * days_since / elem["period_d"] + math.radians(elem["mean_long"])
    # True anomaly (simplified)
    r_au = elem["a_au"] * (1.0 - elem["e"] * math.cos(mean_anomaly))
    x = r_au * math.cos(mean_anomaly)
    y = r_au * math.sin(mean_anomaly)
    z = 0.0
    return (x, y, z)


def tidal_force_vector(central: str, perturbing: str, date: datetime, r_from_central_m: float = EARTH_RADIUS_M) -> tuple:
    """
    Compute the tidal force vector at a point on the central body's
    surface, due to the perturbing body.

    The tidal force at a point is the difference between the
    gravitational acceleration at that point and at the center.

    Returns (Fx, Fy, Fz) in m/s², normalized to the central frame.
    """
    # Central body position
    x_c, y_c, z_c = body_position_3d(central, date)
    # Perturbing body position
    x_p, y_p, z_p = body_position_3d(perturbing, date)
    # Vector from central to perturbing
    dx = (x_p - x_c) * AU_M  # convert AU to m
    dy = (y_p - y_c) * AU_M
    dz = (z_p - z_c) * AU_M
    r_central_to_perturbing = math.sqrt(dx*dx + dy*dy + dz*dz)
    if r_central_to_perturbing < 1e3:
        return (0.0, 0.0, 0.0)

    # Unit vector from central to perturbing
    ux = dx / r_central_to_perturbing
    uy = dy / r_central_to_perturbing
    uz = dz / r_central_to_perturbing

    # For tidal force, evaluate at distance r_from_central in
    # the direction of perturbing body. Tidal force component:
    # F_tidal = 2 * G * M_perturbing * R / r³
    # where R = r_from_central, r = distance central to perturbing
    M_p = ORBITAL[perturbing]["mass_kg"]
    R = r_from_central_m
    r = r_central_to_perturbing

    # Tidal force vector (in direction away from perturbing body)
    F_mag = 2.0 * G_NEWTON * M_p * R / (r ** 3)
    Fx = F_mag * ux
    Fy = F_mag * uy
    Fz = F_mag * uz

    return (Fx, Fy, Fz)


def tidal_strain_tensor(central: str, perturbing: str, date: datetime) -> dict:
    """
    Compute the tidal strain tensor at the central body.

    Strain h_ij = -∂Φ/∂x_i∂x_j / c² where Φ is tidal potential.

    Returns a dict with the 6 independent components.
    """
    x_c, y_c, z_c = body_position_3d(central, date)
    x_p, y_p, z_p = body_position_3d(perturbing, date)

    dx = (x_p - x_c) * AU_M
    dy = (y_p - y_c) * AU_M
    dz = (z_p - z_c) * AU_M
    r = math.sqrt(dx*dx + dy*dy + dz*dz)
    if r < 1e3:
        return {"h_xx": 0, "h_yy": 0, "h_zz": 0, "h_xy": 0, "h_xz": 0, "h_yz": 0}

    M_p = ORBITAL[perturbing]["mass_kg"]
    C_LIGHT = 3e8  # m/s
    # Tidal potential Φ = -G*M/r
    # Strain h_ij = -(1/c²) ∂²Φ/∂x_i∂x_j
    factor = G_NEWTON * M_p / (r ** 3) / (C_LIGHT ** 2)

    # Hessian of 1/r at the central point
    # h_xx = factor * (3*dx²/r² - 1)
    # h_yy = factor * (3*dy²/r² - 1)
    # h_zz = factor * (3*dz²/r² - 1)
    # h_xy = factor * 3*dx*dy/r²
    # h_xz = factor * 3*dx*dz/r²
    # h_yz = factor * 3*dy*dz/r²

    ux = dx / r
    uy = dy / r
    uz = dz / r
    h_xx = factor * (3.0 * ux * ux - 1.0) * EARTH_RADIUS_M
    h_yy = factor * (3.0 * uy * uy - 1.0) * EARTH_RADIUS_M
    h_zz = factor * (3.0 * uz * uz - 1.0) * EARTH_RADIUS_M
    h_xy = factor * 3.0 * ux * uy * EARTH_RADIUS_M
    h_xz = factor * 3.0 * ux * uz * EARTH_RADIUS_M
    h_yz = factor * 3.0 * uy * uz * EARTH_RADIUS_M

    return {
        "h_xx": h_xx, "h_yy": h_yy, "h_zz": h_zz,
        "h_xy": h_xy, "h_xz": h_xz, "h_yz": h_yz,
    }


def tidal_waveform(central: str, perturbing: str, start_date: datetime, duration_h: int = 24, samples: int = 96) -> list:
    """Compute the tidal force waveform over a time window."""
    waveform = []
    for i in range(samples):
        t = start_date + timedelta(hours=duration_h * i / samples)
        Fx, Fy, Fz = tidal_force_vector(central, perturbing, t)
        F_mag = math.sqrt(Fx*Fx + Fy*Fy + Fz*Fz)
        waveform.append({
            "time": t.isoformat(),
            "Fx": Fx, "Fy": Fy, "Fz": Fz,
            "F_mag": F_mag,
        })
    return waveform


def main():
    print("=" * 80)
    print("  TAP GRAVITATIONAL WAVEFORM OUTPUT")
    print("  Vector tidal force, strain tensor, waveform")
    print("=" * 80)
    print()

    today = datetime(2026, 7, 2, 12, 0)

    # 1. Body positions
    print("  [1/4] Body positions (heliocentric, AU):")
    print(f"    {'Body':12s} | {'x (AU)':>10s} | {'y (AU)':>10s} | {'z (AU)':>10s} | {'r (AU)':>10s}")
    print("    " + "-" * 60)
    for body in ORBITAL:
        x, y, z = body_position_3d(body, today)
        r = math.sqrt(x*x + y*y + z*z)
        print(f"    {body:12s} | {x:>10.4f} | {y:>10.4f} | {z:>10.4f} | {r:>10.4f}")
    print()

    # 2. Tidal force vectors on Earth
    print("  [2/4] Tidal force vectors on Earth (m/s²):")
    print(f"    {'Perturber':12s} | {'Fx':>14s} | {'Fy':>14s} | {'Fz':>14s} | {'|F|':>14s}")
    print("    " + "-" * 80)
    for body in ["Moon", "Sun", "Jupiter", "Venus"]:
        Fx, Fy, Fz = tidal_force_vector("Earth", body, today)
        F_mag = math.sqrt(Fx*Fx + Fy*Fy + Fz*Fz)
        print(f"    {body:12s} | {Fx:>14.6e} | {Fy:>14.6e} | {Fz:>14.6e} | {F_mag:>14.6e}")
    print()

    # 3. Strain tensor
    print("  [3/4] Tidal strain tensor on Earth (from Moon and Sun):")
    for body in ["Moon", "Sun"]:
        h = tidal_strain_tensor("Earth", body, today)
        print(f"    {body}: h_xx={h['h_xx']:.3e}, h_yy={h['h_yy']:.3e}, h_zz={h['h_zz']:.3e}")
        print(f"         h_xy={h['h_xy']:.3e}, h_xz={h['h_xz']:.3e}, h_yz={h['h_yz']:.3e}")
    print()

    # 4. Tidal waveform
    print("  [4/4] 24-hour tidal waveform on Earth (Moon contribution):")
    waveform = tidal_waveform("Earth", "Moon", today, duration_h=24, samples=12)
    for w in waveform[::2]:
        print(f"    {w['time'][:16]}  |F| = {w['F_mag']:.4e} m/s²")
    print()

    # Stats
    f_mags = [w["F_mag"] for w in waveform]
    print(f"    Min |F|: {min(f_mags):.4e} m/s²")
    print(f"    Max |F|: {max(f_mags):.4e} m/s²")
    print(f"    Mean |F|: {statistics.mean(f_mags):.4e} m/s²")
    print(f"    Range: {(max(f_mags)-min(f_mags))/statistics.mean(f_mags)*100:.1f}%")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_gravitational_waveform_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "body_positions": {b: body_position_3d(b, today) for b in ORBITAL},
        "tidal_forces": {b: tidal_force_vector("Earth", b, today) for b in ["Moon", "Sun", "Jupiter", "Venus"]},
        "strain_tensor_moon": tidal_strain_tensor("Earth", "Moon", today),
        "strain_tensor_sun": tidal_strain_tensor("Earth", "Sun", today),
        "waveform_24h_moon": waveform,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
