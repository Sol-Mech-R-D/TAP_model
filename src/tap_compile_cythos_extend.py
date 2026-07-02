# -*- coding: utf-8 -*-
"""
tap_compile_cythos_extend.py
=================================
TAP v5.3.2 — Extend Cython Bridge Library.

Tries to compile ALL available Cython-generated .c
files in the bridge/ directory and rebuild the
static library.

Tracks which files compile and which fail, with
honest reasons for each failure.
"""

import os
import json
import subprocess
import re
from datetime import datetime


def categorize_error(stderr: str) -> str:
    """Categorize the error from gcc output."""
    if "x86 and x64 architecture" in stderr:
        return "x86-intrinsics-on-ARM"
    if "Python.h" in stderr:
        return "missing-Python.h"
    if "numpy/arrayobject.h" in stderr:
        return "missing-numpy"
    if "Cython .pyx" in stderr or "Do not use this file" in stderr:
        return "Cython-stub-file"
    if "fatal error" in stderr:
        # Extract the missing header
        m = re.search(r"fatal error:\s*['\"]?([^'\"]+?)(?:['\"]|\s*$)", stderr, re.MULTILINE)
        if m:
            return f"missing-{m.group(1).strip()}"
    return "unknown"


def compile_one(src_path: str, obj_path: str) -> dict:
    """Compile a single .c file with the right includes."""
    PYTHON_INC = "/data/data/com.termux/files/usr/include/python3.13"
    NUMPY_INC = "/data/data/com.termux/files/usr/lib/python3.13/site-packages/numpy/_core/include"
    BRIDGE_DIR = "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge"
    result = {
        'src': os.path.basename(src_path),
        'obj': os.path.basename(obj_path),
        'success': False,
        'error': None,
        'category': None,
    }
    r = subprocess.run([
        'gcc', '-c', '-fPIC', '-O2',
        f'-I{PYTHON_INC}',
        f'-I{NUMPY_INC}',
        f'-I{BRIDGE_DIR}',
        src_path,
        '-o', obj_path,
    ], capture_output=True, text=True, timeout=300)
    if r.returncode == 0:
        result['success'] = True
    else:
        result['error'] = r.stderr[:500]
        result['category'] = categorize_error(r.stderr)
    return result


def main():
    print("=" * 80)
    print("  TAP COMPILE CYTHOS EXTEND")
    print("  Compile all available bridge/ .c files")
    print("=" * 80)
    print()

    bridge_dir = "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge"
    build_dir = "/data/data/com.termux/files/home/TAP_model/build/cythos"
    os.makedirs(build_dir, exist_ok=True)

    # All .c files in bridge/
    all_c_files = sorted([
        os.path.join(bridge_dir, f)
        for f in os.listdir(bridge_dir)
        if f.endswith('.c')
    ])
    print(f"  [1/3] DISCOVER: {len(all_c_files)} .c files in bridge/")
    print()

    # Compile each
    print("  [2/3] COMPILE EACH:")
    results = []
    for src in all_c_files:
        basename = os.path.basename(src).replace('.c', '.o')
        obj = os.path.join(build_dir, basename)
        r = compile_one(src, obj)
        results.append(r)
        marker = "✓" if r['success'] else "✗"
        cat = f" ({r['category']})" if r['category'] else ""
        print(f"    {marker} {os.path.basename(src):30s}{cat}")
    print()

    # Stats
    n_success = sum(1 for r in results if r['success'])
    n_fail = len(results) - n_success
    print(f"  Results: {n_success}/{len(results)} compiled, {n_fail} failed")
    print()

    # Categorize failures
    fail_categories = {}
    for r in results:
        if not r['success']:
            cat = r['category'] or 'unknown'
            fail_categories[cat] = fail_categories.get(cat, 0) + 1
    if fail_categories:
        print("  FAILURE CATEGORIES:")
        for cat, n in fail_categories.items():
            print(f"    {cat}: {n}")
        print()

    # Rebuild library
    print("  [3/3] REBUILD STATIC LIBRARY:")
    obj_paths = [os.path.join(build_dir, f) for f in os.listdir(build_dir) if f.endswith('.o')]
    obj_paths = [p for p in obj_paths if os.path.getsize(p) > 0]
    if obj_paths:
        lib_path = os.path.join(build_dir, 'libcythos_bridge.a')
        if os.path.exists(lib_path):
            os.remove(lib_path)
        r = subprocess.run(['ar', 'rcs', lib_path] + obj_paths, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"    [OK] {lib_path}")
            print(f"    Size: {os.path.getsize(lib_path):,} bytes")
            r = subprocess.run(['ar', 't', lib_path], capture_output=True, text=True)
            members = [l for l in r.stdout.split('\n') if l]
            print(f"    Members: {len(members)}")
            for m in members:
                print(f"      {m}")

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_cythos_bridge_extend_results.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_total": len(results),
        "n_compiled": n_success,
        "n_failed": n_fail,
        "fail_categories": fail_categories,
        "results": results,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    print(f"  EXTENDED BRIDGE: {n_success} files compiled, library has {len(obj_paths)} members")
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
