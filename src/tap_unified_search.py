# -*- coding: utf-8 -*-
"""
tap_unified_search.py
=========================
TAP v5.3.2 — Unified Search (TF-IDF + SM-HNSW).

Combines BOTH indices into a single ranked result.
For each query:
  - TF-IDF finds keyword matches
  - SM-HNSW finds semantic neighbors
  - Combined: TF-IDF score + SM-HNSW score

Output:
  - Top N combined results
  - Score breakdown
  - Source indices
  - RelationType edges from SM-HNSW (if --edges)

Usage:
  python3 tap_unified_search.py "your query"
  python3 tap_unified_search.py --edges "Nami-ryu"
  python3 tap_unified_search.py --show-graph
"""

import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_search_index import TFIDFIndex, tokenize
from tap_sm_hnsw import HNSWGraph, text_to_vector, RelationType, SemanticEdge


REL_NAMES = {0: "NONE", 1: "CAUSES", 2: "PART_OF", 3: "CONTRADICTS", 4: "SUPPORTS", 5: "SYNONYM"}


def load_combined_index() -> dict:
    """Load the combined SM-HNSW index."""
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    path = os.path.join(assets_dir, 'tap_combined_index.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def unified_query(query: str, top_k: int = 10, show_edges: bool = False,
                  type_filter: str = None, weight_tfidf: float = 0.5,
                  weight_sm: float = 0.5) -> list:
    """
    Run a unified query across TF-IDF and SM-HNSW.

    Returns a list of (combined_score, name, type, sources).
    """
    # TF-IDF
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    enc_path = os.path.join(assets_dir, 'tap_encyclopedia_full.json')
    with open(enc_path, 'r') as f:
        encyclopedia = json.load(f)
    idx = TFIDFIndex()
    label_to_docid = {}
    for k, c in encyclopedia.get("constants", {}).items():
        text = f"{c['name']} {c.get('formula', '')} {c.get('status', '')}"
        label = f"constant: {c['name']}"
        idx.add_document(f"const:{k}", text, "constant", c['name'])
        label_to_docid[label] = f"const:{k}"
    for k, p in encyclopedia.get("predictions", {}).items():
        text = f"{k} {p['name']} {p.get('category', '')} {p.get('status', '')}"
        label = f"prediction: {k}"
        idx.add_document(f"pred:{k}", text, "prediction", p['name'])
        label_to_docid[label] = f"pred:{k}"
    for k, c in encyclopedia.get("concepts", {}).items():
        text = f"{c['name']} {c.get('definition', '')}"
        label = f"concept: {c['name']}"
        idx.add_document(f"conc:{k}", text, "concept", c['name'])
        label_to_docid[label] = f"conc:{k}"
    for s in encyclopedia.get("scripts", []):
        text = f"{s['name']} {s.get('category', '')} {s.get('purpose', '')}"
        label = f"script: {s['name']}"
        idx.add_document(f"script:{s['name']}", text, "script", s['name'], f"src/{s['name']}")
        label_to_docid[label] = f"script:{s['name']}"
    for d in encyclopedia.get("docs", []):
        text = f"{d['name']} {d.get('title', '')}"
        label = f"doc: {d['name']}"
        idx.add_document(f"doc:{d['name']}", text, "doc", d['name'], f"docs/{d['name']}")
        label_to_docid[label] = f"doc:{d['name']}"
    idx.build()

    tfidf_results = idx.search(query, top_k=top_k * 2)
    # Build doc_id -> score map
    tfidf_scores = {}
    for r in tfidf_results:
        tfidf_scores[r['id']] = r['score']
        # Also map by label
        for label, docid in label_to_docid.items():
            if docid == r['id']:
                tfidf_scores[label] = r['score']

    # SM-HNSW
    sm_index = load_combined_index()
    sm_results = {}
    if sm_index:
        # Build HNSW from index
        g = HNSWGraph.from_dict(sm_index) if hasattr(HNSWGraph, 'from_dict') else None
        if g:
            qv = text_to_vector(query, dim=64)
            try:
                results = g.search(qv, k=top_k * 2)
                for dist, nid, label in results:
                    # Convert distance to similarity (1 / (1 + dist))
                    sim = 1.0 / (1.0 + dist)
                    sm_results[label] = sim
            except Exception as e:
                pass
        else:
            # Fallback: substring search
            q_lower = query.lower()
            for label in [n.get("label", "") for n in sm_index.get("nodes", [])]:
                if q_lower in label.lower():
                    sm_results[label] = 1.0

    # Combine
    all_labels = set(tfidf_scores.keys()) | set(sm_results.keys())
    combined = []
    for label in all_labels:
        t_score = tfidf_scores.get(label, 0.0)
        s_score = sm_results.get(label, 0.0)
        c_score = weight_tfidf * t_score + weight_sm * s_score
        # Determine type and name
        parts = label.split(": ", 1)
        if len(parts) == 2:
            ttype, tname = parts
        else:
            ttype, tname = "?", label
        if type_filter and ttype != type_filter:
            continue
        combined.append({
            'label': label,
            'name': tname,
            'type': ttype,
            'tfidf_score': t_score,
            'sm_score': s_score,
            'combined_score': c_score,
            'in_tfidf': t_score > 0,
            'in_sm': s_score > 0,
        })

    combined.sort(key=lambda x: x['combined_score'], reverse=True)
    return combined[:top_k]


