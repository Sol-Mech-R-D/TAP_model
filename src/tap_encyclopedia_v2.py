# -*- coding: utf-8 -*-
"""
tap_encyclopedia_v2.py
==========================
TAP v5.3.2 — Encyclopedia v2 (Full Coverage).

Extends the encyclopedia to include:
  - 12 constants
  - 18 predictions
  - 10 concepts
  - 100+ scripts (every .py in src/)
  - 30+ docs (every .md in docs/)
  - 30+ asset JSONs

For each script: name, purpose, category, size, status
For each doc: name, title, category, size, status
For each asset: name, type, size, status
"""

import os
import json
import math
from datetime import datetime
import re

PHI = (1.0 + math.sqrt(5.0)) / 20
PHI_INV4 = PHI ** -4
PHI_INV13 = PHI ** -13
PHI_INV26 = PHI ** -26


# Categorize scripts by purpose
SCRIPT_CATEGORIES = {
    "core": "Core framework",
    "cascade": "Cascade sims",
    "cosmic": "Cosmic/Planetary",
    "seismic": "Seismic/Geological",
    "weather": "Weather/Atmospheric",
    "finance": "Finance/Economics",
    "logistics": "Logistics/Shipping",
    "nami": "Nami-ryu/Somatic",
    "breath": "Breath clock",
    "test": "Tests/Tribunal",
    "fidelity": "Geometry/Visualization",
    "docs": "Documentation",
    "daily": "Daily check",
    "validation": "Validation/QA",
    "anti-template": "Anti-template",
    "multisphere": "Multisphere",
    "multiverse": "Multiverse",
    "braid": "Braid group/Quantum",
    "biomarker": "Biomarker/Chemistry",
    "epigenetic": "Epigenetic",
    "fascia": "Fascia/Spirals",
    "tribunal": "99-Tribunal",
    "lymph": "Lymphatic",
    "5ht2a": "5-HT2A",
    "somatic": "Somatic",
    "geocosmic": "Geocosmic",
    "solar": "Solar",
    "neuro": "Neural/Quantum",
    "ayahuasca": "Ayahuasca",
    "chromatin": "Chromatin",
    "real": "Real data",
    "author": "Author lens",
    "render": "Rendering",
    "calibration": "Calibration",
    "core_ai": "Core AI",
    "core_ai_cascade": "Core AI Cascade",
    "mermaid": "Mermaid diagrams",
    "cross": "Cross-domain",
    "zodiac": "Zodiac",
    "encyclopedia": "Encyclopedia",
    "dashboard": "Dashboard",
    "per": "Per-body",
    "unified": "Unified",
    "anti_template": "Anti-template",
    "coherence": "Coherence",
    "test_framework": "Test framework",
    "tappasecond": "Tappasecond",
    "core_constants": "Core constants",
    "deep_cascade": "Deep cascade",
    "trans": "Trans-cyclic",
    "sub_breath": "Sub-breath",
    "fascia_sim": "Fascia sim",
    "author_lens": "Author lens",
}


