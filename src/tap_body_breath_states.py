# -*- coding: utf-8 -*-
"""
tap_body_breath_states.py
============================
TAP v5.3 — Per-Body Breath State Library.

Builds on tap_breath_per_body.py. For each cosmic body
(Sun, Earth, Moon, Mars, etc.), computes:

  - N_B: which breath cycle the body is in
  - Γ(N_B): the breath correction factor
  - ψ: breath phase (where in current Exhale)
  - s_setpoint: analogous to epigenetic setpoint
  - t_setpoint: temporal setpoint
  - drift_sign: drift direction (+1 or -1)
  - breath_at(date): full state at a given date
  - body_drift(date): per-body drift contribution

The breath state is analogous to the epigenetic state in
tap_epigenetic_cosmic_cascade.py but at the cosmic-body level.

Usage:
    from tap_body_breath_states import get_body_breath_state
    state = get_body_breath_state("Earth", datetime(2026, 7, 2))
    print(state['n_b'], state['gamma_n_b'], state['psi'])
"""

import os
import json
import math
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26

N_B_EARTH = 8  # chi² fit reference

# Body registry (subset of tap_breath_per_body.py)
BODIES = {
    "Sun":      {"rotation_days": 25.38,    "phi_depth": 3,  "age_gyr": 4.6,  "type": "star",         "core_radius_km": 139000,  "core_mass_kg": 1.989e30},
    "Mercury":  {"rotation_days": 58.646,   "phi_depth": 4,  "age_gyr": 4.5,  "type": "rocky planet", "core_radius_km": 2440,    "core_mass_kg": 3.30e23},
    "Venus":    {"rotation_days": 243.025,  "phi_depth": 4,  "age_gyr": 4.5,  "type": "rocky planet", "core_radius_km": 6050,    "core_mass_kg": 4.87e24},
    "Earth":    {"rotation_days": 1.0,      "phi_depth": 4,  "age_gyr": 4.54, "type": "rocky planet", "core_radius_km": 6371,    "core_mass_kg": 5.97e24},
    "Moon":     {"rotation_days": 27.3217,  "phi_depth": 4,  "age_gyr": 4.51, "type": "satellite",    "core_radius_km": 1737,    "core_mass_kg": 7.35e22},
    "Mars":     {"rotation_days": 1.026,    "phi_depth": 4,  "age_gyr": 4.6,  "type": "rocky planet", "core_radius_km": 3389,    "core_mass_kg": 6.42e23},
    "Jupiter":  {"rotation_days": 0.4135,   "phi_depth": 13, "age_gyr": 4.6,  "type": "gas giant",    "core_radius_km": 69911,   "core_mass_kg": 1.90e27},
    "Saturn":   {"rotation_days": 0.444,     "phi_depth": 13, "age_gyr": 4.5,  "type": "gas giant",    "core_radius_km": 58232,   "core_mass_kg": 5.68e26},
    "Uranus":   {"rotation_days": 0.718,    "phi_depth": 13, "age_gyr": 4.5,  "type": "ice giant",    "core_radius_km": 25362,   "core_mass_kg": 8.68e25},
    "Neptune":  {"rotation_days": 0.671,    "phi_depth": 13, "age_gyr": 4.5,  "type": "ice giant",    "core_radius_km": 24622,   "core_mass_kg": 1.02e26},
    "Proxima Centauri": {"rotation_days": 31.0, "phi_depth": 4, "age_gyr": 4.85, "type": "red dwarf", "core_radius_km": 100000, "core_mass_kg": 2.4e29},
    "Sirius A": {"rotation_days": 5.4,       "phi_depth": 4,  "age_gyr": 0.24, "type": "A1V star",     "core_radius_km": 1.2e6,   "core_mass_kg": 2.02e30},
    "Crab Pulsar": {"rotation_days": 0.0331, "phi_depth": 2, "age_gyr": 9.7e-4, "type": "neutron star", "core_radius_km": 10,    "core_mass_kg": 1.4e30},
}

# Anchor for breath phase: solstice 2026 (arbitrary)
PHASE_ANCHOR = datetime(2026, 6, 21, 19, 46)


def get_body_n_b(body_name: str) -> int:
    """Get N_B for a body (computed from age and sub-breath)."""
    body = BODIES[body_name]
    age_yr = body["age_gyr"] * 1e9
    T_sub = abs(body["rotation_days"]) * (PHI ** -body["phi_depth"])
    sub_breath_yr = T_sub / 365.25
    if sub_breath_yr <= 0:
        return 0
    return round(age_yr / sub_breath_yr)


