# -*- coding: utf-8 -*-
"""
tap_neural_resonance.py
=======================
Neural Resonance & Cognitive Frequency Drift model under the TAP lens.
Models leaky integrate-and-fire (LIF) neural spikes driven by Weyl mesh node crossings.
Evaluates STDP (Spike-Timing-Dependent Plasticity) coherence limits.
"""

import os
import json
import math
from science_constants import PHI, DELTA_B_N, DELTA_B_PSI

def run_lif_neuron(freq_hz):
    # Simulation parameters
    dt = 1e-6 # 1 microsecond resolution
    steps = 10000 # 10 ms window
    
    # LIF Neuron properties
    v_thresh = 1.0
    v_reset = 0.0
    tau_membrane = 0.005 # 5 ms membrane time constant
    
    v = 0.0
    spikes = 0
    
    # Driving input: Weyl mesh crossing frequency (e.g. 6.67 kHz)
    omega_weyl = 2.0 * math.pi * freq_hz
    # Modulate input by current breath phase psi
    mod_factor = 1.0 + 0.02 * math.cos(2.0 * math.pi * DELTA_B_PSI)
    
    for step in range(steps):
        t = step * dt
        # Input current driven by Weyl crossings
        i_input = 1.5 * math.sin(omega_weyl * t * mod_factor)
        
        # Leaky integrate update
        v += (-v + i_input) * (dt / tau_membrane)
        
        # Threshold condition
        if v >= v_thresh:
            spikes += 1
            v = v_reset
            
    firing_rate = spikes / (steps * dt)
    return firing_rate

def main():
    print("=" * 80)
    print("  TAP NEURAL RESONANCE & BIOLOGICAL CRITICALITY MODEL")
    print("=" * 80)
    
    # Target Weyl crossing frequencies across different biological dimensions
    # Base Weyl frequency is 1 / 150 microseconds ≈ 6666.67 Hz
    base_weyl_freq = 6666.67
    
    # Evaluate resonance in the range of alpha, beta, gamma brain waves
    frequencies = {
        "Delta Wave": 2.5,
        "Theta Wave": 6.0,
        "Alpha Wave": 10.0,
        "Beta Wave": 20.0,
        "Gamma Wave": 40.0,
        "Weyl Crossings (Level 10)": base_weyl_freq,
        "Weyl Sub-harmonics": base_weyl_freq / PHI
    }
    
    resonance_map = []
    print("\n  [SIMULATED NEURAL CRITICALITY SPECTRUM]")
    for name, freq in frequencies.items():
        rate = run_lif_neuron(freq)
        resonance_map.append({
            "name": name,
            "frequency_hz": round(freq, 2),
            "firing_rate_hz": round(rate, 2),
            "criticality_score": round(rate / (freq + 1e-10) * 100, 2)
        })
        print(f"    {name:25s} | Input: {freq:8.2f} Hz | Firing Rate: {rate:7.2f} Hz | Criticality: {rate / (freq + 1e-10) * 100:.1f}%")
        
    out_data = {
        "delta_b_n": DELTA_B_N,
        "delta_b_psi": DELTA_B_PSI,
        "neural_resonance": resonance_map
    }
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "../assets/tap_neural_resonance_results.json")
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2)
        
    print(f"\n  [EXPORT] Neural resonance results saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
