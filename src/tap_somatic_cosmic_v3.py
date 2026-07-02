# -*- coding: utf-8 -*-
"""
tap_somatic_cosmic_v3.py
==============================
TAP v5.3.2 — Somatic vs Cosmic Geometry v3 (30+ somatics).

Extends v2 to include:
  - Connective tissue cell types (fibroblasts, adipocytes,
    chondrocytes, osteocytes, etc.)
  - Neurons and glial cells
  - Muscle cells (smooth, cardiac, skeletal)
  - Epithelial cells
  - More protein structures (intermediate filaments,
    G-proteins, etc.)

Total somatics: 30+

Each is mapped to the cosmic template(s) it most
resembles. The comparison uses geometry, symmetry, and
φ-rate.
"""

import os
import json
import math
import statistics
from datetime import datetime

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13


# All 22 cosmic templates (from v2)
COSMIC_TEMPLATES = [
    {"name": "Superfluid Vortex Braids", "zone": "cold", "T_K": 3.0, "geometry": "vortex lattice", "symmetry": "U(1)"},
    {"name": "Polythiazyl (SN)x Helices", "zone": "cold", "T_K": 8.0, "geometry": "helical polymer", "symmetry": "C_2"},
    {"name": "Fluorocarbon (PTFE-like) Sleeves", "zone": "cold", "T_K": 120.0, "geometry": "sleeve", "symmetry": "C_infty"},
    {"name": "Phosphaalkene Ribbons", "zone": "cold", "T_K": 130.0, "geometry": "ribbon polymer", "symmetry": "C_2v"},
    {"name": "Carbon DNA", "zone": "temperate", "T_K": 150.0, "geometry": "double helix", "symmetry": "D_2"},
    {"name": "PNA Helices", "zone": "temperate", "T_K": 180.0, "geometry": "double helix", "symmetry": "D_2"},
    {"name": "Quadruplet Codon DNA", "zone": "temperate", "T_K": 150.0, "geometry": "quadruplet", "symmetry": "C_4"},
    {"name": "Metallo-Nucleic Wires", "zone": "temperate", "T_K": 200.0, "geometry": "wire", "symmetry": "D_infty"},
    {"name": "Se-DNA", "zone": "temperate", "T_K": 200.0, "geometry": "double helix", "symmetry": "D_2"},
    {"name": "Germoxane Gels", "zone": "temperate", "T_K": 200.0, "geometry": "gel network", "symmetry": "fractal"},
    {"name": "Phosphazene Braids", "zone": "temperate", "T_K": 220.0, "geometry": "braid", "symmetry": "B_n"},
    {"name": "Thioester Matrices", "zone": "warm", "T_K": 300.0, "geometry": "tetrahedral", "symmetry": "C_3v"},
    {"name": "Ge-Sn Photonic Wafers", "zone": "warm", "T_K": 320.0, "geometry": "crystal wafer", "symmetry": "D_2d"},
    {"name": "Fe-S Grids", "zone": "warm", "T_K": 400.0, "geometry": "cubane", "symmetry": "T_d"},
    {"name": "Organosilicon Hybrids", "zone": "warm", "T_K": 400.0, "geometry": "tetrahedral", "symmetry": "T_d"},
    {"name": "Siloxane Helices", "zone": "warm", "T_K": 450.0, "geometry": "triple helix", "symmetry": "B_3"},
    {"name": "Carborane Cages", "zone": "warm", "T_K": 550.0, "geometry": "cage", "symmetry": "I_h"},
    {"name": "BCN Braids", "zone": "hot", "T_K": 35.0, "geometry": "braid", "symmetry": "B_n"},
    {"name": "BN Tubes", "zone": "hot", "T_K": 42.5, "geometry": "cylinder", "symmetry": "D_nh"},
    {"name": "SiC Whiskers", "zone": "hot", "T_K": 55.0, "geometry": "whisker", "symmetry": "C_infty"},
    {"name": "Lanthanide Networks", "zone": "hot", "T_K": 65.0, "geometry": "network", "symmetry": "fractal"},
    {"name": "Dusty Plasma Helices", "zone": "hot", "T_K": 125.0, "geometry": "helical plasma", "symmetry": "helical"},
]

