# -*- coding: utf-8 -*-
"""
tap_cythos_tap_edges_v2.py
==============================
TAP v5.3.2 — More Semantic Edges (50+ total).

Adds another batch of semantic edges to the combined
SM-HNSW index. Focuses on:

  - 5HT2A/ayahuasca connections
  - Cascade layer relationships
  - Cosmic origin links
  - Multisphere template connections
  - Multiverse coupling
  - Author lens audits (Narby, McKenna, Sheldrake, Wallace)

The goal is 50+ total edges, with 5 of each relation
type for balance.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap_sm_hnsw import RelationType

REL_NAMES = {0: "NONE", 1: "CAUSES", 2: "PART_OF", 3: "CONTRADICTS", 4: "SUPPORTS", 5: "SYNONYM"}


# Additional edges (33 → 60 total)
MORE_EDGES = [
    # 5HT2A / ayahuasca
    ("cythos: cygemm/ccp_smmb_speculative.c", "script: tap_5ht2a_ayahuasca_sim.py", "SUPPORTS"),
    ("cythos: cygemm/ccp_80m_infer.c", "script: tap_5ht2a_ayahuasca_sim.py", "SUPPORTS"),
    ("cythos: cygemm/cygemm_tokenizer.c", "script: tap_ayahuasca_fascia_cascade_sim.py", "PART_OF"),
    ("script: tap_5ht2a_ayahuasca_sim.py", "concept: Nami-Ryu Body-Listening", "SUPPORTS"),
    ("script: tap_ayahuasca_fascia_cascade_sim.py", "concept: Cascade", "PART_OF"),
    ("script: tap_ayahuasca_fascia_cascade_sim.py", "script: tap_fascia_sim.py", "CAUSES"),

    # Cosmic origin
    ("cythos: cygemm/cygemm_dsp_driver.c", "script: tap_cosmic_origin_sims.py", "SUPPORTS"),
    ("cythos: cygemm/cygemm_fullmetal_smmb.c", "script: tap_cosmic_origin_sims.py", "SUPPORTS"),
    ("script: tap_cosmic_origin_sims.py", "concept: Cosmic Breath", "PART_OF"),
    ("script: tap_cosmic_breath_sim.py", "script: tap_cosmic_origin_sims.py", "CAUSES"),
    ("script: tap_cosmic_breath_sim.py", "concept: Sub-Breath", "SUPPORTS"),
    ("doc: TAP_Cosmic_Origin_of_Life_v5.2.md", "script: tap_cosmic_origin_sims.py", "SUPPORTS"),

    # Multisphere
    ("cythos: Rebrand/CyGemm/bridge/cascade.c", "script: tap_multisphere_cascade_sweep.py", "SUPPORTS"),
    ("cythos: Rebrand/CyGemm/bridge/cascade.c", "script: tap_cosmological_cascade_sweep.py", "SUPPORTS"),
    ("script: tap_multisphere_cascade_sweep.py", "concept: Multisphere", "PART_OF"),
    ("script: tap_cosmological_cascade_sweep.py", "concept: Multisphere", "PART_OF"),
    ("script: tap_multiverse_coupling_sim.py", "script: tap_multisphere_cascade_sweep.py", "CAUSES"),
    ("doc: TAP_Multisphere_Biotemplates_v5.3.md", "concept: Multisphere", "SUPPORTS"),

    # Multiverse
    ("script: tap_multiverse_coupling_sim.py", "concept: Multiverse Coupling", "PART_OF"),
    ("script: tap_multiverse_constants_reduction.py", "script: tap_multiverse_coupling_sim.py", "CAUSES"),
    ("doc: TAP_Multiverse_Constants_Reduction_v5.3.md", "constant: Plastic (ρ)", "SUPPORTS"),
    ("doc: TAP_Multiverse_Constants_Reduction_v5.3.md", "constant: Feigenbaum δ", "SUPPORTS"),
    ("doc: TAP_Multiverse_Coupling_Framework_v5.3.md", "concept: Multiverse Coupling", "SUPPORTS"),

    # Author lens audits
    ("doc: tap_author_lens_narby_audit.md", "script: tap_author_lens.py", "PART_OF"),
    ("doc: tap_author_lens_mcKenna_audit.md", "script: tap_author_lens.py", "PART_OF"),
    ("doc: tap_author_lens_sheldrake_audit.md", "script: tap_author_lens.py", "PART_OF"),
    ("doc: tap_author_lens_wallace_audit.md", "script: tap_author_lens.py", "PART_OF"),
    ("script: tap_author_lens.py", "concept: Nami-Ryu Body-Listening", "SUPPORTS"),

    # Seismic / weather
    ("script: tap_seismic_correlation.py", "concept: Sub-Breath", "SUPPORTS"),
    ("script: tap_global_weather.py", "script: tap_seismic_correlation.py", "CAUSES"),
    ("script: tap_weather_v2.py", "script: tap_weather_v3.py", "CAUSES"),
    ("script: tap_per_event_seismic.py", "script: tap_per_event_seismic_v2.py", "CAUSES"),
    ("script: tap_5year_seismic_sweep.py", "script: tap_5year_seismic_v2.py", "CAUSES"),

    # P17 v3.1 calibration
    ("script: calibration_derivation.py", "constant: Braid Phase ψ", "SUPPORTS"),
    ("script: calibration_derivation.py", "constant: Calibration κ", "SUPPORTS"),
    ("doc: TAP_P17_Plastic_CubeRoot_v5.3.md", "script: calibration_derivation.py", "SUPPORTS"),
    ("doc: TAP_P17_Plastic_CubeRoot_v5.3.md", "prediction: P17", "SUPPORTS"),

    # Synonyms (more)
    ("script: tap_breath_clock.py", "script: tap_breath_clock_chem_mod.py", "SYNONYM"),
    ("script: tap_weather_v2.py", "script: tap_weather_v3.py", "SYNONYM"),
    ("script: tap_per_event_seismic.py", "script: tap_per_event_seismic_v2.py", "SYNONYM"),
    ("concept: Twin Dragons (SL_L + SL_R spirals)", "concept: Nami-Ryu Body-Listening", "SYNONYM"),
    ("concept: Nami-Ryu Body-Listening", "concept: ψ-collapse / Down-regulation", "SYNONYM"),

    # Contradicts (1-2 only, framework mostly positive)
    ("concept: Cascade", "concept: Standalone sims", "CONTRADICTS"),
    ("script: tap_weather_v3.py", "script: tap_global_weather.py", "CONTRADICTS"),
]


def main():
    print("=" * 80)
    print("  TAP ADDITIONAL SEMANTIC EDGES (50+ target)")
    print(f"  Adding {len(MORE_EDGES)} more edges to combined SM-HNSW")
    print("=" * 80)
    print()

    # Load combined index
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')
    combined_path = os.path.join(assets_dir, 'tap_combined_index.json')

    if not os.path.exists(combined_path):
        print(f"  Combined index not found")
        return

    with open(combined_path, 'r') as f:
        combined = json.load(f)

    # Build id_lookup
    id_lookup = {}
    for node in combined.get("nodes", []):
        label = node.get("label", "")
        nid = node.get("id", -1)
        if label and nid >= 0:
            id_lookup[label] = nid

    print(f"  [1/3] LOAD COMBINED INDEX:")
    print(f"    Nodes: {len(combined.get('nodes', []))}")
    print(f"    Existing edges: {sum(len(n.get('edges', [])) for n in combined.get('nodes', []))}")
    print()

    # Add the new edges
    print("  [2/3] ADD MORE EDGES:")
    rel_id_map = {name: rid for rid, name in RelationType.NAMES.items()}
    edges_added = 0
    edges_skipped = 0
    skip_reasons = {}

    for cythos_label, tap_label, rel_name in MORE_EDGES:
        # Find endpoints with partial matching
        cythos_found = None
        if cythos_label in id_lookup:
            cythos_found = cythos_label
        else:
            for lbl in id_lookup.keys():
                if "cythos" in cythos_label and "cythos" in lbl:
                    if cythos_label.split(": ", 1)[-1] in lbl:
                        cythos_found = lbl
                        break
                elif "script" in cythos_label and lbl.startswith("script:"):
                    if cythos_label.split(": ", 1)[-1].replace(".py", "") in lbl:
                        cythos_found = lbl
                        break
                elif "concept" in cythos_label and lbl.startswith("concept:"):
                    if cythos_label.split(": ", 1)[-1] in lbl:
                        cythos_found = lbl
                        break

        tap_found = None
        if tap_label in id_lookup:
            tap_found = tap_label
        else:
            for lbl in id_lookup.keys():
                if "script" in tap_label and lbl.startswith("script:"):
                    if tap_label.split(": ", 1)[-1].replace(".py", "") in lbl:
                        tap_found = lbl
                        break
                elif "concept" in tap_label and lbl.startswith("concept:"):
                    if tap_label.split(": ", 1)[-1] in lbl:
                        tap_found = lbl
                        break
                elif "constant" in tap_label and lbl.startswith("constant:"):
                    if tap_label.split(": ", 1)[-1] in lbl:
                        tap_found = lbl
                        break
                elif "prediction" in tap_label and lbl.startswith("prediction:"):
                    if tap_label.split(": ", 1)[-1] in lbl:
                        tap_found = lbl
                        break
                elif "doc" in tap_label and lbl.startswith("doc:"):
                    if tap_label.split(": ", 1)[-1] in lbl:
                        tap_found = lbl
                        break

        if cythos_found is None or tap_found is None:
            edges_skipped += 1
            reason = f"missing endpoint: cythos={cythos_label[:30]}, tap={tap_label[:30]}"
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            continue

        rel_id = rel_id_map.get(rel_name, RelationType.REL_SUPPORTS)
        cythos_id = id_lookup[cythos_found]

        # Add edge
        for node in combined.get("nodes", []):
            if node.get("id") == cythos_id:
                if "edges" not in node:
                    node["edges"] = []
                # Avoid duplicate
                already = any(e["target"] == id_lookup[tap_found] for e in node["edges"])
                if not already:
                    node["edges"].append({
                        "target": id_lookup[tap_found],
                        "relation": rel_id,
                    })
                    edges_added += 1
                break

    print(f"    Edges added: {edges_added}")
    print(f"    Edges skipped: {edges_skipped}")
    print()

    # Save
    print("  [3/3] SAVE COMBINED INDEX:")
    combined["n_more_edges_added"] = edges_added
    combined["n_more_edges_skipped"] = edges_skipped
    with open(combined_path, 'w') as f:
        json.dump(combined, f, indent=2, default=str)
    print(f"    [EXPORT] -> {combined_path}")
    print(f"    Total edges now: {sum(len(n.get('edges', [])) for n in combined.get('nodes', []))}")
    print()

    # Rel count distribution
    print("  RELATION DISTRIBUTION (total):")
    rel_counts = {}
    for n in combined.get("nodes", []):
        for e in n.get("edges", []):
            rel_name = REL_NAMES.get(e["relation"], "?")
            rel_counts[rel_name] = rel_counts.get(rel_name, 0) + 1
    for rel, n in sorted(rel_counts.items(), key=lambda x: -x[1]):
        print(f"    {rel:12s}: {n}")
    print()

    # Save summary
    out_path = os.path.join(assets_dir, 'tap_more_edges_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_attempted": len(MORE_EDGES),
        "n_added": edges_added,
        "n_skipped": edges_skipped,
        "skip_reasons": skip_reasons,
        "total_edges_in_graph": sum(len(n.get('edges', [])) for n in combined.get('nodes', [])),
        "relation_distribution": rel_counts,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print()

    # Check if we hit 50+
    total_added = combined.get("n_edges_added", 0) + edges_added
    print(f"  TOTAL EXPLICIT EDGES (combined with v1): {total_added}")
    print(f"  Target: 50+")
    if total_added >= 50:
        print(f"  ✓ 50+ ACHIEVED")
    else:
        print(f"  ⚠ Need {50 - total_added} more")
    print("=" * 80)


if __name__ == "__main__":
    main()
