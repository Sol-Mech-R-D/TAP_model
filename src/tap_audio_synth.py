# -*- coding: utf-8 -*-
"""
tap_audio_synth.py
==================
TAP Model -- DAW Deep Physical Modeling Instrument Engine
Simulates advanced structural physical modeling for instruments:
1. MIDI Mapping Engine: Translates MIDI note numbers (0-127) and velocities (0-127) 
   to physical gauge frequencies, excitation energy, and harmonic profiles.
2. Guitar Model (Wood, Neck & Body Coupling): Simulates string vibrations coupled 
   to the neck damping factor and the wooden body's plate/Helmholtz resonances.
3. Drum Model (Head & Shell Coupling): Simulates a 2D membrane head coupled 
   to the cylindrical wood shell resonance.
4. Grand Piano Model (Unison Strings & Soundboard): Simulates triple-unison strings
   coupled to a wooden soundboard with golden-ratio mechanical impedance.
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

# =============================================================================
# 1. MIDI MAPPING ENGINE
# =============================================================================
class MidiEngine:
    @staticmethod
    def note_to_frequency(midi_note, scale_type="standard"):
        """Converts a MIDI note (0-127) to frequency (Hz)."""
        if scale_type == "standard":
            # Standard 12-Tone Equal Temperament (A440 at note 69)
            return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
        elif scale_type == "golden":
            # TAP Microtonal Golden Scale (A220 at note 57, interval is phi)
            # 5 steps per golden octave (phi)
            return 220.0 * (PHI ** ((midi_note - 57) / 5.0))
        return 440.0

    @staticmethod
    def velocity_to_dynamics(midi_velocity):
        """Converts MIDI velocity (0-127) to amplitude and harmonic richness."""
        norm_vel = midi_velocity / 127.0
        # Amplitude follows a natural logarithmic/exponential hearing curve
        amplitude = norm_vel ** 1.5
        # Higher velocity excites higher-frequency harmonics (brighter sound)
        brightness = 1.0 + norm_vel * PHI
        return amplitude, brightness

# =============================================================================
# 2. GUITAR MODEL (String, Neck, Wood & Body Coupling)
# =============================================================================
class GuitarModel:
    def __init__(self, sr=44100):
        self.sr = sr
        
    def synthesize_note(self, midi_note, midi_velocity, duration=1.0):
        N_samples = int(duration * self.sr)
        time_grid = np.linspace(0, duration, N_samples)
        
        freq = MidiEngine.note_to_frequency(midi_note, "standard")
        amp, brightness = MidiEngine.velocity_to_dynamics(midi_velocity)
        
        # 1. String Waveguide (Karplus-Strong)
        delay_len = int(self.sr / freq)
        string_buffer = np.random.rand(delay_len) * 2.0 - 1.0
        
        # 2. Neck Damping (fretboard absorption)
        # Neck material dampens energy. TAP neck model scales decay using phi^-4
        neck_damping = 1.0 - (0.01 * (PHI ** -4) * v_ratio)
        
        # 3. Wood Body Resonance (Helmholtz & Plate Coupling)
        # The guitar body has wood plate resonances (e.g. 100Hz, 200Hz) and air Helmholtz (80Hz)
        body_helmholtz = 80.0
        body_plate = 190.0
        
        out_signal = np.zeros(N_samples)
        body_state_h = 0.0
        body_state_p = 0.0
        
        ptr = 0
        for n in range(N_samples):
            # Read from string waveguide
            val = string_buffer[ptr]
            
            # Neck damping filter
            next_val = 0.5 * (val + string_buffer[(ptr + 1) % delay_len]) * neck_damping
            string_buffer[ptr] = next_val
            ptr = (ptr + 1) % delay_len
            
            # Couple string to hollow wooden body (simple resonant filters)
            # Body acts as a resonator driven by the string output
            w_h = 2.0 * PI * body_helmholtz / self.sr
            w_p = 2.0 * PI * body_plate / self.sr
            
            # Resonator differential equations
            body_state_h += w_h * (val - body_state_h) - 0.02 * body_state_h
            body_state_p += w_p * (val - body_state_p) - 0.04 * body_state_p
            
            # Combine string output with body plate resonance
            # Coupling coefficient is governed by phi^-4
            out_signal[n] = val + (PHI ** -4) * (body_state_h + body_state_p) * v_ratio
            
        # Normalize and apply MIDI velocity amplitude
        out_signal = out_signal / (np.max(np.abs(out_signal)) + 1e-9)
        return out_signal * amp

# =============================================================================
# 3. DRUM MODEL (Head & Wood Shell Coupling)
# =============================================================================
class DrumModel:
    def __init__(self, sr=44100):
        self.sr = sr
        
    def synthesize_note(self, midi_note, midi_velocity, duration=1.0):
        N_samples = int(duration * self.sr)
        time_grid = np.linspace(0, duration, N_samples)
        
        freq_base = MidiEngine.note_to_frequency(midi_note, "standard") * 0.25 # Lower for drum fundamental
        amp, brightness = MidiEngine.velocity_to_dynamics(midi_velocity)
        
        # 1. 2D Membrane Head Modes
        # Spaced according to Fibonacci steps (phi^(i/2))
        head_modes = [freq_base * (PHI ** (i / 2.0)) for i in range(4)]
        
        # 2. Cylindrical Wood Shell Resonance
        # Drum shell has acoustic resonance frequencies based on cylinder volume
        # Shell mode is coupled to the base head mode
        shell_resonance = freq_base * PHI
        
        out_signal = np.zeros(N_samples)
        
        for i, freq in enumerate(head_modes):
            # Higher velocity excites higher frequency modes (brightness)
            mode_amp = amp / (1.0 + i * PHI / brightness)
            decay_rate = 40.0 * (PHI ** i)
            
            # Head membrane wave
            head_wave = np.sin(2.0 * PI * freq * time_grid) * np.exp(-decay_rate * time_grid)
            
            # Shell coupling: shell absorbs and re-radiates head vibration
            # Shell decay is longer (resonance)
            shell_wave = np.sin(2.0 * PI * shell_resonance * time_grid) * np.exp(-15.0 * time_grid)
            
            # Combine head and shell signals
            out_signal += mode_amp * (head_wave + (PHI ** -4) * shell_wave)
            
        out_signal = out_signal / (np.max(np.abs(out_signal)) + 1e-9)
        return out_signal * amp

# =============================================================================
# 4. GRAND PIANO MODEL (Triple-Unison Strings & Wooden Soundboard)
# =============================================================================
class GrandPianoModel:
    def __init__(self, sr=44100):
        self.sr = sr
        
    def synthesize_note(self, midi_note, midi_velocity, duration=1.5):
        N_samples = int(duration * self.sr)
        time_grid = np.linspace(0, duration, N_samples)
        
        freq = MidiEngine.note_to_frequency(midi_note, "standard")
        amp, brightness = MidiEngine.velocity_to_dynamics(midi_velocity)
        
        # Grand pianos use 3 strings per note (unisons) tuned slightly apart (detuning)
        # Detuning introduces beating and chorusing effects
        detunes = [-0.15, 0.0, 0.15] # Hz detuning
        string_freqs = [freq + d for d in detunes]
        
        # Waveguide delay buffers for the 3 strings
        delays = [int(self.sr / f) for f in string_freqs]
        buffers = [np.random.rand(d) * 2.0 - 1.0 for d in delays]
        ptrs = [0 for _ in delays]
        
        # Wooden Soundboard Impedance
        # Soundboard absorbs energy from the bridge and radiates sound.
        # TAP soundboard impedance filter coefficient is governed by phi^-8
        soundboard_impedance = 1.0 - (0.005 * (PHI ** -8))
        
        out_signal = np.zeros(N_samples)
        soundboard_state = 0.0
        
        for n in range(N_samples):
            # Sum of the 3 unison strings
            unison_sum = 0.0
            for i in range(3):
                val = buffers[i][ptrs[i]]
                next_val = 0.5 * (val + buffers[i][(ptrs[i] + 1) % delays[i]]) * soundboard_impedance
                buffers[i][ptrs[i]] = next_val
                ptrs[i] = (ptrs[i] + 1) % delays[i]
                unison_sum += val
                
            # Soundboard coupling: wood soundboard adds rich acoustic sustain
            # Modeled as a lossy integrator coupled to the unison strings
            soundboard_state = 0.995 * soundboard_state + (PHI ** -4) * unison_sum
            
            # Combine string output with soundboard radiation
            out_signal[n] = unison_sum * 0.33 + (PHI ** -8) * soundboard_state
            
        out_signal = out_signal / (np.max(np.abs(out_signal)) + 1e-9)
        return out_signal * amp

# =============================================================================
# RUN SIMULATION & MIDI TRIGGERS
# =============================================================================
def simulate_synth():
    print("=" * 72)
    print("  TAP PHYSICAL INSTRUMENT SYNTHESIS DEMO (MIDI TRIGGER)")
    print("=" * 72)
    
    guitar = GuitarModel()
    drum = DrumModel()
    piano = GrandPianoModel()
    
    # Trigger MIDI events: Note Number 60 (Middle C), Velocity 100
    midi_note = 60
    midi_velocity = 100
    
    print(f"  Triggering MIDI Event: Note {midi_note}, Velocity {midi_velocity}")
    
    # Synthesize outputs
    out_guitar = guitar.synthesize_note(midi_note, midi_velocity)
    out_drum = drum.synthesize_note(midi_note, midi_velocity)
    out_piano = piano.synthesize_note(midi_note, midi_velocity)
    
    print("  Physical modeling synthesis complete.")
    
    # Save raw data
    data = {
        "midi_note": midi_note,
        "midi_velocity": midi_velocity,
        "guitar_waveform": out_guitar[::100].tolist(),
        "drum_waveform": out_drum[::100].tolist(),
        "piano_waveform": out_piano[::100].tolist()
    }
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    data_path = os.path.join(out_dir, "tap_synth_data.json")
    with open(data_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [EXPORT] Raw data saved -> {data_path}")
    
    # Plotting results
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#0a0a0f")
    fig.suptitle("TAP Model -- DAW Deep Physical Modeling Instrument Engine", color="white", fontsize=14, fontweight="bold")
    
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
    
    # Panel 1: Guitar vs. Piano Waveform Decay
    ax = axes[0]
    time_grid = np.linspace(0, 1000, 1000)
    ax.plot(time_grid, out_guitar[:1000], color=ORANGE, alpha=0.8, label="Guitar (String + Neck + Wood Body)")
    ax.plot(time_grid, out_piano[:1000], color=BLUE, alpha=0.8, label="Grand Piano (Triple Unison + Soundboard)")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Waveform Amplitude")
    ax.set_title("Acoustic Structural Waveguide Comparison")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    # Panel 2: Drum Head-Shell FFT Spectrum
    ax = axes[1]
    sr = 44100
    N_samples = len(out_drum)
    fft_drum = np.abs(np.fft.rfft(out_drum))
    freqs_drum = np.fft.rfftfreq(N_samples, 1.0/sr)
    
    ax.plot(freqs_drum[:1000], fft_drum[:1000], color=GREEN, lw=1.5, label="TAP Drum (Head + Shell Coupling)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Spectral Magnitude")
    ax.set_xlim(0, 800)
    ax.set_title("Percussion Coupled Head-Shell Resonances")
    ax.legend(facecolor="#10101a", labelcolor="white")
    
    plot_path = os.path.join(out_dir, "tap_synth.png")
    plt.savefig(plot_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [PLOT] Synth visualization saved -> {plot_path}\n")

if __name__ == "__main__":
    simulate_synth()