def get_body_breath_state(body_name: str, date: datetime = None) -> dict:
    """
    Get the full breath state of a body at a given date.

    Returns:
      - name, type
      - n_b: which breath cycle
      - gamma_n_b: breath correction factor
      - psi: phase in current Exhale [0, 1]
      - s_setpoint: epigenetic-style setpoint [0, 1]
      - t_setpoint: temporal setpoint
      - drift_sign: +1 or -1
      - sub_breath_days: sub-breath period
      - age_gyr: age
    """
    if date is None:
        date = datetime.now()
    body = BODIES[body_name]
    n_b = get_body_n_b(body_name)
    gamma = 1.0 + 1.0 * n_b * PHI_INV13  # drift_sign=+1 (default)

    # Phase
    T_sub = abs(body["rotation_days"]) * (PHI ** -body["phi_depth"])
    days_since_anchor = (date - PHASE_ANCHOR).total_seconds() / 86400.0
    phase = (days_since_anchor / T_sub) * 2.0 * math.pi
    phase = (phase + math.pi) % (2.0 * math.pi) - math.pi
    psi = phase / (2.0 * math.pi) + 0.5  # normalize to [0, 1]

    # Setpoints: derived from psi
    s_setpoint = 0.5 + 0.5 * math.cos(phase)
    t_setpoint = 0.5 + 0.5 * math.sin(phase)

    # Drift sign: different per body type
    drift_sign = +1 if body["type"] in ("star", "neutron star", "red dwarf", "A1V star") else -1
    gamma_with_sign = 1.0 + drift_sign * n_b * PHI_INV13

    return {
        "name": body_name,
        "type": body["type"],
        "date": date.isoformat(),
        "n_b": n_b,
        "gamma_n_b": round(gamma_with_sign, 6),
        "psi": round(psi, 6),
        "phase_rad": round(phase, 4),
        "s_setpoint": round(s_setpoint, 4),
        "t_setpoint": round(t_setpoint, 4),
        "drift_sign": drift_sign,
        "sub_breath_days": round(T_sub, 4),
        "age_gyr": body["age_gyr"],
    }


def get_body_drift(body_name: str, date: datetime) -> float:
    """
    Get the per-body drift contribution at a given date.
    ε_body = ε_0 * n_b * cos(phase) * drift_sign
    """
    state = get_body_breath_state(body_name, date)
    return state["gamma_n_b"] * math.cos(state["phase_rad"])


def main():
    print("=" * 80)
    print("  TAP PER-BODY BREATH STATES")
    print("  Full state (N_B, Γ, ψ, setpoints) per cosmic body")
    print("=" * 80)
    print()

    today = datetime(2026, 7, 2, 12, 0)

    print(f"  {'Body':20s} | {'N_B':>12s} | {'Γ':>10s} | {'ψ':>6s} | {'s_sp':>5s} | {'t_sp':>5s} | {'T_sub (d)':>10s} | {'drift':>8s}")
    print("  " + "-" * 100)

    body_data = []
    for name in BODIES:
        state = get_body_breath_state(name, today)
        drift = get_body_drift(name, today)
        n_b_str = f"{state['n_b']:.3e}" if state['n_b'] > 1e6 else f"{state['n_b']}"
        print(f"  {name:20s} | {n_b_str:>12s} | {state['gamma_n_b']:>10.6f} | {state['psi']:>6.3f} | {state['s_setpoint']:>5.2f} | {state['t_setpoint']:>5.2f} | {state['sub_breath_days']:>10.4f} | {drift:>8.4f}")
        body_data.append(state)

    print()

    # Earth reference
    earth_state = get_body_breath_state("Earth", today)
    print(f"  Earth reference: N_B = {earth_state['n_b']}, Γ = {earth_state['gamma_n_b']:.6f}")
    print(f"  Earth's ψ (position in Exhale): {earth_state['psi']:.4f}")
    print()

    # Forward 30 days
    print("  Forward 30 days — Earth's breath state evolution:")
    forward = []
    for d in range(30):
        date = today + timedelta(days=d)
        st = get_body_breath_state("Earth", date)
        forward.append({
            "date": date.strftime("%Y-%m-%d"),
            "psi": st["psi"],
            "s_setpoint": st["s_setpoint"],
            "t_setpoint": st["t_setpoint"],
            "gamma": st["gamma_n_b"],
        })
    for f in forward[::5]:
        print(f"    {f['date']}  ψ={f['psi']:.4f}  s={f['s_setpoint']:.3f}  t={f['t_setpoint']:.3f}  Γ={f['gamma']:.6f}")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_body_breath_states_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "anchor": PHASE_ANCHOR.isoformat(),
        "earth_n_b_reference": N_B_EARTH,
        "body_states": body_data,
        "earth_forward_30d": forward,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
