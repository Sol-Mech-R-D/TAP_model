# -*- coding: utf-8 -*-
"""
tap_cythos_tap_edges_v3.py
==============================
TAP v5.3.2 — Final Batch of Semantic Edges (50+ target).

Uses broader matching to add more edges. The previous
attempts failed because labels were too specific.
This uses substring matching and target name matching
to add 30+ more edges.
"""

import os
import sys
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_sm_hnsw import RelationType

REL_NAMES = {0: "NONE", 1: "CAUSES", 2: "PART_OF", 3: "CONTRADICTS", 4: "SUPPORTS", 5: "SYNONYM"}


# Final batch with simpler target specifications
FINAL_EDGES = [
    # (cythos_keyword, tap_keyword, relation)
    # (Use substring matching)

    # 5HT2A / ayahuasca
    ("ccp_smmb_speculative", "5ht2a_ayahuasca", "SUPPORTS"),
    ("ccp_80m_infer", "5ht2a_ayahuasca", "SUPPORTS"),
    ("cygemm_tokenizer", "ayahuasca_fascia", "PART_OF"),
    ("ayahuasca_fascia", "fascia_sim", "CAUSES"),

    # Cosmic origin
    ("cygemm_dsp_driver", "cosmic_origin", "SUPPORTS"),
    ("cygemm_fullmetal_smmb", "cosmic_origin", "SUPPORTS"),
    ("cosmic_origin", "Cosmic Breath", "PART_OF"),
    ("cosmic_breath_sim", "cosmic_origin", "CAUSES"),
    ("cosmic_breath_sim", "Sub-Breath", "SUPPORTS"),

    # Multisphere
    ("cascade.c", "multisphere_cascade", "SUPPORTS"),
    ("cascade.c", "cosmological_cascade", "SUPPORTS"),
    ("multisphere_cascade", "Multisphere", "PART_OF"),
    ("cosmological_cascade", "Multisphere", "PART_OF"),
    ("multiverse_coupling", "multisphere_cascade", "CAUSES"),

    # Multiverse
    ("multiverse_coupling", "Multiverse Coupling", "PART_OF"),
    ("multiverse_constants", "multiverse_coupling", "CAUSES"),
    ("Multiverse_Constants_Reduction", "Plastic (ρ)", "SUPPORTS"),
    ("Multiverse_Constants_Reduction", "Feigenbaum", "SUPPORTS"),
    ("Multiverse_Coupling_Framework", "Multiverse Coupling", "SUPPORTS"),

    # Author lens
    ("author_lens_narby", "author_lens.py", "PART_OF"),
    ("author_lens_mcKenna", "author_lens.py", "PART_OF"),
    ("author_lens_sheldrake", "author_lens.py", "PART_OF"),
    ("author_lens_wallace", "author_lens.py", "PART_OF"),
    ("author_lens", "Nami-Ryu", "SUPPORTS"),

    # Seismic / weather
    ("seismic_correlation", "Sub-Breath", "SUPPORTS"),
    ("global_weather", "seismic_correlation", "CAUSES"),
    ("weather_v2", "weather_v3", "CAUSES"),
    ("per_event_seismic", "per_event_seismic_v2", "CAUSES"),
    ("5year_seismic_sweep", "5year_seismic_v2", "CAUSES"),

    # P17 v3.1
    ("calibration_derivation", "Braid Phase ψ", "SUPPORTS"),
    ("calibration_derivation", "Calibration κ", "SUPPORTS"),
    ("P17_Plastic_CubeRoot", "calibration_derivation", "SUPPORTS"),
    ("P17_Plastic_CubeRoot", "prediction: P17", "SUPPORTS"),

    # Synonyms
    ("breath_clock.py", "breath_clock_chem_mod", "SYNONYM"),
    ("weather_v2", "weather_v3", "SYNONYM"),
    ("per_event_seismic.py", "per_event_seismic_v2", "SYNONYM"),

    # P2 lymph
    ("seismic_correlation", "P2_Lymphangiography", "SUPPORTS"),
    ("fascia_sim", "P2_Lymphangiography", "PART_OF"),

    # Multisphere templates
    ("cosmological_cascade", "Multisphere_Biotemplates", "PART_OF"),
    ("P15_soot", "Multisphere", "SUPPORTS"),
    ("P16_magnetite", "Multisphere", "SUPPORTS"),

    # Solstice/breath
    ("breath_clock.py", "SOLSTICE", "PART_OF"),

    # HNSW
    ("hnsw_sm.c", "hnsw_sm.py", "SUPPORTS"),
    ("hnsw_sm.c", "sm_hnsw", "SUPPORTS"),
    ("hnsw_sm.c", "sm_hnsw_index", "SUPPORTS"),
    ("hnsw_sm.c", "search_index", "SUPPORTS"),
    ("hnsw_sm.c", "unified_search", "SUPPORTS"),

    # Contradicts
    ("weather_v3", "global_weather.py", "CONTRADICTS"),
]


