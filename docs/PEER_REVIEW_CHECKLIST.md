# Peer-Review Checklist for the TAP Cascade Model v5.1

This document provides a structured checklist for peer reviewers
of the TAP (Tensegrity-Anatomy-Polyvagal) cascade model. Each
item is a specific testable claim that the reviewer can verify
by running the code, reading the documentation, or examining
the validation results.

The model is presented in `docs/TAP_v5_Paper.md` (the main
submission). This checklist is supplementary.

---

## 1. Repository structure

Verify the repo is complete and well-organized:

  - [ ] All 10 sims are present in `src/`
  - [ ] All 7 cascade docs are present in `docs/`
  - [ ] `scripts/run_all_validations.sh` is present and runnable
  - [ ] `CITATION.cff`, `LICENSE.md`, `CHANGELOG.md` are at
        the top level
  - [ ] `docs/INDEX.md` provides a clear entry point
  - [ ] No extraneous untracked files in `assets/`
  - [ ] `.gitignore` excludes `__pycache__/`, `.pyc`, large
        binary logs

Run `bash scripts/run_all_validations.sh --quick` to verify
the test suite runs and passes (expected: 15/15).

---

## 2. Reproducibility

The model must reproduce the reported results from a clean
checkout:

  - [ ] Run `bash scripts/run_all_validations.sh --quick` from
        a clean clone → 15/15 PASS
  - [ ] Verify the cascade sim outputs match the claimed
        values (see §4 below)
  - [ ] Verify the chromatin sim biomarkers MATCH (6/6)
  - [ ] Verify the fascia sim verifications (4/4)
  - [ ] Verify the ayahuasca pathway sim verifications (7/7)
  - [ ] Verify the sim audit (10/10 TAP-AUGMENTED)

If any of these fail on a clean clone, the model is not
reproducible and the reviewer should note which sims/outputs
do not match.

---

## 3. Falsifiability

The model must be **falsifiable** — specific experimental
results would refute it. The six testable predictions
(`docs/TAP_Testable_Predictions_v5.md`) define this:

  - [ ] **P1 (opposite cascade signatures)**: the model's
        unique prediction is tensegrity UP, ayahuasca DOWN
        in serum serotonin / HRV / chromatin openness.
        Alternative models (null, simple stress, simple
        psychedelic) do not predict this directional
        inversion. A finding of "both groups similar" or
        "both groups elevated" would refute P1.

  - [ ] **P2 (lymph flow)**: tensegrity should show
        15-25% greater thoracic duct ICG clearance.
        A null result would refute P2.

  - [ ] **P3 (fidelity vs amplitude)**: tensegrity should
        DECREASE raw piezo but INCREASE signal fidelity.
        A null result (no difference) or opposite pattern
        would refute P3.

  - [ ] **P4 (rotational antenna)**: the spiral lines
        should show 180° phase difference in piezo response.
        A null result would refute P4.

  - [ ] **P5 (transgenerational)**: F1/F2 offspring of
        chronic ayahuasca users should show attenuated
        chromatin signature. A null result (F1 = control)
        would refute P5.

  - [ ] **P6 (Nami-ryu specific)**: spiral coupling should
        be selectively elevated in Nami-ryu practitioners
        vs SBL/SFL. A null result would refute P6.

If at least one of P1-P6 is refuted by experimental data, the
cascade model must be revised. The model makes
**quantitative, specific, discriminating predictions** — not
just "this might correlate with that."

---

## 4. Quantitative claims to verify

The paper makes these specific quantitative claims. Reviewers
can verify them by running the sims and checking the output
files.

### 4.1. Hormonal cascade (parent sim, v4.0.1 fix)

  - **Claim**: 30-day Tensegrity phase shifts s_setpoint
    0.5000 → 0.5820
  - **Verify**: run `python3 src/tap_epigenetic_flop_sim.py`
    and check the last line of output
  - **Expected**: s_setpoint = 0.5820 at day 30

