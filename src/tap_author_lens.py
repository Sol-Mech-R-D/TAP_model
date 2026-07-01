# -*- coding: utf-8 -*-
"""
tap_author_lens.py
==================
TAP Model — Author Lens: a generalized rubric for auditing any
author's claim through the TAP primitive set.

The lens takes an author and their primary claim, and produces a
structured audit walking the claim through each TAP primitive
relevant to the domain. For each primitive, the audit reports:
  - TAP claim (the model's stance)
  - Author claim (what the author says)
  - Verdict (TAP-LEGAL / TAP-ILLOGICAL / TAP-SILENT / TAP-AUGMENTED)
  - Evidence (citations from the author and from TAP)
  - Refined reading (if applicable)

USAGE:
  python3 tap_author_lens.py --author narby
  python3 tap_author_lens.py --author sheldrake
  python3 tap_author_lens.py --author mcKenna
  python3 tap_author_lens.py --author wallace
  python3 tap_author_lens.py --list-authors
  python3 tap_author_lens.py --author all   # run all registered authors

The audit is exported to:
  assets/tap_author_lens_<author>_audit.json
  assets/tap_author_lens_<author>_audit.md

Each author's primary claim is encoded in the AUTHOR_REGISTRY
below. To add a new author, add an entry to AUTHOR_REGISTRY with
the primary claim, the supporting citations, and a list of which
TAP primitives to invoke. The lens will walk each primitive and
produce a verdict.

The Narby audit is the canonical worked example, drawing on the
existing TAP_Narby_Review.md and TAP_DNA_Topology_Epigenetics.md
reviews. Other authors use the same scaffold with author-specific
content.
"""

import os
import json
import argparse
from datetime import datetime
from science_constants import PHI, PHI_INV4

# The full φ-cascade is referenced by the audit primitives; compute
# the other time-constants locally for documentation/printing only.
PHI_INV2 = PHI ** -2
PHI_INV8 = PHI ** -8
PHI_INV10 = PHI ** -10
PHI_INV13 = PHI ** -13


# ─────────────────────────────────────────────────────────────────────────────
# TAP PRIMITIVE LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
# Each primitive is a self-contained audit question with:
#   - id: short identifier
#   - domain: which author's domain this primitive applies to
#   - question: the audit question
#   - tap_claim: what TAP says
#   - verdict_legal: the verdict string when author's claim is consistent
#   - verdict_illegal: the verdict string when author's claim violates TAP
#   - verdict_silent: the verdict string when TAP has nothing to say
#   - verdict_augmented: TAP adds to the claim
#   - reference: where in TAP docs this primitive is defined

