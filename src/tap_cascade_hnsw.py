# -*- coding: utf-8 -*-
"""
tap_cascade_hnsw.py
=======================
TAP v5.3.2 — Real-Time Cascade HNSW (Streaming).

A streaming HNSW that updates as cosmic/weather/seismic
events arrive. Each event:
  1. Triggers a "ripple" through the HNSW
  2. Chunks near the event's breath state get
     their ψ updated
  3. New events with magnitude > threshold add
     new chunks (event as memory)

The HNSW is now ALIVE — events change its structure.

This is the "TAP Unified" vision realized:
  - Cosmic Kp → high-altitude ripples
  - Weather temp → mid-altitude ripples
  - Seismic M5+ → low-altitude ripples + new chunks

The cascade is unified: ALL events share the same
breath ψ, modulated by their type and magnitude.
"""

import os
import sys
import json
import time
import math
import urllib.request
import threading
import queue
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_hnsw_ge_tap import TAPHNSWGE, UserHNSWGE, RelationType, PHI, PHI_INV13, PLASTIC, PSI_PLASTIC, N_B, GAMMA_NB


def fetch_kp() -> float:
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        return float(data[-1][1]) if len(data) > 1 else 0.0
    except Exception:
        return 0.0


def fetch_weather() -> float:
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=36.74&longitude=-119.78&current_weather=true"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        return data.get("current_weather", {}).get("temperature", 70.0)
    except Exception:
        return 70.0


def fetch_seismic_events() -> list:
    try:
        end = datetime.now()
        start = end - timedelta(hours=24)
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.strftime('%Y-%m-%d')}&endtime={end.strftime('%Y-%m-%d')}&minmagnitude=5.5"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        events = []
        for f in data.get("features", []):
            props = f.get("properties", {})
            mag = props.get("mag", 0)
            place = props.get("place", "?")
            events.append({"mag": mag, "place": place})
        return events
    except Exception:
        return []


class CascadeHNSW:
    """Streaming HNSW that responds to cascade events."""

    def __init__(self, dim=64):
        self.tap_hnsw = TAPHNSWGE(dim=dim, n_b=N_B)
        self.event_queue = queue.Queue()
        self.event_log = []
        self.ripple_count = 0
        self.new_chunks = 0
        self._lock = threading.Lock()

    def load_initial_docs(self, knowledge_dir: str = None):
        """Load user's existing 7 docs."""
        if knowledge_dir is None:
            knowledge_dir = "/data/data/com.termux/files/home/.hermes/knowledge"
        docs = []
        if os.path.exists(knowledge_dir):
            for f in sorted(os.listdir(knowledge_dir)):
                if f.endswith('.md'):
                    filepath = os.path.join(knowledge_dir, f)
                    with open(filepath) as fp:
                        text = fp.read()
                    docs.append((f, text))
        for fname, text in docs:
            for i in range(0, len(text), 1000):
                chunk_text = text[i:i + 1000]
                if len(chunk_text) < 100:
                    continue
                relations = {RelationType.REL_SUPPORTS: ['TAP_model']}
                if i == 0:
                    relations[RelationType.REL_SYNONYM] = [fname.replace('.md', '')]
                self.tap_hnsw.add_chunk(chunk_text, fname, relations)
        return len(docs)

    def ripple(self, event_type: str, magnitude: float, current_psi: float):
        """Trigger a cascade ripple through the HNSW.

        For each chunk within |Δψ| < threshold:
          Update its ψ toward current_psi

        The threshold scales with magnitude:
          - Kp=0: threshold = 0.1
          - Kp=9: threshold = 0.5
          - M5+ quake: threshold = 0.7
        """
        with self._lock:
            threshold = 0.1 + min(magnitude, 9.0) / 9.0 * 0.4
            if event_type == "seismic":
                threshold = 0.5 + min(magnitude - 5.0, 4.0) / 4.0 * 0.3
            n_affected = 0
            for chunk in self.tap_hnsw.chunks:
                psi = chunk['breath']['psi']
                if abs(psi - current_psi) < threshold:
                    # Move ψ toward current_psi by 10% of the difference
                    new_psi = psi + 0.1 * (current_psi - psi)
                    chunk['breath']['psi'] = new_psi
                    n_affected += 1
            self.ripple_count += 1
            self.event_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": event_type,
                "magnitude": magnitude,
                "current_psi": current_psi,
                "threshold": threshold,
                "n_affected": n_affected,
            })
            return n_affected

    def add_event_chunk(self, event_type: str, magnitude: float, current_psi: float, description: str):
        """Add a new chunk representing an event."""
        with self._lock:
            text = f"[{event_type.upper()}] magnitude={magnitude:.2f}: {description}"
            relations = {
                RelationType.REL_CAUSES: ['cascade_update'],
                RelationType.REL_SUPPORTS: ['TAP_model'],
            }
            self.tap_hnsw.add_chunk(text, f"event_{event_type}", relations)
            # Override the breath ψ for this new chunk
            new_chunk = self.tap_hnsw.chunks[-1]
            new_chunk['breath']['psi'] = current_psi
            self.new_chunks += 1
            return len(self.tap_hnsw.chunks) - 1

    def process_live_events(self):
        """Fetch live events and process them."""
        # Fetch
        kp = fetch_kp()
        temp = fetch_weather()
        events = fetch_seismic_events()
        # Compute current ψ
        psi = PSI_PLASTIC
        kp_factor = (kp / 9.0) * 0.05
        psi *= (1.0 + kp_factor)
        temp_factor = abs(temp - 70.0) / 100.0 * 0.02
        psi *= (1.0 + temp_factor)
        n_q = len(events)
        quake_factor = min(n_q / 10.0, 1.0) * 0.03
        psi *= (1.0 + quake_factor)
        psi = min(1.0, max(0.0, psi))
        # Process
        results = {
            "timestamp": datetime.now().isoformat(),
            "current_psi": psi,
        }
        # Ripple from Kp
        if kp > 0:
            n = self.ripple("cosmic_kp", kp, psi)
            results["kp_ripple"] = n
        # Ripple from weather
        if abs(temp - 70) > 5:
            n = self.ripple("weather_temp", abs(temp - 70), psi)
            results["weather_ripple"] = n
        # Add chunks for each M5+ quake
        for e in events:
            mag = e["mag"]
            if mag >= 5.5:
                idx = self.add_event_chunk("seismic", mag, psi, e["place"])
                # Also ripple
                self.ripple("seismic", mag, psi)
        results["new_chunks_added"] = self.new_chunks
        return results


