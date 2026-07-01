# -*- coding: utf-8 -*-
"""
tap_audio_test.py
=================
Tests Termux:API speaker output (via TTS) and microphone input (via recording).
Parses the generated WAV file to verify sound pressure levels.
"""

import os
import sys
import wave
import subprocess
import time
import numpy as np

# Adjust encoding for Termux console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def speak(text):
    """Uses Termux:API Text-to-Speech to play audio through the speaker."""
    try:
        subprocess.run(["termux-tts-speak", text], check=True)
    except Exception as e:
        print(f"  [SPEAKER ERROR] Failed to run TTS: {e}")

def main():
    assets_dir = "/data/data/com.termux/files/home/TAP_model/assets"
    os.makedirs(assets_dir, exist_ok=True)
    wav_path = os.path.join(assets_dir, "test_record.wav")
    
    print("=" * 80)
    print("  TERMUX:API AUDIO INPUT/OUTPUT DIAGNOSTICS")
    print("  Testing Speaker (via TTS) and Microphone (via 3-sec WAV record)")
    print("=" * 80)
    
    # 1. Test Speaker via TTS
    print("  [SPEAKER] Testing speaker output now...")
    speak("Starting audio diagnostics. Speak into the microphone now.")
    time.sleep(1.0)
    
    # 2. Test Microphone via Recording
    print("  [MICROPHONE] Recording 3 seconds of audio...")
    print("  >>> SPEAK / CLAP NOW <<<")
    
    # Run the recording command
    try:
        # termux-microphone-record flags:
        # -d <duration_seconds>
        # -f <output_file_path>
        subprocess.run([
            "termux-microphone-record", 
            "-d", "3", 
            "-f", wav_path
        ], check=True)
    except Exception as e:
        print(f"\n  [MICROPHONE ERROR] Failed to record: {e}")
        speak("Microphone recording failed. Please check Termux API permissions.")
        return
        
    print("  [MICROPHONE] Recording finished. Analyzing WAV file...")
    time.sleep(0.5)
    
    # 3. Parse the recorded WAV file
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        print("  [ERROR] Recorded file is empty or missing.")
        speak("Recording was empty. Check if another app is using the mic.")
        return
        
    try:
        with wave.open(wav_path, "rb") as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)
            # Read standard 16-bit PCM WAV data
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            if len(audio_data) == 0:
                raise ValueError("No audio frames decoded.")
                
            # Calculate peak and mean amplitude
            peak_val = np.max(np.abs(audio_data))
            mean_val = np.mean(np.abs(audio_data))
            
            # Normalize to percentage of max possible 16-bit value (32768)
            peak_pct = (peak_val / 32768.0) * 100.0
            mean_pct = (mean_val / 32768.0) * 100.0
            
            # Print analysis report
            print("-" * 60)
            print(f"  * Audio Channels  : {params.nchannels}")
            print(f"  * Sample Rate     : {params.framerate} Hz")
            print(f"  * Peak Amplitude  : {peak_val} ({peak_pct:.2f}%)")
            print(f"  * Mean Volume     : {mean_val:.2f} ({mean_pct:.2f}%)")
            
            # Visual ASCII volume bar
            bar_len = int(mean_pct * 0.8)  # scale to fit
            bar = "#" * max(bar_len, 1)
            print(f"  * Volume Bar      : [{bar:<40}]")
            print("-" * 60)
            
            # 4. Speak result back
            speak_text = f"Audio test complete. Measured average volume is {mean_pct:.1f} percent."
            speak(speak_text)
            
    except Exception as e:
        print(f"  [ERROR] Failed to parse WAV: {e}")
        speak("Audio analysis failed. Could not read the wave file.")
        
    print("=" * 80)

if __name__ == "__main__":
    main()