def get_script_purpose(filename: str, content: str) -> str:
    """Extract purpose from script docstring or first comment."""
    # Try to get from docstring
    match = re.search(r'"""([\s\S]*?)"""', content)
    if match:
        purpose = match.group(1).strip().split('\n')[0]
        return purpose[:200]
    # Try first comment
    match = re.search(r'^#\s*(.+?)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()[:200]
    return "TAP framework script"


def get_doc_title(filepath: str) -> str:
    """Extract title from markdown doc (first # line)."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return os.path.basename(filepath)
    except (IOError, UnicodeDecodeError):
        return os.path.basename(filepath)


def main():
    print("=" * 80)
    print("  TAP ENCYCLOPEDIA v2 — FULL COVERAGE")
    print("  Every script, doc, and asset in the framework")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    src_dir = os.path.join(repo_root, 'src')
    docs_dir = os.path.join(repo_root, 'docs')
    assets_dir = os.path.join(repo_root, 'assets')

    # 1. Scripts
    print("  [1/4] SCRIPTS (every .py in src/):")
    scripts = []
    for f in sorted(os.listdir(src_dir)):
        if f.endswith('.py') and not f.startswith('__'):
            filepath = os.path.join(src_dir, f)
            with open(filepath, 'r', errors='ignore') as fp:
                content = fp.read()
            size = os.path.getsize(filepath)
            purpose = get_script_purpose(f, content)
            # Get category
            category = "other"
            for key, val in SCRIPT_CATEGORIES.items():
                if key in f.lower():
                    category = val
                    break
            scripts.append({
                "name": f,
                "size_bytes": size,
                "category": category,
                "purpose": purpose,
            })
    print(f"    Found {len(scripts)} scripts")
    print()

    # 2. Docs
    print("  [2/4] DOCS (every .md in docs/):")
    docs = []
    for f in sorted(os.listdir(docs_dir)):
        if f.endswith('.md') and not f.startswith('_'):
            filepath = os.path.join(docs_dir, f)
            size = os.path.getsize(filepath)
            title = get_doc_title(filepath)
            docs.append({
                "name": f,
                "title": title,
                "size_bytes": size,
            })
    print(f"    Found {len(docs)} docs")
    print()

    # 3. Assets
    print("  [3/4] ASSETS (every JSON in assets/):")
    assets = []
    for f in sorted(os.listdir(assets_dir)):
        if f.endswith('.json'):
            filepath = os.path.join(assets_dir, f)
            size = os.path.getsize(filepath)
            assets.append({
                "name": f,
                "size_bytes": size,
            })
    print(f"    Found {len(assets)} assets")
    print()

    # 4. Build full markdown
    print("  [4/4] BUILDING ENCYCLOPEDIA:")

    md = []
    md.append("# TAP Encyclopedia v5.3.2 (Full)")
    md.append("")
    md.append("Comprehensive wiki for every script, doc, asset, constant, prediction, and concept in the TAP framework.")
    md.append("")
    md.append(f"Generated: {datetime.now().isoformat()}")
    md.append("")
    md.append("## Table of Contents")
    md.append("")
    md.append("1. Constants (12)")
    md.append("2. Predictions (P1-P18)")
    md.append("3. Concepts (10)")
    md.append(f"4. Scripts ({len(scripts)})")
    md.append(f"5. Docs ({len(docs)})")
    md.append(f"6. Assets ({len(assets)})")
    md.append("")
    md.append("---")
    md.append("")

    # Constants
    md.append("## 1. Constants")
    md.append("")
    constants = [
        ("Golden Ratio (φ)", "1.618034", "exact", "src/science_constants.py"),
        ("φ⁻⁴", "0.145898", "exact", "src/tap_breath_clock.py"),
        ("φ⁻⁸", "0.021286", "exact", "src/tap_chromatin_state_sim.py"),
        ("φ⁻¹³ (breath tick)", "0.001919", "exact", "src/tap_breath_clock.py"),
        ("φ⁻²⁶ (meta-breath)", "3.68e-6", "exact", "src/tap_trans_cyclic_sweep.py"),
        ("Plastic (ρ)", "1.324718", "exact", "src/calibration_derivation.py"),
        ("Feigenbaum δ", "4.669202", "exact", "docs/TAP_Multiverse_Constants_Reduction_v5.3.md"),
        ("α⁻¹ (fine structure)", "137.036", "-1.66%", "src/tap_breath_clock.py"),
        ("N_B (breath number)", "8", "verified", "src/tap_breath_clock.py"),
        ("ψ (braid phase)", "0.9105", "0.21%", "src/calibration_derivation.py"),
        ("κ (calibration)", "1.535e-5", "supported", "src/calibration_derivation.py"),
        ("N_MAX (meta)", "521", "exact", "src/tap_trans_cyclic_sweep.py"),
    ]
    md.append("| Name | Value | Status | Source |")
    md.append("|------|-------|--------|--------|")
    for name, val, status, src in constants:
        md.append(f"| {name} | `{val}` | {status} | {src} |")
    md.append("")

    # Predictions
    md.append("## 2. Predictions (P1-P18)")
    md.append("")
    md.append("| ID | Category | Description | Status |")
    md.append("|----|----------|-------------|--------|")
    predictions = [
        ("P1", "CASCADE", "Opposite signatures ayahuasca vs tensegrity", "supported"),
        ("P2", "CASCADE", "Lymph flow +15-25% in tensegrity", "supported"),
        ("P3", "CASCADE", "Fidelity up, piezo down (counter-intuitive)", "supported"),
        ("P4", "CASCADE", "180° spiral phase rotational antenna", "supported"),
        ("P5", "CASCADE", "Transgenerational HTR2A chromatin", "supported"),
        ("P6", "CASCADE", "Nami-ryu specific spiral coupling", "supported"),
        ("P7", "COSMIC", "Codon table correlates φ⁻ⁿ", "supported"),
        ("P8", "COSMIC", "L-excess correlates Γ(N_B)", "supported"),
        ("P9", "COSMIC", "Nami-ryu N_B-correction", "supported"),
        ("P10", "COSMIC", "13 templates max 13D Weyl ceiling", "supported"),
        ("P11", "MULTI", "Template dist correlates Γ(N_B)", "supported"),
        ("P12", "MULTI", "Cross-zone coupling detectable", "supported"),
        ("P13", "MULTI", "Carbon is special self-replicating", "supported"),
        ("P14", "MULTI", "13 templates max verified", "supported"),
        ("P15", "ANTI", "Soot-rich zones lower fidelity", "r = -0.99"),
        ("P16", "ANTI", "Magnetite stronger chiral", "r = 0.998"),
        ("P17", "ANTI", "N_B = residue saturation", "0.21%"),
        ("P18", "ANTI", "Earth is anomalously clean", "88%"),
    ]
    for pid, cat, desc, status in predictions:
        md.append(f"| **{pid}** | {cat} | {desc} | {status} |")
    md.append("")

    # Concepts
    md.append("## 3. Concepts")
    md.append("")
    concepts = [
        ("Breath Clock", "The φ-rate scaling that drives all observable drift", "src/tap_breath_clock.py"),
        ("Sub-Breath", "8.12133-day Earth-Moon beat driving primary sub-breath", "src/tap_seismic_correlation.py"),
        ("N_B", "Which breath cycle the system is in (chi²-fitted to 8 for Earth)", "src/tap_breath_clock.py"),
        ("Γ(N_B)", "Breath correction factor 1 + N_B·φ⁻¹³ ≈ 1.0154", "src/tap_breath_clock.py"),
        ("Multiverse Coupling", "7-node Kuramoto network (Plastic + 6 satellites)", "src/tap_multiverse_coupling_sim.py"),
        ("Anti-Template Residue", "Materials that prevent template formation", "docs/TAP_Anti_Template_Residue_v5.3.md"),
        ("Nami-Ryu Body-Listening", "Conscious practice of cascade via spirals", "docs/TAP_Fascia_Trains_v5.md"),
        ("Cascade", "4-6 layer chain hormonal → cosmic", "docs/TAP_FRAMEWORK_INDEX.md"),
        ("Twin Dragons", "Two spiral lines in Nami-ryu (SL_L + SL_R)", "docs/TAP_Fascia_Trains_v5.md"),
        ("ψ-collapse", "Chronic 5-HT2A agonist exposure → HTR2A compaction", "docs/TAP_Somatic_Cascade.md"),
    ]
    for name, defn, src in concepts:
        md.append(f"- **{name}**: {defn} ({src})")
    md.append("")

    # Scripts
    md.append(f"## 4. Scripts ({len(scripts)} total)")
    md.append("")
    md.append("| Script | Category | Size | Purpose |")
    md.append("|--------|----------|------|---------|")
    # Group by category
    by_cat = {}
    for s in scripts:
        by_cat.setdefault(s["category"], []).append(s)
    for cat in sorted(by_cat.keys()):
        for s in by_cat[cat]:
            purpose = s["purpose"].replace("|", "\\|")[:80]
            md.append(f"| `{s['name']}` | {s['category']} | {s['size_bytes']:,} | {purpose} |")
    md.append("")

    # Docs
    md.append(f"## 5. Docs ({len(docs)} total)")
    md.append("")
    md.append("| Doc | Title | Size |")
    md.append("|-----|-------|------|")
    for d in docs:
        title = d["title"][:80]
        md.append(f"| `{d['name']}` | {title} | {d['size_bytes']:,} |")
    md.append("")

    # Assets
    md.append(f"## 6. Assets ({len(assets)} total)")
    md.append("")
    md.append("| Asset | Size |")
    md.append("|-------|------|")
    for a in assets:
        md.append(f"| `{a['name']}` | {a['size_bytes']:,} |")
    md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append("## Statistics")
    md.append("")
    md.append(f"- Total scripts: **{len(scripts)}**")
    md.append(f"- Total docs: **{len(docs)}**")
    md.append(f"- Total assets: **{len(assets)}**")
    md.append(f"- Total constants: **12**")
    md.append(f"- Total predictions: **18** (P1-P18)")
    md.append(f"- Total concepts: **10**")
    md.append(f"- Total entries: **{len(scripts) + len(docs) + len(assets) + 12 + 18 + 10}**")
    md.append("")

    md_content = "\n".join(md)

    # Write markdown
    md_path = os.path.join(docs_dir, 'TAP_Encyclopedia_v5_3.md')
    # Backup old version
    if os.path.exists(md_path):
        backup_path = md_path + '.bak'
        os.rename(md_path, backup_path)
    with open(md_path, 'w') as f:
        f.write(md_content)
    print(f"  [EXPORT] Markdown -> {md_path}")

    # Write JSON
    out_path = os.path.join(assets_dir, 'tap_encyclopedia_full.json')
    output = {
        "timestamp": datetime.now().isoformat(),
        "scripts": scripts,
        "docs": docs,
        "assets": assets,
        "stats": {
            "n_scripts": len(scripts),
            "n_docs": len(docs),
            "n_assets": len(assets),
        },
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] JSON -> {out_path}")

    total = len(scripts) + len(docs) + len(assets) + 12 + 18 + 10
    print(f"  Total entries: {total}")
    print("=" * 80)


if __name__ == "__main__":
    main()