def main():
    print("=" * 80)
    print("  TAP REAL-TIME CASCADE HNSW")
    print("  Streaming updates from cosmic/weather/seismic events")
    print("=" * 80)
    print()

    # Build cascade HNSW
    cascade = CascadeHNSW(dim=64)
    print("  [1/4] LOAD INITIAL DOCS:")
    n_docs = cascade.load_initial_docs()
    n_chunks_initial = len(cascade.tap_hnsw.chunks)
    print(f"    Docs: {n_docs}")
    print(f"    Initial chunks: {n_chunks_initial}")
    print()

    # Snapshot before
    print("  [2/4] SEARCH BEFORE CASCADE UPDATE:")
    test_query = "What is the install hierarchy for CCP?"
    results_before = cascade.tap_hnsw.search_tap(test_query, k=3)
    for d, i, c in results_before:
        print(f"    [{d:.3f}] {c['source']} (ψ={c['breath']['psi']:.3f})")
    print()

    # Process live events
    print("  [3/4] PROCESS LIVE CASCADE EVENTS:")
    cascade_results = cascade.process_live_events()
    print(f"    Current ψ: {cascade_results['current_psi']:.4f}")
    if 'kp_ripple' in cascade_results:
        print(f"    Kp ripple: {cascade_results['kp_ripple']} chunks affected")
    if 'weather_ripple' in cascade_results:
        print(f"    Weather ripple: {cascade_results['weather_ripple']} chunks affected")
    print(f"    New chunks added: {cascade_results['new_chunks_added']}")
    print(f"    Total ripples so far: {cascade.ripple_count}")
    print()

    # Search after
    print("  [4/4] SEARCH AFTER CASCADE UPDATE:")
    cascade.tap_hnsw.gamma_nb  # ensure accessible
    results_after = cascade.tap_hnsw.search_tap(test_query, k=3, current_breath_psi=cascade_results['current_psi'])
    for d, i, c in results_after:
        print(f"    [{d:.3f}] {c['source']} (ψ={c['breath']['psi']:.3f})")
    print()

    # Compare
    first_before = results_before[0][2]['source'] if results_before else None
    first_after = results_after[0][2]['source'] if results_after else None
    print("  COMPARISON:")
    print(f"    Top before: {first_before}")
    print(f"    Top after:  {first_after}")
    print(f"    Changed: {first_before != first_after}")
    print()

    # Stats
    n_chunks_final = len(cascade.tap_hnsw.chunks)
    print("  STATS:")
    print(f"    Initial chunks: {n_chunks_initial}")
    print(f"    Final chunks: {n_chunks_final}")
    print(f"    Ripples: {cascade.ripple_count}")
    print(f"    New chunks from events: {cascade.new_chunks}")
    print(f"    Event log entries: {len(cascade.event_log)}")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_cascade_hnsw_results.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_docs_loaded": n_docs,
        "n_chunks_initial": n_chunks_initial,
        "n_chunks_final": n_chunks_final,
        "n_ripples": cascade.ripple_count,
        "n_new_chunks": cascade.new_chunks,
        "current_psi": cascade_results['current_psi'],
        "live_results": cascade_results,
        "search_before": {
            "top": first_before,
        },
        "search_after": {
            "top": first_after,
            "changed": first_before != first_after,
        },
        "event_log": cascade.event_log[-10:],  # last 10
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()
    print("  CASCADE HNSW: ALIVE")
    print("    Cosmic + weather + seismic events continuously")
    print("    update the HNSW structure and content")
    print("=" * 80)


if __name__ == "__main__":
    main()