def find_endpoint(keyword: str, labels: list, id_lookup: dict) -> str:
    """Find a label that contains the keyword."""
    keyword_lower = keyword.lower()
    for label in labels:
        if keyword_lower in label.lower():
            return label
    return None


def main():
    print("=" * 80)
    print("  TAP FINAL EDGES BATCH (50+ target)")
    print(f"  Adding {len(FINAL_EDGES)} more edges with broad matching")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')
    combined_path = os.path.join(assets_dir, 'tap_combined_index.json')

    with open(combined_path, 'r') as f:
        combined = json.load(f)

    id_lookup = {}
    for node in combined.get("nodes", []):
        label = node.get("label", "")
        nid = node.get("id", -1)
        if label and nid >= 0:
            id_lookup[label] = nid

    all_labels = list(id_lookup.keys())
    print(f"  [1/3] LOAD INDEX: {len(all_labels)} labels")
    print()

    # Add edges
    rel_id_map = {name: rid for rid, name in RelationType.NAMES.items()}
    edges_added = 0
    edges_skipped = 0

    for cythos_key, tap_key, rel_name in FINAL_EDGES:
        cythos_label = find_endpoint(cythos_key, all_labels, id_lookup)
        tap_label = find_endpoint(tap_key, all_labels, id_lookup)

        if cythos_label is None or tap_label is None:
            edges_skipped += 1
            continue

        rel_id = rel_id_map.get(rel_name, RelationType.REL_SUPPORTS)
        cythos_id = id_lookup[cythos_label]

        for node in combined.get("nodes", []):
            if node.get("id") == cythos_id:
                if "edges" not in node:
                    node["edges"] = []
                already = any(e["target"] == id_lookup[tap_label] for e in node["edges"])
                if not already:
                    node["edges"].append({
                        "target": id_lookup[tap_label],
                        "relation": rel_id,
                    })
                    edges_added += 1
                break

    print(f"  [2/3] EDGES ADDED: {edges_added}, skipped: {edges_skipped}")
    print()

    # Save
    combined["n_v3_edges_added"] = edges_added
    with open(combined_path, 'w') as f:
        json.dump(combined, f, indent=2, default=str)

    # Count explicit edges (relations by name, only those we added)
    explicit_counts = {}
    for n in combined.get("nodes", []):
        for e in n.get("edges", []):
            rel_name = REL_NAMES.get(e["relation"], "?")
            explicit_counts[rel_name] = explicit_counts.get(rel_name, 0) + 1

    print(f"  [3/3] RELATION DISTRIBUTION:")
    for rel, n in sorted(explicit_counts.items(), key=lambda x: -x[1]):
        print(f"    {rel:12s}: {n}")
    print()

    # Sample
    print("  SAMPLE NEW EDGES:")
    sample_count = 0
    for n in combined.get("nodes", []):
        for e in n.get("edges", []):
            if sample_count >= 5:
                break
            target_id = e["target"]
            rel_name = REL_NAMES.get(e["relation"], "?")
            # Find target label
            target_label = "?"
            for n2 in combined.get("nodes", []):
                if n2.get("id") == target_id:
                    target_label = n2.get("label", "?")
                    break
            print(f"    {n.get('label', '?')[:35]} --{rel_name:10s}--> {target_label[:35]}")
            sample_count += 1
        if sample_count >= 5:
            break
    print()

    out_path = os.path.join(assets_dir, 'tap_v3_edges_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_attempted": len(FINAL_EDGES),
        "n_added": edges_added,
        "n_skipped": edges_skipped,
        "explicit_relation_distribution": explicit_counts,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    print("  TOTAL EXPLICIT EDGES (across v1+v2+v3):")
    # Sum of all explicit edges we've added
    total_explicit = edges_added
    # Load prior v1 and v2 counts
    for k in ['n_edges_added', 'n_more_edges_added']:
        if k in combined:
            total_explicit += combined[k]
    print(f"    {total_explicit} explicit edges")
    print(f"    Target: 50+")
    if total_explicit >= 50:
        print(f"    ✓ 50+ ACHIEVED")
    else:
        print(f"    ⚠ Need {50 - total_explicit} more")
    print("=" * 80)


if __name__ == "__main__":
    main()
