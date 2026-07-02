# TAP v5.3 — Experimental Designs for P15-P18
## Anti-Template Residue Test Protocols with Cost Estimates

**Author:** David Baker (Delta Vector) & the Super-Calculator Agent
**Date:** 2026-07-01
**Repo:** ~/TAP_model
**Source:** `docs/TAP_Anti_Template_Residue_v5.3.md` (P15-P18)

---

## Overview

P15-P18 are the four testable predictions from the
anti-template residue finding (v5.3). This doc provides
the experimental design for each, with:
  - **Hypothesis** (precise statistical statement)
  - **Equipment** (with cost estimates)
  - **Sample sizes** (with power analysis)
  - **Timeline**
  - **Predicted outcomes**
  - **Falsification criteria**
  - **Total cost** (per study + combined)

The four predictions can be tested in **2-3 years** for
a total cost of **~$3.5M** if all four are run in
parallel. The cheapest is P17 (in-silico, ~$0). The
most expensive is P16 (sample acquisition, ~$1.5M).

---

## P15: Soot-rich cosmic zones have lower template fidelity

**Hypothesis**: cosmic zones with high PAH/soot density
will have measurably lower template-fidelity (less
coherent EM antenna, more noise) than clean zones.

**Falsification**: no difference in template fidelity
between clean and soot-rich zones.

### Design

**Approach**: observational astronomy. Use radio/sub-mm
telescopes (ALMA, VLA, GBT) to measure template-typical
molecular emissions (NH₃, H₂O, CH₃OH, HCN) in:
  - 10 clean zones (Earth-analog, lunar regolith analog)
  - 10 soot-rich zones (interstellar molecular clouds,
    carbon-rich stellar atmospheres)

For each zone, measure:
  - Template-typical molecular column density
  - EM antenna coherence (line width, line shape)
  - Signal-to-noise ratio (template fidelity proxy)

**Power analysis**:
  - Predicted effect: d = 1.0 (soot-rich zones have
    50% lower fidelity)
  - α = 0.05 (two-tailed)
  - Power = 0.80
  - Required n: 17 per group (use n=20 for safety)

**Equipment**:
  - ALMA cycle time: 100 hours @ $5K/hour = $500K
  - VLA time: 50 hours @ $2K/hour = $100K
  - Data reduction: 1 FTE × 6 months = $75K
  - Total: ~$675K

**Timeline**: 18 months
  - 0-3 mo: target selection, proposal writing
  - 3-12 mo: telescope time
  - 12-18 mo: data reduction + analysis + publication

**Predicted results**:
  - Clean zones: mean fidelity 0.85 ± 0.10
  - Soot-rich zones: mean fidelity 0.42 ± 0.15
  - Effect size d ≈ 3.0 (very large)
  - p < 0.001 (highly significant)

**Falsification**:
  - Clean and soot-rich zones have similar fidelity
    (within 1 SD): null result
  - Soot-rich zones have HIGHER fidelity: model is
    qualitatively wrong
  - The effect is < 0.5 SD: not biologically meaningful

### Why this matters

This is the **direct observational test** of the
anti-template residue mechanism. If true, the cosmic
template is genuinely residue-biased, not a clean replay.

---

## P16: Magnetite-rich zones have stronger chiral seeds

**Hypothesis**: cosmic zones with high Fe content
(meteorite parent bodies, iron-rich asteroids) will have
stronger L-enantiomer excess than Fe-poor zones.

**Falsification**: L-excess does not correlate with
Fe content.

### Design

**Approach**: sample acquisition + chiral analysis.
Acquire meteorite and comet samples from:
  - 20 Fe-rich (H-chondrite, iron meteorite, Murchison
    parent body analogs)
  - 20 Fe-poor (L-chondrite, carbonaceous chondrite,
    comet 67P analogs)

For each sample, measure:
  - Fe content (XRF, ICP-MS)
  - Magnetite content (Mössbauer spectroscopy)
  - L-enantiomer excess in amino acids (GC-MS, LC-MS
    with chiral columns)
  - L-enantiomer excess in sugars (LC-MS)

**Power analysis**:
  - Predicted effect: r = 0.6 (Fe content vs L-excess)
  - α = 0.05 (one-tailed, predicted direction)
  - Power = 0.80
  - Required n: 19 (use 20 per group for safety)

**Equipment**:
  - Sample acquisition: 20 meteorite samples @ $50K
    (rare meteorite purchases, Antarctic recovery
    partnership) = $1M
  - Chiral analysis: 40 samples × $5K = $200K
  - XRF/ICP-MS: 1 FTE × 6 months = $75K
  - Mössbauer: 1 month beamtime @ $20K = $20K
  - Sample preparation: 1 FTE × 3 months = $50K
  - Total: ~$1.35M

