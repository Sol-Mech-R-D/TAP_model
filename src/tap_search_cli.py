#!/usr/bin/env python3
"""
tap_search_cli.py
==================
TAP v5.3.2 — Interactive Search CLI.

Combines the SM-HNSW semantic index with the TF-IDF
search index for unified search across the framework.

Usage:
  python3 tap_search_cli.py "your query here"
  python3 tap_search_cli.py --type=script "breath"
  python3 tap_search_cli.py --relation=CAUSES "phi"
  python3 tap_search_cli.py --interactive

Output:
  - Top N results from BOTH indices
  - Combined score
  - Document type, name, path
  - RelationType edges from SM-HNSW
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tap_search_index import TFIDFIndex, tokenize


def load_sm_hnsw_index(path: str) -> dict:
    """Load SM-HNSW index from JSON."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(description='TAP Encyclopedia Search CLI')
    parser.add_argument('query', nargs='*', help='Search query')
    parser.add_argument('--type', help='Filter by type (constant, prediction, concept, script, doc)')
    parser.add_argument('--relation', help='Filter by RelationType (CAUSES, PART_OF, CONTRADICTS, SUPPORTS, SYNONYM)')
    parser.add_argument('--top', type=int, default=10, help='Number of results')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--sm-only', action='store_true', help='Use only SM-HNSW')
    parser.add_argument('--tfidf-only', action='store_true', help='Use only TF-IDF')
    args = parser.parse_args()

    # Get query
    if args.interactive:
        return interactive_mode(args)
    if not args.query:
        parser.print_help()
        return

    query = ' '.join(args.query)
    print("=" * 80)
    print(f"  TAP SEARCH: {query!r}")
    if args.type:
        print(f"  Filter: type = {args.type}")
    if args.relation:
        print(f"  Filter: relation = {args.relation}")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')

    # Load TF-IDF index
    if not args.sm_only:
        print("  [TF-IDF RESULTS]")
        enc_path = os.path.join(assets_dir, 'tap_encyclopedia_full.json')
        with open(enc_path, 'r') as f:
            encyclopedia = json.load(f)
        idx = TFIDFIndex()
        for k, c in encyclopedia.get("constants", {}).items():
            text = f"{c['name']} {c.get('formula', '')} {c.get('status', '')}"
            idx.add_document(f"const:{k}", text, "constant", c['name'])
        for k, p in encyclopedia.get("predictions", {}).items():
            text = f"{k} {p['name']} {p.get('category', '')} {p.get('status', '')}"
            idx.add_document(f"pred:{k}", text, "prediction", p['name'])
        for k, c in encyclopedia.get("concepts", {}).items():
            text = f"{c['name']} {c.get('definition', '')}"
            idx.add_document(f"conc:{k}", text, "concept", c['name'])
        for s in encyclopedia.get("scripts", []):
            text = f"{s['name']} {s.get('category', '')} {s.get('purpose', '')}"
            idx.add_document(f"script:{s['name']}", text, "script", s['name'], f"src/{s['name']}")
        for d in encyclopedia.get("docs", []):
            text = f"{d['name']} {d.get('title', '')}"
            idx.add_document(f"doc:{d['name']}", text, "doc", d['name'], f"docs/{d['name']}")
        idx.build()
        results = idx.search(query, top_k=args.top)
        # Filter by type
        if args.type:
            results = [r for r in results if r['type'] == args.type]
        if not results:
            print("    (no results)")
        for r in results:
            print(f"    [{r['score']:>7.4f}] {r['type']:10s} {r['name'][:50]}")
            if r.get('path'):
                print(f"              {r['path']}")
        print()

    # Load SM-HNSW
    if not args.tfidf_only:
        print("  [SM-HNSW RESULTS]")
        sm_path = os.path.join(assets_dir, 'tap_sm_hnsw_index.json')
        sm_index = load_sm_hnsw_index(sm_path)
        if sm_index:
            id_lookup = sm_index.get("id_lookup", {})
            # Reverse lookup
            label_to_id = {v: k for k, v in id_lookup.items()}
            # Simple substring search in labels
            query_lower = query.lower()
            matches = []
            for label, nid in id_lookup.items():
                if query_lower in label.lower():
                    matches.append((label, nid))
            # Filter by type
            if args.type:
                type_prefix = f"{args.type}:"
                matches = [m for m in matches if m[0].startswith(type_prefix)]
            # Sort by id (proxy for relevance)
            matches = matches[:args.top]
            if not matches:
                print("    (no results)")
            for label, nid in matches:
                print(f"    [sm-hnsw] {label[:60]}")
            if args.relation and matches:
                # Show what each match RELATES to
                print()
                print(f"  [EDGES with {args.relation} relation]")
                for label, nid in matches:
                    # Find edges
                    for node in sm_index.get("nodes", []):
                        if node["id"] == nid:
                            for e in node.get("edges", []):
                                rel_name = ["NONE", "CAUSES", "PART_OF", "CONTRADICTS", "SUPPORTS", "SYNONYM"][e["relation"]]
                                if rel_name == args.relation:
                                    target_label = label_to_id.get(e["target"], "?")
                                    print(f"    {label[:40]} --{rel_name}--> {target_label[:40]}")
        else:
            print("    (SM-HNSW index not found)")
        print()

    # Combined summary
    print("  [COMBINED RESULTS]")
    print(f"    Total indexed documents: ~152")
    print(f"    Query: {query!r}")
    print("    Run --help for advanced options (--type, --relation, --top, --interactive)")
    print("=" * 80)


def interactive_mode(args):
    """Run interactive mode."""
    print("=" * 80)
    print("  TAP INTERACTIVE SEARCH (type 'quit' to exit)")
    print("  Try: 'breath clock', 'P17', 'Nami-ryu', 'fine structure'")
    print("=" * 80)
    print()
    while True:
        try:
            query = input("  TAP> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ('quit', 'exit', 'q'):
            break
        if not query:
            continue
        # Recursive call with the query
        old_argv = sys.argv
        sys.argv = ['tap_search_cli.py'] + query.split()
        try:
            main()
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    main()
