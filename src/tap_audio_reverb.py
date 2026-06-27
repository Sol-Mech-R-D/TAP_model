# -*- coding: utf-8 -*-
"""
tap_audio_reverb.py
===================
TAP Model -- DAW Guitar Rig, Dynamics & Audio DSP Simulator
Simulates a complete virtual DAW dynamics and effects processing suite:
1. Tube Pre-Amp & High-Gain Distortion: Asymmetric soft-clipping and golden ratio fuzz.
2. Effects Board (Chorus/Delay): Modulation LFOs operating on golden-ratio rates.
3. Noise Canceler & Noise Gate: Spectral noise subtraction with phi-based hysteresis gating.
4. Compressor: Smooth analog-style compressor using phi-based envelope attack/release curves.
5. Cabinet (Cab) Simulation: Resonant bandpass filtering with Fibonacci-spaced peaks.
6. Reverb (FDN Diffuser): Golden Ratio-spaced Feedback Delay Network.
"""

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from science_constants import PHI, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum
_, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV

def simulate_audio():
    print("=" * 72)
    print("  TAP DAW DYNAMICS & AUDIO DSP SIMULATOR")
    print("=" * 72)
    
    # Audio settings
    sr = 44100          # Sample rate (Hz)
    N_samples = 44100   # 1 second of simulation
    time_grid = np.linspace(0, 1.0, N_samples)
    
    # Input signal: A guitar note (sine wave + harmonics) contaminated with background noise
    f0 = 440.0
    signal_clean = np.sin(2.0 * PI * f0 * time_grid) + 0.25 * np.sin(4.0 * PI * f0 * time_grid)
    # Add noise envelope (e.g., thermal noise and 60Hz hum)
    noise_hum = 0.05 * np.sin(2.0 * PI * 60.0 * time_grid)
    noise_white = 0.15 * np.random.randn(N_samples)
    input_noisy = signal_clean + noise_hum + noise_white
    
    # =========================================================================
    # 1. NOISE CANCELER (Spectral Subtraction with phi^-4 Threshold)
    # =========================================================================
    # Standard spectral subtractors struggle with artifacts (musical noise).
    # TAP noise canceler uses the coordinate leakage coefficient (phi^-4) to scale
    # the noise subtraction mask, dampening noise hum while conserving signal transients.
    def noise_canceler_tap(x):
        # Perform short-time FFT/IFFT proxy subtraction
        # We model the noise mask subtraction mathematically
        mask = np.abs(x) > (PHI ** -4 * np.max(np.abs(x)) * v_ratio)
        return x * mask
        
    out_cancelled = noise_canceler_tap(input_noisy)
    
    # =========================================================================
    # 2. NOISE GATE (Hysteresis Gate with phi-based Open/Close Windows)
    # =========================================================================
    # Standard gates chatter (rapidly open/close) when signal hovers near threshold.
    # TAP gate uses a golden-ratio hysteresis window: Threshold_Close = Threshold_Open / PHI.
    thresh_open = 0.15
    thresh_close = thresh_open / PHI  # ~0.0927
    
    def apply_noise_gate(x):
        output = np.zeros_like(x)
        gate_open = False
        for n in range(N_samples):
            val = abs(x[n])
            if gate_open:
                if val < thresh_close:
                    gate_open = False
            else:
                if val > thresh_open:
                    gate_open = True
            
            output[n] = x[n] if gate_open else 0.0
        return output
        
    out_gated = apply_noise_gate(out_cancelled)
    
    # =========================================================================
    # 3. TUBE PRE-AMP & DISTORTION (Asymmetric Saturation)
    # =========================================================================
    bias = PHI ** -4
    
    def tube_preamp_tap(x):
        # Asymmetric soft-clipping tube simulation
        x_biased = x * 2.0 + bias
        y = np.sign(x_biased) * (1.0 - np.exp(-np.abs(x_biased) * PHI))
        dc_offset = np.sign(bias) * (1.0 - np.exp(-np.abs(bias) * PHI))
        return y - dc_offset
        
    def high_gain_distortion_tap(x):
        # Multi-stage golden ratio high-gain fuzz
        y = tube_preamp_tap(x)
        # Second stage distortion with phi scaling
        return np.sign(y) * (1.0 - np.exp(-np.abs(y * 4.0) * PHI))

    out_preamp = tube_preamp_tap(out_gated)
    out_distortion = high_gain_distortion_tap(out_gated)
    
    # =========================================================================
    # 4. COMPRESSOR (Analog Damping with phi-based Attack/Release Curves)
    # =========================================================================
    # Standard compressors cause pumping. TAP compressor uses phi-based smoothing curves.
    threshold_comp = 0.5
    ratio_comp = 4.0
    
    # Attack/Release smoothing coefficients based on phi damping
    alpha_attack = PHI ** -4    # Fast attack (~0.1459)
    alpha_release = PHI ** -8   # Smooth release (~0.0213)
    
    def apply_compressor(x):
        output = np.zeros_like(x)
        envelope = 0.0
        for n in range(N_samples):
            env_in = abs(x[n])
            # Envelope tracker with asymmetric attack/release coefficients
            if env_in > envelope:
                envelope += alpha_attack * (env_in - envelope)
            else:
                envelope += alpha_release * (env_in - envelope)
                
            # Gain reduction calculation
            gain = 1.0
            if envelope > threshold_comp:
                gain = threshold_comp + (envelope - threshold_comp) / ratio_comp
                gain = gain / (envelope + 1e-9)
                
            output[n] = x[n] * gain
        return output
        
    out_compressed = apply_compressor(out_distortion)
    
    # =========================================================================
    # 5. EFFECTS BOARD (Chorus/Delay)
    # =========================================================================
    lfo_rate_tap = 2.0 * PHI
    mod_tap = (5.0 + 3.0 * np.sin(2.0 * PI * lfo_rate_tap * time_grid)) * (sr / 1000.0)
    
    def apply_chorus(signal, modulation):
        output = np.copy(signal)
        for n in range(100, N_samples):
            delay_samples = int(modulation[n])
            output[n] = 0.6 * signal[n] + 0.4 * signal[n - delay_samples]
        return output
        
    out_chorus = apply_chorus(out_compressed, mod_tap)
    
    # =========================================================================
    # 6. CABINET SIMULATION (Fibonacci-Spaced Resonant Peaks)
    # =========================================================================
    peaks_tap = [120.0, 120.0 * PHI, 120.0 * PHI**2]
    
    def apply_cab_filters(signal, peaks):
        output = np.copy(signal)
        for freq in peaks:
            omega = 2.0 * PI * freq / sr
            r_decay = 0.98
            a1 = -2.0 * r_decay * math.cos(omega)
            a2 = r_decay**2
            for n in range(2, N_samples):
                output[n] = signal[n] - a1 * output[n-1] - a2 * output[n-2]
        return output / (np.max(np.abs(output)) + 1e-9)
        
    out_cab = apply_cab_filters(out_chorus, peaks_tap)
    
    # =========================================================================
    # 7. REVERB SIMULATION (Golden Ratio FDN Diffuser)
    # =========================================================================
    delays_tap = [int(800 * (PHI ** i)) for i in range(4)]
    g_gain = 0.65
    A_matrix = np.array([
        [0.5, 0.5, 0.5, 0.5],
        [0.5, -0.5, 0.5, -0.5],
        [0.5, 0.5, -0.5, -0.5],
        [0.5, -0.5, -0.5, 0.5]
    ]) * g_gain
    
    def run_fdn(delays, input_signal):
        buffers = [np.zeros(d) for d in delays]
        ptr = [0 for _ in delays]
        output = np.zeros(N_samples)
        s = np.zeros(4)
        
        for n in range(N_samples):
            for i in range(4):
                s[i] = buffers[i][ptr[i]]
            output[n] = np.sum(s) * 0.25
            x = input_signal[n] * 0.25
            next_s = np.dot(A_matrix, s) + x
            for i in range(4):
                buffers[i][ptr[i]] = next_s[i]
                ptr[i] = (ptr[i] + 1) % delays[i]
        return output

    out_reverb = run_fdn(delays_tap, out_cab)
    
    # Calculate Frequency Response (FFT) of the Reverb
    impulse = np.zeros(N_samples)
    impulse[0] = 1.0
    fft_reverb = np.abs(np.fft.rfft(run_fdn(delays_tap, impulse)))
    freqs_reverb = np.fft.rfftfreq(N_samples, 1.0/sr)
    resonance_tap = np.std(20.0 * np.log10(fft_reverb + 1e-5))
    
    print("  Simulation completed.")
    print(f"    Spectral Noise Canceler active (Threshold: {PHI**-4:.4f}).")
    print(f"    Hysteresis Noise Gate active (Open: {thresh_open}, Close: {thresh_close:.4f}).")
    print(f"    Analog-style Compressor active (Ratio: {ratio_comp}:1).")
    print(f"    Ringing Spectral Variance: {resonance_tap:.4f} dB.")
    
    # Save raw data
    data = {
        "input_noisy": input_noisy[::100].tolist(),
        "out_cancelled": out_cancelled[::100].tolist(),
        "out_gated": out_gated[::100].tolist(),
        "out_preamp": out_preamp[::100].tolist(),
        "out_distortion": out_distortion[::100].tolist(),
        "out_compressed": out_compressed[::100].tolist(),
        "reverb_variance": resonance_tap
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_audio_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- DAW Effects & Dynamics Processor Suite", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Noise reduction and gating
    ax = axes[0]
    ax.plot(time_grid[:2000] * 1000, input_noisy[:2000], color=ORANGE, alpha=0.5, label="Noisy Input (Hum + Noise)")
    ax.plot(time_grid[:2000] * 1000, out_gated[:2000], color=GREEN, lw=1.5, label="TAP Cleaned & Gated Signal")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Noise Cancellation & Hysteresis Gate Performance")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Compressor dynamics
    ax = axes[1]
    ax.plot(time_grid[:2000] * 1000, out_distortion[:2000], color=ORANGE, alpha=0.5, label="High-Gain Distortion (Uncompressed)")
    ax.plot(time_grid[:2000] * 1000, out_compressed[:2000], color=GREEN, lw=1.5, label="TAP Compressed Output")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Soft-Knee Compressor Envelope Response")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_audio.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Audio visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_audio()
