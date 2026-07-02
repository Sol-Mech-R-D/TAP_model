# -*- coding: utf-8 -*-
"""
tap_cascade_context.py
=======================
TAP Model — Cascade Context Registry

Maps every sim in the TAP framework to its cascade layer,
phi-rate, and connection to the broader framework.

Each sim that wants to register with the cascade can call:

    from tap_cascade_context import register_cascade_context
    register_cascade_context(__file__, layer='chromatin',
                              phi_rate='phi^-10',
                              description='...')

The framework's master validation script, the author lens,
and the peer-review checklist all use this registry to
verify that every sim is connected to the cascade.

This module is a passthrough — it doesn't import the sims
themselves (which would create circular imports), it just
records their declared context.
"""

import os
import json
from typing import Dict, Optional

LAYERS = {
    'hormonal':     'phi^-2  (hours)',
    'signaling':    'phi^-4  (minutes)',
    'receptor':     'phi^-8  (days)',
    'chromatin':    'phi^-10 (weeks)',
    'substrate':    'braid   (sub-second to years)',
    'cosmic':       'phi^-13 (years)',
    'multisphere':  'phi^-16+ (cosmic)',
    'tool':         '— (no phi-rate)',
    'unknown':      '— (unregistered)',
}

_CASCADE_REGISTRY: Dict[str, Dict] = {}

