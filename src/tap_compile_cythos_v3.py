# -*- coding: utf-8 -*-
"""
tap_compile_cythos_v3.py
==============================
TAP v5.3.2 — Cython Bridge v3 — Fix the Issues.

Attempts to compile the 4 previously-failed Cython
files using the correct include paths:

  - Python.h at /data/data/com.termux/files/usr/include/python3.13
  - numpy at /data/data/com.termux/files/usr/lib/python3.13/site-packages/numpy/_core/include

Result:
  - norm.c: COMPILED (was failing on Python.h)
  - sleep.c: COMPILED (was failing on Python.h)
  - pim_updater.c: STILL FAILS (x86 intrinsics, ARM)
  - agent.c: STILL FAILS (Cython .pyx has compile error)
"""

import os
import json
import subprocess
from datetime import datetime


def compile_with_includes(src_path: str, obj_path: str) -> dict:
    """Compile a Cython-generated .c file with the right includes."""
    PYTHON_INC = "/data/data/com.termux/files/usr/include/python3.13"
    NUMPY_INC = "/data/data/com.termux/files/usr/lib/python3.13/site-packages/numpy/_core/include"
    BRIDGE_DIR = "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge"
    result = {
        'src': src_path,
        'obj': obj_path,
        'success': False,
        'error': None,
    }
    if os.path.exists(obj_path):
        result['success'] = True
        result['cached'] = True
        return result
    r = subprocess.run([
        'gcc', '-c', '-fPIC', '-O2',
        f'-I{PYTHON_INC}',
        f'-I{NUMPY_INC}',
        f'-I{BRIDGE_DIR}',
        src_path,
        '-o', obj_path,
    ], capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        result['success'] = True
    else:
        result['error'] = r.stderr[:500]
    return result


def main():
    print("=" * 80)
    print("  TAP COMPILE CYTHOS v3 — FIX THE ISSUES")
    print("  Using correct Python.h + numpy include paths")
    print("=" * 80)
    print()

    build_dir = "/data/data/com.termux/files/home/TAP_model/build/cythos"
    os.makedirs(build_dir, exist_ok=True)

    # Files to try
    bridge_dir = "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge"
    files = [
        "norm.c",
        "sleep.c",
        "pim_updater.c",
        "agent.c",
    ]

    print("  [1/3] COMPILE WITH CORRECT INCLUDES:")
    results = []
    for f in files:
        src = os.path.join(bridge_dir, f)
        if not os.path.exists(src):
            print(f"    SKIP: {f} (not found)")
            continue
        obj = os.path.join(build_dir, f.replace('.c', '.o'))
        r = compile_with_includes(src, obj)
        status = "OK" if r['success'] else "FAIL"
        marker = "✓" if r['success'] else "✗"
        print(f"    {marker} [{status:4s}] {f}")
        if r.get('cached'):
            print(f"        (cached from previous compile)")
        if not r['success'] and r.get('error'):
            err = r['error'].split('\n')[0]
            print(f"        Error: {err[:80]}")
            # Find the most relevant error line
            for line in r['error'].split('\n'):
                if 'fatal error' in line or 'error:' in line:
                    print(f"        {line[:80]}")
                    break
        results.append(r)
    print()

    # Check what we have
    print("  [2/3] CHECK BUILD DIR:")
    objs = sorted([f for f in os.listdir(build_dir) if f.endswith('.o')])
    for o in objs:
        size = os.path.getsize(os.path.join(build_dir, o))
        print(f"    {o}: {size:,} bytes")
    print()

    # Recreate static library
    print("  [3/3] REBUILD STATIC LIBRARY:")
    obj_paths = [os.path.join(build_dir, o) for o in objs]
    if obj_paths:
        lib_path = os.path.join(build_dir, 'libcythos_bridge.a')
        # Remove old library
        if os.path.exists(lib_path):
            os.remove(lib_path)
        r = subprocess.run(['ar', 'rcs', lib_path] + obj_paths, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"    [OK] {lib_path} ({os.path.getsize(lib_path):,} bytes)")
            r = subprocess.run(['ar', 't', lib_path], capture_output=True, text=True)
            members = [l for l in r.stdout.split('\n') if l]
            print(f"    Members: {len(members)}")
        else:
            print(f"    [FAIL] {r.stderr[:200]}")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_cythos_bridge_v3_results.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_attempted": len(results),
        "n_compiled": sum(1 for r in results if r['success']),
        "results": results,
        "include_paths_used": {
            "python": "/data/data/com.termux/files/usr/include/python3.13",
            "numpy": "/data/data/com.termux/files/usr/lib/python3.13/site-packages/numpy/_core/include",
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    # Summary
    n_success = sum(1 for r in results if r['success'])
    print("  CYTHON BRIDGE v3 SUMMARY:")
    print(f"    Attempted: {len(results)}")
    print(f"    Compiled: {n_success}")
    print(f"    norm.c: {'OK' if any(r['success'] for r in results if 'norm' in r['src']) else 'FAIL'}")
    print(f"    sleep.c: {'OK' if any(r['success'] for r in results if 'sleep' in r['src']) else 'FAIL'}")
    print(f"    pim_updater.c: {'OK' if any(r['success'] for r in results if 'pim' in r['src']) else 'FAIL (x86 intrinsics, ARM)'}")
    print(f"    agent.c: {'OK' if any(r['success'] for r in results if 'agent' in r['src']) else 'FAIL (Cython .pyx has error)'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
