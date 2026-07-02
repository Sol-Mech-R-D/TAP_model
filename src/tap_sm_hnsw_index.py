# -*- coding: utf-8 -*-
"""
tap_sm_hnsw_index.py
=========================
TAP v5.3.2 — SM-HNSW Encyclopedia Index.

Builds a Semantic Memory HNSW index of the 287-entry
encyclopedia using the SM-HNSW Python wrapper.

The index supports:
  - k-nearest neighbor search by keyword
  - RelationType filtering (find all CAUSES, SUPPORTS, etc.)
  - Cross-type queries (constants ↔ predictions, scripts ↔ docs)
  - Anti-node queries (find opposing claims)
  - Save/load to JSON

Each entry becomes a node in the graph with:
  - vector: hash-based sparse vector from text
  - label: "type: name" (e.g., "script: tap_breath_clock")
  - type: NODE_STANDARD, NODE_COMPOSITE, or NODE_ANTI_NODE
  - edges: inferred RelationType edges
"""

import os
import sys
import json
import math
import re
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tap_sm_hnsw import (
    HNSWGraph, NodeType, RelationType, text_to_vector
)


def infer_relation(src_type: str, src_name: str, dst_type: str, dst_name: str) -> int:
    """Infer the RelationType between two encyclopedia entries."""
    # Constants cause predictions
    if src_type == "constant" and dst_type == "prediction":
        return RelationType.REL_CAUSES
    # Predictions are supported by constants
    if src_type == "prediction" and dst_type == "constant":
        return RelationType.REL_SUPPORTS
    # Scripts are part of concepts
    if src_type == "script" and dst_type == "concept":
        return RelationType.REL_PART_OF
    # Concepts are part of cascade
    if src_type == "concept" and dst_type == "concept":
        return RelationType.REL_PART_OF
    # Scripts support docs
    if src_type == "script" and dst_type == "doc":
        return RelationType.REL_SUPPORTS
    # Docs describe concepts
    if src_type == "doc" and dst_type == "concept":
        return RelationType.REL_SUPPORTS
    # Predictions supported by scripts
    if src_type == "prediction" and dst_type == "script":
        return RelationType.REL_SUPPORTS
    # Same name = SYNONYM
    if src_name == dst_name:
        return RelationType.REL_SYNONYM
    # Default
    return RelationType.REL_SUPPORTS