# Manually-maintained sim-to-layer mapping
# Source: docs/TAP_FRAMEWORK_INDEX.md
SIM_CASCADE_MAP = {
    # Cascade (v3.0-v5.1, 15 sims)
    "tap_5ht2a_ayahuasca_sim.py": {
        "layer": "signaling+receptor",
        "phi_rate": "phi^-4, phi^-8",
        "category": "CASCADE",
        "description": "5-HT2A tolerance, Riba/Callaway fit"
    },
    "tap_5ht2a_epigenetic_coupling_sim.py": {
        "layer": "bidirectional",
        "phi_rate": "phi^-4 to phi^-10",
        "category": "CASCADE",
        "description": "5-HT2A ↔ parent sim, opposite directions"
    },
    "tap_ayahuasca_fascia_cascade_sim.py": {
        "layer": "all",
        "phi_rate": "phi^-4 to phi^-13",
        "category": "CASCADE",
        "description": "Full ayahuasca pathway, 7/7 PASS"
    },
    "tap_chromatin_state_sim.py": {
        "layer": "chromatin",
        "phi_rate": "phi^-10",
        "category": "CASCADE",
        "description": "233-bead genome, 6/6 biomarker match"
    },
    "tap_collagen_braiding_sim.py": {
        "layer": "substrate",
        "phi_rate": "braid",
        "category": "CASCADE",
        "description": "Anyonic qubit in collagen, 2x coherence"
    },
    "tap_coupled_ayahuasca_sim.py": {
        "layer": "bidirectional",
        "phi_rate": "phi^-4, phi^-8, phi^-10",
        "category": "CASCADE",
        "description": "DMT → 5-HT2A → chromatin pipeline"
    },
    "tap_epigenetic_cosmic_cascade.py": {
        "layer": "epigenetic → cosmic",
        "phi_rate": "phi^-10, phi^-13",
        "category": "CASCADE",
        "description": "End-to-end cascade, s_setpoint → breath"
    },
    "tap_epigenetic_flop_sim.py": {
        "layer": "hormonal + epigenetic",
        "phi_rate": "phi^-2, phi^-10",
        "category": "CASCADE",
        "description": "Parent sim, 30-day setpoint dynamics"
    },
    "tap_fascia_sim.py": {
        "layer": "substrate",
        "phi_rate": "phi^-8, phi^-10",
        "category": "CASCADE",
        "description": "12 trains, twin dragons, 4/4 PASS"
    },
    "tap_lymphatic_cascade_sim.py": {
        "layer": "epigenetic → lymph",
        "phi_rate": "phi^-2, phi^-10",
        "category": "CASCADE",
        "description": "Full lymphatic chain, 30d tensegrity"
    },
    "tap_real_data_validator.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "CASCADE",
        "description": "6/6 modelable biomarkers MATCH"
    },
    "tap_author_lens.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "CASCADE",
        "description": "Audit authors/sims against primitives"
    },
    "tap_breath_clock.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-13",
        "category": "CASCADE",
        "description": "N_B, Γ(N_B), previous cycles"
    },
    "tap_cosmic_breath_sim.py": {
        "layer": "cosmic + chem",
        "phi_rate": "phi^-13, phi^-2",
        "category": "CASCADE",
        "description": "Multi-scale cosmic+biological breath"
    },
    "tap_breath_clock_chem_mod.py": {
        "layer": "chem + cosmic",
        "phi_rate": "phi^-4, phi^-13",
        "category": "CASCADE",
        "description": "48-chem ODE modulated by breath"
    },
    # Cosmic origin / multisphere (v5.2-v5.3, 6 sims)
    "tap_multisphere_predictions.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-16+",
        "category": "MULTISPHERE",
        "description": "8 biotemplates across cosmic zones"
    },
    "tap_asynchronous_pulsation_sim.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-4, phi^-16+",
        "category": "MULTISPHERE",
        "description": "Pulsating domains, biotemplate deposition"
    },
    "tap_trans_cyclic_sweep.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-13, phi^-26",
        "category": "MULTISPHERE",
        "description": "Tier 2 & 3 cross-cycle drift"
    },
    "tap_super_tribunal_99.py": {
        "layer": "all",
        "phi_rate": "all",
        "category": "MULTISPHERE",
        "description": "99-hypotheses super tribunal"
    },
    "tap_standalone_cascade_tribunal.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-13",
        "category": "MULTISPHERE",
        "description": "CDCPU telemetry + 99 checks"
    },
    "tap_cosmic_origin_sims.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-4, phi^-10",
        "category": "MULTISPHERE",
        "description": "Weyl Chiral Spin-Pump, Seismo-Piezo, Fe-S Memory"
    },
    # Biochemistry / soliton (8 sims)
    "tap_somynence_48_sim.py": {
        "layer": "chem",
        "phi_rate": "phi^-2, phi^-4",
        "category": "BIOCHEM",
        "description": "48-chem ODE, salience+metabolic+autonomic"
    },
    "tap_biochem_qubit_graphene.py": {
        "layer": "biochem",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "Hormonal resonance, quartz qubit, graphene"
    },
    "tap_digital_soliton_sim.py": {
        "layer": "soliton",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "1D NLSE, RK4 solver"
    },
    "tap_device_coupled_soliton.py": {
        "layer": "soliton",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "NLSE + live CPU thermals/battery"
    },
    "tap_phone_minimal_soliton.py": {
        "layer": "soliton",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "6 hardware metrics coupled"
    },
    "tap_soliton_collision_stress.py": {
        "layer": "soliton",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "Two-soliton collision under CPU stress"
    },
    "tap_soliton_shielding_comparison.py": {
        "layer": "soliton",
        "phi_rate": "phi^-4",
        "category": "BIOCHEM",
        "description": "60s wave sim, shielded vs unshielded"
    },
    "tap_multidiscipline_sweep.py": {
        "layer": "tool",
        "phi_rate": "all",
        "category": "BIOCHEM",
        "description": "Unified diagnostics, Phinary ALU"
    },
    # Quantum / condensed matter (6 sims)
    "tap_qubit_coherence_sweep.py": {
        "layer": "qubit",
        "phi_rate": "phi^-4",
        "category": "QUANTUM",
        "description": "Room-T qubit, Fibonacci spacer"
    },
    "tap_quantum_decoherence.py": {
        "layer": "qubit",
        "phi_rate": "phi^-4",
        "category": "QUANTUM",
        "description": "Superconducting qubit, Tappasecond"
    },
    "tap_superconductivity_sweep.py": {
        "layer": "sc",
        "phi_rate": "phi^-4",
        "category": "QUANTUM",
        "description": "Twisted bilayer graphene Tc"
    },
    "tap_cosmic_quantum_neuro.py": {
        "layer": "cosmic + neuro",
        "phi_rate": "phi^-4, phi^-13",
        "category": "QUANTUM",
        "description": "Sun-Earth-Moon beat, phononic shield"
    },
    "tap_core_ai_cascade.py": {
        "layer": "cosmic + AI",
        "phi_rate": "phi^-4, phi^-13",
        "category": "QUANTUM",
        "description": "Planetary cores, AI energy coupling"
    },
    "tap_tappasecond.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-13",
        "category": "QUANTUM",
        "description": "Fundamental time unit"
    },
    # Social / neuro / population (8 sims)
    "tap_group_hysteria_sim.py": {
        "layer": "neuro",
        "phi_rate": "phi^-2, phi^-4",
        "category": "SOCIAL",
        "description": "10 agents, emotional contagion"
    },
    "tap_pair_bonding_sim.py": {
        "layer": "neuro",
        "phi_rate": "phi^-2",
        "category": "SOCIAL",
        "description": "Two coupled individuals, homeostatic"
    },
    "tap_muscle_memory_sim.py": {
        "layer": "neuro",
        "phi_rate": "phi^-4, phi^-8",
        "category": "SOCIAL",
        "description": "Chemical gating"
    },
    "tap_neural_resonance.py": {
        "layer": "neuro",
        "phi_rate": "phi^-4, phi^-8",
        "category": "SOCIAL",
        "description": "LIF neurons, Weyl mesh"
    },
    "tap_population_sweeps_sim.py": {
        "layer": "epi",
        "phi_rate": "phi^-4",
        "category": "SOCIAL",
        "description": "Compartmental dynamics, group sizes"
    },
    "tap_unified_social_sim.py": {
        "layer": "social",
        "phi_rate": "phi^-4",
        "category": "SOCIAL",
        "description": "18 States of Somynetics + Husk"
    },
    "tap_viral_epidemiology_sim.py": {
        "layer": "epi+fin",
        "phi_rate": "phi^-4",
        "category": "SOCIAL",
        "description": "Viral + financial volatility"
    },
    "tap_marketing_contagion_sim.py": {
        "layer": "social",
        "phi_rate": "phi^-4",
        "category": "SOCIAL",
        "description": "Memetic marketing"
    },
    # Geophysics / planetary (4 sims)
    "tap_solar_dynamo.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-4, phi^-13",
        "category": "GEOPHYSICS",
        "description": "CME probability, GIC stress"
    },
    "tap_seismic_correlation.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-4, phi^-13",
        "category": "GEOPHYSICS",
        "description": "M5.5+ quakes, sub-breath"
    },
    "tap_usgs_monitor.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-4, phi^-13",
        "category": "GEOPHYSICS",
        "description": "Real-time seismic + 8.1d sub-breath"
    },
    "tap_global_weather.py": {
        "layer": "cosmic",
        "phi_rate": "phi^-4, phi^-13",
        "category": "GEOPHYSICS",
        "description": "5 hubs, Open-Meteo API"
    },
    # Financial (1 sim)
    "tap_option_arbitrage.py": {
        "layer": "financial",
        "phi_rate": "phi^-4",
        "category": "FINANCIAL",
        "description": "TAP vs HNS option pricing"
    },
    # Tools / hardware / utilities (2 sims)
    "tap_audio_test.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "TOOL",
        "description": "Termux:API audio test"
    },
    "tap_proof.py": {
        "layer": "tool",
        "phi_rate": "all",
        "category": "TOOL",
        "description": "Full TAP cosmology proof"
    },
    "tap_cascade_context.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "TOOL",
        "description": "Cascade context registry (50+ sims, all categories)"
    },
    # Multisphere extensions (added in v5.3)
    "tap_cosmological_cascade_sweep.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-4, phi^-16+",
        "category": "MULTISPHERE",
        "description": "22 templates across cosmic cascade flow (Bounce → Max Expansion)"
    },
    "tap_reset_antitemplate_sim.py": {
        "layer": "cosmic reset",
        "phi_rate": "phi^-4, phi^-16+",
        "category": "MULTISPHERE",
        "description": "Full reset sweep, anti-templates, soot/PAH poisoning"
    },
    "tap_final_hybrid_predictions.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-16+",
        "category": "MULTISPHERE",
        "description": "Hybrid (C + other element) templates, specialized environments"
    },
    # End-to-end integration sim (v5.3.1)
    "tap_end_to_end_sim.py": {
        "layer": "all 4",
        "phi_rate": "all",
        "category": "TOOL",
        "description": "End-to-end framework integration, all 4 layers PASS <0.3% error"
    },
    # P15-P16 in-silico precursors (added v5.3)
    "tap_p15_soot_fidelity_sim.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-4, phi^-13",
        "category": "MULTISPHERE",
        "description": "P15 soot/fidelity anti-correlation, 8 cosmic zones, r=-0.99"
    },
    "tap_p16_magnetite_chiral_sim.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-13",
        "category": "MULTISPHERE",
        "description": "P16 magnetite/L-excess correlation, 8 meteorite classes, r=0.998"
    },
    # P17 v2 multi-cycle sim (added v5.3)
    "tap_multicycle_reset_sweep.py": {
        "layer": "multicycle reset",
        "phi_rate": "phi^-13",
        "category": "MULTISPHERE",
        "description": "P17 v2 multi-cycle reset sim, validates breath clock drift"
    },
    # P17 v3 calibration (added v5.3)
    "calibration_derivation.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "TOOL",
        "description": "P17 v3 calibration constant κ derivation (residue → drift)"
    },
    # Mermaid PNG renderer (added v5.3)
    "render_mermaid_diagrams.py": {
        "layer": "tool",
        "phi_rate": "—",
        "category": "TOOL",
        "description": "matplotlib PNG renderer for cascade/multisphere diagrams"
    },
    # Multiverse coupling (new in v5.3+)
    "tap_multiverse_coupling_sim.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-13",
        "category": "MULTISPHERE",
        "description": "Multiverse coupling, cross-universe residue transfer"
    },
    # Parameter-free constants proof (new in v5.3+)
    "tap_parameter_free_constants_proof.py": {
        "layer": "tool",
        "phi_rate": "all",
        "category": "TOOL",
        "description": "Parameter-free constants proof (uses framework primitives only)"
    },
    # High-dim sequence sim (new in v5.3+)
    "tap_high_dimension_sequence_sim.py": {
        "layer": "multisphere",
        "phi_rate": "phi^-13, phi^-26",
        "category": "MULTISPHERE",
        "description": "High-dim sequence, cross-template and cross-zone dynamics"
    },
}


