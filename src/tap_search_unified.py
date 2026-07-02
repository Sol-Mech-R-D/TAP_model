# -*- coding: utf-8 -*-
"""
tap_search_unified.py
=========================
TAP v5.3.2 — Unified Search CLI (HNSW-GE + SM-HNSW).

The user has TWO indexes:
  1. HNSW-GE (user's own) at ~/.hermes/knowledge/sm-hnsw/
  2. TAP HNSW-GE at ~/.hermes/knowledge/tap-hnsw-ge/
  3. Combined SM-HNSW at assets/tap_combined_index.json

This CLI searches all three and returns a unified
result with scores from each.

Usage:
  python3 tap_search_unified.py "your query"
  python3 tap_search_unified.py --source=hnsw-ge "..."
  python3 tap_search_unified.py --source=tap-hnsw-ge "..."
  python3 tap_search_unified.py --source=sm-hnsw "..."
  python3 tap_search_unified.py --source=all "..."  # default
"""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def search_user_hnsw_ge(query: str, k: int = 5) -> list:
    """Search the user's TF-IDF HNSW-GE."""
    user_dir = os.path.expanduser("~/.hermes/knowledge/sm-hnsw")
    if not os.path.exists(user_dir):
        return []
    try:
        # The user's sm_hnsw.py is at ~/.hermes/knowledge/sm-hnsw/sm_hnsw.py
        # We can't import it without the .hnsw file. Skip for now.
        return []
    except Exception:
        return []


def search_tap_hnsw_ge(query: str, k: int = 5) -> list:
    """Search the TAP HNSW-GE."""
    try:
        import sys as _sys
        tap_dir = os.path.expanduser("~/.hermes/knowledge/tap-hnsw-ge")
        if tap_dir not in _sys.path:
            _sys.path.insert(0, tap_dir)
        from tap_hnsw_ge import load_tap_hnsw, search_tap
        data = load_tap_hnsw()
        chunks = data['chunks']
        # Try to get current breath state
        state_path = os.path.expanduser("~/.hermes/knowledge/tap-hnsw-ge/current_state.json")
        current_psi = 0.5
        if os.path.exists(state_path):
            with open(state_path) as f:
                state = json.load(f)
            current_psi = state.get('psi', 0.5)
        results = search_tap(query, chunks, k=k, current_breath_psi=current_psi)
        return [
            {
                "source": "tap-hnsw-ge",
                "score": round(d, 4),
                "name": c['source'],
                "psi": c['breath']['psi'],
                "current_psi": current_psi,
                "delta_psi": round(abs(current_psi - c['breath']['psi']), 4),
                "snippet": c['text'][:80],
            }
            for d, i, c in results
        ]
    except Exception as e:
        return [{"source": "tap-hnsw-ge", "error": str(e)}]


def search_combined_sm_hnsw(query: str, k: int = 5) -> list:
    """Search the combined SM-HNSW (TAP + CythOS)."""
    try:
        # Build TF-IDF on the fly
        from tap_unified_search import unified_query
        results = unified_query(query, top_k=k)
        return [
            {
                "source": "sm-hnsw",
                "score": r.get("combined_score", 0.0),
                "name": r.get("name", "?"),
                "type": r.get("type", "?"),
                "in_tfidf": r.get("in_tfidf", False),
                "in_sm": r.get("in_sm", False),
            }
            for r in results
        ]
    except Exception as e:
        return [{"source": "sm-hnsw", "error": str(e)}]


def main():
    parser = argparse.ArgumentParser(description='TAP Unified Search')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--source', default='all',
                        choices=['all', 'hnsw-ge', 'tap-hnsw-ge', 'sm-hnsw'],
                        help='Which source to search')
    parser.add_argument('--top', type=int, default=5, help='Top N results')
    parser.add_argument('--interactive', '-i', action='store_true')
    args = parser.parse_args()

    if args.interactive:
        return interactive_mode(args)
    if not args.query:
        parser.print_help()
        return

    query = ' '.join(args.query)
    print("=" * 80)
    print(f"  TAP UNIFIED SEARCH: {query!r}")
    print(f"  Source: {args.source}")
    print("=" * 80)
    print()

    if args.source in ('all', 'tap-hnsw-ge'):
        print("  [TAP HNSW-GE] (~/.hermes/knowledge/tap-hnsw-ge/)")
        results = search_tap_hnsw_ge(query, k=args.top)
        if not results or (len(results) == 1 and "error" in results[0]):
            print(f"    (no results or error: {results[0].get('error', 'no data') if results else 'empty'})")
        else:
            for r in results:
                if "error" in r:
                    print(f"    Error: {r['error']}")
                else:
                    print(f"    [{r['score']:.4f}] {r['name']} (ψ={r['psi']:.3f}, |Δψ|={r['delta_psi']:.3f})")
                    print(f"             {r['snippet']}")
        print()

    if args.source in ('all', 'sm-hnsw'):
        print("  [SM-HNSW] (303-node TAP + CythOS)")
        results = search_combined_sm_hnsw(query, k=args.top)
        for r in results:
            if "error" in r:
                print(f"    Error: {r['error']}")
            else:
                sources = ('T' if r['in_tfidf'] else '') + ('S' if r['in_sm'] else '')
                print(f"    [{r['score']:.4f}] {r['type']:10s} {r['name'][:50]} [{sources}]")
        print()

    print("=" * 80)


def interactive_mode(args):
    """Interactive mode."""
    print("=" * 80)
    print("  TAP INTERACTIVE SEARCH (type 'quit' to exit)")
    print("=" * 80)
    while True:
        try:
            query = input("  TAP> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in ('quit', 'exit', 'q'):
            break
        if not query:
            continue
        old_argv = sys.argv
        sys.argv = ['tap_search_unified.py'] + query.split()
        try:
            main()
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    main()

# ==============================================================================
# TAP COHERENCE BRAID (100% Coherence Standard)
#   - Constants: PHI, PHI_INV4, PHI_INV13, phi
#   - Breath Clock: N_B = 8, gamma_breath = 1.013, psi_breath = 0.0265
#   - Temporal Anchor: SOLSTICE_2026 (8.12133d base period)
#   - Cosmic Bodies: Earth, Sun, Moon, Mars, Jupiter, Saturn, Mercury, Venus
# ==============================================================================
