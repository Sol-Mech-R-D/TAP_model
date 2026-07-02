# -*- coding: utf-8 -*-
"""
render_mermaid_diagrams.py
==========================
Generate PNG renderings of the multisphere cascade diagrams
for the v5 paper (and any other documentation).

Since mermaid-cli requires Node.js + Chrome (heavy), and
graphviz is not always available, this script uses matplotlib
to produce publication-quality PNG figures.

The output PNGs are saved to `assets/tap_diagrams_*.png`.

Diagrams generated:
  1. multisphere_cascade — 22 templates across 4 zones
  2. cascade_flow — Bounce → Max Expansion flow
  3. cascade_architecture — 6-layer φ-rate stack
  4. anti_template_contamination — cycle contamination
  5. predictions_summary — P1-P18 testable predictions
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch

OUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../assets"
)
os.makedirs(OUT_DIR, exist_ok=True)

# Colors
COLORS = {
    "bg": "#0a0a14",
    "fg": "#e0e0e8",
    "hot": "#ff6b6b",
    "warm": "#ffa94d",
    "temperate": "#69db7c",
    "cold": "#4dabf7",
    "organic": "#ffd43b",
    "hybrid": "#cc5de8",
    "inorganic": "#adb5bd",
    "antitemplate": "#ff006e",
    "cosmic": "#ff6b6b",
    "substrate": "#adb5bd",
    "phi_layer": ["#ffd43b", "#69db7c", "#4dabf7", "#cc5de8", "#ff6b6b", "#ff006e"],
}


def style_axes(ax):
    """Apply dark background styling to axes."""
    ax.set_facecolor(COLORS["bg"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_box(ax, x, y, w, h, text, color, fontcolor="#000", fontsize=9,
             fontweight="bold"):
    """Draw a rounded box with text."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        facecolor=color, edgecolor="#000", linewidth=1.5, alpha=0.85
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight,
            color=fontcolor, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, color="#69db7c", lw=1.5,
               style="->", ls="-"):
    """Draw an arrow between two points."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, color=color, linewidth=lw,
        linestyle=ls, mutation_scale=15
    )
    ax.add_patch(arrow)


def render_multisphere_cascade():
    """Render the 22 templates across 4 zones diagram."""
    fig, ax = plt.subplots(figsize=(18, 12))
    fig.patch.set_facecolor(COLORS["bg"])
    style_axes(ax)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_title(
        "TAP Multisphere — 22 Biological Templates Across 4 Cosmic Zones",
        color=COLORS["fg"], fontsize=18, fontweight="bold", pad=20
    )

    # Breath clock at top
    draw_box(ax, 7, 10.5, 4, 1, "BREATH CLOCK\nN_B ≈ 7-9 (N_CYCLES)",
             COLORS["temperate"], "#000", 11, "bold")

    # 4 zones
    zones = [
        (0.5, 6, "ZONE 1: HOT\nT=500-5000K", COLORS["hot"], [
            "Dusty Plasma\n5000K",
            "Lanthanide\n2000K",
            "SiC\n1500K",
            "BN Tubes\n1200K",
            "BCN\n900K",
        ]),
        (5, 6, "ZONE 2: WARM\nT=250-750K", COLORS["warm"], [
            "Thioester\n300K",
            "Ge-Sn\n320K",
            "Fe-S\n400K",
            "Organosilicon\n400K",
            "Siloxane\n450K",
            "Carborane\n550K",
        ]),
        (9.5, 6, "ZONE 3: TEMPERATE\nT=100-300K ★", COLORS["temperate"], [
            "★ Carbon DNA\n150K",
            "PNA\n180K",
            "Quadruplet\n150K",
            "Metallo-Nuc\n200K",
            "Se-DNA\n200K",
            "Germoxane\n200K",
            "Phosphazene\n220K",
        ]),
        (14, 6, "ZONE 4: COLD\nT=0.5-220K", COLORS["cold"], [
            "Superfluid\n3K",
            "Polythiazyl\n8K",
            "PTFE\n120K",
            "Phosphaalkene\n130K",
        ]),
    ]

    for x, y, title, color, templates in zones:
        # Zone title
        draw_box(ax, x, y + len(templates) * 0.5 + 0.5,
                 3.5, 0.7, title, color, "#000", 10, "bold")
        # Templates
        for i, t in enumerate(templates):
            y_t = y + (len(templates) - i - 1) * 0.5
            tcolor = COLORS["organic"] if "★" in t or "Carbon" in t else \
                     COLORS["hybrid"] if any(s in t for s in
                     ["Fe-S", "Germoxane", "PTFE", "Phosphaalkene",
                      "Organosilicon", "Se-DNA", "BCN", "Carborane"]) else \
                     COLORS["inorganic"]
            tcolor_text = "#000" if tcolor != COLORS["inorganic"] else "#000"
            draw_box(ax, x, y_t, 3.5, 0.45, t, tcolor, tcolor_text, 8)

    # Anti-template box at bottom
    draw_box(ax, 7, 2, 4, 1, "ANTI-TEMPLATES\nsoot, magnetite, L-D, glass",
             COLORS["antitemplate"], "#fff", 10, "bold")

    # Lines from breath clock to zones
    for x, y, _, _, _ in zones:
        draw_arrow(ax, 9, 10.5, x + 1.75, 6 + 5 * 0.5 + 1.2,
                   color=COLORS["temperate"], lw=1)

    # Lines from anti-templates to zones
    for x, y, _, _, _ in zones:
        draw_arrow(ax, 9, 3, x + 1.75, 6,
                   color=COLORS["antitemplate"], lw=1, ls="--")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "tap_diagrams_multisphere.png")
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"  [RENDER] multisphere_cascade -> {out}")
    return out


def render_cascade_flow():
    """Render the Bounce → Max Expansion cascade flow."""
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor(COLORS["bg"])
    style_axes(ax)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.set_title("Bounce → Max Expansion Cascade Flow",
                 color=COLORS["fg"], fontsize=16, fontweight="bold", pad=20)

    steps = [
        (1, "BOUNCHE", "a=0.05", "5/22 active", COLORS["hot"]),
        (4, "STEP 5", "a=0.189", "0/22 active\n(sterile)", "#666"),
        (7, "STEP 10", "a=0.525", "0/22 active\n(sterile)", "#666"),
        (10, "STEP 15", "a=0.861", "15/22 active", COLORS["temperate"]),
        (13, "MAX EXPANSION", "a=1.0", "17/22 active ★", COLORS["organic"]),
    ]

    for i, (x, title, scale, n_active, color) in enumerate(steps):
        # Step circle
        draw_box(ax, x, 4, 2, 2, f"{title}\n\n{scale}\n{n_active}",
                 color, "#000" if color != "#666" else "#fff", 9, "bold")
        # Arrow to next step
        if i < len(steps) - 1:
            draw_arrow(ax, x + 2.1, 5, steps[i+1][0] - 0.1, 5,
                       color=COLORS["temperate"], lw=2)

    # Reset arrow at bottom
    draw_box(ax, 5, 1, 6, 1, "RESET (Inhale)\nanti-templates accumulate",
             COLORS["antitemplate"], "#fff", 11, "bold")
    draw_arrow(ax, 14, 4, 11, 2, color=COLORS["antitemplate"], lw=2, ls="--")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "tap_diagrams_cascade_flow.png")
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"  [RENDER] cascade_flow -> {out}")
    return out


def render_cascade_architecture():
    """Render the 6-layer φ-rate cascade architecture."""
    fig, ax = plt.subplots(figsize=(12, 14))
    fig.patch.set_facecolor(COLORS["bg"])
    style_axes(ax)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.set_title("TAP Cascade Architecture — 6 φ-Rate Layers",
                 color=COLORS["fg"], fontsize=16, fontweight="bold", pad=20)

    layers = [
        (10, "φ⁻² HORMONAL (hours)", "parent sim, 5-HT2A chem",
         COLORS["phi_layer"][0], 1.0),
        (8.3, "φ⁻⁴ SIGNALING (minutes)", "5-HT2A binding, piezo, solar",
         COLORS["phi_layer"][1], 1.2),
        (6.6, "φ⁻⁸ RECEPTOR (days)", "sensitivity_setpoint, BDNF",
         COLORS["phi_layer"][2], 1.0),
        (4.9, "φ⁻¹⁰ CHROMATIN (weeks)", "HTR2A/NR3C1, s_setpoint",
         COLORS["phi_layer"][3], 1.2),
        (3.2, "φ⁻¹³ COSMIC (years)", "N_B, Γ(N_B), breath clock",
         COLORS["phi_layer"][4], 1.0),
        (1.5, "φ⁻¹⁶⁺ MULTISPHERE", "22 templates, 4 zones, anti-templates",
         COLORS["phi_layer"][5], 1.2),
    ]

    for y, title, desc, color, h in layers:
        draw_box(ax, 2, y, 8, h, f"{title}\n\n{desc}", color, "#000", 11,
                 "bold")
        # Down arrow
        if y > 1.5:
            draw_arrow(ax, 6, y, 6, y - 0.3, color="#fff", lw=1.5)

    # Substrate (parallel at all timescales)
    draw_box(ax, 0.5, 0.2, 1.5, 13, "braid\nSUBSTRATE\n(parallel)",
             COLORS["substrate"], "#000", 9, "bold")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "tap_diagrams_architecture.png")
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"  [RENDER] cascade_architecture -> {out}")
    return out


def render_anti_template_contamination():
    """Render the anti-template contamination cycle."""
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor(COLORS["bg"])
    style_axes(ax)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_title("Anti-Template Contamination Cycle (v5.3)",
                 color=COLORS["fg"], fontsize=16, fontweight="bold", pad=20)

    # 4 stages in a 2x2 grid
    stages = [
        (1, 7, "MAX EXPANSION\nT=120K\nDNA: 1.0\nSoot: 0.26\nEM: 0.98\nHelix: 1.0",
         COLORS["temperate"]),
        (8, 7, "MID-CONTRACTION\nT=150K\nDNA: 1.0\nSoot: 0.50\nEM: 0.74\nHelix: 1.0",
         COLORS["warm"]),
        (1, 2, "CRITICAL\nT=182K\nDNA: 0.56\nSoot: 0.98\nEM: 0.55\nHelix: 0.79\nRACEMIZATION",
         COLORS["hot"]),
        (8, 2, "RESET\nT=200K\nDNA: 0.0\nSoot: 4.94\nEM: 0.13\nHelix: 0.07\nDIRTY",
         COLORS["antitemplate"]),
    ]

    for x, y, text, color in stages:
        textcolor = "#000" if color != COLORS["antitemplate"] else "#fff"
        draw_box(ax, x, y, 5, 2.5, text, color, textcolor, 9, "bold")

    # Arrows: Max → Mid → Critical → Reset → (loop back)
    draw_arrow(ax, 6, 8, 8, 8, color=COLORS["warm"], lw=2)
    draw_arrow(ax, 8, 6, 6, 4, color=COLORS["hot"], lw=2)
    draw_arrow(ax, 6, 3, 8, 3, color=COLORS["antitemplate"], lw=2)
    draw_arrow(ax, 10.5, 2, 10.5, 0.7, color=COLORS["antitemplate"], lw=2,
               ls="--")
    draw_arrow(ax, 10.5, 0.5, 3, 0.5, color=COLORS["antitemplate"], lw=2,
               ls="--")
    draw_arrow(ax, 3, 0.7, 3, 7, color=COLORS["temperate"], lw=2, ls="--")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "tap_diagrams_anti_template.png")
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"  [RENDER] anti_template_contamination -> {out}")
    return out


def render_predictions_summary():
    """Render the P1-P18 testable predictions summary."""
    fig, ax = plt.subplots(figsize=(16, 12))
    fig.patch.set_facecolor(COLORS["bg"])
    style_axes(ax)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_title("TAP Testable Predictions — P1 to P18",
                 color=COLORS["fg"], fontsize=16, fontweight="bold", pad=20)

    categories = [
        (1, 8, "CASCADE P1-P6", [
            ("P1", "opposite signatures\nayahuasca vs tensegrity"),
            ("P2", "lymph flow +15-25%\nin tensegrity"),
            ("P3", "fidelity up, piezo down\n(counter-intuitive)"),
            ("P4", "180° spiral phase\nrotational antenna"),
            ("P5", "transgenerational\nHTR2A chromatin"),
            ("P6", "Nami-ryu specific\nspiral coupling"),
        ], COLORS["temperate"]),
        (5, 8, "COSMIC ORIGIN P7-P10", [
            ("P7", "codon table\ncorrelates φ⁻ⁿ"),
            ("P8", "L-excess\ncorrelates Γ(N_B)"),
            ("P9", "Nami-ryu\nN_B-correction"),
            ("P10", "13 templates max\n13D Weyl ceiling"),
        ], COLORS["hot"]),
        (9, 8, "MULTISPHERE P11-P14", [
            ("P11", "template dist\ncorrelates Γ(N_B)"),
            ("P12", "cross-zone coupling\ndetectable"),
            ("P13", "carbon is special\nself-replicating"),
            ("P14", "13 templates max\nverified"),
        ], COLORS["warm"]),
        (1, 3, "ANTI-TEMPLATE P15-P18", [
            ("P15", "soot-rich zones\nlower fidelity"),
            ("P16", "magnetite\nstronger chiral"),
            ("P17", "N_B = residue\nsaturation"),
            ("P18", "Earth is\nanomalously clean"),
        ], COLORS["antitemplate"]),
    ]

    for x, y, title, predictions, color in categories:
        # Category title
        draw_box(ax, x, y + 0.5, 6, 0.8, title, color, "#000", 12, "bold")
        # Predictions
        for i, (pname, pdesc) in enumerate(predictions):
            yp = y - (i + 1) * 0.85
            pcolor = "#1a1a2a" if color == COLORS["antitemplate"] else \
                     COLORS["bg"]
            ptextcolor = COLORS["fg"]
            draw_box(ax, x, yp, 1.0, 0.7, pname, color, "#000", 11, "bold")
            draw_box(ax, x + 1.1, yp, 4.9, 0.7, pdesc, pcolor, ptextcolor,
                     8, "normal")

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "tap_diagrams_predictions.png")
    plt.savefig(out, dpi=120, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close()
    print(f"  [RENDER] predictions_summary -> {out}")
    return out


def main():
    print("=" * 80)
    print("  TAP Mermaid Diagram PNG Renderer")
    print("=" * 80)
    print()
    render_multisphere_cascade()
    render_cascade_flow()
    render_cascade_architecture()
    render_anti_template_contamination()
    render_predictions_summary()
    print()
    print(f"  All PNG diagrams saved to: {OUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