### 4.2. 5-HT2A ayahuasca sim (Riba 2001 fit)

  - **Claim**: 2.05% error against Riba 2001 (4 doses →
    4th dose 60% of 1st)
  - **Verify**: run `python3 src/tap_5ht2a_ayahuasca_sim.py`
  - **Expected**: 4-dose protocol, ratio of 4th to 1st ≈ 0.60

### 4.3. 5-HT2A ayahuasca sim (Callaway 1994 fit)

  - **Claim**: 7.14% error against Callaway 1994 (single
    dose → 14d setpoint recovery)
  - **Verify**: same sim as 4.2
  - **Expected**: setpoint recovers to 95% in 13-14 days

### 4.4. Chromatin sim (8 stress loci)

  - **Claim**: 6/6 modelable biomarkers MATCH published data
  - **Verify**: run `python3 src/tap_real_data_validator.py`
  - **Expected**: MATCH × 6, MISMATCH × 0

### 4.5. Coupled 5-HT2A + chromatin (Riba coupled)

  - **Claim**: 2.19% error in coupled sim
  - **Verify**: run `python3 src/tap_coupled_ayahuasca_sim.py`
  - **Expected**: 4-dose ratio in 2.0-2.5% error range

### 4.6. Epigenetic → cosmic cascade (Tensegrity)

  - **Claim**: drift_multiplier = 0.8591x, implied φ⁻¹³ shift
    0.00192 → 0.00165 (14% reduction)
  - **Verify**: run `python3 src/tap_epigenetic_cosmic_cascade.py`
  - **Expected**: implied φ⁻¹³ ≈ 0.00165

### 4.7. 5-HT2A ↔ parent sim coupling (opposite directions)

  - **Claim**: tensegrity s_setpoint 0.582, ayahuasca 0.382
    (opposite directions)
  - **Verify**: run `python3 src/tap_5ht2a_epigenetic_coupling_sim.py --plot`
  - **Expected**: opposite-direction verification PASS

### 4.8. Fascia sim (12 trains, dual spirals)

  - **Claim**: 4/4 verifications (lymph, coherence, tension,
    spiral coupling)
  - **Verify**: run `python3 src/tap_fascia_sim.py --plot`
  - **Expected**: 4 PASS, 1 INFO (raw piezo)

### 4.9. Full ayahuasca pathway (v5.0.1)

  - **Claim**: 7/7 verifications for chronic ayahuasca
    signature (lymph stagnation, spiral collapse, HTR2A
    closure, cosmic breath +67%)
  - **Verify**: run `python3 src/tap_ayahuasca_fascia_cascade_sim.py --plot`
  - **Expected**: 7 PASS

### 4.10. Sim audit

  - **Claim**: 10/10 sims TAP-AUGMENTED, mean coverage 0.98
  - **Verify**: run `python3 src/tap_author_lens.py --audit-sim all`
  - **Expected**: 10 TAP-AUGMENTED, mean coverage ≥ 0.95

---

## 5. Conceptual claims to verify

The paper makes these conceptual claims. Reviewers can verify
them by reading the documents.

  - [ ] **5-layer φ-cascade structure**: read
        `docs/TAP_DNA_Topology_Epigenetics.md` section 2
        and verify the 5 layers are correctly defined
  - [ ] **Narby reframe**: read `docs/TAP_Narby_Review.md`
        and verify the verdicts (TAP-LEGAL, TAP-ILLEGAL,
        TAP-AUGMENTED) are coherent
  - [ ] **Somatic cascade mapping**: read
        `docs/TAP_Somatic_Cascade.md` and verify each
        tradition is correctly mapped to its φ-rate
  - [ ] **Myers' Anatomy Trains substrate**: read
        `docs/TAP_Fascia_Trains_v5.md` and verify the 12
        trains are correctly described
  - [ ] **Polyvagal → tensegrity → ayahuasca spectrum**:
        verify the three regimes map correctly (ventral
        vagal ↔ tensegrity, sympathetic ↔ stress, dorsal
        vagal ↔ chronic ayahuasca)
  - [ ] **Fidelity-not-amplitude signature**: verify this
        is consistently framed across all docs