# Extended somatics (30+)
EXTENDED_SOMATICS = [
    # Original 7
    {"name": "Collagen triple helix", "category": "ECM", "geometry": "triple helix", "symmetry": "B_3", "phi_rate": "φ⁻⁴"},
    {"name": "DNA double helix", "category": "nucleic", "geometry": "double helix", "symmetry": "D_2", "phi_rate": "φ⁻⁴"},
    {"name": "Anatomy Train spirals", "category": "ECM", "geometry": "twin spirals", "symmetry": "B_2", "phi_rate": "φ⁻²"},
    {"name": "Lymph vessel", "category": "vascular", "geometry": "fractal tree", "symmetry": "fractal", "phi_rate": "φ⁻¹³"},
    {"name": "Actin filament", "category": "cytoskeleton", "geometry": "double helix", "symmetry": "D_2", "phi_rate": "φ⁻⁸"},
    {"name": "Microtubule", "category": "cytoskeleton", "geometry": "hollow cylinder", "symmetry": "D_25", "phi_rate": "φ⁻¹³"},
    {"name": "Myofibril (sarcomere)", "category": "muscle", "geometry": "stacked bands", "symmetry": "translation", "phi_rate": "φ⁻²"},
    # Connective tissue cell types
    {"name": "Fibroblast", "category": "cell", "geometry": "spindle", "symmetry": "C_2", "phi_rate": "φ⁻⁴", "size_um": 50},
    {"name": "Adipocyte", "category": "cell", "geometry": "sphere", "symmetry": "K_h", "phi_rate": "φ⁻⁸", "size_um": 100},
    {"name": "Chondrocyte", "category": "cell", "geometry": "ovoid", "symmetry": "C_2v", "phi_rate": "φ⁻⁴", "size_um": 20},
    {"name": "Osteocyte", "category": "cell", "geometry": "stellate", "symmetry": "D_2h", "phi_rate": "φ⁻⁸", "size_um": 30},
    {"name": "Tenocyte", "category": "cell", "geometry": "spindle", "symmetry": "C_2", "phi_rate": "φ⁻⁴", "size_um": 100},
    {"name": "Mast cell", "category": "cell", "geometry": "sphere (granular)", "symmetry": "K_h", "phi_rate": "φ⁻⁴", "size_um": 15},
    {"name": "Macrophage", "category": "cell", "geometry": "ameboid", "symmetry": "C_1", "phi_rate": "φ⁻⁸", "size_um": 25},
    # Neurons
    {"name": "Pyramidal neuron", "category": "neuron", "geometry": "pyramidal", "symmetry": "C_4v", "phi_rate": "φ⁻⁴", "size_um": 50},
    {"name": "Purkinje neuron", "category": "neuron", "geometry": "fan-shaped", "symmetry": "C_s", "phi_rate": "φ⁻²", "size_um": 60},
    {"name": "Bipolar neuron", "category": "neuron", "geometry": "bipolar", "symmetry": "C_infty_v", "phi_rate": "φ⁻⁴", "size_um": 20},
    {"name": "Astrocyte", "category": "glial", "geometry": "stellate", "symmetry": "D_2h", "phi_rate": "φ⁻⁸", "size_um": 40},
    {"name": "Oligodendrocyte", "category": "glial", "geometry": "myelinating", "symmetry": "C_infty", "phi_rate": "φ⁻⁸", "size_um": 20},
    {"name": "Schwann cell", "category": "glial", "geometry": "myelinating", "symmetry": "C_infty", "phi_rate": "φ⁻⁸", "size_um": 30},
    {"name": "Microglia", "category": "glial", "geometry": "ramified", "symmetry": "fractal", "phi_rate": "φ⁻⁸", "size_um": 15},
    # Muscle
    {"name": "Cardiomyocyte", "category": "muscle", "geometry": "branched cylinder", "symmetry": "C_2v", "phi_rate": "φ⁻²", "size_um": 100},
    {"name": "Smooth muscle cell", "category": "muscle", "geometry": "spindle", "symmetry": "C_2", "phi_rate": "φ⁻²", "size_um": 50},
    {"name": "Skeletal muscle fiber", "category": "muscle", "geometry": "long cylinder (syncytium)", "symmetry": "C_infty", "phi_rate": "φ⁻²", "size_um": 30000},
    # Epithelial
    {"name": "Squamous epithelial", "category": "epithelial", "geometry": "flat polygon", "symmetry": "C_6", "phi_rate": "φ⁻⁴", "size_um": 25},
    {"name": "Columnar epithelial", "category": "epithelial", "geometry": "tall column", "symmetry": "C_infty_v", "phi_rate": "φ⁻⁴", "size_um": 20},
    {"name": "Ciliated epithelial", "category": "epithelial", "geometry": "column with cilia", "symmetry": "C_infty", "phi_rate": "φ⁻²", "size_um": 25},
    # More proteins
    {"name": "Intermediate filament (vimentin)", "category": "cytoskeleton", "geometry": "coiled coil", "symmetry": "C_2", "phi_rate": "φ⁻⁸", "size_nm": 10},
    {"name": "G-protein alpha subunit", "category": "protein", "geometry": "alpha-beta fold", "symmetry": "C_1", "phi_rate": "φ⁻⁴", "size_nm": 5},
    {"name": "Hemoglobin tetramer", "category": "protein", "geometry": "tetramer", "symmetry": "D_2", "phi_rate": "φ⁻⁴", "size_nm": 6.5},
    {"name": "Ferritin cage", "category": "protein", "geometry": "24-mer cage", "symmetry": "O_h", "phi_rate": "φ⁻⁸", "size_nm": 12},
    {"name": "Myelin sheath", "category": "membrane", "geometry": "wrapped sleeve", "symmetry": "C_infty", "phi_rate": "φ⁻⁸", "size_nm": 1000},
]


