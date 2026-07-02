# -*- coding: utf-8 -*-
"""
tap_cythos_tap_edges.py
==============================
TAP v5.3.2 — Semantic Edges: CythOS ↔ TAP.

Adds explicit semantic edges between the CythOS
codebase and the TAP framework. The SM-HNSW
RelationType values map to:

  CAUSES:      "X is required to make Y work"
  PART_OF:     "X is a component of Y"
  CONTRADICTS: "X contradicts Y"
  SUPPORTS:    "X supports / implements Y"
  SYNONYM:     "X is functionally equivalent to Y"

CythOS-TAP mapping examples:
  hnsw_sm.c  SUPPORTS  tap_sm_hnsw.py  (semantic memory impl)
  hnsw_sm.c  PART_OF   CyGemm          (CythOS subsystem)
  tap_sm_hnsw.py  SUPPORTS  tap_search_index.py  (Python wrapper)
  CyGemm  PART_OF   CythOS
  cygemm_hnsw.c  CAUSES  hnsw_sm.c  (HNSW depends on cygemm)

The edges are stored in the combined SM-HNSW index
and queryable via the CLI.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_sm_hnsw import HNSWGraph, SemanticEdge, RelationType, text_to_vector

# RelationType names
REL_NAMES = {0: "NONE", 1: "CAUSES", 2: "PART_OF", 3: "CONTRADICTS", 4: "SUPPORTS", 5: "SYNONYM"}
REL_DESC = {
    "CAUSES": "X is required to make Y work",
    "PART_OF": "X is a component of Y",
    "CONTRADICTS": "X contradicts Y",
    "SUPPORTS": "X supports / implements Y",
    "SYNONYM": "X is functionally equivalent to Y",
}


# Hand-curated edges between CythOS and TAP entries
EDGES = [
    # (cythos_path, tap_target, relation_name)
    # Core HNSW support
    ("hnsw_sm.c", "tap_sm_hnsw.py", "SUPPORTS"),
    ("hnsw_sm.c", "CyGemm", "PART_OF"),
    ("hnsw_sm.h", "tap_sm_hnsw.py", "SUPPORTS"),
    ("cygemm_hnsw.c", "hnsw_sm.c", "CAUSES"),
    ("cygemm_hnsw.c", "CyGemm", "PART_OF"),

    # CythOS to framework
    ("CyGemm", "TAP_cascade", "SUPPORTS"),
    ("CCP", "TAP_cascade", "SUPPORTS"),
    ("Six_Dragons", "TAP_cascade", "SUPPORTS"),
    ("HARDE", "TAP_cascade", "SUPPORTS"),
    ("Makie", "TAP_cascade", "SUPPORTS"),

    # Python wrappers
    ("tap_sm_hnsw.py", "tap_search_index.py", "SUPPORTS"),
    ("tap_sm_hnsw.py", "tap_sm_hnsw_index.py", "SUPPORTS"),
    ("tap_sm_hnsw.py", "tap_cythos_index.py", "SUPPORTS"),
    ("tap_search_cli.py", "tap_search_index.py", "PART_OF"),
    ("tap_search_cli.py", "tap_sm_hnsw.py", "PART_OF"),

    # CythOS subsystems
    ("cascade.c", "CythOS", "PART_OF"),
    ("cascade.c", "TAP_cascade", "SUPPORTS"),
    ("runtime.c", "CythOS", "PART_OF"),
    ("kernel.c", "CythOS", "PART_OF"),
    ("memory.c", "CythOS", "PART_OF"),
    ("dispatcher.c", "CythOS", "PART_OF"),
    ("gemm_engine.c", "CythOS", "PART_OF"),
    ("agent.c", "CythOS", "PART_OF"),
    ("routing.c", "CythOS", "PART_OF"),
    ("backprop.c", "CythOS", "PART_OF"),
    ("bfloat16.c", "CythOS", "PART_OF"),

    # Test files
    ("test_cascade.c", "TAP_cascade", "SUPPORTS"),
    ("test_hnsw.c", "hnsw_sm.c", "SUPPORTS"),

    # Verifications (semantic)
    ("hnsw_sm.c", "tap_5year_seismic_sweep.py", "SUPPORTS"),  # HNSW supports
    ("tap_encyclopedia.py", "tap_encyclopedia_v2.py", "CAUSES"),  # v1 caused v2
    ("calibration_derivation.py", "tap_p1p18_re_evaluation.py", "CAUSES"),

    # Conceptual synonomies
    ("Nami_Ryu", "twin_dragons", "SYNONYM"),
    ("Six_Dragons", "twin_dragons", "SYNONYM"),
]


def main():
    print("=" * 80)
    print("  TAP CYTHOS-TAP SEMANTIC EDGES")
    print("  Linking CythOS code to TAP framework")
    print("=" * 80)
    print()

    # Load combined index
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')
    combined_path = os.path.join(assets_dir, 'tap_combined_index.json')

    if not os.path.exists(combined_path):
        print(f"  Combined index not found: {combined_path}")
        print(f"  Run tap_cythos_index.py first")
        return

    with open(combined_path, 'r') as f:
        combined = json.load(f)

    # Build id_lookup by scanning nodes
    id_lookup = {}
    for node in combined.get("nodes", []):
        label = node.get("label", "")
        nid = node.get("id", -1)
        if label and nid >= 0:
            id_lookup[label] = nid

    print(f"  [1/3] LOAD COMBINED INDEX:")
    print(f"    Nodes in index: {len(combined.get('nodes', []))}")
    print(f"    id_lookup size: {len(id_lookup)}")
    print()

    # Add the edges
    print("  [2/3] ADD SEMANTIC EDGES:")
    edges_added = 0
    edges_skipped = 0
    for cythos_path, tap_target, rel_name in EDGES:
        # Try to find both endpoints
        # CythOS path could match several variants
        cythos_candidates = [
            f"cythos: cygemm/{cythos_path}",
            f"cythos: Rebrand/CyGemm/bridge/{cythos_path}",
            f"cythos: Rebrand/CyGemm/{cythos_path}",
            f"cythos: {cythos_path}",
        ]
        cythos_label = None
        for cand in cythos_candidates:
            if cand in id_lookup:
                cythos_label = cand
                break
        if cythos_label is None:
            # Search labels containing the cythos_path
            for lbl in id_lookup.keys():
                if cythos_path.lower() in lbl.lower():
                    cythos_label = lbl
                    break
        # TAP target could match several variants
        tap_candidates = [
            f"script: {tap_target}.py",
            f"doc: {tap_target}.md",
            f"concept: {tap_target}",
            f"constant: {tap_target}",
            f"prediction: {tap_target}",
            f"script: {tap_target}",
        ]
        # Also try searching for partial matches
        tap_label = None
        for cand in tap_candidates:
            if cand in id_lookup:
                tap_label = cand
                break
        if tap_label is None:
            # Search labels containing the target name
            for lbl in id_lookup.keys():
                if tap_target.lower() in lbl.lower():
                    tap_label = lbl
                    break

        if cythos_label is None or tap_label is None:
            edges_skipped += 1
            continue

        # Build reverse lookup for relation names
        rel_id_map = {name: rid for rid, name in RelationType.NAMES.items()}
        rel_id = rel_id_map.get(rel_name, RelationType.REL_SUPPORTS)

        # Add edge to the index
        cythos_id = id_lookup[cythos_label]
        # Find the node and add an edge
        for node in combined.get("nodes", []):
            if node.get("id") == cythos_id:
                if "edges" not in node:
                    node["edges"] = []
                # Avoid duplicate
                already = any(e["target"] == id_lookup[tap_label] for e in node["edges"])
                if not already:
                    node["edges"].append({
                        "target": id_lookup[tap_label],
                        "relation": rel_id,
                    })
                    edges_added += 1
                break
    print(f"    Edges added: {edges_added}")
    print(f"    Edges skipped (missing endpoints): {edges_skipped}")
    print()

    # Save the index with edges
    print("  [3/3] SAVE COMBINED INDEX WITH EDGES:")
    combined["n_edges_added"] = edges_added
    combined["edges_metadata"] = {
        "n_total": len(EDGES),
        "n_added": edges_added,
        "n_skipped": edges_skipped,
        "relation_types": list(set(e[2] for e in EDGES)),
    }
    with open(combined_path, 'w') as f:
        json.dump(combined, f, indent=2, default=str)
    print(f"    [EXPORT] -> {combined_path}")
    print(f"    Index size: {os.path.getsize(combined_path):,} bytes")
    print()

    # Print edge summary
    print("  SEMANTIC EDGES SUMMARY:")
    print(f"    Total edges defined: {len(EDGES)}")
    print(f"    Edges added to graph: {edges_added}")
    print()
    rel_counts = {}
    for e in EDGES:
        rel_counts[e[2]] = rel_counts.get(e[2], 0) + 1
    for rel, n in sorted(rel_counts.items()):
        print(f"    {rel:12s}: {n} edges ({REL_DESC.get(rel, '')})")
    print()

    # Show 10 random edges
    print("  SAMPLE EDGES (10):")
    for cythos, tap, rel in EDGES[:10]:
        print(f"    {cythos:25s} --{rel:10s}--> {tap}")
    print()

    # Stats
    nodes_with_edges = sum(1 for n in combined.get("nodes", []) if n.get("edges"))
    print(f"  GRAPH STATS:")
    print(f"    Total nodes: {len(combined.get('nodes', []))}")
    print(f"    Nodes with edges: {nodes_with_edges}")
    print(f"    Total edges: {sum(len(n.get('edges', [])) for n in combined.get('nodes', []))}")
    print("=" * 80)


if __name__ == "__main__":
    main()
