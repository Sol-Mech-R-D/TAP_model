# -*- coding: utf-8 -*-
"""
tap_schumann_resonance.py
=============================
TAP v5.3 — Schumann Resonance Coupling.

The Schumann resonance is the fundamental electromagnetic
mode of the Earth-ionosphere cavity. The fundamental
frequency is f_1 = 7.83 Hz (the alpha-theta brain wave
band), with harmonics at 14.3, 20.8, 27.3, 33.8 Hz, etc.

In TAP terms, the Schumann resonance is the BREATH of
the Earth as a whole — the standing wave in the
Earth-ionosphere cavity. It couples to:

  - Brain waves (alpha-theta band, 7.83 Hz)
  - Cosmic breath (φ⁻¹³ rate)
  - Per-body N_B (Schumann is a function of N_B)
  - Sub-breath clock (Schumann is the 8.121d envelope)

This sim computes the Schumann resonance and shows how
it modulates the gravitational waveform and per-body
breath state.

The Schumann amplitude is also affected by:
  - Solar activity (Kp index modulates the ionosphere)
  - Lunar position (Moon affects the ionosphere via tides)
  - Time of day (the cavity is asymmetric in daylight)

The framework predicts:
  - Schumann amplitude correlates with breath clock
  - Schumann-Kp coupling: high Kp → stronger Schumann
  - Schumann-brain coupling: 7.83 Hz entrains alpha band
"""

import os
import json
import math
import urllib.request
import statistics
from datetime import datetime, timedelta

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
C_LIGHT = 3e8  # m/s
EARTH_RADIUS_M = 6.371e6
IONOSPHERE_HEIGHT_M = 1e5  # ~100 km (F-layer)

# Schumann fundamental and harmonics
SCHUMANN_FREQS = [7.83, 14.3, 20.8, 27.3, 33.8, 39.0, 45.0]


def schumann_wavelength(n: int = 1) -> float:
    """Wavelength of nth Schumann mode (circumference / n)."""
    circumference = 2.0 * math.pi * (EARTH_RADIUS_M + IONOSPHERE_HEIGHT_M / 2.0)
    return circumference / n


def schumann_frequency(n: int = 1) -> float:
    """Frequency of nth Schumann mode (c / wavelength)."""
    return C_LIGHT / schumann_wavelength(n)


def schumann_phase_angle(date: datetime) -> float:
    """
    Compute the phase angle of the Schumann fundamental at
    a given date. The Schumann resonance drifts slowly with
    solar activity, ionosphere height, etc.

    The TAP prediction: the Schumann phase is locked to the
    sub-breath clock (8.121d). So:
      phase = 2π * (t - t_anchor) / 8.121d
    """
    days_since = (date - datetime(2026, 6, 21)).total_seconds() / 86400.0
    return (days_since / 8.12133) * 2.0 * math.pi


def schumann_amplitude(date: datetime, kp: float = 2.0) -> dict:
    """
    Compute the Schumann amplitude at a given date and Kp.

    The amplitude depends on:
    - Solar activity (Kp)
    - Lunar position
    - Time of day

    Returns the amplitude of each harmonic (mV/km).
    """
    # Base amplitude
    base = 0.5  # mV/km at quiet conditions
    # Kp amplifies the amplitude (more ionospheric activity)
    kp_factor = 1.0 + 0.3 * (kp - 2.0)  # baseline Kp=2
    # Lunar tide modulates the ionosphere
    lunar_phase = schumann_phase_angle(date)  # use sub-breath as proxy
    lunar_factor = 1.0 + 0.1 * math.cos(lunar_phase)
    # Time of day factor
    hour = date.hour + date.minute / 60.0
    tod_factor = 1.0 + 0.2 * math.sin(hour / 24.0 * 2.0 * math.pi)
    # Combined
    amps = {}
    for n, freq in enumerate(SCHUMANN_FREQS, start=1):
        # Higher harmonics have lower amplitude
        harmonic_factor = 1.0 / math.sqrt(n)
        amp = base * kp_factor * lunar_factor * tod_factor * harmonic_factor
        amps[f"f_{freq}"] = round(amp, 4)
    return amps


