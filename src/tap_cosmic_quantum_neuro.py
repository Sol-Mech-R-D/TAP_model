# -*- coding: utf-8 -*-
"""
tap_cosmic_quantum_neuro.py
===========================
Mathematical sweeps and calculations for the extended TAP models:
  1. Planetary Beat Frequencies (Sun-Earth-Moon-Jupiter sub-breath resonance).
  2. Phononic Bandgap Attenuation in a Fibonacci Quasi-Crystal (Room-temp Qubits).
  3. Interpersonal Phase-Locking (Dual LIF neuron alignment).
"""

import os
import json
import math
from science_constants import PHI, PHI_INV4

def run_cosmic_beats():
    # Base sub-breath periods (in days)
    periods = {
        "Sun": 27.2753 * (PHI ** -3),       # ~6.438 days
        "Earth": 8.1213,                    # ~8.121 days
        "Moon": 27.3217 * (PHI ** -4),       # ~3.987 days
        "Jupiter": 4332.59 * (PHI ** -13),   # ~8.303 days
    }
    
    # Calculate beat frequencies between Earth and others: f_beat = |1/T1 - 1/T2|
    beats = {}
    f_earth = 1.0 / periods["Earth"]
    
    for name, T in periods.items():
        if name != "Earth":
            f_other = 1.0 / T
            f_beat = abs(f_earth - f_other)
            T_beat_days = 1.0 / f_beat if f_beat > 0 else float('inf')
            beats[f"Earth-{name}"] = {
                "period_days": round(T_beat_days, 4),
                "resonance_ratio": round(periods["Earth"] / T, 4)
            }
    return beats

def run_phononic_crystal():
    # Compare standard periodic lattice vs Fibonacci quasi-crystal attenuation
    # of thermal phonon noise at the Weyl frequency (6.67 kHz)
    thicknesses_periodic = [1.0] * 10
    
    # Fibonacci thickness sequence: F_n scaling
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    thicknesses_fib = [f * (PHI ** -4) for f in fib]
    
    # Acoustic attenuation model: Attenuation = exp(sum(thicknesses * impedance_mismatch))
    mismatch_factor = 0.45
    
    attenuation_periodic = math.exp(-sum(thicknesses_periodic) * mismatch_factor)
    # Fibonacci quasi-crystal exhibits topological destructive interference (higher attenuation)
    attenuation_fib = math.exp(-sum(thicknesses_fib) * mismatch_factor * PHI)
    
    return {
        "periodic_transmission": round(attenuation_periodic, 6),
        "fibonacci_transmission": round(attenuation_fib, 6),
        "shielding_factor_db": round(20 * math.log10(attenuation_periodic / (attenuation_fib + 1e-20)), 2)
    }

def run_interpersonal_locking():
    # Two LIF neurons representing two people's brains, checking coupling
    dt = 1e-4 # 0.1 ms steps
    steps = 1000
    
    v1, v2 = 0.0, 0.0
    spikes1, spikes2 = [], []
    
    # Coupling strength (interpersonal proximity / empathy coefficient)
    g_coupling = 0.25
    
    for step in range(steps):
        t = step * dt
        # Shared background Weyl mesh field driving both brains
        weyl_field = 1.2 * math.sin(2.0 * math.pi * 6666.67 * t)
        
        # LIF updates with cross-coupling
        v1 += (-v1 + weyl_field + g_coupling * v2) * (dt / 0.005)
        v2 += (-v2 + weyl_field + g_coupling * v1) * (dt / 0.005)
        
        if v1 >= 1.0:
            spikes1.append(t)
            v1 = 0.0
        if v2 >= 1.0:
            spikes2.append(t)
            v2 = 0.0
            
    # Calculate synchronization (fraction of spikes aligned within 1 ms)
    aligned = 0
    for t1 in spikes1:
        for t2 in spikes2:
            if abs(t1 - t2) < 0.001:
                aligned += 1
                break
                
    sync_pct = (aligned / max(1, len(spikes1))) * 100.0
    return {
        "spikes_person_a": len(spikes1),
        "spikes_person_b": len(spikes2),
        "sync_percentage": round(sync_pct, 2)
    }

def main():
    print("=" * 80)
    print("  TAP COSMIC, QUANTUM, AND NEURO-RESONANCE EXTENDED MODEL")
    print("=" * 80)
    
    beats = run_cosmic_beats()
    print("\n  [1. COSMIC SUB-BREATHS BEATS]")
    for pair, data in beats.items():
        print(f"    {pair:15s} | Beat Period: {data['period_days']:8.2f} days | Ratio: {data['resonance_ratio']:.4f}")
        
    shielding = run_phononic_crystal()
    print("\n  [2. FIBONACCI QUANTUM SHIELDING]")
    print(f"    Periodic Crystal Transmission: {shielding['periodic_transmission']:.6f}")
    print(f"    Fibonacci Crystal Transmission: {shielding['fibonacci_transmission']:.6f}")
    print(f"    Shielding Boost (Fibonacci)   : {shielding['shielding_factor_db']} dB")
    
    sync = run_interpersonal_locking()
    print("\n  [3. INTERPERSONAL NEURAL SYNC]")
    print(f"    Person A Spikes   : {sync['spikes_person_a']}")
    print(f"    Person B Spikes   : {sync['spikes_person_b']}")
    print(f"    Empathy Sync Ratio: {sync['sync_percentage']:.2f}%")
    
    # Export results
    out_data = {
        "cosmic_beats": beats,
        "phononic_shielding": shielding,
        "interpersonal_sync": sync
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "../assets/tap_cosmic_quantum_neuro_results.json")
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"\n  [EXPORT] Extended cascade results saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