def homology_score(template: dict, somatic: dict) -> float:
    """Compute the homology score."""
    score = 0.0
    geo = template["geometry"].lower()
    som_geo = somatic["geometry"].lower()
    if geo == som_geo:
        score += 0.4
    elif "helix" in geo and "helix" in som_geo:
        score += 0.3
    elif "braid" in geo and "braid" in som_geo:
        score += 0.3
    elif "fractal" in geo and "fractal" in som_geo:
        score += 0.3
    elif "cylinder" in geo and "cylinder" in som_geo:
        score += 0.3
    elif "polymer" in geo and "polymer" in som_geo:
        score += 0.3
    elif "cage" in geo and "cage" in som_geo:
        score += 0.3
    elif "tube" in geo and "tube" in som_geo:
        score += 0.3
    elif "wire" in geo and "wire" in som_geo:
        score += 0.3
    elif "sleeve" in geo and "sleeve" in som_geo:
        score += 0.3
    elif "sphere" in geo and "sphere" in som_geo:
        score += 0.3
    sym = template["symmetry"]
    som_sym = somatic["symmetry"]
    if sym == som_sym:
        score += 0.3
    elif "B_" in sym and "B_" in som_sym:
        score += 0.25
    elif "D_" in sym and "D_" in som_sym:
        score += 0.25
    elif "fractal" in sym and "fractal" in som_sym:
        score += 0.2
    elif "C_infty" in sym and "C_infty" in som_sym:
        score += 0.25
    if template.get("phi_rate") == somatic["phi_rate"]:
        score += 0.2
    return min(1.0, score)


def main():
    print("=" * 80)
    print("  TAP SOMATIC vs COSMIC v3 — EXTENDED SOMATICS (30+)")
    print(f"  {len(COSMIC_TEMPLATES)} cosmic templates × {len(EXTENDED_SOMATICS)} somatics = {len(COSMIC_TEMPLATES)*len(EXTENDED_SOMATICS)} cells")
    print("=" * 80)
    print()

    # 1. Best matches per somatic
    print("  [1/3] BEST COSMIC MATCH PER SOMATIC:")
    print(f"  {'Somatic':35s} | {'Category':12s} | {'Best cosmic':25s} | {'Score':>5s}")
    print("  " + "-" * 90)
    best_matches = []
    for s in EXTENDED_SOMATICS:
        row_scores = [(homology_score(t, s), t["name"]) for t in COSMIC_TEMPLATES]
        row_scores.sort(reverse=True)
        best_score, best_template = row_scores[0]
        best_matches.append((s, best_template, best_score))
        print(f"  {s['name'][:35]:35s} | {s['category']:12s} | {best_template[:25]:25s} | {best_score:>5.2f}")
    print()

    # 2. Per-category statistics
    print("  [2/3] PER-CATEGORY STATISTICS:")
    categories = {}
    for s in EXTENDED_SOMATICS:
        categories.setdefault(s["category"], []).append(s)
    for cat, soms in categories.items():
        scores = [b[2] for b in best_matches if b[0]["category"] == cat]
        if scores:
            print(f"    {cat:15s} ({len(soms)} somatics): avg = {statistics.mean(scores):.3f}, max = {max(scores):.3f}")
    print()

    # 3. Overall
    all_scores = [b[2] for b in best_matches]
    print(f"  [3/3] OVERALL:")
    print(f"    Total somatics: {len(EXTENDED_SOMATICS)}")
    print(f"    Avg best-match score: {statistics.mean(all_scores):.3f}")
    print(f"    Strong matches (>0.5): {sum(1 for s in all_scores if s > 0.5)}/{len(all_scores)} ({100*sum(1 for s in all_scores if s > 0.5)/len(all_scores):.1f}%)")
    print()

    # Top 10 matches
    print("  TOP 10 BEST MATCHES:")
    sorted_matches = sorted(best_matches, key=lambda x: x[2], reverse=True)
    for s, t, sc in sorted_matches[:10]:
        print(f"    {s['name']:30s} ↔ {t:25s} ({sc:.2f})")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_somatic_cosmic_v3_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_cosmic": len(COSMIC_TEMPLATES),
        "n_somatic": len(EXTENDED_SOMATICS),
        "cosmic_templates": COSMIC_TEMPLATES,
        "somatics": EXTENDED_SOMATICS,
        "best_matches": [{"somatic": s["name"], "cosmic": t, "score": round(sc, 4)} for s, t, sc in best_matches],
        "stats": {
            "mean_score": round(statistics.mean(all_scores), 4),
            "max_score": max(all_scores),
            "strong_matches": sum(1 for s in all_scores if s > 0.5),
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
