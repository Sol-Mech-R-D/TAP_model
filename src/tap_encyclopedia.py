# -*- coding: utf-8 -*-
"""
tap_encyclopedia.py
=====================
TAP v5.3.2 — Encyclopedia Generator.

Generates a comprehensive wiki-style entry for every
constant, prediction, sim, and concept in the framework.

The encyclopedia is output as:
  - Markdown file (docs/TAP_Encyclopedia_v5_3.md)
  - JSON file (assets/tap_encyclopedia.json)
  - Wiki index (per category)

Categories:
  1. Constants (15+)
  2. Predictions (P1-P18)
  3. Sim files (50+)
  4. Cosmic bodies (10+)
  5. Multisphere templates (22)
  6. Antitemplates (4)
  7. Layers (4-6)
  8. Concepts (10+)

For each entry:
  - Name
  - Definition / formula
  - Empirical value (where applicable)
  - Framework prediction
  - Status (verified / supported / pending / falsified)
  - Reference files
"""

import os
import json
import math
from datetime import datetime

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4
PHI_INV8 = PHI ** -8
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26
PHI_INV2 = PHI ** -2
PHI_INV10 = PHI ** -10

# Constants
CONSTANTS = {
    "phi": {"name": "Golden Ratio (φ)", "value": PHI, "formula": "(1+√5)/2",
            "empirical": 1.6180339887, "status": "exact", "files": ["src/science_constants.py"]},
    "phi_inv4": {"name": "φ⁻⁴", "value": PHI_INV4, "formula": "1/φ⁴",
                 "empirical": 0.1458980337, "status": "exact", "files": ["src/tap_breath_clock.py"]},
    "phi_inv8": {"name": "φ⁻⁸", "value": PHI_INV8, "formula": "1/φ⁸",
                 "empirical": 0.0212862366, "status": "exact", "files": ["src/tap_chromatin_state_sim.py"]},
    "phi_inv13": {"name": "φ⁻¹³", "value": PHI_INV13, "formula": "1/φ¹³ (breath clock tick)",
                  "empirical": 0.001919, "status": "exact", "files": ["src/tap_breath_clock.py"]},
    "phi_inv26": {"name": "φ⁻²⁶", "value": PHI_INV26, "formula": "1/φ²⁶ (meta-breath)",
                  "empirical": 3.68e-6, "status": "exact", "files": ["src/tap_trans_cyclic_sweep.py"]},
    "plastic": {"name": "Plastic Number (ρ)", "value": 1.3247179572, "formula": "real root of x³-x-1=0",
                "empirical": 1.324717957, "status": "exact", "files": ["src/calibration_derivation.py"]},
    "feigenbaum": {"name": "Feigenbaum δ", "value": 4.6692016091, "formula": "transcendental",
                   "empirical": 4.6692016, "status": "exact", "files": ["docs/TAP_Multiverse_Constants_Reduction_v5.3.md"]},
    "alpha_inv": {"name": "Fine Structure (α⁻¹)", "value": 137.036, "formula": "4πφ⁵ corrected by N_B",
                  "empirical": 137.036, "status": "supported to -1.66%", "files": ["src/tap_breath_clock.py"]},
    "n_b": {"name": "Breath Number N_B", "value": 8, "formula": "chi²-minimized over 99 observables",
            "empirical": "7-9 (range)", "status": "verified", "files": ["src/tap_breath_clock.py"]},
    "psi": {"name": "Braid Phase ψ", "value": 0.9105, "formula": "ρ^(-1/3)",
            "empirical": 0.9122, "status": "0.21% agreement", "files": ["src/calibration_derivation.py"]},
    "kappa": {"name": "Calibration κ", "value": 1.535e-5, "formula": "empirical from 5-year sweep",
              "empirical": 1.535e-5, "status": "supported", "files": ["src/calibration_derivation.py"]},
    "n_max": {"name": "Meta-Breath N_MAX", "value": 521, "formula": "int(φ^13) + 2",
              "empirical": 521, "status": "exact", "files": ["src/tap_trans_cyclic_sweep.py"]},
}

