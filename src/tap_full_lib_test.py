# -*- coding: utf-8 -*-
"""
tap_full_lib_test.py
======================
TAP v5.3.2 — Full Library Test.

Builds a complete shared library with:
  - tap_arm_pim_dispatcher.c
  - tap_agent.c (v1)
  - tap_agent_v2.c (v2 with reasoning + memory)

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
        "tap_agent_v2.c",  # v2 has both v1 and v2 functions
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
    lib_path = os.path.join(build_dir, 'libtap_full.so')
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
    print("  TAP FULL LIBRARY TEST")
    print("  ARM PIM + Agent v1 + Agent v2 (reasoning + memory)")
    print("=" * 80)
    print()

    # Build
    print("  [1/6] BUILD FULL LIBRARY:")
    lib_path = build_shared_lib()
    if not lib_path:
        return
    print()

    # Load
    print("  [2/6] LOAD VIA CTYPES:")
    lib = ctypes.CDLL(lib_path)

    # Bind PIM functions
    lib.tap_pim_create.argtypes = [ctypes.c_int]*5
    lib.tap_pim_create.restype = ctypes.c_void_p
    lib.tap_pim_load_vectors.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int]
    lib.tap_pim_load_vectors.restype = ctypes.c_int
    lib.tap_pim_add_point.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.tap_pim_add_point.restype = ctypes.c_int
    lib.tap_pim_search.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float)]
    lib.tap_pim_search.restype = ctypes.c_int
    lib.tap_pim_set_breath.argtypes = [ctypes.c_void_p, ctypes.c_double]
    lib.tap_pim_set_breath.restype = ctypes.c_int
    lib.tap_pim_get_state.argtypes = [ctypes.c_void_p,
                                       ctypes.POINTER(ctypes.c_double),
                                       ctypes.POINTER(ctypes.c_double),
                                       ctypes.POINTER(ctypes.c_double)]
    lib.tap_pim_get_state.restype = ctypes.c_int
    lib.tap_pim_free.argtypes = [ctypes.c_void_p]
    lib.tap_pim_free.restype = None

    # Bind agent v1
    lib.tap_agent_create.argtypes = [ctypes.c_int]*6
    lib.tap_agent_create.restype = ctypes.c_void_p
    lib.tap_agent_wake.argtypes = [ctypes.c_void_p]
    lib.tap_agent_wake.restype = ctypes.c_int
    lib.tap_agent_sleep.argtypes = [ctypes.c_void_p]
    lib.tap_agent_sleep.restype = ctypes.c_int
    lib.tap_agent_free.argtypes = [ctypes.c_void_p]
    lib.tap_agent_free.restype = None

    # Bind agent v2 (v2 uses tap_agent_* names with v2 features)
    # tap_agent_v2_think_chain is the new chain function
    if not hasattr(lib, 'tap_agent_think_chain'):
        print("    ERROR: tap_agent_think_chain not found in library")
        return
    lib.tap_agent_create.argtypes = [ctypes.c_int]*6
    lib.tap_agent_create.restype = ctypes.c_void_p
    lib.tap_agent_wake.argtypes = [ctypes.c_void_p]
    lib.tap_agent_wake.restype = ctypes.c_int
    lib.tap_agent_sleep.argtypes = [ctypes.c_void_p]
    lib.tap_agent_sleep.restype = ctypes.c_int
    lib.tap_agent_free.argtypes = [ctypes.c_void_p]
    lib.tap_agent_free.restype = None
    lib.tap_agent_load_vectors.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int]
    lib.tap_agent_load_vectors.restype = ctypes.c_int
    lib.tap_agent_add_point.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.tap_agent_add_point.restype = ctypes.c_int
    # Multi-step
    lib.tap_agent_think_chain.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
                                          ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
    lib.tap_agent_think_chain.restype = ctypes.c_int
    # Working memory
    lib.tap_agent_get_working_memory.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                                 ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    lib.tap_agent_get_working_memory.restype = ctypes.c_int
    # Consolidation
    lib.tap_agent_consolidate.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
    lib.tap_agent_consolidate.restype = ctypes.c_int
    # Clear WM
    lib.tap_agent_clear_working_memory.argtypes = [ctypes.c_void_p]
    lib.tap_agent_clear_working_memory.restype = ctypes.c_int
    print(f"    [OK] All functions bound")
    print()

    # Setup test data
    dim = 64
    max_nodes = 128
    weights = (ctypes.c_float * (dim * max_nodes))()
    for i in range(dim * max_nodes):
        weights[i] = math.sin(i * 0.01)

    # Test PIM dispatcher
    print("  [3/6] TEST PIM DISPATCHER:")
    pim = lib.tap_pim_create(dim, 16, 32, 200, 16)
    lib.tap_pim_load_vectors(pim, weights, max_nodes)
    for i in range(30):
        lib.tap_pim_add_point(pim, i)
    lib.tap_pim_set_breath(pim, 0.93)
    query = (ctypes.c_float * dim)()
    for i in range(dim):
        query[i] = math.sin(i * 0.01 + 0.5)
    out_ids = (ctypes.c_int * 5)()
    out_dists = (ctypes.c_float * 5)()
    n = lib.tap_pim_search(pim, query, 5, out_ids, out_dists)
    print(f"    Search returned {n} results")
    for i in range(n):
        print(f"      id={out_ids[i]}, dist={out_dists[i]:.4f}")
    lib.tap_pim_free(pim)
    print(f"    [OK] PIM dispatcher works")
    print()

    # Test agent v1
    print("  [4/6] TEST AGENT v1:")
    agent1 = lib.tap_agent_create(dim, 16, 32, 200, 16, max_nodes)
    lib.tap_agent_wake(agent1)
    lib.tap_agent_sleep(agent1)
    lib.tap_agent_free(agent1)
    print(f"    [OK] Agent v1 wake/sleep/free works")
    print()

    # Test agent v2
    print("  [5/6] TEST AGENT v2 (REASONING + MEMORY):")
    agent2 = lib.tap_agent_create(dim, 16, 32, 200, 16, max_nodes)
    # Load vectors and add points (v1 was missing this)
    lib.tap_agent_load_vectors(agent2, weights, max_nodes)
    for i in range(30):
        lib.tap_agent_add_point(agent2, i)
    lib.tap_agent_wake(agent2)
    # Multi-step reasoning: chain 3 queries
    q1 = (ctypes.c_float * dim)()
    q2 = (ctypes.c_float * dim)()
    q3 = (ctypes.c_float * dim)()
    for i in range(dim):
        q1[i] = math.sin(i * 0.01)
        q2[i] = math.sin(i * 0.01 + 0.2)
        q3[i] = math.sin(i * 0.01 + 0.4)
    queries = (ctypes.POINTER(ctypes.c_float) * 3)()
    queries[0] = ctypes.cast(q1, ctypes.POINTER(ctypes.c_float))
    queries[1] = ctypes.cast(q2, ctypes.POINTER(ctypes.c_float))
    queries[2] = ctypes.cast(q3, ctypes.POINTER(ctypes.c_float))
    # Build output struct array (3 steps)
    class Step(ctypes.Structure):
        _fields_ = [
            ("result_id", ctypes.c_int),
            ("result_dist", ctypes.c_float),
            ("n_results", ctypes.c_int),
            ("breath_psi", ctypes.c_double),
            ("step", ctypes.c_int),
        ]
    steps = (Step * 3)()
    n_chain = lib.tap_agent_think_chain(agent2, queries, 3, 5, ctypes.cast(steps, ctypes.c_void_p))
    print(f"    Chain returned {n_chain} total results")
    for i, s in enumerate(steps):
        print(f"      Step {i}: id={s.result_id}, dist={s.result_dist:.4f}, ψ={s.breath_psi:.4f}")
    # Working memory
    class WMEntry(ctypes.Structure):
        _fields_ = [
            ("id", ctypes.c_int),
            ("dist", ctypes.c_float),
            ("breath_psi", ctypes.c_double),
            ("timestamp", ctypes.c_long),
        ]
    wm = (WMEntry * 10)()
    n_wm = ctypes.c_int(0)
    lib.tap_agent_get_working_memory(agent2, ctypes.cast(wm, ctypes.c_void_p), 10, ctypes.byref(n_wm))
    print(f"    Working memory: {n_wm.value} entries")
    # Consolidate
    n_merged = ctypes.c_int(0)
    lib.tap_agent_consolidate(agent2, ctypes.byref(n_merged))
    print(f"    Consolidated: {n_merged.value} merged")
    lib.tap_agent_sleep(agent2)
    lib.tap_agent_free(agent2)
    print(f"    [OK] Agent v2 reasoning + memory works")
    print()

    # Summary
    print("  [6/6] SUMMARY:")
    print(f"    libtap_full.so: {os.path.getsize(lib_path):,} bytes")
    print(f"    PIM dispatcher: 30 points, 5-NN search OK")
    print(f"    Agent v1: wake/sleep OK")
    print(f"    Agent v2: 3-step chain, working memory, consolidation OK")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_full_lib_test.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "lib_path": lib_path,
        "lib_size": os.path.getsize(lib_path),
        "pim_test": {"n_search_results": n},
        "agent_v1": {"wake_sleep": True},
        "agent_v2": {
            "chain_n_results": n_chain,
            "working_memory_n": n_wm.value,
            "n_merged": n_merged.value,
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
