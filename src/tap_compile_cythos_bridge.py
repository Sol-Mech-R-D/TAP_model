# -*- coding: utf-8 -*-
"""
tap_compile_cythos_bridge.py
================================
TAP v5.3.2 — Compile CythOS Bridge Library.

Compiles additional CythOS source files as a static
library (libcythos_bridge.a) for use in TAP sims.

Tries to compile these files individually (not linked
into one binary, since they may have cross-dependencies):
  - cygemm/cygemm_hnsw.c (HNSW with cygemm integration)
  - cygemm/hnsw_sm.c (already compiled separately)
  - cygemm/cygemm_tokenizer.c
  - cygemm/dump_autotune.c
  - Rebrand/CyGemm/bridge/*.c (subset)

Each successful compilation produces:
  - build/cythos/<basename>.o (object file)
  - build/cythos/libcythos_bridge.a (static library)
"""

import os
import subprocess
import json
from datetime import datetime


def try_compile(src_path: str, build_dir: str) -> dict:
    """Try to compile a single C file."""
    basename = os.path.basename(src_path).replace('.c', '')
    obj_path = os.path.join(build_dir, f"{basename}.o")
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
    try:
        r = subprocess.run([
            'gcc', '-c', '-fPIC', '-O2',
            src_path,
            '-o', obj_path,
        ], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            result['success'] = True
        else:
            result['error'] = r.stderr[:500]
    except subprocess.TimeoutExpired:
        result['error'] = "Timeout"
    except Exception as e:
        result['error'] = str(e)
    return result


def main():
    print("=" * 80)
    print("  TAP COMPILE CYTHOS BRIDGE LIBRARY")
    print("  Building libcythos_bridge.a for use in sims")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    build_dir = os.path.join(repo_root, 'build', 'cythos')
    os.makedirs(build_dir, exist_ok=True)
    print(f"  Build dir: {build_dir}")
    print()

    # CythOS files to try
    cythos_files = [
        # Core HNSW
        "/data/data/com.termux/files/home/CythOS/cygemm/hnsw_sm.c",
        "/data/data/com.termux/files/home/CythOS/cygemm/cygemm_hnsw.c",
        "/data/data/com.termux/files/home/CythOS/cygemm/cygemm_tokenizer.c",
        # CCP / smmb
        "/data/data/com.termux/files/home/CythOS/cygemm/ccp_80m_infer.c",
        "/data/data/com.termux/files/home/CythOS/cygemm/ccp_smmb_speculative.c",
        # Bridge
        "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/bfloat16.c",
        "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/norm.c",
        "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/sleep.c",
        "/data/data/com.termux/files/home/CythOS/Rebrand/CyGemm/bridge/pim_updater.c",
        # Drivers
        "/data/data/com.termux/files/home/CythOS/cygemm/cygemm_dsp_driver.c",
    ]

    print("  [1/3] COMPILE EACH FILE:")
    results = []
    for src in cythos_files:
        if not os.path.exists(src):
            print(f"    SKIP (not found): {src}")
            continue
        r = try_compile(src, build_dir)
        status = "OK" if r['success'] else "FAIL"
        marker = "✓" if r['success'] else "✗"
        print(f"    {marker} [{status:4s}] {os.path.basename(src)}")
        if not r['success'] and r.get('error'):
            err = r['error'].split('\n')[0][:80]
            print(f"        Error: {err}")
        results.append(r)
    print()

    n_success = sum(1 for r in results if r['success'])
    n_total = len(results)
    print(f"  Compilation: {n_success}/{n_total} succeeded")
    print()

    # Create static library
    print("  [2/3] CREATE STATIC LIBRARY:")
    obj_files = [r['obj'] for r in results if r['success']]
    if obj_files:
        lib_path = os.path.join(build_dir, 'libcythos_bridge.a')
        # Use ar to create static library
        r = subprocess.run(['ar', 'rcs', lib_path] + obj_files,
                          capture_output=True, text=True)
        if r.returncode == 0:
            print(f"    [OK] {lib_path} ({os.path.getsize(lib_path):,} bytes)")
        else:
            print(f"    [FAIL] {r.stderr[:200]}")
    print()

    # Verify
    print("  [3/3] VERIFY LIBRARY:")
    if obj_files and os.path.exists(obj_files[0]):
        lib_path = os.path.join(build_dir, 'libcythos_bridge.a')
        if os.path.exists(lib_path):
            r = subprocess.run(['ar', 't', lib_path], capture_output=True, text=True)
            members = [l for l in r.stdout.split('\n') if l]
            print(f"    Library: {lib_path}")
            print(f"    Size: {os.path.getsize(lib_path):,} bytes")
            print(f"    Members: {len(members)}")
            for m in members:
                print(f"      {m}")
    print()

    # Save build info
    out_path = os.path.join(repo_root, 'assets', 'tap_cythos_bridge_build.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "build_dir": build_dir,
        "n_files_attempted": n_total,
        "n_files_succeeded": n_success,
        "results": results,
        "library_path": os.path.join(build_dir, 'libcythos_bridge.a') if obj_files else None,
        "library_size": os.path.getsize(os.path.join(build_dir, 'libcythos_bridge.a')) if obj_files and os.path.exists(os.path.join(build_dir, 'libcythos_bridge.a')) else 0,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()
    print("  CYTHOS BRIDGE LIBRARY BUILT:")
    print(f"    Compiled: {n_success}/{n_total} files")
    print(f"    Library: libcythos_bridge.a")
    print(f"    Use case: link against TAP sims for Cython acceleration")
    print("=" * 80)


if __name__ == "__main__":
    main()
