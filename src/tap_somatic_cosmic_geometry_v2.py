# -*- coding: utf-8 -*-
"""
tap_somatic_cosmic_geometry_v2.py
======================================
TAP v5.3.2 — Somatic vs Cosmic Geometry v2 (full 22 templates).

Extends tap_somatic_cosmic_geometry.py to map ALL 22
multisphere templates × 4 zones, against the 7 somatic
geometries.

Each template gets a homology score against the somatic
geometries. The total homology matrix shows the
quantitative relationship between body and cosmos.

Template zones (from tap_cosmological_cascade_sweep.py):
  - Cold (a=1.0, 4 templates): Vortex braids, polythiazyl,
    PTFE, phosphaalkene
  - Temperate (a=1.0, 7 templates): Carbon DNA, PNA, codon
    DNA, metallo-nucleic, Se-DNA, germoxane, phosphazene
  - Warm (intermediate a, 6 templates): Thioester, Ge-Sn,
    Fe-S, organosilicon, siloxane, carborane
  - Hot (a=0.05, 5 templates): BCN, BN tubes, SiC,
    lanthanide, dusty plasma

Somatic geometries (7):
  - Collagen (B_3), DNA, anatomy spirals, lymph, actin,
    microtubule, myofibril
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


# All 22 multisphere templates
ALL_22_TEMPLATES = [
    # Cold (4)
    {"name": "Superfluid Vortex Braids", "zone": "cold", "T_K": 3.0, "geometry": "vortex lattice", "symmetry": "U(1)", "type": "Pure Inorganic", "somatic_match": "Anatomy Train spirals (twin vortices)"},
    {"name": "Polythiazyl (SN)x Helices", "zone": "cold", "T_K": 8.0, "geometry": "helical polymer", "symmetry": "C_2", "type": "Pure Inorganic", "somatic_match": "Collagen triple helix (polymer)"},
    {"name": "Fluorocarbon (PTFE-like) Sleeves", "zone": "cold", "T_K": 120.0, "geometry": "sleeve", "symmetry": "C_infty", "type": "Hybrid", "somatic_match": "Myelin sheath (insulating sleeve)"},
    {"name": "Phosphorus-Carbon (Phosphaalkene) Ribbons", "zone": "cold", "T_K": 130.0, "geometry": "ribbon polymer", "symmetry": "C_2v", "type": "Hybrid", "somatic_match": "Beta-sheet protein (ribbon)"},
    # Temperate (7)
    {"name": "Carbon Biotemplates (DNA)", "zone": "temperate", "T_K": 150.0, "geometry": "double helix", "symmetry": "D_2", "type": "Organic", "somatic_match": "DNA double helix (IDENTICAL)"},
    {"name": "Peptide Nucleic Acid (PNA) Helices", "zone": "temperate", "T_K": 180.0, "geometry": "double helix", "symmetry": "D_2", "type": "Organic", "somatic_match": "Actin filament (helical polymer)"},
    {"name": "Quadruplet Codon DNA", "zone": "temperate", "T_K": 150.0, "geometry": "quadruplet", "symmetry": "C_4", "type": "Organic", "somatic_match": "Hemoglobin tetramer (C_4)"},
    {"name": "Metallo-Nucleic Wires", "zone": "temperate", "T_K": 200.0, "geometry": "wire", "symmetry": "D_infty", "type": "Hybrid", "somatic_match": "Actin/myosin (linear wires)"},
    {"name": "Organoselenium (Se-DNA)", "zone": "temperate", "T_K": 200.0, "geometry": "double helix", "symmetry": "D_2", "type": "Hybrid", "somatic_match": "DNA (analog)"},
    {"name": "Carbon-Germanium (Germoxane) Gels", "zone": "temperate", "T_K": 200.0, "geometry": "gel network", "symmetry": "fractal", "type": "Hybrid", "somatic_match": "Extracellular matrix (gel)"},
    {"name": "Phosphazene (P-N) Braids", "zone": "temperate", "T_K": 220.0, "geometry": "braid", "symmetry": "B_n", "type": "Pure Inorganic", "somatic_match": "Collagen B_3 braid (analog)"},
    # Warm (6)
    {"name": "Thioester Matrices", "zone": "warm", "T_K": 300.0, "geometry": "tetrahedral", "symmetry": "C_3v", "type": "Organic", "somatic_match": "Amino acid tetrahedral center"},
    {"name": "Ge-Sn Photonic Wafers", "zone": "warm", "T_K": 320.0, "geometry": "crystal wafer", "symmetry": "D_2d", "type": "Pure Inorganic", "somatic_match": "Apatite crystal (bone)"},
    {"name": "Metal-Sulfur-Carbon (Fe-S) Grids", "zone": "warm", "T_K": 400.0, "geometry": "cubane", "symmetry": "T_d", "type": "Hybrid", "somatic_match": "Iron-sulfur cluster (biology)"},
    {"name": "Carbon-Silicon (Organosilicon) Hybrids", "zone": "warm", "T_K": 400.0, "geometry": "tetrahedral", "symmetry": "T_d", "type": "Hybrid", "somatic_match": "Silicon in connective tissue (analog)"},
    {"name": "Siloxane (Si-O) Helices", "zone": "warm", "T_K": 450.0, "geometry": "triple helix", "symmetry": "B_3", "type": "Pure Inorganic", "somatic_match": "Collagen triple helix (B_3)"},
    {"name": "Carborane Cages (C-B)", "zone": "warm", "T_K": 550.0, "geometry": "cage", "symmetry": "I_h", "type": "Hybrid", "somatic_match": "Ferritin cage (I_h)"},
    # Hot (5)
    {"name": "Boron-Carbon-Nitrogen (BCN) Braids", "zone": "hot", "T_K": 35.0, "geometry": "braid", "symmetry": "B_n", "type": "Hybrid", "somatic_match": "B_3 braid in collagen (analog)"},
    {"name": "Boron-Nitrogen (BN) Tubes", "zone": "hot", "T_K": 42.5, "geometry": "cylinder", "symmetry": "D_nh", "type": "Pure Inorganic", "somatic_match": "Microtubule hollow cylinder"},
    {"name": "Silicon Carbide (SiC) Whiskers", "zone": "hot", "T_K": 55.0, "geometry": "whisker", "symmetry": "C_infty", "type": "Pure Inorganic", "somatic_match": "Cilia/flagella whisker"},
    {"name": "Lanthanide Upconversion Networks", "zone": "hot", "T_K": 65.0, "geometry": "network", "symmetry": "fractal", "type": "Pure Inorganic", "somatic_match": "Lymphatic network (fractal)"},
    {"name": "Dusty Plasma Helices", "zone": "hot", "T_K": 125.0, "geometry": "helical plasma", "symmetry": "helical", "type": "Pure Inorganic", "somatic_match": "Anatomy Train spirals (helical)"},
]


SOMATIC_GEOMETRIES = [
    {"name": "Collagen triple helix", "geometry": "triple helix", "symmetry": "B_3", "phi_rate": "φ⁻⁴", "test": "P17 v3.1"},
    {"name": "DNA double helix", "geometry": "double helix", "symmetry": "D_2", "phi_rate": "φ⁻⁴", "test": "P7"},
    {"name": "Anatomy Train spirals", "geometry": "twin spirals", "symmetry": "B_2", "phi_rate": "φ⁻²", "test": "P4"},
    {"name": "Lymph vessel", "geometry": "fractal tree", "symmetry": "fractal", "phi_rate": "φ⁻¹³", "test": "P2"},
    {"name": "Actin filament", "geometry": "double helix", "symmetry": "D_2", "phi_rate": "φ⁻⁸", "test": "fidelity"},
    {"name": "Microtubule", "geometry": "hollow cylinder", "symmetry": "D_25", "phi_rate": "φ⁻¹³", "test": "fidelity"},
    {"name": "Myofibril (sarcomere)", "geometry": "stacked bands", "symmetry": "translation", "phi_rate": "φ⁻²", "test": "P3"},
]


def homology_score(template: dict, somatic: dict) -> float:
    """
    Compute the homology score between a template and somatic geometry.

    Score: 0-1, based on:
      - Geometry match (40%)
      - Symmetry match (30%)
      - φ-rate match (20%)
      - Test overlap (10%)
    """
    score = 0.0
    # Geometry match
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
    # Symmetry match
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
    # φ-rate match (bonus if both use φ⁻⁴ or both use φ⁻¹³)
    if template.get("phi_rate") == somatic["phi_rate"]:
        score += 0.2
    # Test overlap (bonus if same test framework)
    return min(1.0, score)


def main():
    print("=" * 80)
    print("  TAP SOMATIC vs COSMIC GEOMETRY v2 — FULL 22 TEMPLATES")
    print("  22 cosmic biotemplates × 7 somatic geometries = 154 cells")
    print("=" * 80)
    print()

    # 1. Homology matrix
    print("  [1/3] HOMOLOGY MATRIX (template × somatic):")
    print(f"  {'Template':30s} | ", end="")
    for s in SOMATIC_GEOMETRIES:
        print(f"{s['name'][:8]:>8s} ", end="")
    print()
    print("  " + "-" * 130)

    best_matches = []
    for t in ALL_22_TEMPLATES:
        row_scores = []
        print(f"  {t['name'][:30]:30s} | ", end="")
        for s in SOMATIC_GEOMETRIES:
            score = homology_score(t, s)
            row_scores.append(score)
            if score > 0.7:
                marker = " ★ "
            elif score > 0.4:
                marker = " ✓ "
            elif score > 0.2:
                marker = " ~ "
            else:
                marker = " · "
            print(f"{marker:>8s} ", end="")
        best_idx = row_scores.index(max(row_scores))
        best_match = SOMATIC_GEOMETRIES[best_idx]["name"]
        best_matches.append((t["name"], best_match, max(row_scores)))
        print()
    print()
    print("  Legend: ★ = strong (>0.7), ✓ = good (0.4-0.7), ~ = fair (0.2-0.4), · = weak (<0.2)")
    print()

    # 2. Per-template best matches
    print("  [2/3] BEST SOMATIC MATCH PER TEMPLATE:")
    for t, match, score in best_matches:
        print(f"    {t:30s} → {match:25s} (score: {score:.2f})")
    print()

    # 3. Per-zone statistics
    print("  [3/3] PER-ZONE HOMOLOGY STATISTICS:")
    for zone in ["cold", "temperate", "warm", "hot"]:
        zone_templates = [t for t in ALL_22_TEMPLATES if t["zone"] == zone]
        zone_scores = [homology_score(t, s) for t in zone_templates for s in SOMATIC_GEOMETRIES]
        avg = statistics.mean(zone_scores)
        max_s = max(zone_scores)
        print(f"    {zone:10s} ({len(zone_templates)} templates): avg = {avg:.3f}, max = {max_s:.3f}")
    print()

    # Overall
    all_scores = [homology_score(t, s) for t in ALL_22_TEMPLATES for s in SOMATIC_GEOMETRIES]
    print(f"  OVERALL: {len(all_scores)} cells, avg score = {statistics.mean(all_scores):.3f}")
    strong_matches = sum(1 for s in all_scores if s > 0.4)
    print(f"  Strong matches (score > 0.4): {strong_matches}/{len(all_scores)} ({100*strong_matches/len(all_scores):.1f}%)")
    print()

    # Export
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'tap_somatic_cosmic_geometry_v2_results.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_templates": len(ALL_22_TEMPLATES),
        "n_somatic": len(SOMATIC_GEOMETRIES),
        "templates": ALL_22_TEMPLATES,
        "somatic_geometries": SOMATIC_GEOMETRIES,
        "best_matches": [{"template": t, "somatic": m, "score": s} for t, m, s in best_matches],
        "all_scores": all_scores,
        "stats": {
            "mean_score": statistics.mean(all_scores),
            "max_score": max(all_scores),
            "strong_matches": strong_matches,
            "strong_match_pct": round(100 * strong_matches / len(all_scores), 1),
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