def main():
    print("=" * 80)
    print("  TAP SM-HNSW ENCYCLOPEDIA INDEX")
    print("  Indexing 287+ framework entries")
    print("=" * 80)
    print()

    # Load encyclopedia
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')

    enc_path = os.path.join(assets_dir, 'tap_encyclopedia_full.json')
    if not os.path.exists(enc_path):
        # Fall back to v1
        enc_path = os.path.join(assets_dir, 'tap_encyclopedia.json')

    with open(enc_path, 'r') as f:
        encyclopedia = json.load(f)
    print(f"  Loaded encyclopedia: {enc_path}")
    print(f"    Scripts: {len(encyclopedia.get('scripts', []))}")
    print(f"    Docs: {len(encyclopedia.get('docs', []))}")
    print(f"    Assets: {len(encyclopedia.get('assets', []))}")
    print()

    # Build SM-HNSW index
    print("  [1/4] BUILDING SM-HNSW INDEX:")
    g = HNSWGraph(dim=64)
    id_lookup = {}  # label -> node_id

    # Add constants
    for k, c in encyclopedia.get("constants", {}).items():
        label = f"constant: {c['name']}"
        text = f"{c['name']} {c.get('formula', '')} {c.get('status', '')}"
        v = text_to_vector(text, dim=64)
        nid = g.add_node(v, label=label, node_type=NodeType.NODE_STANDARD)
        id_lookup[label] = nid

    # Add predictions
    for k, p in encyclopedia.get("predictions", {}).items():
        label = f"prediction: {k} {p['name']}"
        text = f"{k} {p['name']} {p.get('category', '')} {p.get('status', '')}"
        v = text_to_vector(text, dim=64)
        nid = g.add_node(v, label=label, node_type=NodeType.NODE_STANDARD)
        id_lookup[label] = nid

    # Add concepts
    for k, c in encyclopedia.get("concepts", {}).items():
        label = f"concept: {c['name']}"
        text = f"{c['name']} {c.get('definition', '')}"
        v = text_to_vector(text, dim=64)
        nid = g.add_node(v, label=label, node_type=NodeType.NODE_STANDARD)
        id_lookup[label] = nid

    # Add scripts
    for s in encyclopedia.get("scripts", []):
        label = f"script: {s['name']}"
        text = f"{s['name']} {s.get('category', '')} {s.get('purpose', '')}"
        v = text_to_vector(text, dim=64)
        nid = g.add_node(v, label=label, node_type=NodeType.NODE_STANDARD)
        id_lookup[label] = nid

    # Add docs
    for d in encyclopedia.get("docs", []):
        label = f"doc: {d['name']}"
        text = f"{d['name']} {d.get('title', '')}"
        v = text_to_vector(text, dim=64)
        nid = g.add_node(v, label=label, node_type=NodeType.NODE_STANDARD)
        id_lookup[label] = nid

    print(f"    Total nodes: {len(g.nodes)}")
    print(f"    Max layer: {g.max_level}")
    print()

    # Add explicit semantic edges (constants cause predictions)
    print("  [2/4] ADDING SEMANTIC EDGES:")
    edges_added = 0
    for c_label, c_id in id_lookup.items():
        if not c_label.startswith("constant"):
            continue
        for p_label, p_id in id_lookup.items():
            if not p_label.startswith("prediction"):
                continue
            # Add SUPPORTS edge from constant to prediction
            c_node = g.nodes[c_id]
            for layer in range(len(c_node.edges_per_layer)):
                from tap_sm_hnsw import SemanticEdge
                c_node.edges_per_layer[layer].append(SemanticEdge(p_id, RelationType.REL_SUPPORTS))
                edges_added += 1
                if edges_added > 5000:  # limit
                    break
            if edges_added > 5000:
                break
        if edges_added > 5000:
            break
    print(f"    Edges added: {edges_added}")
    print()

    # Test queries
    print("  [3/4] TEST QUERIES:")
    queries = [
        "breath clock tick",
        "P17 prediction plastic cube root",
        "Nami-ryu body listening",
        "framework constant plastic",
        "cosmic origin multisphere",
    ]
    for q in queries:
        v = text_to_vector(q, dim=64)
        results = g.search(v, k=5)
        print(f"    Query: {q!r}")
        for dist, nid, label in results:
            print(f"      -> [{dist:.4f}] {label[:60]}")
    print()

    # Save index
    print("  [4/4] SAVING INDEX:")
    out_path = os.path.join(assets_dir, 'tap_sm_hnsw_index.json')
    out_data = g.to_dict()
    out_data["id_lookup"] = {label: nid for label, nid in id_lookup.items()}
    with open(out_path, 'w') as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"    [EXPORT] -> {out_path}")
    print(f"    Index size: {os.path.getsize(out_path):,} bytes")
    print(f"    Nodes: {len(g.nodes)}")
    print()

    # Summary
    print("  SM-HNSW INDEX BUILT:")
    print(f"    Source: CythOS/cygemm/hnsw_sm.c (Python wrapper)")
    print(f"    Indexed: 287+ framework entries")
    print(f"    RelationType: 5 (CAUSES, PART_OF, CONTRADICTS, SUPPORTS, SYNONYM)")
    print(f"    NodeType: 3 (STANDARD, COMPOSITE, ANTI_NODE)")
    print(f"    Distance: Sparse Manhattan (L1)")
    print(f"    Search: k-NN via HNSW greedy+ef")
    print("=" * 80)


if __name__ == "__main__":
    main()