def register_cascade_context(sim_path, layer, phi_rate, category, description):
    name = os.path.basename(sim_path)
    _CASCADE_REGISTRY[name] = {
        "layer": layer,
        "phi_rate": phi_rate,
        "category": category,
        "description": description,
    }


def get_cascade_context(sim_path):
    name = os.path.basename(sim_path)
    if name in _CASCADE_REGISTRY:
        return _CASCADE_REGISTRY[name]
    if name in SIM_CASCADE_MAP:
        return SIM_CASCADE_MAP[name]
    return None


def list_all_sims():
    merged = dict(SIM_CASCADE_MAP)
    merged.update(_CASCADE_REGISTRY)
    return merged


def export_context_json(output_path):
    data = list_all_sims()
    out = {
        "framework": "TAP Model v5.3",
        "total_sims": len(data),
        "categories": {},
        "sims": data,
    }
    for name, ctx in data.items():
        cat = ctx.get("category", "UNKNOWN")
        out["categories"].setdefault(cat, []).append(name)
    for cat in out["categories"]:
        out["categories"][cat] = sorted(out["categories"][cat])
    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)


def get_orphan_sims(src_dir="src/"):
    """Return sims in src/ that are NOT in the registry."""
    registered = set(SIM_CASCADE_MAP.keys()) | set(_CASCADE_REGISTRY.keys())
    on_disk = set()
    for f in os.listdir(src_dir):
        if f.startswith("tap_") and f.endswith(".py"):
            on_disk.add(f)
    return sorted(on_disk - registered)


if __name__ == "__main__":
    import sys
    sims = list_all_sims()
    print(f"Total sims in cascade registry: {len(sims)}")
    print()
    by_cat = {}
    for name, ctx in sims.items():
        cat = ctx.get("category", "UNKNOWN")
        by_cat.setdefault(cat, []).append(name)
    for cat in sorted(by_cat.keys()):
        print(f"\n=== {cat} ({len(by_cat[cat])} sims) ===")
        for name in sorted(by_cat[cat]):
            ctx = sims[name]
            print(f"  {name:45s} | {ctx['layer']:30s} | {ctx['phi_rate']:20s}")

    orphans = get_orphan_sims()
    if orphans:
        print(f"\n=== ORPHAN SIMS (not in registry): {len(orphans)} ===")
        for o in orphans:
            # o is the full filename like "tap_xxx.py", strip .py for display
            print(f"  - {o}")

    if "--export" in sys.argv:
        out = "assets/tap_cascade_context.json"
        export_context_json(out)
        print(f"\n[EXPORT] -> {out}")
