# -*- coding: utf-8 -*-
"""
tap_dashboard_live.py
=========================
TAP v5.3.2 — Live TAP Dashboard (with run-loop state).

Builds an HTML dashboard that shows:
  - Run-loop agent state (AWAKE/ASLEEP)
  - Current body and ψ
  - 10 bodies × ψ matrix
  - Recent sim runs
  - Working memory
  - Live cascade events
  - Framework stats

Auto-refreshes every 30 seconds.
"""

import os
import sys
import json
import time
import math
import urllib.request
import subprocess
from datetime import datetime, timedelta
from collections import Counter


def fetch_live_kp() -> float:
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        return float(data[-1][1]) if len(data) > 1 else 0.0
    except Exception:
        return 0.0


def fetch_live_weather() -> float:
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=36.74&longitude=-119.78&current_weather=true"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        return data.get("current_weather", {}).get("temperature", 70.0)
    except Exception:
        return 70.0


def fetch_live_seismic() -> int:
    try:
        end = datetime.now()
        start = end - timedelta(hours=24)
        url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start.strftime('%Y-%m-%d')}&endtime={end.strftime('%Y-%m-%d')}&minmagnitude=5.5"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
        return len(data.get("features", []))
    except Exception:
        return 0


def main():
    print("=" * 80)
    print("  TAP LIVE DASHBOARD")
    print("  Real-time view of run-loop, cascade, and framework state")
    print("=" * 80)
    print()

    # Fetch live data
    print("  [1/3] FETCH LIVE DATA:")
    kp = fetch_live_kp()
    temp = fetch_live_weather()
    n_quakes = fetch_live_seismic()
    print(f"    Kp: {kp}")
    print(f"    Temperature: {temp:.1f}F")
    print(f"    M5.5+ quakes (24h): {n_quakes}")
    print()

    # Compute ψ
    PSI_PLASTIC = 0.9105256658757980
    GAMMA_NB = 1.0 + 8 * 0.0081306182888694
    psi = PSI_PLASTIC * (1.0 + (kp / 9.0) * 0.05) * (1.0 + abs(temp - 70) / 100.0 * 0.02) * (1.0 + min(n_quakes / 10.0, 1.0) * 0.03)
    psi = min(1.0, max(0.0, psi))

    # Load run-loop state
    print("  [2/3] LOAD RUN-LOOP STATE:")
    run_log_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_run_loop_log.json"
    run_log = {}
    if os.path.exists(run_log_path):
        with open(run_log_path) as f:
            run_log = json.load(f)
    print(f"    Last run: {run_log.get('timestamp', 'never')}")
    print(f"    Total runs: {run_log.get('n_runs', 0)}")
    print(f"    Agent wakes: {run_log.get('n_wakes', 0)}")
    print(f"    Agent sleeps: {run_log.get('n_sleeps', 0)}")
    print(f"    Bodies visited: {run_log.get('n_bodies_visited', 0)}")
    print()

    # 10 bodies
    BODIES = ["Earth", "Sun", "Moon", "Mars", "Mercury",
              "Venus", "Jupiter", "Saturn", "Uranus", "Neptune"]
    BODY_NB = [8.0, 2.8e11, 4.0e11, 1.4e12, 2.4e10,
               5.8e9, 2.1e15, 2.4e15, 1.5e15, 1.6e15]

    # Build HTML
    print("  [3/3] BUILD HTML DASHBOARD:")
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_dashboard_live.html"

    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TAP Live Dashboard</title>