def schumann_to_breath_coupling(schumann_amps: dict) -> dict:
    """
    Compute the coupling between Schumann amplitude and
    breath clock state.

    The framework predicts: Schumann_amplitude ∝ γ(N_B) × breath_phase
    """
    earth_breath_phase = schumann_phase_angle(datetime.now())
    # Coupling: amplitude of f_7.83 modulates the breath clock
    f7 = schumann_amps.get("f_7.83", 0.5)
    coupling = f7 * math.cos(earth_breath_phase)
    return {
        "f7_amplitude": f7,
        "breath_phase": round(earth_breath_phase, 4),
        "coupling": round(coupling, 6),
    }


def schumann_waveform(date: datetime, duration_s: int = 60, kp: float = 2.0) -> list:
    """Compute the Schumann waveform over a duration."""
    waveform = []
    for i in range(duration_s):
        t = date + timedelta(seconds=i)
        amps = schumann_amplitude(t, kp)
        # Sum the contributions
        total = sum(amps.values())
        # Time of day factor
        hour = t.hour + t.minute / 60.0 + t.second / 3600.0
        tod_factor = 1.0 + 0.2 * math.sin(hour / 24.0 * 2.0 * math.pi)
        waveform.append({
            "time": t.isoformat(),
            "amplitude": round(total, 4),
            "tod_factor": round(tod_factor, 4),
        })
    return waveform


def main():
    print("=" * 80)
    print("  TAP SCHUMANN RESONANCE COUPLING")
    print("  Earth-ionosphere cavity = breath of Earth as a whole")
    print("=" * 80)
    print()

    # 1. Schumann frequencies
    print("  [1/4] Schumann resonance frequencies (Earth-ionosphere cavity):")
    print(f"    Cavity circumference: {2.0*math.pi*(EARTH_RADIUS_M + IONOSPHERE_HEIGHT_M/2.0):.4e} m")
    print(f"    {'Mode':6s} | {'Theoretical':>12s} | {'Observed':>10s} | {'Match':>8s}")
    print("    " + "-" * 50)
    for n, obs_freq in enumerate(SCHUMANN_FREQS, start=1):
        theo_freq = schumann_frequency(n)
        match = abs(theo_freq - obs_freq) / obs_freq * 100
        print(f"    f_{n:1d}   | {theo_freq:>10.2f} Hz | {obs_freq:>8.2f} Hz | {match:>6.2f}%")
    print()

    # 2. Current state
    print("  [2/4] Current Schumann amplitude (July 2, 2026, Kp=2):")
    today = datetime(2026, 7, 2, 12, 0)
    amps = schumann_amplitude(today, kp=2.0)
    for f, a in amps.items():
        print(f"    {f}: {a:.4f} mV/km")
    total = sum(amps.values())
    print(f"    Total: {total:.4f} mV/km")
    print()

    # 3. Coupling to breath clock
    print("  [3/4] Schumann-breath clock coupling:")
    coupling = schumann_to_breath_coupling(amps)
    print(f"    f_7.83 amplitude: {coupling['f7_amplitude']:.4f} mV/km")
    print(f"    Breath phase (sub-breath): {coupling['breath_phase']:.4f} rad")
    print(f"    Coupling: {coupling['coupling']:.6f}")
    print()

    # 4. 60-second waveform
    print("  [4/4] 60-second Schumann waveform (Kp=2):")
    waveform = schumann_waveform(today, duration_s=20, kp=2.0)
    for w in waveform[::3]:
        print(f"    {w['time'][:19]}  amp = {w['amplitude']:.4f} mV/km  tod = {w['tod_factor']:.4f}")
    print()

    # Kp sensitivity
    print("  KP SENSITIVITY (Schumann amplitude vs Kp):")
    for kp in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
        a = schumann_amplitude(today, kp=kp)
        print(f"    Kp={kp}: f_7.83 = {a['f_7.83']:.4f} mV/km, total = {sum(a.values()):.4f} mV/km")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_schumann_resonance_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "schumann_frequencies_theoretical": {f"f_{n}": schumann_frequency(n) for n in range(1, 8)},
        "schumann_frequencies_observed": SCHUMANN_FREQS,
        "current_amplitudes": amps,
        "breath_coupling": coupling,
        "kp_sensitivity": {kp: schumann_amplitude(today, kp=kp) for kp in range(10)},
        "waveform_60s": waveform,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
