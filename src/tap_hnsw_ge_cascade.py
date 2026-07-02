# -*- coding: utf-8 -*-
"""
tap_hnsw_ge_cascade.py
==========================
TAP v5.3.2 — Cascade Integration for HNSW-GE.

Wires cosmic/weather/seismic events to the HNSW-GE
so the index is ALIVE. Events affect the current
breath state, which modulates search results.

The flow:
  1. Live event arrives (cosmic Kp, weather, seismic)
  2. Update current_breath_psi based on event
  3. Search the HNSW-GE with new breath state
  4. Return results that are in breath-sync

This makes the user's knowledge DB RESPONSIVE to
real-world events.

Cosmic: Kp index modulates ψ (high Kp = disturbed ψ)
Weather: pressure/temp modulates ψ
Seismic: M5+ quakes add breath phase shift
"""

import os
import sys
import json
import math
import urllib.request
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_hnsw_ge_tap import TAPHNSWGE, UserHNSWGE, RelationType, PHI, PHI_INV13, PLASTIC, PSI_PLASTIC, N_B, GAMMA_NB


def fetch_live_kp() -> float:
    """Fetch current Kp index from NOAA SWPC."""
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        # Last value
        if len(data) > 1:
            last_kp = float(data[-1][1])
            return last_kp
    except Exception:
        pass
    return 0.0


def fetch_live_weather_temp(lat: float = 36.74, lon: float = -119.78) -> float:
    """Fetch current temperature from Open-Meteo."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        return data.get("current_weather", {}).get("temperature", 70.0)
    except Exception:
        return 70.0


def fetch_live_seismic_count(hours: int = 24, min_mag: float = 5.5) -> int:
    """Fetch recent M5.5+ earthquake count from USGS."""
    try:
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(hours=hours)
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.strftime('%Y-%m-%d')}&endtime={end.strftime('%Y-%m-%d')}&minmagnitude={min_mag}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        return len(data.get("features", []))
    except Exception:
        return 0


def compute_breath_state(kp: float, temp_f: float, n_quakes: int) -> dict:
    """
    Compute current breath state from live events.

    ψ = ψ_0 * (1 + kp_factor) * (1 + temp_factor) * (1 + quake_factor)
    """
    # Base ψ from plastic cube root
    psi = PSI_PLASTIC
    # Kp factor (0-9 scale, normalized to 0-1)
    kp_factor = (kp / 9.0) * 0.05  # max 5% modulation
    psi *= (1.0 + kp_factor)
    # Temperature factor (deviation from 70F)
    temp_factor = abs(temp_f - 70.0) / 100.0 * 0.02  # max 2%
    psi *= (1.0 + temp_factor)
    # Quake factor (count of M5.5+ in last 24h)
    quake_factor = min(n_quakes / 10.0, 1.0) * 0.03  # max 3%
    psi *= (1.0 + quake_factor)
    # Clamp
    psi = min(1.0, max(0.0, psi))
    return {
        'psi': psi,
        'kp': kp,
        'temp_f': temp_f,
        'n_quakes': n_quakes,
        'kp_factor': kp_factor,
        'temp_factor': temp_factor,
        'quake_factor': quake_factor,
    }


def main():
    print("=" * 80)
    print("  TAP HNSW-GE CASCADE INTEGRATION")
    print("  Cosmic + weather + seismic events → HNSW-GE")
    print("=" * 80)
    print()

    # Load docs and build TAP HNSW-GE
    knowledge_dir = "/data/data/com.termux/files/home/.hermes/knowledge"
    docs = []
    for f in sorted(os.listdir(knowledge_dir)):
        if f.endswith('.md'):
            filepath = os.path.join(knowledge_dir, f)
            with open(filepath) as fp:
                text = fp.read()
            docs.append((f, text))

    tap_hnsw = TAPHNSWGE(dim=64, n_b=N_B)
    n_chunks = 0
    for fname, text in docs:
        for i in range(0, len(text), 1000):
            chunk_text = text[i:i + 1000]
            if len(chunk_text) < 100:
                continue
            relations = {RelationType.REL_SUPPORTS: ['TAP_model']}
            if i == 0:
                relations[RelationType.REL_SYNONYM] = [fname.replace('.md', '')]
            tap_hnsw.add_chunk(chunk_text, fname, relations)
            n_chunks += 1
    print(f"  Built TAP HNSW-GE: {n_chunks} chunks")
    print()

    # Fetch live events
    print("  [1/3] FETCH LIVE EVENTS:")
    print("    Fetching Kp index...")
    kp = fetch_live_kp()
    print(f"      Kp = {kp}")
    print("    Fetching weather (Fresno)...")
    temp_f = fetch_live_weather_temp()
    print(f"      Temp = {temp_f:.1f}F")
    print("    Fetching seismic count (M5.5+, last 24h)...")
    n_quakes = fetch_live_seismic_count()
    print(f"      Quakes = {n_quakes}")
    print()

    # Compute breath state
    print("  [2/3] COMPUTE BREATH STATE FROM EVENTS:")
    breath = compute_breath_state(kp, temp_f, n_quakes)
    print(f"    Base ψ: {PSI_PLASTIC:.4f}")
    print(f"    Kp factor: +{breath['kp_factor']*100:.2f}%")
    print(f"    Temp factor: +{breath['temp_factor']*100:.2f}%")
    print(f"    Quake factor: +{breath['quake_factor']*100:.2f}%")
    print(f"    Current ψ: {breath['psi']:.4f}")
    print()

    # Test queries with cascade state
    print("  [3/3] SEARCH WITH CASCADE STATE:")
    queries = [
        "What is the install hierarchy for CCP?",
        "sm-hnsw knowledge base",
        "Braid group topology",
    ]
    for q in queries:
        print(f"    Q: {q!r}")
        # With cascade state
        results = tap_hnsw.search_tap(q, k=3, current_breath_psi=breath['psi'])
        for d, i, c in results:
            print(f"      [{d:.3f}] {c['source']} (chunk ψ={c['breath']['psi']:.3f}, "
                  f"|Δψ|={abs(breath['psi']-c['breath']['psi']):.3f})")
        # Compare without cascade
        results_no_breath = tap_hnsw.search_tap(q, k=3, use_breath_correction=False)
        first_diff = results[0][2]['source'] != results_no_breath[0][2]['source']
        print(f"      Cascade changed top result: {first_diff}")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_hnsw_ge_cascade_results.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "live_events": {
            "kp": kp,
            "temp_f": temp_f,
            "n_quakes_24h": n_quakes,
        },
        "breath_state": breath,
        "n_chunks": n_chunks,
        "summary": {
            "current_psi": breath['psi'],
            "psi_range": f"[{PSI_PLASTIC:.4f}, {min(1.0, PSI_PLASTIC * 1.10):.4f}]",
            "breath_correction_active": True,
            "cascade_integration": "cosmic + weather + seismic",
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()
    print("  CASCADE INTEGRATION COMPLETE:")
    print(f"    Cosmic (Kp={kp}) → ψ modulation")
    print(f"    Weather (Temp={temp_f:.1f}F) → ψ modulation")
    print(f"    Seismic (Quakes={n_quakes}) → ψ modulation")
    print(f"    Current breath ψ = {breath['psi']:.4f}")
    print(f"    The HNSW-GE is now ALIVE — events affect search results")
    print("=" * 80)


if __name__ == "__main__":
    main()
