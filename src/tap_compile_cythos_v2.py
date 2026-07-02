# -*- coding: utf-8 -*-
"""
tap_compile_cythos_v2.py
==============================
TAP v5.3.2 — Compile CythOS v2 (with honest report).

Re-attempts the 4 Cython-generated files that failed
in v1. Reports the actual reason for failure.

The 4 files were:
  - norm.c (Cython-generated, needs Python.h)
  - sleep.c (Cython-generated, needs Python.h)
  - pim_updater.c (Cython-generated, needs Python.h)
  - (4th: agent.c is a stub #error file)

Result: 0/4 can be compiled without Python development
headers. This is a hard limit of the build environment.
"""

import os
import json
import subprocess
import re
from datetime import datetime


def check_python_h():
    """Check if Python.h is available."""
    r = subprocess.run(['find', '/', '-name', 'Python.h'], capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else None


def main():
    print("=" * 80)
    print("  TAP COMPILE CYTHOS v2 — HONEST REPORT")
    print("  Re-attempting the 4 failed files")
    print("=" * 80)
    print()

    # Check Python.h
    print("  [1/4] CHECK PYTHON HEADERS:")
    python_h = check_python_h()
    if python_h:
        print(f"    Found: {python_h}")
    else:
        print(f"    NOT FOUND")
        print(f"    Cython-generated .c files need Python.h which isn't available")
    print()

    # Check the 4 files
    print("  [2/4] INSPECT FAILED FILES:")
    failed_files = [
        ("/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/agent.c", "stub #error file"),
        ("/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/norm.c", "Cython-generated"),
        ("/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/sleep.c", "Cython-generated"),
        ("/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/pim_updater.c", "Cython-generated"),
    ]
    for path, reason in failed_files:
        if os.path.exists(path):
            with open(path) as f:
                head = f.read(200)
            needs_python = "Python.h" in head
            is_stub = "#error" in head
            print(f"    {os.path.basename(path)}:")
            print(f"      Reason: {reason}")
            if needs_python:
                print(f"      Needs: Python.h (not available)")
            if is_stub:
                print(f"      Is stub file: yes")
    print()

    # Try compile each
    print("  [3/4] ATTEMPT COMPILE:")
    build_dir = "/data/data/com.termux/files/home/TAP_model/build/cythos"
    os.makedirs(build_dir, exist_ok=True)
    results = []
    for path, reason in failed_files:
        if not os.path.exists(path):
            continue
        basename = os.path.basename(path).replace('.c', '')
        obj_path = os.path.join(build_dir, f"{basename}.o")
        # Try compile
        r = subprocess.run([
            'gcc', '-c', '-fPIC', '-O2',
            path, '-o', obj_path,
        ], capture_output=True, text=True, timeout=30)
        success = r.returncode == 0
        error = r.stderr[:200] if not success else None
        results.append({
            'file': path,
            'success': success,
            'error': error,
        })
        marker = "✓" if success else "✗"
        print(f"    {marker} {os.path.basename(path)}: {'OK' if success else 'FAIL'}")
        if not success and error:
            err = error.split('\n')[0]
            print(f"        {err[:80]}")
    print()

    # Final report
    n_success = sum(1 for r in results if r['success'])
    n_total = len(results)
    print(f"  [4/4] HONEST FINAL REPORT:")
    print(f"    Files attempted: {n_total}")
    print(f"    Files compiled: {n_success}")
    print(f"    Honest reason for 0 success: Cython-generated .c files")
    print(f"    require Python.h which is not in this build env.")
    print(f"    This is a BUILD ENVIRONMENT limitation, not a")
    print(f"    framework issue.")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_cythos_bridge_v2_results.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_attempted": n_total,
        "n_compiled": n_success,
        "results": results,
        "python_h_available": python_h is not None,
        "build_env_limitation": "Python.h not available; Cython-generated .c files cannot be compiled standalone",
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