TAP_PRIMITIVES = {
    "soliton_3_1": {
        "domain": "biology / consciousness",
        "question": "Does the author treat the focal system as a 3:1 "
                    "structural/interface soliton, with the 1/4 interface "
                    "carrying information?",
        "tap_claim": "Any 3D stable system has a 1/4 interface that is "
                     "informational (Theory Paper §2).",
        "verdict_legal": "Author's system maps onto 3:1 soliton structure",
        "verdict_illegal": "Author treats system as 1:1 (no interface) or 4:1 (no core)",
        "verdict_silent": "TAP has no claim about this domain",
        "verdict_augmented": "TAP adds the 1/4 interface as a specific mechanism",
        "reference": "TAP_White_Paper.md §2.1, TAP_Theory_Paper.md §2"
    },
    "universality_class": {
        "domain": "cross-cultural / convergent motif",
        "question": "Is the author inferring a specific empirical instance "
                    "from what TAP would identify as a universality class?",
        "tap_claim": "Recurrence of a motif across unrelated systems "
                     "indicates a universality class, not a specific "
                     "shared cause (Theory Paper §1.1).",
        "verdict_legal": "Author identifies the motif as a universality class",
        "verdict_illegal": "Author reads the motif as a specific cause",
        "verdict_silent": "No convergent motif in the claim",
        "verdict_augmented": "TAP specifies the universality class structure",
        "reference": "TAP_Theory_Paper.md §1.1"
    },
    "lexicon_projection": {
        "domain": "cross-cultural symbol / narrative",
        "question": "Is the author treating a culturally-specific narrative "
                    "as if it were a geometric universal?",
        "tap_claim": "The same geometric motif projects onto different "
                     "cultural lexicons (snake / naga / machine elf / "
                     "smoke coil). The geometry is invariant; the "
                     "narrative is human.",
        "verdict_legal": "Author distinguishes geometry from projection",
        "verdict_illegal": "Author treats the local projection as universal",
        "verdict_silent": "No cross-cultural claim",
        "verdict_augmented": "TAP provides the projection table",
        "reference": "TAP_Narby_Review.md §3a"
    },
    "phi_cascade_timescales": {
        "domain": "biology / pharmacology",
        "question": "Does the author's mechanism use the φ-cascade timescales "
                    "(φ⁻² hr, φ⁻⁴ 6hr, φ⁻⁸ 2day, φ⁻¹⁰ 5day, φ⁻¹³ 22day)?",
        "tap_claim": "Time-scales in biological systems are quantized in "
                     "φ. Multiple timescales (hormonal, signaling, "
                     "receptor, chromatin, cosmic) coexist in the "
                     "same cascade.",
        "verdict_legal": "Author invokes or accepts the cascade timescales",
        "verdict_illegal": "Author uses single timescale or wrong scale",
        "verdict_silent": "Time-scale not central to claim",
        "verdict_augmented": "TAP predicts which timescale governs which effect",
        "reference": "TAP_DNA_Topology_Epigenetics.md §2.1"
    },
    "microtubule_coherence": {
        "domain": "consciousness / neuroscience",
        "question": "Does the author invoke quantum coherence in the brain "
                    "and at what timescale?",
        "tap_claim": "Microtubule coherence is shielded to 939.57 fs by "
                     "Fibonacci lattice geometry (Theory Paper §7.5). "
                     "Sub-picosecond, not millisecond.",
        "verdict_legal": "Author accepts sub-picosecond coherence",
        "verdict_illegal": "Author invokes millisecond-scale quantum memory",
        "verdict_silent": "No consciousness claim",
        "verdict_augmented": "TAP specifies the sub-ps gate + classical cascade",
        "reference": "TAP_Theory_Paper.md §7.5"
    },
    "dna_topology": {
        "domain": "biology / DNA / genetic code",
        "question": "Does the author treat DNA as a passive storage medium "
                    "or as a topological object?",
        "tap_claim": "DNA is a Fibonacci topological object (H68 pitch, "
                     "H74 hydration shell, H69 codon redundancy). The "
                     "1/4 hydration shell is the informational interface.",
        "verdict_legal": "Author treats DNA as topological/active",
        "verdict_illegal": "Author treats DNA as passive 1D code",
        "verdict_silent": "DNA not central to claim",
        "verdict_augmented": "TAP adds three specific DNA-topology hypotheses",
        "reference": "TAP_DNA_Topology_Epigenetics.md §1"
    },
    "hnsw_agency": {
        "domain": "cognition / memory / agency",
        "question": "Does the author invoke a graph/state-machine "
                    "structure for cognition?",
        "tap_claim": "sm-hnsw is the state DB. Nodes + SemanticEdges "
                     "with RelationType (CAUSES, PART_OF, CONTRADICTS, "
                     "SUPPORTS, SYNONYM). 5 paradigms in distance.",
        "verdict_legal": "Author invokes a structured semantic graph",
        "verdict_illegal": "Author invokes unstructured mental content",
        "verdict_silent": "No cognition/agency claim",
        "verdict_augmented": "TAP specifies the edge types and distance metric",
        "reference": "sm-hnsw thesis (KiKaiRyu SMDB)"
    },
    "breath_clock": {
        "domain": "cosmology / time / rhythm",
        "question": "Does the author invoke cosmic-breath / Exhale-Inhale "
                    "rhythms at any scale?",
        "tap_claim": "Spacetime pulsates through Fibonacci dimensions at "
                     "rates set by the breath clock (Theory Paper §3).",
        "verdict_legal": "Author accepts pulsation/breath structure",
        "verdict_illegal": "Author treats time as static",
        "verdict_silent": "No temporal-cosmic claim",
        "verdict_augmented": "TAP provides the breath-clock tick rate (φ⁻¹³)",
        "reference": "TAP_Theory_Paper.md §3"
    },
    "pheromonal_waveguide": {
        "domain": "interpersonal / endocrine",
        "question": "Does the author invoke biochemical waveguides or "
                    "interpersonal chemical coupling?",
        "tap_claim": "VOCs and pheromones form physical waveguides "
                     "carrying phase information between individuals "
                     "(Biochem Qubit Brainstorm §1).",
        "verdict_legal": "Author invokes chemical coupling",
        "verdict_illegal": "Author treats individuals as biochemically isolated",
        "verdict_silent": "No interpersonal claim",
        "verdict_augmented": "TAP specifies the phase-lock mechanism",
        "reference": "TAP_Biochem_Qubit_Graphene_Brainstorm.md §1"
    },
    "fibonacci_dimensional_cascade": {
        "domain": "structural / recursive",
        "question": "Does the author invoke a recursive cascade of "
                    "dimensions (1, 2, 3, 5, 8, 13, ...)?",
        "tap_claim": "Stable dimensions form the Fibonacci cascade. "
                     "Each step is a topological bundle.",
        "verdict_legal": "Author invokes a recursive cascade",
        "verdict_illegal": "Author uses a non-recursive dimensional set",
        "verdict_silent": "No dimensional/structural claim",
        "verdict_augmented": "TAP specifies the cascade",
        "reference": "TAP_White_Paper.md §5.1"
    },
    "weyl_curvature_ceiling": {
        "domain": "high-energy / black hole / limits",
        "question": "Does the author invoke a saturation ceiling at "
                    "D=13 for any quantity (Weyl curvature, particle "
                    "generations, etc.)?",
        "tap_claim": "13D is the Weyl curvature ceiling; 4th fermion "
                     "generation is geometrically prohibited (White Paper §5).",
        "verdict_legal": "Author invokes a 13D limit",
        "verdict_illegal": "Author assumes unbounded high-D structure",
        "verdict_silent": "No high-D / limit claim",
        "verdict_augmented": "TAP specifies the ceiling value φ¹³ ≈ 521",
        "reference": "TAP_White_Paper.md §5.1, TAP_Theory_Paper.md §7.2"
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# AUTHOR REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
# Each entry encodes the author's primary claim, supporting
# citations, and the relevant TAP primitives to invoke.

AUTHOR_REGISTRY = {
    "narby": {
        "name": "Jeremy Narby",
        "primary_works": ["The Cosmic Serpent (1998)", "Intelligence in Nature (2005)"],
        "primary_claim": "Ayahuasca's DMT enables direct molecular dialogue with DNA. "
                         "Cross-cultural serpent+DNA symbolism is evidence of "
                         "shamans empirically accessing DNA's information content.",
        "claim_components": [
            {"id": "structured_info",
             "summary": "Ayahuasca produces structured visionary content",
             "primitives": ["microtubule_coherence", "soliton_3_1", "phi_cascade_timescales"]},
            {"id": "dna_as_source",
             "summary": "DNA is the molecular target; the 1/4 interface IS the source",
             "primitives": ["dna_topology", "soliton_3_1", "phi_cascade_timescales"]},
            {"id": "serpent_motif_evidence",
             "summary": "Cross-cultural serpent+DNA symbolism is empirical evidence",
             "primitives": ["universality_class", "lexicon_projection"]},
        ],
        "known_audit_doc": "TAP_Narby_Review.md (v1.1) and TAP_DNA_Topology_Epigenetics.md (v3.0)",
    },
    "sheldrake": {
        "name": "Rupert Sheldrake",
        "primary_works": ["A New Science of Life (1981)", "Dogs That Know (1999)",
                          "The Sense of Being Stared At (2003)"],
        "primary_claim": "Morphic resonance: self-organizing wholes are "
                         "influenced by similar past wholes via non-local "
                         "fields. Memory is inherent in nature; biological "
                         "and social forms are shaped by accumulated "
                         "influence of similar forms.",
        "claim_components": [
            {"id": "morphic_fields",
             "summary": "Non-local 'morphic fields' carry information from past to present",
             "primitives": ["breath_clock", "fibonacci_dimensional_cascade",
                            "pheromonal_waveguide"]},
            {"id": "telepathy_premonition",
             "summary": "Dogs know when owners are coming; people feel stares",
             "primitives": ["pheromonal_waveguide", "hnsw_agency"]},
            {"id": "crystallization_memory",
             "summary": "Crystals form more easily where similar crystals have formed",
             "primitives": ["phi_cascade_timescales", "weyl_curvature_ceiling"]},
        ],
        "known_audit_doc": None,  # To be written after this run
    },
    "mcKenna": {
        "name": "Terence McKenna",
        "primary_works": ["Food of the Gods (1992)", "True Hallucinations (1993)",
                          "The Archaic Revival (1991)"],
        "primary_claim": "Psilocybin mushrooms and other psychedelics are "
                         "the 'strophoid' that triggered human language "
                         "evolution. The 'transdimensional object at the "
                         "end of time' (eschaton) is approaching as novelty "
                         "increases monotonically through time.",
        "claim_components": [
            {"id": "stoned_ape",
             "summary": "Psychedelics drove human cognitive/language evolution",
             "primitives": ["phi_cascade_timescales", "microtubule_coherence",
                            "dna_topology"]},
            {"id": "novelty_theory",
             "summary": "Time-wave / novelty theory: novelty increases toward eschaton",
             "primitives": ["breath_clock", "weyl_curvature_ceiling",
                            "fibonacci_dimensional_cascade"]},
            {"id": "machine_elves",
             "summary": "DMT produces self-transforming machine elves (autonomous entities)",
             "primitives": ["lexicon_projection", "microtubule_coherence",
                            "hnsw_agency"]},
        ],
        "known_audit_doc": None,
    },
    "wallace": {
        "name": "Alfred Russel Wallace",
        "primary_works": ["On the Law Which Has Regulated the Introduction of New Species (1855)",
                          "The Malay Archipelago (1869)", "The World of Life (1910)"],
        "primary_claim": "Natural selection alone is insufficient; there is "
                         "a 'continuous overarching intelligence' directing "
                         "the evolution of life. The universe has purpose; "
                         "biological complexity is the result of an "
                         "organizing principle beyond blind variation.",
        "claim_components": [
            {"id": "overarching_intelligence",
             "summary": "An organizing intelligence shapes evolution",
             "primitives": ["hnsw_agency", "breath_clock",
                            "fibonacci_dimensional_cascade"]},
            {"id": "biogeography_pattern",
             "summary": "Wallace Line and biogeographic boundaries reflect deep structure",
             "primitives": ["fibonacci_dimensional_cascade", "soliton_3_1"]},
            {"id": "life_from_matter",
             "summary": "Life arises from matter given the right conditions",
             "primitives": ["soliton_3_1", "phi_cascade_timescales",
                            "dna_topology"]},
        ],
        "known_audit_doc": None,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def audit_claim_component(component, author_key):
    """
    Walk a single claim component through the relevant TAP primitives.
    Returns a list of primitive-audit dicts.
    """
    audits = []
    for prim_id in component["primitives"]:
        prim = TAP_PRIMITIVES[prim_id]
        audit = {
            "primitive_id": prim_id,
            "primitive_domain": prim["domain"],
            "audit_question": prim["question"],
            "tap_claim": prim["tap_claim"],
            "author_component": component["summary"],
            "reference": prim["reference"],
            # Verdict is determined by the specific author audit below;
            # this stub is replaced by the per-author verdict function.
            "verdict": "TBD",
            "verdict_rationale": ""
        }
        audits.append(audit)
    return audits


# ─────────────────────────────────────────────────────────────────────────────
# PER-AUTHOR VERDICT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
# Each function takes the audit list and replaces the "TBD" verdicts
# with the specific verdict for that author.

def verdicts_narby(audits):
    """
    Verdict assignments for Narby, based on the v1.1 / v3.0 reviews.
    """
    for a in audits:
        if a["primitive_id"] == "microtubule_coherence":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Narby invokes vision as 'seeing' DNA. TAP reframes as sub-picosecond gate event + classical cascade, not direct perception. The 1/4 interface opens; the user's narrative reconstructs."
        elif a["primitive_id"] == "soliton_3_1":
            a["verdict"] = "TAP-LEGAL"
            a["verdict_rationale"] = "DNA is a 3:1 soliton; the 1/4 hydration shell is informational. Narby's 'DNA is intelligent' is TAP-endorsed in the weak sense."
        elif a["primitive_id"] == "phi_cascade_timescales":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Narby doesn't engage timescales. The 5-HT2A sim shows the 4-stage φ-cascade (hormonal φ⁻², signaling φ⁻⁴, receptor φ⁻⁸, chromatin φ⁻¹⁰) is the actual bridge from DMT to visionary experience."
        elif a["primitive_id"] == "dna_topology":
            a["verdict"] = "TAP-LEGAL"
            a["verdict_rationale"] = "DNA is a Fibonacci topological object (H68 pitch, H74 hydration shell). Narby's intuition is correct in the strong information-theoretic sense; wrong in the encyclopedic sense."
        elif a["primitive_id"] == "universality_class":
            a["verdict"] = "TAP-ILLEGAL"
            a["verdict_rationale"] = "Narby reads cross-cultural serpent motif as evidence for DNA. TAP says the motif is a universality class (coil/serpent is the natural projection of any 1/4-interface soliton). Narby has confused a universality with a specific instance."
        elif a["primitive_id"] == "lexicon_projection":
            a["verdict"] = "TAP-ILLEGAL"
            a["verdict_rationale"] = "Narby treats the Amazonian projection (cosmic anaconda) as the literal referent. TAP says the projection is culture-specific (anaconda / naga / Quetzalcoatl / machine elf), and the universal is the geometry, not the narrative."
    return audits


def verdicts_sheldrake(audits):
    """Verdicts for Sheldrake's morphic resonance claim."""
    for a in audits:
        if a["primitive_id"] == "breath_clock":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Sheldrake's 'morphic resonance' is non-local, cumulative, and acts on form. TAP's breath clock is local (cosmic Exhale/Inhale) but the *cumulative* aspect maps to the φ⁻¹³ 'per-breath drift' that accumulates information across cosmic cycles. Reframing: morphic resonance may be the breath clock at smaller scales."
        elif a["primitive_id"] == "fibonacci_dimensional_cascade":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Sheldrake invokes 'fields' without specifying geometry. TAP's Fibonacci cascade (1, 2, 3, 5, 8, 13) provides a specific geometry for how form propagates. The TAP claim: morphic fields are Fibonacci-bundled."
        elif a["primitive_id"] == "pheromonal_waveguide":
            a["verdict"] = "TAP-LEGAL"
            a["verdict_rationale"] = "TAP explicitly endorses pheromonal/biochemical waveguides carrying phase information between individuals (Biochem Qubit Brainstorm §1). Sheldrake's telepathy/premonition claims are TAP-LEGAL if framed as chemical-coupling at long distances (perhaps via shared environmental VOCs)."
        elif a["primitive_id"] == "hnsw_agency":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Sheldrake's 'collective memory' is consistent with a structured semantic graph (HNSW with RelationType edges) that persists across instances. The 'dogs know' claim is TAP-LEGAL if the graph edges encode semantic patterns that propagate via the waveguide."
        elif a["primitive_id"] == "phi_cascade_timescales":
            a["verdict"] = "TAP-SILENT"
            a["verdict_rationale"] = "Sheldrake's claim doesn't specify timescales. TAP would need to know whether crystallization memory is φ⁻⁴ (signaling), φ⁻⁸ (receptor), or φ⁻¹⁰ (chromatin) to apply."
        elif a["primitive_id"] == "weyl_curvature_ceiling":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Sheldrake claims morphic fields are unbounded. TAP imposes a 13D ceiling (φ¹³ ≈ 521). Morphic fields may be bounded by Weyl curvature saturation, giving a specific maximum 'memory depth.'"
    return audits


def verdicts_mckenna(audits):
    """Verdicts for McKenna's stoned ape / novelty theory claims."""
    for a in audits:
        if a["primitive_id"] == "phi_cascade_timescales":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna's stoned-ape hypothesis: psilocybin drove human language evolution ~100 kya. TAP's microtubule coherence (939.57 fs) is sub-picosecond; the cascade from psilocybin to language would be: 5-HT2A binding (φ⁻⁴ signaling) → receptor sensitivity shift (φ⁻⁸ chronic) → chromatin consolidation (φ⁻¹⁰) → germline transmission → evolutionary selection. TAP-compatible, with specific timescales."
        elif a["primitive_id"] == "microtubule_coherence":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna's 'visionary' states invoke millisecond-scale perception. TAP reframes as sub-picosecond gate events, with classical cascades doing the heavy perceptual lifting. The phenomenology is real; the timescale is wrong."
        elif a["primitive_id"] == "dna_topology":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna suggests psychedelics 'unlock' latent DNA capacities. TAP's DNA-topology framework provides the mechanism: psychedelics open the 1/4 interface temporarily, allowing the chromatin state to shift. This is the material basis for 'tuning' the genome's expression without changing the sequence. TAP-legal in principle, but the *germline* transmission claim is unverified."
        elif a["primitive_id"] == "breath_clock":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna's novelty theory: complexity increases toward an eschaton. TAP's breath clock: cosmic Exhale/Inhale cycle. TAP-AUGMENTED if novelty corresponds to a monotonic increase in 1/4-interface information content across breath cycles. But TAP's breath is a *cyclic* event, not a one-way arrow; novelty may increase within an Exhale and reset at the Inhale."
        elif a["primitive_id"] == "weyl_curvature_ceiling":
            a["verdict"] = "TAP-ILLEGAL"
            a["verdict_rationale"] = "McKenna's eschaton is a singularity (transdimensional object at the end of time). TAP forbids singularities via the 13D Weyl curvature ceiling — the Inhale is a unitary reset, not a transcendence. The 'end of time' is a topological reset, not an escape."
        elif a["primitive_id"] == "fibonacci_dimensional_cascade":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna's dimensional transcendence maps onto the Fibonacci cascade. The 'transdimensional object' is the 13D boundary wall; encountering it is the Exhale peak, not an escape to higher dimensions. The cascade saturates; it does not exceed."
        elif a["primitive_id"] == "lexicon_projection":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "McKenna's 'machine elves' are the Western/modern projection of the universal coil motif (anaconda for Amazonian, naga for South Asian, machine elf for industrial Western). TAP-endorsed as a *projection*; the autonomous-entity claim is the projection being mistaken for the referent."
        elif a["primitive_id"] == "hnsw_agency":
            a["verdict"] = "TAP-LEGAL"
            a["verdict_rationale"] = "Machine elves as 'autonomous entities' are consistent with semantic-graph nodes that have causal density (high RelationType weight) and can drive narrative construction. TAP-legal as a pattern-completion result, not as actual entities."
    return audits


def verdicts_wallace(audits):
    """Verdicts for Wallace's 'overarching intelligence' claim."""
    for a in audits:
        if a["primitive_id"] == "hnsw_agency":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Wallace's 'continuous overarching intelligence' maps onto a structured semantic graph (HNSW) that spans biological and ecological scales. The 'intelligence' is the graph topology, not a homunculus. TAP-endorsed as a *structure*, with the caveat that 'intelligence' is being used metaphorically."
        elif a["primitive_id"] == "breath_clock":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Wallace's purpose-driven evolution is consistent with a *directed* cosmic process if 'purpose' is read as 'the structural requirement of the 3:1 soliton to maintain its 1/4 interface against degradation.' TAP-AUGMENTED: there is no teleology, but there is a topological imperative."
        elif a["primitive_id"] == "fibonacci_dimensional_cascade":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Wallace's biogeographic boundaries (the Wallace Line is a sharp boundary between Asian and Australian fauna) reflect deep structural discontinuities. TAP's Fibonacci cascade provides the geometric substrate: each Fibonacci step is a stable boundary, and evolution respects these boundaries."
        elif a["primitive_id"] == "soliton_3_1":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Wallace's 'life from matter' is TAP-compatible. The 3:1 soliton structure emerges naturally from matter under the right conditions (prebiotic chemistry at mineral boundaries, Theory Paper H75). The 'organizing principle' Wallace invokes is the topological stability of the 3:1 partition."
        elif a["primitive_id"] == "phi_cascade_timescales":
            a["verdict"] = "TAP-AUGMENTED"
            a["verdict_rationale"] = "Wallace's evolution operates on multiple timescales (geological, biological, ecological). TAP's φ-cascade provides the specific timescales: φ⁻⁸ for receptor-level adaptation (within a species), φ⁻¹⁰ for chromatin-level (within a population), φ⁻¹³ for cosmic (across species)."
        elif a["primitive_id"] == "dna_topology":
            a["verdict"] = "TAP-LEGAL"
            a["verdict_rationale"] = "Wallace predates DNA's discovery, but his 'life from matter' is consistent with TAP's DNA-topology (H68-H75). The Fibonacci-derived geometry of the helix is what makes life-from-matter specifically possible at the right mineral-boundary conditions."
    return audits


VERDICT_FUNCTIONS = {
    "narby": verdicts_narby,
    "sheldrake": verdicts_sheldrake,
    "mcKenna": verdicts_mckenna,
    "wallace": verdicts_wallace,
}


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT FORMATTERS
# ─────────────────────────────────────────────────────────────────────────────

def format_audit_markdown(author_key, author_info, components, audits_by_component):
    """Format the audit as a human-readable markdown document."""
    lines = []
    lines.append(f"# TAP Author Lens — {author_info['name']}")
    lines.append(f"## Audit generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"**Primary works:** {', '.join(author_info['primary_works'])}")
    lines.append("")
    lines.append(f"**Primary claim:**")
    lines.append(f"> {author_info['primary_claim']}")
    lines.append("")
    if author_info.get("known_audit_doc"):
        lines.append(f"**Existing audit doc:** {author_info['known_audit_doc']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Claim Components and TAP Primitive Audits")
    lines.append("")

    # Aggregate verdicts
    verdict_counts = {"TAP-LEGAL": 0, "TAP-ILLEGAL": 0, "TAP-SILENT": 0,
                      "TAP-AUGMENTED": 0, "TBD": 0}
    for comp_key, audits in audits_by_component.items():
        for a in audits:
            verdict_counts[a["verdict"]] = verdict_counts.get(a["verdict"], 0) + 1

    lines.append("### Verdict Summary")
    lines.append("")
    lines.append("| Verdict | Count |")
    lines.append("|---------|-------|")
    for v, c in verdict_counts.items():
        if c > 0:
            lines.append(f"| {v} | {c} |")
    lines.append("")

    for comp in components:
        lines.append(f"### Component: {comp['summary']}")
        lines.append("")
        lines.append(f"_Primitives invoked:_ {', '.join(f'`{p}`' for p in comp['primitives'])}")
        lines.append("")
        for a in audits_by_component[comp["id"]]:
            lines.append(f"#### `{a['primitive_id']}` ({a['primitive_domain']})")
            lines.append(f"**Question:** {a['audit_question']}")
            lines.append("")
            lines.append(f"**TAP claim:** {a['tap_claim']}")
            lines.append("")
            lines.append(f"**Verdict:** {a['verdict']}")
            lines.append("")
            lines.append(f"**Rationale:** {a['verdict_rationale']}")
            lines.append("")
            lines.append(f"**Reference:** {a['reference']}")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Net assessment
    lines.append("## Net Assessment")
    lines.append("")
    if verdict_counts.get("TAP-ILLEGAL", 0) > 0:
        lines.append(f"The author makes {verdict_counts['TAP-ILLEGAL']} claim(s) that are TAP-illegal. "
                     "These should be re-examined using the lexicon-projection or universality-class framework.")
    if verdict_counts.get("TAP-AUGMENTED", 0) > 0:
        lines.append(f"The author makes {verdict_counts['TAP-AUGMENTED']} claim(s) that TAP augments. "
                     "TAP provides a specific geometric, topological, or φ-cascade mechanism for these claims.")
    if verdict_counts.get("TAP-LEGAL", 0) > 0:
        lines.append(f"The author makes {verdict_counts['TAP-LEGAL']} claim(s) that are TAP-legal as stated.")
    if verdict_counts.get("TAP-SILENT", 0) > 0:
        lines.append(f"The author makes {verdict_counts['TAP-SILENT']} claim(s) where TAP has no opinion.")
    lines.append("")

    return "\n".join(lines)


def format_audit_json(author_key, author_info, components, audits_by_component):
    """Format the audit as JSON for programmatic use."""
    verdict_counts = {}
    for comp_key, audits in audits_by_component.items():
        for a in audits:
            verdict_counts[a["verdict"]] = verdict_counts.get(a["verdict"], 0) + 1

    return {
        "author_key": author_key,
        "author_name": author_info["name"],
        "primary_works": author_info["primary_works"],
        "primary_claim": author_info["primary_claim"],
        "audit_timestamp": datetime.now().isoformat(),
        "verdict_summary": verdict_counts,
        "components": [
            {
                "id": comp["id"],
                "summary": comp["summary"],
                "audits": audits_by_component[comp["id"]]
            }
            for comp in components
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def run_audit(author_key, output_dir):
    """Run the full audit pipeline for an author."""
    if author_key not in AUTHOR_REGISTRY:
        print(f"ERROR: Author '{author_key}' not in registry. Available: {list(AUTHOR_REGISTRY.keys())}")
        return None

    author_info = AUTHOR_REGISTRY[author_key]
    components = author_info["claim_components"]

    # Step 1: Audit each component against its primitives
    audits_by_component = {}
    for comp in components:
        audits = audit_claim_component(comp, author_key)
        audits_by_component[comp["id"]] = audits

    # Step 2: Apply per-author verdicts
    verdict_fn = VERDICT_FUNCTIONS[author_key]
    for comp_id, audits in audits_by_component.items():
        audits_by_component[comp_id] = verdict_fn(audits)

    # Step 3: Format and save
    os.makedirs(output_dir, exist_ok=True)
    md = format_audit_markdown(author_key, author_info, components, audits_by_component)
    json_data = format_audit_json(author_key, author_info, components, audits_by_component)

    md_path = os.path.join(output_dir, f"tap_author_lens_{author_key}_audit.md")
    json_path = os.path.join(output_dir, f"tap_author_lens_{author_key}_audit.json")

    with open(md_path, "w") as f:
        f.write(md)
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    # Print summary
    print(f"\n{'='*80}")
    print(f"  TAP AUTHOR LENS — {author_info['name']}")
    print(f"{'='*80}")
    print(f"  Primary claim: {author_info['primary_claim'][:100]}...")
    print(f"\n  Verdict summary:")
    for v, c in json_data["verdict_summary"].items():
        if c > 0:
            print(f"    {v}: {c}")
    print(f"\n  Output: {md_path}")
    print(f"  Output: {json_path}")

    return json_data


def list_authors():
    print("\nRegistered authors in the TAP Author Lens:\n")
    for key, info in AUTHOR_REGISTRY.items():
        print(f"  {key:12s} — {info['name']}")
        print(f"                  {info['primary_claim'][:100]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="TAP Author Lens — audit any author's claim through TAP primitives"
    )
    parser.add_argument("--author", type=str, default="narby",
                        help="Author key (narby, sheldrake, mcKenna, wallace, all)")
    parser.add_argument("--list-authors", action="store_true",
                        help="List all registered authors")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory (default: assets/)")
    args = parser.parse_args()

    if args.list_authors:
        list_authors()
        return

    output_dir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../assets"
    )

    if args.author == "all":
        for key in AUTHOR_REGISTRY:
            run_audit(key, output_dir)
            print()
    else:
        run_audit(args.author, output_dir)


if __name__ == "__main__":
    main()
