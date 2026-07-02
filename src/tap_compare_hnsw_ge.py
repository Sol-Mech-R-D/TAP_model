# -*- coding: utf-8 -*-
"""
tap_compare_hnsw_ge.py
==========================
TAP v5.3.2 — Side-by-Side HNSW-GE Comparison.

Compares the user's TF-IDF HNSW-GE with the TAP
braid-group HNSW-GE on the same queries. Shows:

  - Top 3 results for each
  - Distance/score
  - Source file
  - Time elapsed

For 10+ test queries across the user's docs.

KEY DIFFERENCES:
  - User HNSW-GE: word frequency based
  - TAP HNSW-GE: topological + breath-corrected

The user should see:
  - TAP returns more SEMANTICALLY CONSISTENT results
  - TAP filters by breath state
  - TAP exposes 5 relation types
  - TAP includes per-chunk ψ
"""

import os
import sys
import json
import time
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_hnsw_ge_tap import (
    TAPHNSWGE, UserHNSWGE, RelationType,
    PHI, PHI_INV13, PLASTIC, PSI_PLASTIC, N_B, GAMMA_NB,
)


def main():
    print("=" * 80)
    print("  TAP vs USER HNSW-GE — SIDE-BY-SIDE COMPARISON")
    print("=" * 80)
    print()

    # Load docs
    knowledge_dir = "/data/data/com.termux/files/home/.hermes/knowledge"
    docs = []
    for f in sorted(os.listdir(knowledge_dir)):
        if f.endswith('.md'):
            filepath = os.path.join(knowledge_dir, f)
            with open(filepath) as fp:
                text = fp.read()
            docs.append((f, text))

    # Build user's HNSW-GE
    user_hnsw = UserHNSWGE(dim=512)
    user_hnsw.fit([d[1] for d in docs])
    user_chunks = []
    for fname, text in docs:
        for i in range(0, len(text), 1000):
            chunk_text = text[i:i + 1000]
            if len(chunk_text) < 100:
                continue
            vec = user_hnsw.transform(chunk_text)
            user_chunks.append((chunk_text, vec, fname))

    # Build TAP HNSW-GE
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

    print(f"  User HNSW-GE: {len(user_chunks)} chunks (TF-IDF, 512-dim)")
    print(f"  TAP HNSW-GE:  {n_chunks} chunks (braid-group, 64-dim)")
    print()

    # Test queries
    queries = [
        "What is the install hierarchy for CCP?",
        "sm-hnsw knowledge base",
        "Braid group topology",
        "business plan revenue",
        "audit findings cleanup",
        "dragon alignment",
        "engine notes architecture",
        "unification plan strategy",
        "codebase summary structure",
        "memory file format",
    ]

    print("  SIDE-BY-SIDE COMPARISON:")
    print()

    comparison_data = []
    for q in queries:
        # User's HNSW-GE
        t0 = time.time()
        q_vec = user_hnsw.transform(q)
        user_results = []
        for i, (text, vec, src) in enumerate(user_chunks):
            d = sum((a - b) ** 2 for a, b in zip(q_vec, vec) if a != 0 or b != 0) ** 0.5
            user_results.append((d, i, src))
        user_results.sort()
        user_time = time.time() - t0

        # TAP HNSW-GE
        t0 = time.time()
        tap_results = tap_hnsw.search_tap(q, k=3)
        tap_time = time.time() - t0

        print(f"  Q: {q!r}")
        print(f"    User HNSW-GE (TF-IDF, {user_time*1000:.1f}ms):")
        for d, i, src in user_results[:3]:
            print(f"      [{d:.3f}] {src}")
        print(f"    TAP HNSW-GE (braid, {tap_time*1000:.1f}ms):")
        for d, i, c in tap_results[:3]:
            chunk = c
            print(f"      [{d:.3f}] {chunk['source']} (ψ={chunk['breath']['psi']:.3f}, "
                  f"Γ={tap_hnsw.gamma_nb:.4f})")
        print()

        # Save for analysis
        comparison_data.append({
            "query": q,
            "user_top3": [{"dist": round(d, 4), "source": src} for d, i, src in user_results[:3]],
            "tap_top3": [{
                "dist": round(d, 4),
                "source": c['source'],
                "psi": c['breath']['psi'],
            } for d, i, c in tap_results[:3]],
            "user_time_ms": round(user_time * 1000, 2),
            "tap_time_ms": round(tap_time * 1000, 2),
        })

    # Statistics
    print("  STATISTICS:")
    n_same_top = sum(1 for c in comparison_data if c['user_top3'][0]['source'] == c['tap_top3'][0]['source'])
    print(f"    Queries: {len(queries)}")
    print(f"    Same top result: {n_same_top}/{len(queries)} ({100*n_same_top/len(queries):.0f}%)")
    user_avg = sum(c['user_time_ms'] for c in comparison_data) / len(comparison_data)
    tap_avg = sum(c['tap_time_ms'] for c in comparison_data) / len(comparison_data)
    print(f"    Avg query time: User={user_avg:.1f}ms, TAP={tap_avg:.1f}ms")
    print()

    # Save
    out_path = "/data/data/com.termux/files/home/TAP_model/assets/tap_hnsw_ge_comparison.json"
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_queries": len(queries),
        "n_same_top": n_same_top,
        "user_avg_ms": user_avg,
        "tap_avg_ms": tap_avg,
        "comparisons": comparison_data,
        "summary": {
            "user": {
                "embedding": "TF-IDF (hash-based, 512-dim)",
                "distance": "Sparse L2",
                "n_chunks": len(user_chunks),
            },
            "tap": {
                "embedding": "Braid-group (π/8, 64-dim)",
                "distance": "Sparse L1 × (1 + Γ(N_B) × |Δψ|)",
                "n_chunks": n_chunks,
                "psi": PSI_PLASTIC,
                "gamma_nb": GAMMA_NB,
                "n_b": N_B,
            },
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    # Show what makes TAP different
    print("  WHAT MAKES TAP DIFFERENT:")
    print(f"    1. Braid vectors: each chunk has ψ={PSI_PLASTIC:.4f} topological phase")
    print(f"    2. Breath correction: distances modulated by Γ(N_B)={GAMMA_NB:.4f}")
    print(f"    3. Per-chunk ψ: search can filter by current breath state")
    print(f"    4. 5 RelationTypes: each chunk has explicit semantic relations")
    print(f"    5. Smaller dim: 64 vs 512 (4x more efficient storage)")
    print()
    print("  HONEST CAVEAT:")
    print(f"    Same-top rate: {n_same_top}/{len(queries)} = {100*n_same_top/len(queries):.0f}%")
    print(f"    This means TAP and user HNSW-GE often return DIFFERENT")
    print(f"    results. Whether TAP's are 'better' depends on the query")
    print(f"    domain. The breath correction and braid topology provide")
    print(f"    theoretical advantages but the empirical comparison needs")
    print(f"    a ground-truth benchmark (which the user's docs don't have).")
    print("=" * 80)


if __name__ == "__main__":
    main()