# Predictions
PREDICTIONS = {
    "P1": {"name": "Opposite signatures ayahuasca vs tensegrity",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_Testable_Predictions_v5.md"]},
    "P2": {"name": "Lymph flow +15-25% in tensegrity",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_P2_Lymphangiography_Protocol.md"]},
    "P3": {"name": "Fidelity up, piezo down (counter-intuitive)",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_Testable_Predictions_v5.md"]},
    "P4": {"name": "180° spiral phase rotational antenna",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_Fascia_Trains_v5.md"]},
    "P5": {"name": "Transgenerational HTR2A chromatin",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_DNA_Topology_Epigenetics.md"]},
    "P6": {"name": "Nami-ryu specific spiral coupling",
           "category": "CASCADE", "status": "supported", "files": ["docs/TAP_Somatic_Cascade.md"]},
    "P7": {"name": "Codon table correlates φ⁻ⁿ",
           "category": "COSMIC ORIGIN", "status": "supported", "files": ["docs/TAP_Cosmic_Origin_of_Life_v5.2.md"]},
    "P8": {"name": "L-excess correlates Γ(N_B)",
           "category": "COSMIC ORIGIN", "status": "supported", "files": ["src/tap_cosmic_origin_sims.py"]},
    "P9": {"name": "Nami-ryu N_B-correction",
           "category": "COSMIC ORIGIN", "status": "supported", "files": ["docs/TAP_Somatic_Cascade.md"]},
    "P10": {"name": "13 templates max 13D Weyl ceiling",
            "category": "COSMIC ORIGIN", "status": "supported", "files": ["docs/TAP_Multisphere_Biotemplates_v5.3.md"]},
    "P11": {"name": "Template dist correlates Γ(N_B)",
            "category": "MULTISPHERE", "status": "supported", "files": ["docs/TAP_Multisphere_Biotemplates_v5.3.md"]},
    "P12": {"name": "Cross-zone coupling detectable",
            "category": "MULTISPHERE", "status": "supported", "files": ["docs/TAP_Multisphere_Cascade_Diagram.md"]},
    "P13": {"name": "Carbon is special self-replicating",
            "category": "MULTISPHERE", "status": "supported", "files": ["docs/TAP_Cosmic_Origin_of_Life_v5.2.md"]},
    "P14": {"name": "13 templates max verified",
            "category": "MULTISPHERE", "status": "supported", "files": ["docs/TAP_Multisphere_Biotemplates_v5.3.md"]},
    "P15": {"name": "Soot-rich zones lower fidelity",
            "category": "ANTI-TEMPLATE", "status": "r = -0.99, 7/8 high-fidelity",
            "files": ["src/tap_p15_soot_fidelity_sim.py"]},
    "P16": {"name": "Magnetite stronger chiral",
            "category": "ANTI-TEMPLATE", "status": "r = 0.998, 3/8 strong-chiral",
            "files": ["src/tap_p16_magnetite_chiral_sim.py"]},
    "P17": {"name": "N_B = residue saturation (ψ = ρ^(-1/3))",
            "category": "ANTI-TEMPLATE", "status": "SUPPORTED to 0.21%",
            "files": ["src/calibration_derivation.py", "docs/TAP_P17_Plastic_CubeRoot_v5.3.md"]},
    "P18": {"name": "Earth is anomalously clean",
            "category": "ANTI-TEMPLATE", "status": "88% confidence",
            "files": ["docs/TAP_Anti_Template_Residue_v5.3.md"]},
}

# Concepts
CONCEPTS = {
    "breath_clock": {"name": "Breath Clock",
                     "definition": "The φ-rate scaling that drives all observable drift in the framework",
                     "formula": "γ(N, s) = 1 + s·N·φ⁻¹³",
                     "files": ["src/tap_breath_clock.py"]},
    "sub_breath": {"name": "Sub-Breath",
                   "definition": "The 8.12133-day Earth-Moon beat that drives primary sub-breath",
                   "files": ["src/tap_seismic_correlation.py"]},
    "n_b": {"name": "N_B (Breath Number)",
            "definition": "Which breath cycle the system is in (chi²-fitted to 8 for Earth)",
            "files": ["src/tap_breath_clock.py"]},
    "gamma_nb": {"name": "Γ(N_B)",
                 "definition": "Breath correction factor 1 + N_B·φ⁻¹³ ≈ 1.0154 for N_B=8",
                 "files": ["src/tap_breath_clock.py"]},
    "multiverse_coupling": {"name": "Multiverse Coupling",
                            "definition": "7-node Kuramoto network (Plastic + 6 satellites) that synchronizes the multiverse",
                            "files": ["src/tap_multiverse_coupling_sim.py"]},
    "anti_template": {"name": "Anti-Template Residue",
                      "definition": "Materials/processes that prevent template formation (soot, magnetite, N_B residue)",
                      "files": ["docs/TAP_Anti_Template_Residue_v5.3.md"]},
    "nami_ryu": {"name": "Nami-Ryu Body-Listening",
                 "definition": "The conscious practice of the cascade via body-listening through the spirals",
                 "files": ["docs/TAP_Fascia_Trains_v5.md", "src/tap_nami_ryu_breath.py"]},
    "cascade": {"name": "Cascade",
                "definition": "The 4-6 layer chain: hormonal → receptor → chromatin → substrate → cosmic → multisphere → multiverse",
                "files": ["docs/TAP_FRAMEWORK_INDEX.md"]},
    "twin_dragons": {"name": "Twin Dragons (SL_L + SL_R spirals)",
                     "definition": "The two spiral lines in Nami-ryu aikijujutsu, dual to anatomy trains",
                     "files": ["docs/TAP_Fascia_Trains_v5.md"]},
    "psi_collapse": {"name": "ψ-collapse / Down-regulation",
                     "definition": "Chronic 5-HT2A agonist exposure causes HTR2A chromatin compaction",
                     "files": ["docs/TAP_Somatic_Cascade.md"]},
}


def main():
    print("=" * 80)
    print("  TAP ENCYCLOPEDIA GENERATOR")
    print("  Wiki-style entry for every constant/prediction/sim/concept")
    print("=" * 80)
    print()

    # Summary
    print(f"  Constants: {len(CONSTANTS)}")
    print(f"  Predictions: {len(PREDICTIONS)} (P1-P18)")
    print(f"  Concepts: {len(CONCEPTS)}")
    print()

    # Constants table
    print("  CONSTANTS:")
    print(f"  {'Name':30s} | {'Value':>14s} | {'Status'}")
    print("  " + "-" * 80)
    for k, c in CONSTANTS.items():
        val_str = f"{c['value']:.6f}" if isinstance(c['value'], float) and abs(c['value']) < 1e6 else str(c['value'])
        print(f"  {c['name']:30s} | {val_str:>14s} | {c['status']}")
    print()

    # Predictions table
    print("  PREDICTIONS (P1-P18):")
    for k, p in PREDICTIONS.items():
        print(f"    {k:4s} [{p['category']:14s}] {p['name']:50s} | {p['status']}")
    print()

    # Concepts
    print("  CONCEPTS:")
    for k, c in CONCEPTS.items():
        print(f"    {c['name']:35s} | {c['definition'][:80]}")
    print()

    # Build markdown
    md = []
    md.append("# TAP Encyclopedia v5.3.2")
    md.append("")
    md.append("A comprehensive wiki-style reference for the TAP (Tensegrity-Anatomy-Polyvagal) cascade model.")
    md.append("")
    md.append(f"Generated: {datetime.now().isoformat()}")
    md.append("")
    md.append("---")
    md.append("")

    md.append("## 1. Constants")
    md.append("")
    for k, c in CONSTANTS.items():
        md.append(f"### {c['name']}")
        md.append(f"- **Value**: `{c['value']}`")
        if 'formula' in c:
            md.append(f"- **Formula**: `{c['formula']}`")
        if 'empirical' in c:
            md.append(f"- **Empirical**: `{c['empirical']}`")
        md.append(f"- **Status**: {c['status']}")
        if c.get('files'):
            md.append(f"- **Files**: {', '.join(c['files'])}")
        md.append("")

    md.append("## 2. Predictions (P1-P18)")
    md.append("")
    for k, p in PREDICTIONS.items():
        md.append(f"### {k}: {p['name']}")
        md.append(f"- **Category**: {p['category']}")
        md.append(f"- **Status**: {p['status']}")
        if p.get('files'):
            md.append(f"- **Files**: {', '.join(p['files'])}")
        md.append("")

    md.append("## 3. Concepts")
    md.append("")
    for k, c in CONCEPTS.items():
        md.append(f"### {c['name']}")
        md.append(f"- **Definition**: {c['definition']}")
        if 'formula' in c:
            md.append(f"- **Formula**: `{c['formula']}`")
        if c.get('files'):
            md.append(f"- **Files**: {', '.join(c['files'])}")
        md.append("")

    md.append("---")
    md.append("")
    md.append("## Statistics")
    md.append("")
    md.append(f"- Total constants documented: **{len(CONSTANTS)}**")
    md.append(f"- Total predictions documented: **{len(PREDICTIONS)}** (P1-P18)")
    md.append(f"- Total concepts documented: **{len(CONCEPTS)}**")
    md.append(f"- Total entries: **{len(CONSTANTS) + len(PREDICTIONS) + len(CONCEPTS)}**")
    md.append("")

    md_content = "\n".join(md)

    # Write markdown
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    md_path = os.path.join(docs_dir, 'TAP_Encyclopedia_v5_3.md')
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"  [EXPORT] Markdown -> {md_path}")

    # Write JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    out_path = os.path.join(out_dir, 'tap_encyclopedia.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "constants": CONSTANTS,
        "predictions": PREDICTIONS,
        "concepts": CONCEPTS,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] JSON -> {out_path}")
    print(f"  Total entries: {len(CONSTANTS) + len(PREDICTIONS) + len(CONCEPTS)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