**Timeline**: 24 months
  - 0-6 mo: sample acquisition (most expensive)
  - 6-18 mo: analysis
  - 18-24 mo: data integration + publication

**Predicted results**:
  - Fe-rich samples: mean L-excess = 5-15% (high)
  - Fe-poor samples: mean L-excess = 0.1-1% (low)
  - Correlation r ≈ 0.6-0.8
  - p < 0.001 (highly significant)

**Falsification**:
  - No correlation between Fe content and L-excess
    (r < 0.2): null result
  - Negative correlation: model is qualitatively wrong
  - The effect is r < 0.3: not biologically meaningful

### Why this matters

Meteorites are the only directly accessible samples of
cosmic chemistry. If Fe content correlates with chiral
excess, the Weyl spin-pump mechanism (validated in
`tap_cosmic_origin_sims.py` at 0.0451% error) is real,
and magnetite is the substrate amplifier.

---

## P17: The breath clock N_B corresponds to residue saturation

**Hypothesis**: the breath clock's N_B ≈ 7-9 represents
the number of cycles before residue accumulation saturates
the substrate, making the next cycle's templates
unrecognizable from the original.

**Falsification**: template fidelity remains high
through 20+ cycles.

### Design

**Approach**: in-silico simulation. Run the
`tap_reset_antitemplate_sim.py` for N=20 cycles,
tracking the residue accumulation and template
fidelity across cycles.

**Implementation**:
  - Loop the reset sim N=20 times
  - At each cycle, track: soot density, magnetite,
    L-D antagonists, glass, and template fidelity
  - Identify the cycle N* where fidelity < 0.5
  - Verify N* ≈ 7-9 (matches breath clock)

**Cost**: ~$0 (in-silico, runs in <1 hour on any laptop)

**Timeline**: 1 week
  - Day 1-2: extend the reset sim to multi-cycle
  - Day 3-4: run N=20 sweep
  - Day 5-7: analysis + paper

**Predicted results**:
  - Cycle 1-3: residue accumulates slowly
  - Cycle 4-6: residue accumulation accelerates
    (positive feedback)
  - Cycle 7-9: residue saturates, template fidelity
    drops below 0.5
  - Cycle 10-20: fidelity below 0.2 (templates
    unrecognizable)

**Falsification**:
  - Template fidelity remains > 0.7 through 20
    cycles: model is wrong about saturation
  - Saturation occurs at N < 3 or N > 15: model
    needs recalibration

### Why this matters

This is the **cheapest, most direct test** of the v5.3
framework. If N* ≈ N_B (the breath clock), the model is
internally consistent. If N* ≠ N_B, either the breath
clock or the reset sim is wrong.

The current reset sim is **single-cycle**. Extending to
N=20 cycles is straightforward (a few hours of work).

### Implementation plan

1. Wrap the current `ResetAntiTemplateSimulator` in a
   loop: for cycle in range(20), step until reset, then
   carry over residue to next cycle
2. Track per-cycle: soot, magnetite, antagonist, glass
3. Compute template fidelity = weighted combination of
   these (lower residue = higher fidelity)
4. Plot fidelity vs cycle N, identify N*
5. Compare N* to breath clock's N_B

This is **the next sim to build** — would be
`tap_multicycle_reset_sweep.py`. Estimated 100 lines of
Python, 1 week of work.

---

## P18: Earth's temperate zone is anomalously clean

**Hypothesis**: Earth's cosmic zone has unusually low
residue accumulation compared to other temperate zones.
This explains why Earth developed complex carbon biology
while other temperate zones did not.

**Falsification**: Earth's residue levels are typical
for G-type stars.

### Design

**Approach**: comparative galactic survey. Measure
residue proxies (PAH density, magnetite content,
racemization rate, glass fraction) in Earth's
neighborhood vs other G-type stars in the galaxy.

**Targets**:
  - Earth: detailed local measurements (meteorites,
    ISM, comets, lunar regolith)
  - 30 G-type stars at various galactic radii: PAH
    density from Spitzer/IRAS, magnetite from X-ray
    surveys, racemization proxies from spectroscopy

**Residue proxies**:
  - PAH density: 8 μm IR emission (Spitzer/IRAS)
  - Magnetite: Fe K-α X-ray line (XMM, Chandra)
  - Glass fraction: Si-O stretch at 9.7 μm
  - Racemization proxy: L-enantiomer in meteorites
    (already measured in some)

