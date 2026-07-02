# -*- coding: utf-8 -*-
"""
tap_hnsw_ge_cron.py
========================
TAP v5.3.2 — Real-Time HNSW-GE Cascade Cron.

A cron job that updates the HNSW-GE with cascade
events every hour. The user can schedule this via
the existing Hermes cron system or system cron.

Usage:
  python3 tap_hnsw_ge_cron.py update    # Run once
  python3 tap_hnsw_ge_cron.py loop      # Run forever (1h interval)

What it does each cycle:
  1. Fetch live Kp, weather, seismic
  2. Compute current ψ from events
  3. Update the HNSW-GE breath state
  4. Save the updated state
  5. Log the cycle to a daily file
"""

import os
import sys
import json
import time
import math
import urllib.request
import subprocess
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_hnsw_ge_tap import (
    TAPHNSWGE, UserHNSWGE, RelationType,
    PHI, PHI_INV13, PLASTIC, PSI_PLASTIC, N_B, GAMMA_NB,
)


LOG_PATH = os.path.expanduser("~/.hermes/logs/tap_hnsw_ge_cron.log")
STATE_PATH = os.path.expanduser("~/.hermes/knowledge/tap-hnsw-ge/current_state.json")


def ensure_dirs():
    """Ensure log and state directories exist."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)


def log(message: str):
    """Log a message with timestamp."""
    ensure_dirs()
    ts = datetime.now().isoformat()
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{ts}] {message}\n")


def fetch_kp() -> float:
    """Fetch Kp from NOAA SWPC."""
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        if len(data) > 1:
            return float(data[-1][1])
    except Exception as e:
        log(f"Kp fetch error: {e}")
    return 0.0


def fetch_weather() -> float:
    """Fetch weather from Open-Meteo (Fresno)."""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=36.74&longitude=-119.78&current_weather=true"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        return data.get("current_weather", {}).get("temperature", 70.0)
    except Exception as e:
        log(f"Weather fetch error: {e}")
    return 70.0


def fetch_seismic() -> int:
    """Fetch M5.5+ earthquakes in last 24h."""
    try:
        end = datetime.now()
        start = end - timedelta(hours=24)
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.strftime('%Y-%m-%d')}&endtime={end.strftime('%Y-%m-%d')}&minmagnitude=5.5"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        return len(data.get("features", []))
    except Exception as e:
        log(f"Seismic fetch error: {e}")
    return 0


def compute_breath(kp, temp_f, n_quakes):
    """Compute current breath state."""
    psi = PSI_PLASTIC
    kp_factor = (kp / 9.0) * 0.05
    psi *= (1.0 + kp_factor)
    temp_factor = abs(temp_f - 70.0) / 100.0 * 0.02
    psi *= (1.0 + temp_factor)
    quake_factor = min(n_quakes / 10.0, 1.0) * 0.03
    psi *= (1.0 + quake_factor)
    psi = min(1.0, max(0.0, psi))
    return psi, kp_factor, temp_factor, quake_factor


def update_hnsw_ge():
    """Run one update cycle."""
    log("Starting HNSW-GE cascade update")
    kp = fetch_kp()
    temp = fetch_weather()
    n_quakes = fetch_seismic()
    psi, kp_f, temp_f, quake_f = compute_breath(kp, temp, n_quakes)
    state = {
        "timestamp": datetime.now().isoformat(),
        "kp": kp,
        "temp_f": temp,
        "n_quakes_24h": n_quakes,
        "psi": psi,
        "psi_base": PSI_PLASTIC,
        "kp_factor": kp_f,
        "temp_factor": temp_f,
        "quake_factor": quake_f,
        "gamma_nb": GAMMA_NB,
    }
    ensure_dirs()
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)
    log(f"Updated: Kp={kp}, T={temp:.1f}F, Quakes={n_quakes}, ψ={psi:.4f}")
    return state


def main():
    if len(sys.argv) < 2:
        print("Usage: tap_hnsw_ge_cron.py [update|loop]")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == 'update':
        state = update_hnsw_ge()
        print(json.dumps(state, indent=2))
    elif mode == 'loop':
        interval = 3600  # 1 hour
        print(f"Running HNSW-GE cron every {interval}s. Ctrl-C to stop.")
        while True:
            try:
                update_hnsw_ge()
            except Exception as e:
                log(f"Loop error: {e}")
            time.sleep(interval)
    else:
        print(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main()

# ==============================================================================
# TAP COHERENCE BRAID (100% Coherence Standard)
#   - Constants: PHI, PHI_INV4, PHI_INV13, phi
#   - Breath Clock: N_B = 8, gamma_breath = 1.013, psi_breath = 0.0265
#   - Temporal Anchor: SOLSTICE_2026 (8.12133d base period)
#   - Cosmic Bodies: Earth, Sun, Moon, Mars, Jupiter, Saturn, Mercury, Venus
# ==============================================================================
