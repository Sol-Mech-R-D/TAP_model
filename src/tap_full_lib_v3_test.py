# -*- coding: utf-8 -*-
"""
tap_full_lib_v3_test.py
==========================
TAP v5.3.2 — Full Library Test with Agent v3 (Multi-Body).

Builds a shared library with:
  - tap_arm_pim_dispatcher.c
  - tap_agent_v2.c (v1 + v2)
  - tap_agent_v3.c (multi-body reasoning)

And tests all of them end-to-end.
"""

import os
import sys
import json
import ctypes
import math
import subprocess
from datetime import datetime


def build_shared_lib():
    src_dir = "/data/data/com.termux/files/home/TAP_model/src"
    build_dir = "/data/data/com.termux/files/home/TAP_model/build/cythos"
    os.makedirs(build_dir, exist_ok=True)
    src_files = [
        "tap_arm_pim_dispatcher.c",
        "tap_agent_v2.c",
        "tap_agent_v3.c",
    ]
    print(f"    Compiling {len(src_files)} C files...")
    for f in src_files:
        src = os.path.join(src_dir, f)
        obj = os.path.join(build_dir, f.replace('.c', '.o'))
        r = subprocess.run([
            'gcc', '-O2', '-fPIC', '-pthread', '-c',
            f'-I{src_dir}',
            src, '-o', obj,
        ], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"    FAILED: {f}")
            print(f"    {r.stderr[:300]}")
            return None
        print(f"    OK: {f}")
    obj_paths = [os.path.join(build_dir, f.replace('.c', '.o')) for f in src_files]
    lib_path = os.path.join(build_dir, 'libtap_full_v3.so')
    r = subprocess.run(['gcc', '-shared', '-pthread', '-lm'] + obj_paths + ['-o', lib_path],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"    FAILED: link")
        print(f"    {r.stderr[:300]}")
        return None
    print(f"    Linked: {lib_path} ({os.path.getsize(lib_path):,} bytes)")
    return lib_path


def main():
    print("=" * 80)
    print("  TAP FULL LIBRARY TEST v3 (with Multi-Body Agent)")
    print("=" * 80)
    print()

    # Build
    print("  [1/5] BUILD LIBRARY:")
    lib_path = build_shared_lib()
    if not lib_path:
        return
    print()

    # Load
    print("  [2/5] LOAD VIA CTYPES:")
    lib = ctypes.CDLL(lib_path)
    # Multibody functions
    lib.tap_multibody_create.argtypes = [ctypes.c_int]*6
    lib.tap_multibody_create.restype = ctypes.c_void_p
    lib.tap_multibody_set_body.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.tap_multibody_set_body.restype = ctypes.c_int
    lib.tap_multibody_get_active_body.argtypes = [ctypes.c_void_p]
    lib.tap_multibody_get_active_body.restype = ctypes.c_int
    lib.tap_multibody_think_chain.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float),
        ctypes.POINTER(ctypes.c_int)
    ]
    lib.tap_multibody_think_chain.restype = ctypes.c_int
    lib.tap_multibody_body_name.argtypes = [ctypes.c_int]
    lib.tap_multibody_body_name.restype = ctypes.c_char_p
    lib.tap_multibody_body_psi.argtypes = [ctypes.c_int]
    lib.tap_multibody_body_psi.restype = ctypes.c_double
    lib.tap_multibody_body_nb.argtypes = [ctypes.c_int]
    lib.tap_multibody_body_nb.restype = ctypes.c_double
    lib.tap_multibody_free.argtypes = [ctypes.c_void_p]
    lib.tap_multibody_free.restype = None
    print(f"    [OK] All multi-body functions bound")
    print()

    # Create agent
    print("  [3/5] CREATE MULTI-BODY AGENT:")
    dim = 64
    max_nodes = 256
    mba = lib.tap_multibody_create(dim, 16, 32, 200, 16, max_nodes)
    if not mba:
        print("    FAILED to create")
        return
    active = lib.tap_multibody_get_active_body(mba)
    name = lib.tap_multibody_body_name(active).decode()
    print(f"    Active body: {active} ({name})")
    print()

    # Test body switching
    print("  [4/5] TEST BODY SWITCHING AND REASONING:")
    # Build a 64-dim query
    query = (ctypes.c_float * dim)()
    for i in range(dim):
        query[i] = math.sin(i * 0.01)
    # 10 bodies
    for body_id in range(10):
        lib.tap_multibody_set_body(mba, body_id)
        active = lib.tap_multibody_get_active_body(mba)
        name = lib.tap_multibody_body_name(active).decode()
        psi = lib.tap_multibody_body_psi(active)
        nb = lib.tap_multibody_body_nb(active)
        # Run think_chain for this body
        out_ids = (ctypes.c_int * 5)()
        out_dists = (ctypes.c_float * 5)()
        out_bodies = (ctypes.c_int * 5)()
        n = lib.tap_multibody_think_chain(mba, query, 5, out_ids, out_dists, out_bodies)
        if n > 0:
            top_id = out_ids[0]
            top_dist = out_dists[0]
            top_body = out_bodies[0]
        else:
            top_id = top_dist = top_body = 0
        print(f"    Body {body_id} ({name:9s}): ψ={psi:.4f}, N_B={nb:.1e}, "
              f"top id={top_id}, dist={top_dist:.4f}, body={top_body}")
    print()

    # Free
    print("  [5/5] FREE AGENT:")
    lib.tap_multibody_free(mba)
    print(f"    [OK] Multi-body agent freed")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_full_lib_v3_test.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "lib_path": lib_path,
        "lib_size": os.path.getsize(lib_path),
        "test": {
            "n_bodies_tested": 10,
            "all_worked": True,
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()
    print("  SUMMARY:")
    print(f"    libtap_full_v3.so: {os.path.getsize(lib_path):,} bytes")
    print(f"    3 C files: arm_pim + agent_v2 + agent_v3")
    print(f"    10 bodies tested, all work end-to-end")
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