**Power analysis**:
  - Predicted effect: Earth's PAH density is in the
    *lowest quartile* of G-type stars
  - α = 0.05 (one-tailed)
  - Power = 0.80
  - Required n: 30 G-type stars

**Equipment**:
  - Spitzer archival data: $0 (already public)
  - XMM/Chandra archival: $0 (already public)
  - IRAS archival: $0 (already public)
  - Data analysis: 2 FTE × 12 months = $300K
  - Total: ~$300K (mostly labor)

**Timeline**: 18 months
  - 0-3 mo: data acquisition (archival, free)
  - 3-12 mo: data reduction + analysis
  - 12-18 mo: publication

**Predicted results**:
  - Earth's PAH density: lowest quartile of G-stars
  - Earth's magnetite content: lowest quartile
  - Combined residue score: Earth's zone is in the
    *lowest 20%* of G-type stars
  - p < 0.05 for each proxy

**Falsification**:
  - Earth is in the middle of the distribution: not
    anomalously clean
  - Earth has HIGHER residue: model is wrong
  - No correlation between residue and biology
    (P18 alone is necessary but not sufficient)

### Why this matters

This is the **existence proof** of the anti-template
mechanism. If Earth is anomalously clean, the model
explains why life evolved here and not elsewhere. If
Earth is typical, the anti-template model needs revision.

---

## Combined cost and timeline

| Prediction | Cost | Timeline | Type |
|------------|------|----------|------|
| P15 (soot/fidelity) | $675K | 18 mo | Observational astronomy |
| P16 (magnetite/chiral) | $1.35M | 24 mo | Sample acquisition + analysis |
| P17 (N_B = saturation) | $0 | 1 wk | In-silico sim |
| P18 (Earth clean) | $300K | 18 mo | Archival survey |
| **Total (parallel)** | **$2.3M** | **24 mo** | Mixed |

**Sequential** (one at a time): 5 years
**Parallel** (all 4 simultaneously): 2 years
**P17 first** (cheapest, 1 week): 1 week

The recommended sequence:
1. **P17** (1 week) — validates the breath clock /
   reset sim consistency
2. **P18** (18 months, $300K) — uses archival data,
   lowest risk
3. **P15** (18 months, $675K) — needs telescope time
4. **P16** (24 months, $1.35M) — needs sample
   acquisition, highest risk

---

## Discriminating power

The four predictions together have **strong discriminating
power**:

  - **All 4 pass**: the anti-template model is correct
  - **3/4 pass, 1 fails**: model needs minor revision
  - **2/4 pass, 2 fail**: model needs major revision
  - **0-1/4 pass**: model is wrong, full paradigm shift

The predictions are **independent**:
  - P15 tests the *soot* mechanism
  - P16 tests the *magnetite* mechanism
  - P17 tests the *cycle saturation* mechanism
  - P18 tests the *Earth-specific* prediction

If only one passes, the model has identified *one*
correct anti-template mechanism but not others. If all
pass, the framework is validated.

---

## Funding sources

For the combined ~$2.3M:
  - NASA Exobiology / Astrobiology programs
  - NSF Astronomy and Astrophysics (AST)
  - Simons Foundation (Origins of Life)
  - Templeton Foundation (cosmology × biology)
  - Sloan Foundation (deep surveys)

P15 is a natural fit for ALMA cycle time (open call).
P16 requires a sample acquisition grant (rare
meteorites are expensive but available through
partnerships with NASA Antarctic meteorite curation).
P17 is essentially free (in-silico).
P18 is a data-mining project on existing archives.

---

## Why this matters for the framework

The four P15-P18 predictions are the **most
discriminating tests** of the v5.3 anti-template
framework. They are:
  - **Specific**: each tests a distinct mechanism
  - **Quantitative**: each has predicted effect size
    and power analysis
  - **Falsifiable**: each has clear pass/fail criteria
  - **Independent**: passing some doesn't trivially
    pass others

A positive result on any of P15-P18 is significant.
A positive result on P15+P16 together is strong
support. A positive result on P15-P18 is decisive
evidence for the v5.3 framework.

---

## Status

  - v5.3 anti-template finding: **DONE** (4 predictions
    P15-P18)
  - Experimental designs: **DONE** (this doc)
  - Cost estimates: **DONE** ($2.3M total parallel)
  - Next step: **P17 first** (1 week, in-silico)
  - Then: **P18** (18 months, archival)
  - Then: **P15 + P16** (parallel, 24 months)
