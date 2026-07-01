# -*- coding: utf-8 -*-
"""
tap_audio_test.py
=================
Tests Termux:API speaker output (via TTS) and microphone input (via recording).
Records to .m4a, waits for completion, converts to .wav, and parses the volume.
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
    m4a_path = os.path.join(assets_dir, "test_record.m4a")
    wav_path = os.path.join(assets_dir, "test_record.wav")
    
    # Clean up old files if they exist
    for path in [m4a_path, wav_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
                
    print("=" * 80)
    print("  TERMUX:API AUDIO INPUT/OUTPUT DIAGNOSTICS")
    print("  Testing Speaker (via TTS) and Microphone (via 3-sec M4A -> WAV record)")
    print("=" * 80)
    
    # 1. Test Speaker via TTS
    print("  [SPEAKER] Testing speaker output now...")
    speak("Starting audio diagnostics. Speak into the microphone now.")
    time.sleep(1.0)
    
    # 2. Test Microphone via Recording
    print("  [MICROPHONE] Recording 3 seconds of audio...")
    print("  >>> SPEAK / CLAP NOW <<<")
    
    try:
        # Correct Termux API flags:
        # -f <file_path>: specifies output file
        # -l <limit>: specifies limit in seconds
        subprocess.run([
            "termux-microphone-record", 
            "-f", m4a_path,
            "-l", "3"
        ], check=True)
    except Exception as e:
        print(f"\n  [MICROPHONE ERROR] Failed to record: {e}")
        speak("Microphone recording failed. Please check Termux API permissions.")
        return
        
    # Wait the full 3 seconds + 0.5s buffer for the background recording to finish
    print("  [MICROPHONE] Recording in progress (3.5 second wait)...")
    time.sleep(3.5)
    
    if not os.path.exists(m4a_path) or os.path.getsize(m4a_path) == 0:
        print("  [ERROR] M4A recording file was not created or is empty.")
        speak("Recording failed to write to disk.")
        return
        
    print(f"  [MICROPHONE] M4A file created ({os.path.getsize(m4a_path)} bytes). Converting to WAV using ffmpeg...")
    
    # 3. Convert M4A to WAV using FFmpeg
    try:
        # Remove check=True because Termux FFmpeg returns exit code 183 on success
        subprocess.run([
            "ffmpeg", "-y", 
            "-i", m4a_path, 
            "-ac", "1", 
            "-ar", "16000", 
            wav_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"  [CONVERSION ERROR] Failed to run FFmpeg: {e}")
        
    # 4. Parse the converted WAV file
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        print("  [ERROR] Converted WAV file is empty or missing.")
        speak("WAV file conversion resulted in an empty file.")
        return
        
    try:
        with wave.open(wav_path, "rb") as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            if len(audio_data) == 0:
                raise ValueError("No audio frames decoded.")
                
            peak_val = np.max(np.abs(audio_data))
            mean_val = np.mean(np.abs(audio_data))
            
            # Normalize to percentage of max possible 16-bit value (32768)
            peak_pct = (peak_val / 32768.0) * 100.0
            mean_pct = (mean_val / 32768.0) * 100.0
            
            print("-" * 60)
            print(f"  * Audio Channels  : {params.nchannels}")
            print(f"  * Sample Rate     : {params.framerate} Hz")
            print(f"  * Peak Amplitude  : {peak_val} ({peak_pct:.2f}%)")
            print(f"  * Mean Volume     : {mean_val:.2f} ({mean_pct:.2f}%)")
            
            # Visual ASCII volume bar
            bar_len = int(mean_pct * 0.8)
            bar = "#" * max(bar_len, 1)
            print(f"  * Volume Bar      : [{bar:<40}]")
            print("-" * 60)
            
            # Speak result back
            speak_text = f"Audio test complete. Measured average volume is {mean_pct:.1f} percent."
            speak(speak_text)
            
    except Exception as e:
        print(f"  [ERROR] Failed to parse WAV: {e}")
        speak("Audio analysis failed. Could not read the wave file.")
        
    print("=" * 80)

if __name__ == "__main__":
    main()