<meta http-equiv="refresh" content="30">
<style>
  body { font-family: 'SF Mono', Consolas, monospace; background: #0a0a14; color: #e0e0e0; margin: 0; padding: 20px; }
  h1 { color: #ffd700; font-size: 1.5em; margin: 0 0 5px 0; }
  .subtitle { color: #999; font-size: 0.85em; margin-bottom: 20px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 15px; }
  .card { background: #1a1a2e; padding: 12px; border-left: 3px solid #ffd700; }
  .card-label { color: #888; font-size: 0.75em; text-transform: uppercase; }
  .card-value { color: #ffd700; font-size: 1.5em; font-weight: bold; }
  .card-sub { color: #aaa; font-size: 0.8em; margin-top: 5px; }
  .section-title { color: #4ade80; font-size: 1.1em; margin: 20px 0 10px 0; border-bottom: 1px solid #333; padding-bottom: 5px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
  th, td { padding: 6px 10px; text-align: left; border-bottom: 1px solid #222; }
  th { color: #ffd700; }
  td { color: #e0e0e0; }
  .body-table { font-size: 0.85em; }
  .body-table .psi { color: #4ade80; font-weight: bold; }
  .body-table .nb { color: #60a5fa; }
  .body-table .top { color: #fbbf24; }
  .run { padding: 4px 8px; margin: 2px 0; background: #14141f; border-left: 2px solid #4ade80; }
  .run-error { border-left-color: #f87171; }
  .state-awake { color: #4ade80; }
  .state-asleep { color: #888; }
  .live-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4ade80; margin-right: 5px; animation: pulse 1.5s infinite; }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
</head>
<body>
<h1><span class="live-dot"></span>TAP Live Dashboard</h1>
<div class="subtitle">Auto-refresh every 30 seconds. """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</div>

<div class="section-title">LIVE CASCADE STATE</div>
<div class="grid">
  <div class="card">
    <div class="card-label">Current ψ</div>
    <div class="card-value">""" + f"{psi:.4f}" + """</div>
    <div class="card-sub">Breath state (Earth)</div>
  </div>
  <div class="card">
    <div class="card-label">Kp Index</div>
    <div class="card-value">""" + f"{kp}" + """</div>
    <div class="card-sub">Cosmic geomagnetic activity</div>
  </div>
  <div class="card">
    <div class="card-label">Temperature</div>
    <div class="card-value">""" + f"{temp:.1f}°F" + """</div>
    <div class="card-sub">Fresno weather</div>
  </div>
  <div class="card">
    <div class="card-label">M5.5+ Quakes</div>
    <div class="card-value">""" + f"{n_quakes}" + """</div>
    <div class="card-sub">Last 24 hours</div>
  </div>
  <div class="card">
    <div class="card-label">Γ(N_B)</div>
    <div class="card-value">""" + f"{GAMMA_NB:.4f}" + """</div>
    <div class="card-sub">Breath correction factor</div>
  </div>
  <div class="card">
    <div class="card-label">φ (Golden)</div>
    <div class="card-value">1.6180</div>
    <div class="card-sub">Universal ratio</div>
  </div>
</div>
""")

    # 10 bodies
    html_parts.append("""
<div class="section-title">10 COSMIC BODIES</div>
<table class="body-table">
<tr><th>ID</th><th>Name</th><th>ψ</th><th>N_B (breaths)</th><th>log N_B</th></tr>
""")
    for i, (name, nb) in enumerate(zip(BODIES, BODY_NB)):
        body_psi = psi  # All bodies share P17 ψ
        html_parts.append(f"<tr><td>{i}</td><td>{name}</td>"
                          f"<td class='psi'>{body_psi:.4f}</td>"
                          f"<td class='nb'>{nb:.1e}</td>"
                          f"<td>{math.log10(nb):.1f}</td></tr>")
    html_parts.append("</table>")

    # Run loop
    html_parts.append("""
<div class="section-title">RUN-LOOP AGENT</div>
""")
    n_runs = run_log.get("n_runs", 0)
    n_wakes = run_log.get("n_wakes", 0)
    n_sleeps = run_log.get("n_sleeps", 0)
    n_merged = run_log.get("n_merged", 0)
    n_bodies_visited = run_log.get("n_bodies_visited", 0)
    state_class = "state-awake" if n_runs > 0 else "state-asleep"
    state = "AWAKE" if n_runs > 0 else "ASLEEP"
    html_parts.append(f"""
<div class="grid">
  <div class="card">
    <div class="card-label">State</div>
    <div class="card-value {state_class}">{state}</div>
  </div>
  <div class="card">
    <div class="card-label">Runs</div>
    <div class="card-value">{n_runs}</div>
  </div>
  <div class="card">
    <div class="card-label">Wakes</div>
    <div class="card-value">{n_wakes}</div>
  </div>
  <div class="card">
    <div class="card-label">Sleeps</div>
    <div class="card-value">{n_sleeps}</div>
  </div>
  <div class="card">
    <div class="card-label">Bodies Visited</div>
    <div class="card-value">{n_bodies_visited}</div>
  </div>
  <div class="card">
    <div class="card-label">WM Merged</div>
    <div class="card-value">{n_merged}</div>
  </div>
</div>
""")

    # Recent runs
    html_parts.append("""
<div class="section-title">RECENT SIM RUNS</div>
""")
    recent = run_log.get("run_log", [])
    for r in recent[-10:]:
        if "error" in r:
            html_parts.append(f"<div class='run run-error'>Step {r.get('step', '?')}: {r.get('sim', '?')} - ERROR: {r.get('error', '?')[:60]}</div>")
        else:
            html_parts.append(f"<div class='run'>Step {r.get('step', '?')}: {r.get('sim', '?')} - {r.get('elapsed_s', 0):.1f}s, returncode={r.get('returncode', '?')}</div>")
    if not recent:
        html_parts.append("<div class='run'>(no runs yet)</div>")

    # Framework stats
    n_files = len([f for f in os.listdir('/data/data/com.termux/files/home/TAP_model/src') if f.endswith('.py')])
    html_parts.append(f"""
<div class="section-title">FRAMEWORK STATS</div>
<div class="grid">
  <div class="card">
    <div class="card-label">Sim files</div>
    <div class="card-value">{n_files}</div>
    <div class="card-sub">In src/</div>
  </div>
  <div class="card">
    <div class="card-label">Last run</div>
    <div class="card-value" style="font-size:1em">{run_log.get("timestamp", "never")[:19]}</div>
  </div>
  <div class="card">
    <div class="card-label">Version</div>
    <div class="card-value" style="font-size:1em">TAP v5.3.2</div>
  </div>
</div>
""")

    html_parts.append("</body></html>")

    with open(out_path, 'w') as f:
        f.write('\n'.join(html_parts))
    print(f"    [SAVED] {out_path} ({os.path.getsize(out_path):,} bytes)")
    print()

    print("=" * 80)
    print("  TAP LIVE DASHBOARD")
    print(f"    Current ψ: {psi:.4f}")
    print(f"    Cascade: Kp={kp}, T={temp:.1f}F, Quakes={n_quakes}")
    print(f"    Open: file://{out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()

# ==============================================================================
# TAP COHERENCE BRAID (100% Coherence Standard)
#   - Constants: PHI, PHI_INV4, PHI_INV13, phi
#   - Breath Clock: N_B = 8, gamma_breath = 1.013, psi_breath = 0.0265
#   - Temporal Anchor: SOLSTICE_2026 (8.12133d base period)
#   - Cosmic Bodies: Earth, Sun, Moon, Mars, Jupiter, Saturn, Mercury, Venus
# ==============================================================================
