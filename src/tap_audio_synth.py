# -*- coding: utf-8 -*-
"""
tap_audio_synth.py
==================
TAP Model -- DAW Physical Modeling Synthesis & Instruments Simulator
Simulates physical waveguide modeling for musical instruments:
1. TAP String Model: Karplus-Strong waveguide string simulation with golden-ratio decay damping.
2. TAP Drum Model: 2D circular membrane percussion synthesis using Fibonacci mode spacing.
3. TAP Synthesizer: Subtractive synthesizer tuned to a golden-ratio microtonal scale (phi intervals).
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PI

def simulate_synth():
    print("=" * 72)
    print("  TAP DAW PHYSICAL MODELING INSTRUMENTS SIMULATOR")
    print("=" * 72)
    
    sr = 44100          # Sample rate (Hz)
    N_samples = 44100   # 1 second of audio
    time_grid = np.linspace(0, 1.0, N_samples)
    
    # =========================================================================
    # 1. TAP STRING MODEL (Karplus-Strong Waveguide)
    # =========================================================================
    # Simulates a plucked string (A440).
    # Feedback loop uses a delay line. Damping is scaled by the golden-ratio leakage.
    f_pitch = 440.0
    delay_len = int(sr / f_pitch)
    
    # Initialize delay buffer with white noise (representing the pluck)
    buffer = np.random.rand(delay_len) * 2.0 - 1.0
    out_string = np.zeros(N_samples)
    
    # Damping factor: decay rate governed by the coordinate leakage (phi^-4)
    # Feedback filter: y[n] = 0.5 * (x[n] + x[n-1]) * S, where S is the decay factor
    S_decay = 1.0 - (PHI ** -4 * 0.05)  # Slightly below 1.0
    
    ptr = 0
    for n in range(N_samples):
        val = buffer[ptr]
        next_val = 0.5 * (val + buffer[(ptr + 1) % delay_len]) * S_decay
        out_string[n] = val
        buffer[ptr] = next_val
        ptr = (ptr + 1) % delay_len
        
    # =========================================================================
    # 2. TAP DRUM MODEL (Fibonacci-Spaced Membrane Modes)
    # =========================================================================
    # Simulates a drum hit. In a 2D membrane, modes are inharmonic (Bessel roots).
    # TAP percussion scales modes using Fibonacci ratios: Mode_i = Mode_0 * phi^(i/2).
    f_drum_base = 80.0  # Deep kick/snare fundamental frequency
    modes = [f_drum_base * (PHI ** (i / 2.0)) for i in range(5)]
    
    out_drum = np.zeros(N_samples)
    # Decay times are faster for higher modes
    for i, freq in enumerate(modes):
        decay = 30.0 * (PHI ** i)  # Faster decay for higher frequencies
        out_drum += np.sin(2.0 * PI * freq * time_grid) * np.exp(-decay * time_grid)
        
    # Normalize drum output
    out_drum = out_drum / (np.max(np.abs(out_drum)) + 1e-9)
    
    # =========================================================================
    # 3. TAP MICROTONAL SYNTHESIZER (Golden Ratio Frequency Scale)
    # =========================================================================
    # Instead of standard 12-tone equal temperament (2^(1/12) intervals),
    # TAP synth uses a golden-ratio microtonal scale where the base interval is phi.
    # Note frequency: f_n = f_base * phi^(n / 5)
    f_base = 220.0  # A3 note
    scale_steps = 10
    synth_frequencies = [f_base * (PHI ** (n / 5.0)) for n in range(scale_steps)]
    
    # Synthesize a chord (Root, 3rd, 5th equivalent in the Golden Ratio scale: steps 0, 3, 5)
    chord_freqs = [synth_frequencies[0], synth_frequencies[3], synth_frequencies[5]]
    out_synth = np.zeros(N_samples)
    
    # Lowpass filter modulated by LFO at golden ratio rate
    lfo_rate = 1.0 * PHI  # ~1.618 Hz LFO
    cutoff_lfo = 1000.0 + 800.0 * np.sin(2.0 * PI * lfo_rate * time_grid)
    
    for freq in chord_freqs:
        # Generate sawtooth wave
        saw = 2.0 * (time_grid * freq - np.floor(time_grid * freq + 0.5))
        out_synth += saw
        
    # Apply time-varying lowpass filter
    filtered_synth = np.zeros(N_samples)
    y_prev = 0.0
    for n in range(N_samples):
        # Calculate filter coefficient from modulated cutoff
        wc = 2.0 * PI * cutoff_lfo[n] / sr
        alpha = wc / (wc + 1.0)
        filtered_synth[n] = alpha * out_synth[n] + (1.0 - alpha) * y_prev
        y_prev = filtered_synth[n]
        
    # Normalize synth output
    filtered_synth = filtered_synth / (np.max(np.abs(filtered_synth)) + 1e-9)
    
    print("  Simulation completed.")
    print(f"    Karplus-String Delay Line: {delay_len} samples")
    print(f"    TAP Drum Modes: {['{:.2f}'.format(m) for m in modes]} Hz")
    print(f"    TAP Synthesizer Golden Scale (first 5 notes): {['{:.2f}'.format(f) for f in synth_frequencies[:5]]} Hz")
    
    # Save raw data
    data = {
        "string_decay": out_string[::100].tolist(),
        "drum_waveform": out_drum[::100].tolist(),
        "drum_modes": modes,
        "synth_chord_frequencies": chord_freqs,
        "synth_waveform": filtered_synth[::100].tolist()
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_synth_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- DAW Physical Modeling Instruments Simulator", color="white", fontsize=14, fontweight="bold")
    
    for ax in axes:
        ax.set_facecolor("#10101a")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")
        ax.tick_params(colors="gray")
        ax.xaxis.label.set_color("gray")
        ax.yaxis.label.set_color("gray")
        ax.title.set_color("white")
        ax.grid(True, color=(1, 1, 1, 0.05))
        
    ORANGE = "#ff6b6b"
    GREEN = "#4ecdc4"
    BLUE = "#7c6af7"
    
    # Panel 1: String Decay Waveform
    ax = axes[0]
    ax.plot(time_grid * 1000, out_string, color=BLUE, alpha=0.8, lw=1.0, label="Plucked String (A440)")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Waveform Amplitude")
    ax.set_title("Physical String Waveguide Decay Curve")
    ax.set_xlim(0, 100)
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Drum hit spectrum
    ax = axes[1]
    fft_drum = np.abs(np.fft.rfft(out_drum))
    freqs_drum = np.fft.rfftfreq(N_samples, 1.0/sr)
    ax.plot(freqs_drum[:2000], fft_drum[:2000], color=GREEN, lw=1.5, label="TAP Drum Hit Spectrum")
    # Draw vertical lines for modes
    for m in modes[:3]:
        ax.axvline(m, color=ORANGE, ls=":", alpha=0.7, label=f"Mode peak ({m:.1f}Hz)")
    # Remove duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), facecolor="#10101a", labelcolor="white")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Spectral Magnitude")
    ax.set_title("Percussion 2D Membrane Frequency Resonances")
    
    plot_path = os.path.join(out_dir, "tap_synth.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Synth visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_synth()