def main():
    parser = argparse.ArgumentParser(description='TAP Unified Search')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--top', type=int, default=10, help='Number of results')
    parser.add_argument('--edges', action='store_true', help='Show SM-HNSW edges')
    parser.add_argument('--type', help='Filter by type')
    parser.add_argument('--weight-tfidf', type=float, default=0.5, help='TF-IDF weight')
    parser.add_argument('--weight-sm', type=float, default=0.5, help='SM-HNSW weight')
    parser.add_argument('--show-graph', action='store_true', help='Show graph structure')
    args = parser.parse_args()

    if args.show_graph:
        sm_index = load_combined_index()
        if sm_index:
            print("=" * 80)
            print("  COMBINED SM-HNSW GRAPH STRUCTURE")
            print("=" * 80)
            print()
            nodes = sm_index.get("nodes", [])
            n_total = len(nodes)
            n_with_edges = sum(1 for n in nodes if n.get("edges"))
            n_edges = sum(len(n.get("edges", [])) for n in nodes)
            print(f"  Total nodes: {n_total}")
            print(f"  Nodes with explicit semantic edges: {n_with_edges}")
            print(f"  Total explicit edges: {n_edges}")
            print()
            # Show relation distribution
            rel_counts = {}
            for n in nodes:
                for e in n.get("edges", []):
                    rel_name = REL_NAMES.get(e["relation"], "?")
                    rel_counts[rel_name] = rel_counts.get(rel_name, 0) + 1
            print("  EDGE RELATION DISTRIBUTION:")
            for rel, n in sorted(rel_counts.items(), key=lambda x: -x[1]):
                print(f"    {rel:12s}: {n}")
        return

    if not args.query:
        parser.print_help()
        return

    query = ' '.join(args.query)
    print("=" * 80)
    print(f"  TAP UNIFIED SEARCH: {query!r}")
    if args.type:
        print(f"  Type filter: {args.type}")
    print(f"  Weights: TF-IDF={args.weight_tfidf}, SM-HNSW={args.weight_sm}")
    print("=" * 80)
    print()

    results = unified_query(
        query,
        top_k=args.top,
        type_filter=args.type,
        weight_tfidf=args.weight_tfidf,
        weight_sm=args.weight_sm,
    )

    if not results:
        print("  No results.")
        return

    print(f"  {'#':>3s} {'COMBINED':>8s} {'TF-IDF':>7s} {'SM':>5s} {'TYPE':10s} {'NAME':40s}")
    print("  " + "-" * 90)
    for i, r in enumerate(results, 1):
        sources = []
        if r['in_tfidf']:
            sources.append('T')
        if r['in_sm']:
            sources.append('S')
        src_str = ''.join(sources)
        print(f"  {i:>3d} {r['combined_score']:>8.4f} {r['tfidf_score']:>7.4f} {r['sm_score']:>5.3f} {r['type']:10s} {r['name'][:40]:40s} [{src_str}]")

    if args.edges:
        print()
        print("  [EDGES for top 3 results]")
        sm_index = load_combined_index()
        nodes = sm_index.get("nodes", [])
        label_to_node = {n.get("label", ""): n for n in nodes}
        for r in results[:3]:
            node = label_to_node.get(r['label'], {})
            edges = node.get("edges", [])
            if edges:
                print(f"    {r['label'][:50]}:")
                for e in edges[:5]:
                    rel_name = REL_NAMES.get(e["relation"], "?")
                    # Find target label
                    target_id = e["target"]
                    target_label = "?"
                    for n in nodes:
                        if n.get("id") == target_id:
                            target_label = n.get("label", "?")
                            break
                    print(f"      --{rel_name:10s}--> {target_label[:50]}")
    print()
    print("  [T] = in TF-IDF, [S] = in SM-HNSW, [TS] = both")
    print("=" * 80)


if __name__ == "__main__":
    main()