---

## 6. Citation and reproducibility

  - [ ] `CITATION.cff` is valid CFF 1.2.0
  - [ ] `LICENSE.md` is present and clear
  - [ ] `CHANGELOG.md` documents v3.0 → v5.1 evolution
  - [ ] All 30+ references in `TAP_v5_Paper.md` are
        real and citable
  - [ ] All sims have docstrings and inline comments
  - [ ] No proprietary or restricted data is used

---

## 7. Specific items reviewers should focus on

If the reviewer has limited time, focus on these high-leverage
items first:

  1. **The cascade sims pass** (item 2 above) — this is the
     minimum bar. If the sims don't pass, the model is broken.

  2. **The six testable predictions are specific and
     discriminating** (item 3 above) — this is the
     falsifiability bar. If the predictions are vague or
     trivially consistent with alternative models, the
     model is unfalsifiable.

  3. **The 5-layer cascade structure is coherent** (item 5
     above) — this is the conceptual bar. If the cascade
     layers are arbitrary or contradictory, the model is
     incoherent.

  4. **The chronic ayahuasca signature is consistent across
     all 7 layers** (item 4.9 above) — this is the
     integration bar. The most distinctive feature of the
     model is the end-to-end cascade from DMT to cosmic
     breath, validated at every layer.

---

## 8. Common objections to consider

The model anticipates these objections. Reviewers should
verify the response is adequate.

  - **"The φ-cascade is just numerology."** Response: the
    cascade rates are derived from the model's geometric
    foundation (13D bulk, 1/4 interface, microtubule 939.57fs
    coherence). The rates are not fitted; they fall out of
    the geometry. See `docs/TAP_White_Paper.md`.

  - **"The model can't be tested because it's not specific
    enough."** Response: 6 falsifiable predictions with
    quantitative expected values, power analysis, and
    discriminating power. See `docs/TAP_Testable_Predictions_v5.md`.

  - **"The somatic cascade is pseudoscience."** Response: the
    somatic cascade maps to published practices (SE,
    Polyvagal, Feldenkrais) and predicts measurable biomarker
    changes. The predictions are testable with current
    clinical equipment (HRV, EMG, ICG lymphangiography).

  - **"The 6/6 biomarker match is cherry-picking."**
    Response: the validator is automated, runs against ALL
    published ayahuasca biomarkers (8 total), and reports
    both matches and mismatches. 6 of 6 modelable biomarkers
    match; 2 are not yet modeled (HTR2A density and
    telomere length are now modeled in v3.1, but the
    original validation was 6/6).

  - **"The cascade sims are over-fit to the data."**
    Response: the cascade architecture (5 layers, φ-rates)
    is independent of the validation data. The Riba and
    Callaway fits are post-hoc predictions, not fits. The
    biomarker matches are emergent from the cascade
    architecture, not from parameter fitting.

---

## 9. Reviewer sign-off

A complete review should:

  1. Run the master validation and confirm 15/15 pass
  2. Verify the 6 testable predictions are concrete and
     discriminating
  3. Read at least one of the cascade docs (e.g.
     `TAP_Fascia_Trains_v5.md` or `TAP_Somatic_Cascade.md`)
     to verify conceptual coherence
  4. Note any sim that does not match its claimed
     quantitative output
  5. Note any conceptual inconsistency
  6. Sign off on the review with a recommendation:
     - **Accept**: model is reproducible, falsifiable, and
       coherent. No major issues.
     - **Minor revision**: model is solid, but specific
       issues need addressing.
     - **Major revision**: model has substantive issues.
     - **Reject**: model is not reproducible, not
       falsifiable, or has fundamental conceptual issues.

---

## 10. Contact

For questions about the model or this checklist, contact
David Baker (Delta Vector) via the GitHub issue tracker at
https://github.com/Sol-Mech-R-D/TAP_model/issues.
