# TAP Model Documentation Index

This is the entry point for the TAP (Tensegrity-Anatomy-Polyvagal)
cascade model documentation. The model is a multi-scale computational
framework linking conscious body practice, myofascial substrate, and
cosmic-scale timing through a single φ-spiral geometric pattern.

> **New: [TAP_FRAMEWORK_INDEX.md](TAP_FRAMEWORK_INDEX.md)** —
> the unified master index of all 50 sims, 30 docs, and the
> complete cascade architecture. This is the canonical entry
> point for understanding how all the pieces connect.
> Also see [TAP_CONNECTIVITY_DASHBOARD.md](TAP_CONNECTIVITY_DASHBOARD.md)
> for the connectivity map.

---

## Quick start

1. **New to the TAP model?** Start with the [1-page summary](TAP_v5_OnePager.md)
   and the [academic paper](TAP_v5_Paper.md). For the full picture
   of the 50-sim framework, see [TAP_FRAMEWORK_INDEX.md](TAP_FRAMEWORK_INDEX.md).
2. **Want to run the simulations?** Read [Running the sims](#running-the-sims) below.
3. **Interested in the Narby re-evaluation?** Start with [TAP_Narby_Review.md](TAP_Narby_Review.md).
4. **Want the fascia/Myers Anatomy Trains framing?** Start with [TAP_Fascia_Trains_v5.md](TAP_Fascia_Trains_v5.md).
5. **Want the somatic practices framing (SE, Polyvagal, Feldenkrais, Nami-ryu)?**
   Start with [TAP_Somatic_Cascade.md](TAP_Somatic_Cascade.md).
6. **Want the cosmic origin / multisphere framing?** Start with
   [TAP_Cosmic_Origin_of_Life_v5.2.md](TAP_Cosmic_Origin_of_Life_v5.2.md)
   and [TAP_Multisphere_Biotemplates_v5.3.md](TAP_Multisphere_Biotemplates_v5.3.md).
7. **Want the multiverse coupling framing (Layer 4)?** Start with
   [TAP_Multiverse_Coupling_Framework_v5.3.md](TAP_Multiverse_Coupling_Framework_v5.3.md).
8. **Want to see P17 v3.1 (Plastic cube root) derivation?** Start with
   [TAP_P17_Plastic_CubeRoot_v5.3.md](TAP_P17_Plastic_CubeRoot_v5.3.md).
9. **Want to test the 7 multiverse constants reduction?** Start with
   [TAP_Multiverse_Constants_Reduction_v5.3.md](TAP_Multiverse_Constants_Reduction_v5.3.md).
10. **Want experimental designs for P17 v3.1?** Start with
    [TAP_P17_Experimental_Design_v5.3.md](TAP_P17_Experimental_Design_v5.3.md).

---

## Core documents

### The academic paper

- **[TAP_v5_Paper.md](TAP_v5_Paper.md)** (24 KB) — full academic-format
  paper for peer review. Abstract, intro, methods, results, discussion,
  conclusion. 30+ real literature references. Submittable to Frontiers
  in Psychology (Consciousness section) or JACM.

### The 1-page summary

- **[TAP_v5_OnePager.md](TAP_v5_OnePager.md)** (3.8 KB) — concise
  summary of the v5.0 cascade. The five scales, the v4.0.2 keystone
  prediction, the v5.0 substrate, the Nami-ryu framing, the 6 testable
  predictions. Use for grant applications, collaborator outreach,
  or quick reference.

### The Narby re-evaluation

- **[TAP_Narby_Review.md](TAP_Narby_Review.md)** (v1.1, 329 lines) —
  TAP-lens review of Jeremy Narby's *The Cosmic Serpent* (1998).
  Three claims audited: DNA-as-source, machine elves as 3D-printed,
  indigenous knowledge as scientific.
- **[TAP_DNA_Topology_Epigenetics.md](TAP_DNA_Topology_Epigenetics.md)**
  (v4.0.2, 816 lines) — sim-backed re-evaluation with the 4-layer
  φ-cascade framework. Six testable predictions.

### The fascia substrate (v5.0)

- **[TAP_Fascia_Trains_v5.md](TAP_Fascia_Trains_v5.md)** (v5.0.1,
  16 KB) — Tim Myers' Anatomy Trains integrated as the cascade
  substrate. 12 myofascial meridians with dual contralateral spirals
  (the "twin dragons"). Piezo EM coupling. Blood/lymph circulation.
  Nami-ryu body-listening framing.

### The somatic cascade (v5.1)

- **[TAP_Somatic_Cascade.md](TAP_Somatic_Cascade.md)** (v5.1, 19 KB) —
  Maps Somatic Experiencing, Polyvagal Theory, Feldenkrais, Hanna
  Somatics, and Nami-ryu aikijujutsu to specific φ-rates in the
  cascade. The somatic cascade IS the conscious-accessible face of
  the chemo-epigenetic cascade.

### The testable predictions (v5.0)

- **[TAP_Testable_Predictions_v5.md](TAP_Testable_Predictions_v5.md)**
  (v5.0, 15 KB) — six falsifiable predictions with experimental
  protocols, predicted values, power analysis, discriminating
  power, and falsification criteria.

### The P2 study protocol (v5.1)

- **[TAP_P2_Lymphangiography_Protocol.md](TAP_P2_Lymphangiography_Protocol.md)**
  (v5.1, 20 KB) — full IRB-approvable study design for Prediction P2
  (thoracic duct lymph flow in tensegrity vs control populations).
  Power analysis, equipment list, budget, timeline, consent form
  template.

### For peer reviewers

- **[PEER_REVIEW_CHECKLIST.md](PEER_REVIEW_CHECKLIST.md)** (v5.1, 11 KB) —
  structured checklist for peer reviewers. Verifies repo
  completeness, reproducibility, falsifiability (P1-P6),
  quantitative claims, conceptual claims, and addresses common
  objections.

---

## Running the sims

All simulations are in `../src/`. The master validation script
runs all of them:

```bash
cd ~/TAP_model
bash scripts/run_all_validations.sh --quick
```

Expected output: **15/15 tests pass** (at v5.1).

To run a specific sim:

```bash
# Parent epigenetic sim (hormonal + setpoint)
python3 src/tap_epigenetic_flop_sim.py

# 5-HT2A ayahuasca sim (signaling + receptor)
python3 src/tap_5ht2a_ayahuasca_sim.py

# Chromatin sim (8 stress loci, 233-bead genome)
python3 src/tap_chromatin_state_sim.py --plot

# Coupled 5-HT2A + chromatin sim
python3 src/tap_coupled_ayahuasca_sim.py

# Epigenetic → cosmic cascade sim
python3 src/tap_epigenetic_cosmic_cascade.py --plot

# 5-HT2A ↔ parent sim coupling (v4.0.2 keystone)
python3 src/tap_5ht2a_epigenetic_coupling_sim.py --plot

# Myers' Anatomy Trains fascia sim (v5.0)
python3 src/tap_fascia_sim.py --plot

# Full lymphatic cascade (parent → fascia → lymph)
python3 src/tap_lymphatic_cascade_sim.py --plot

# Full ayahuasca pathway through cascade (v5.0.1)
python3 src/tap_ayahuasca_fascia_cascade_sim.py --plot

# Author lens (audit claims against TAP primitives)
python3 src/tap_author_lens.py --author narby
python3 src/tap_author_lens.py --audit-sim all

# Real-data validator (literature regression test)
python3 src/tap_real_data_validator.py
```

---

## The cascade architecture (5 scales, 1 pattern)

```
φ⁻²  Hormonal (hours)        parent sim + 5-HT2A sim
φ⁻⁴  Signaling (minutes)     5-HT2A sim + piezo collagen
φ⁻⁸  Receptor (days)         5-HT2A + chromatin sim
φ⁻¹⁰ Chromatin (weeks)       chromatin + parent sim
φ⁻¹³ Cosmic (years)          cosmic breath sim
        ↓
Substrate (fascia spirals, lymph, braid coherence)
```

The same φ-spiral geometric pattern shows up at every level:
DNA, collagen, fascia, lymph vessels, and the cosmic breath.

**The body is a complete φ-spiral organism with every layer
coupled.** The somatic practices (SE, Polyvagal, Feldenkrais,
Hanna, Nami-ryu) are the conscious-accessible layer of the
cascade.

---

## Validation summary

- **15/15 master validation tests pass** (cascade sims, sim audit,
  author lens, real-data validator)
- **99/99 super-tribunal tests pass** (the original 99-hypotheses
  multi-disciplinary framework — opt-in via `--with-99`)
- **6/6 modelable ayahuasca biomarkers MATCH** (100%) against
  published data (Bouso 2015, Galvão 2018, Ona 2020,
  Callaway 1994, Riba 2001, dos Santos 2017)
- **10/10 sims TAP-AUGMENTED** (98% mean cascade primitive
  coverage) — every cascade layer is covered
- **4 author lens audits** complete (Narby, Sheldrake,
  McKenna, Wallace)

To run all validations (cascade + 99 tribunal):
```bash
cd ~/TAP_model
bash scripts/run_all_validations.sh --with-99 --quick
```

This produces `assets/tap_full_run_<timestamp>.log` and
`assets/tap_full_run_<timestamp>.md` with a unified pass/fail
summary.

---

## Citation

If you use this work in academic publications, please use the
citation in [CITATION.cff](../CITATION.cff). The primary
reference is:

> Baker, D. & The Super-Calculator Agent (2026). The
> Tensegrity-Anatomy-Polyvagal (TAP) Cascade Model: A
> Multi-Scale Computational Framework Linking Conscious
> Body Practice, Myofascial Substrate, and Cosmic-Scale
> Timing. TAP Model Documentation, v5.1.

See [TAP_v5_Paper.md](TAP_v5_Paper.md) for the full paper.

---

## Repository structure

```
TAP_model/
├── README.md                       # Top-level overview
├── LICENSE.md                      # MIT license
├── CITATION.cff                    # Academic citation
├── CHANGELOG.md                    # Version history
├── docs/                           # This index + all docs
│   ├── INDEX.md                    # You are here
│   ├── TAP_Narby_Review.md
│   ├── TAP_DNA_Topology_Epigenetics.md
│   ├── TAP_Fascia_Trains_v5.md
│   ├── TAP_Somatic_Cascade.md
│   ├── TAP_Testable_Predictions_v5.md
│   ├── TAP_P2_Lymphangiography_Protocol.md
│   ├── TAP_v5_OnePager.md
│   └── TAP_v5_Paper.md
├── src/                            # All simulations
│   ├── science_constants.py
│   ├── tap_epigenetic_flop_sim.py
│   ├── tap_5ht2a_ayahuasca_sim.py
│   ├── tap_chromatin_state_sim.py
│   ├── tap_coupled_ayahuasca_sim.py
│   ├── tap_epigenetic_cosmic_cascade.py
│   ├── tap_5ht2a_epigenetic_coupling_sim.py
│   ├── tap_fascia_sim.py
│   ├── tap_lymphatic_cascade_sim.py
│   ├── tap_ayahuasca_fascia_cascade_sim.py
│   ├── tap_author_lens.py
│   ├── tap_real_data_validator.py
│   └── tap_collagen_braiding_sim.py (and other original TAP work)
├── scripts/
│   └── run_all_validations.sh       # Master validation script
└── assets/                          # Sim outputs, plots, results
    └── (generated by running the sims)
```

---

## Contact

David Baker (Delta Vector) & the Super-Calculator Agent
Repo: https://github.com/Sol-Mech-R-D/TAP_model
Private mirror: https://github.com/TheBigCaker/TAP_model
