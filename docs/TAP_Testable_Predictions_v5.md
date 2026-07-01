# TAP v5.0 — Testable Predictions and Experimental Protocols
## How to Validate the Cascade in the Real World

**Author:** David Baker (Delta Vector) & the Super-Calculator Agent
**Date:** 2026-07-01
**Repo:** ~/TAP_model/

---

## 1. What This Doc Is

The v4.0.2 + v5.0 cascade sims make **specific quantitative
predictions** about measurable quantities in real human
populations. This doc lists each prediction, the experimental
protocol to test it, the expected result, and the
discriminating power (i.e., does the prediction distinguish
TAP from null/alternative models).

All predictions are testable with current clinical equipment
and IRB-approvable study designs. No exotic instrumentation
required for most.

---

## 2. PREDICTION 1 — Opposite-direction cascade signatures
                       (v4.0.2 keystone prediction)

### 2.1. The claim

Chronic ayahuasca users and tensegrity-trained individuals
should show **opposite cascade signatures** in serum
serotonin, heart-rate variability, and any
informational-density measure.

### 2.2. Predicted values

  | Metric                | Baseline | Tensegrity | Ayahuasca |
  |-----------------------|----------|------------|-----------|
  | Serum serotonin (μg/L)| 100      | 145        | 70        |
  | s_setpoint (model)    | 0.500    | 0.582      | 0.382     |
  | HRV (RMSSD, ms)       | 35       | 65         | 25        |
  | cosmic breath tick    | 0.00192  | 0.00165    | 0.00251   |
  | implied N_B           | 7.0      | 8.15       | 5.35      |

### 2.3. Experimental protocol

**Population:** 3 groups of n=20 each
  - **Tensegrity group**: ≥5 years of regular tensegrity
    practice (yoga, qigong, tai chi, Nami-ryu, or similar)
  - **Ayahuasca group**: ≥50 ceremonies over ≥2 years
    (Santo Daime, União do Vegetal, or shamanic traditions)
  - **Control group**: matched for age/sex, no regular
    body-practice, no psychedelic use

**Measures (each subject, single session):**
  1. Blood draw → serum serotonin (HPLC), cortisol (ELISA),
     BDNF (ELISA), 5-HT2A receptor density (PBMC
     radioligand binding)
  2. ECG (5 min) → HRV (RMSSD, LF/HF ratio, pNN50)
  3. Breath protocol (8 min, paced 6 breaths/min) →
     HRV during breath, breath-coherence score
  4. ATAC-seq on PBMCs → chromatin openness at HTR2A,
     BDNF, NR3C1, FKBP5, FOS loci (the v3.0 sim's loci)
  5. Optional: 7T MRI of the SBL/SFL → fascial hydration
     (T2 mapping)
  6. Optional: lymphangiography of left supraclavicular
     region → thoracic duct flow

**Expected results:**
  - Tensegrity: high serum serotonin, low cortisol, high
    HRV, slow breath-coherence
  - Ayahuasca: low serum serotonin, moderate cortisol,
    low HRV, fast breath-coherence
  - Control: baseline values for all
  - ATAC-seq: tensegrity → open at HTR2A, BDNF; ayahuasca
    → open at FOS, NR3C1 (stress); control → baseline

### 2.4. Discriminating power

This is the **strongest test** of the v4.0.2 model. The
opposite-direction prediction in serum serotonin alone
distinguishes TAP from:
  - Null (no difference between groups)
  - Simple-stress (both groups elevated)
  - Simple-psychedelic (ayahuasca elevated, tensegrity no change)

TAP uniquely predicts: tensegrity UP, ayahuasca DOWN.

### 2.5. Power analysis

For serum serotonin, the predicted effect size is large
(d ≈ 1.5-2.0 for the extreme groups). With n=20 per group,
a t-test has >95% power to detect d=0.8 at α=0.05. The
predicted effect is detectable.

---

## 3. PREDICTION 2 — Tensegrity training increases lymph flow
                       (v5.0 keystone prediction)

### 3.1. The claim

Tensegrity training (chronic practice of body-coherence
disciplines) should increase thoracic duct lymph flow by
15-25% compared to matched controls.

### 3.2. Predicted values

  | Group       | Thoracic duct flow (mL/hr) | +17% mean |
  |-------------|----------------------------|-----------|
  | Tensegrity  | 95 ± 15                    | +15-25%   |
  | Control     | 80 ± 18                    | baseline  |

### 3.3. Experimental protocol

**Population:** 2 groups of n=15 each
  - **Tensegrity group**: as above
  - **Control group**: matched, no body practice

**Measures (each subject):**
  1. **Lymphangiography** (indocyanine green, ICG): inject
     ICG in web spaces of feet, image the left
     supraclavicular region with near-infrared camera for
     30 min. Measure time-to-peak fluorescence at the
     left venous angle (thoracic duct terminus) and the
     total integrated fluorescence over 30 min (proxy for
     cumulative flow).
  2. Optional: **Bioimpedance spectroscopy** at multiple
     frequencies to estimate extracellular fluid volume
     and lymph pooling.

**Expected results:**
  - Tensegrity group: shorter time-to-peak, higher
    integrated fluorescence (more flow)
  - Control group: longer time-to-peak, lower integrated
    fluorescence

### 3.4. Discriminating power

Distinguishes TAP from null (no difference) and from
simple-cardiovascular-fitness (the prediction is
specific to LYMPH, not blood, and to TENSEGRITY practice
specifically, not generic exercise).

### 3.5. Power analysis

For lymph flow, the predicted effect size is medium
(d ≈ 0.8-1.2). With n=15 per group, power is ~75-90%.
Larger samples (n=25) would give >95% power.

---

## 4. PREDICTION 3 — The cascade signature is in the fidelity,
                       not the amplitude

### 4.1. The claim

Tensegrity training DECREASES raw myofascial piezo
amplitude (because the trains are relaxed) but INCREASES
the signal-to-noise ratio (because the substrate is
coherent). Stress does the opposite.

### 4.2. Predicted values

  | Group       | Raw piezo amp (μV) | Signal/noise (dB) | Coherence |
  |-------------|--------------------|--------------------|-----------|
  | Tensegrity  | 5-10 (LOW)         | 40-60 (HIGH)       | 0.95-0.99 |
  | Control     | 15-25              | 20-30              | 0.80-0.90 |
  | Stressed    | 30-50 (HIGH)       | 5-15 (LOW)         | 0.40-0.60 |

### 4.3. Experimental protocol

**Population:** 3 groups, n=15 each
  - Tensegrity, control, stressed (high perceived stress
    scale, PSS-10 > 27)

**Measures:**
  1. **High-density surface EMG** (64-channel) on the
     spiral lines, SBL, and SFL
  2. **Shear-wave elastography** (ultrasound) of the
     same trains — measures stiffness
  3. **Coherence analysis** of the EMG signals between
     contralateral sites (SL_L ↔ SL_R is the key
     comparison)
  4. **Power spectral analysis** of the EMG — separates
     raw amplitude from coherence

**Expected results:**
  - Tensegrity: low raw EMG, high coherence, low
    elastography stiffness
  - Stressed: high raw EMG, low coherence, high
    elastography stiffness
  - Control: middle values

### 4.4. Discriminating power

This is the most **counterintuitive** prediction. Most
bodywork literature assumes that "more tension = more
signal" and that the goal of practice is to *increase*
muscle/fascia activity. TAP predicts the opposite: the
goal is to *decrease* raw activity while *increasing*
coherence. This is the "clean signal, low noise" framing.

A null result (no difference in any EMG metric) would
refute the prediction. A finding of "high raw activity
in both groups" would refute the discrimination between
tensegrity and stress. The specific pattern
(tensegrity LOW raw, stress HIGH raw, but tensegrity
HIGH coherence, stress LOW coherence) is the TAP signature.

---

## 5. PREDICTION 4 — The "twin dragons" are the body's
                       rotational antenna

### 5.1. The claim

The dual contralateral Spiral Lines (SL_L, SL_R) form
a rotational antenna that reads the body's EM field as
it rotates. The two spirals should show 180° phase
difference in their piezo response to a rotating EM
field, with coherence that varies with breath phase.

### 5.2. Predicted values

  - SL_L piezo response leads SL_R by 180° (counter-phase)
  - Coherence between SL_L and SL_R is breath-phase
    modulated: max at full inhale, min at full exhale
  - Coupling metric (from v5.0 sim) tracks coherence
    1:1

### 5.3. Experimental protocol

**Setup:** Single-subject, repeated measures
  - Subject lies supine in a magnetically shielded room
  - **Magnetocardiography (MCG)** with 64-channel SQUID
    array positioned over the spiral lines
  - Subject performs paced breathing (6 breaths/min)
    for 10 minutes
  - **Surface piezo EMG** on both spiral lines, sampled
    simultaneously with MCG

**Analysis:**
  1. Cross-correlation between SL_L and SL_R piezo
     signals as a function of breath phase
  2. Coherence between piezo signals and the cardiac
     field (MCG R-wave triggered average)
  3. Spectral analysis of piezo signals during inhale
     vs exhale

**Expected results:**
  - Counter-phase: SL_L leads SL_R by ~180° in the
    0.1-1 Hz band (breath frequency range)
  - Breath-phase modulation: coherence higher at
    full inhale
  - Cardiac coupling: piezo signals track the cardiac
    field with a delay

### 5.4. Discriminating power

A null result (no counter-phase, no breath modulation)
would refute the rotational-antenna claim. The specific
counter-phase + breath modulation pattern is the
TAP signature.

### 5.5. Difficulty

This prediction requires specialized equipment (SQUID
MCG, magnetically shielded room) and is harder to
implement than P1-P3. But it's a direct test of the
"twin dragons" framing.

---

## 6. PREDICTION 5 — Transgenerational chromatin signature
                       (v4.0 keystone prediction)

### 6.1. The claim

Offspring of chronic ayahuasca users (F1, exposed in
utero) should show HTR2A chromatin shift WITHOUT
direct exposure, mediated by small RNAs and H3K36me3
histone marks from parental germline.

### 6.2. Predicted values

  | Locus | Parental (chronic user) | F1 offspring | F2 (grandchild) |
  |-------|-------------------------|--------------|-----------------|
  | HTR2A openness | -0.15 (closed) | -0.10 (closed) | -0.05 (subtle) |
  | NR3C1 openness | +0.23 (open)   | +0.15 (open)   | +0.08 (subtle)  |
  | BDNF openness   | +0.28 (open)   | +0.18 (open)   | +0.09 (subtle)  |

The signature attenuates by ~50% per generation, consistent
with the small-RNA dilution model (Rechavi lab) and
H3K36me3 transgenerational inheritance (Liu et al. 2026).

### 6.3. Experimental protocol

**Population:** 3 groups, n=10 each
  - **F1 ayahuasca**: offspring of chronic ayahuasca users
    (mother ≥50 ceremonies), no direct exposure
  - **F1 control**: offspring of matched controls, no
    ayahuasca exposure
  - **F2 ayahuasca**: grandchildren of chronic users
    (both parents F1 ayahuasca), no direct exposure

**Measures:**
  1. ATAC-seq on PBMCs → chromatin openness at HTR2A,
     NR3C1, BDNF, FKBP5, FOS
  2. **Small-RNA sequencing** of serum and PBMCs →
     tRNA fragments, miRNAs matching the parental
     signature
  3. **ChIP-seq** for H3K36me3 and H3K4me3 at the
     same loci
  4. Serum serotonin, BDNF, cortisol

**Expected results:**
  - F1 ayahuasca: HTR2A closed (-0.10), NR3C1/BDNF
    open (+0.15/+0.18)
  - F2 ayahuasca: attenuated signature (~50%)
  - F1 control: baseline at all loci
  - Small-RNA: ayahuasca F1 share small-RNA species
    with their ayahuasca parents that are absent in
    control F1

### 6.4. Discriminating power

This is the **strongest transgenerational test** of the
TAP model. A positive result would show that the cascade
has a heritable component mediated by small RNA / histone
marks, consistent with the 2024-2026 transgenerational
epigenetic inheritance literature (Khatib 2024, Rieger
2026, Liu 2026).

A null result (F1 = control) would refute the
transgenerational cascade claim. An intermediate result
(partial signature, attenuated in F2) would partially
support TAP and require refinement.

### 6.5. Power and difficulty

n=10 per group is small for transgenerational studies;
ideally n=30. But the predicted effect size is large
(d ≈ 1.0-1.5) and the F1 attenuation pattern is the
key signal. Recruitment is the main challenge (need
to identify multi-generational ayahuasca-using families).

---

## 7. PREDICTION 6 — Nami-ryu practitioners show
                       higher fascial coherence

### 7.1. The claim

Skilled Nami-ryu (and other aikijujutsu/aikido) practitioners
should show measurably higher fascial coherence than
matched controls, in both the spirals (the primary
substrate) and the SBL/SFL (the long-axis lines).

### 7.2. Predicted values

  | Group            | Spiral coupling | SBL elastography (kPa) |
  |------------------|-----------------|------------------------|
  | Nami-ryu (10+ yr)| 0.15-0.25       | 8-12                   |
  | Control          | 0.001-0.01      | 18-25                  |

### 7.3. Experimental protocol

**Population:** 2 groups, n=12 each
  - **Nami-ryu group**: black-belt or 10+ years of
    regular practice
  - **Control group**: matched for age/fitness, no
    martial arts

**Measures:**
  1. Shear-wave elastography of SBL, SFL, both
     Spiral Lines
  2. Surface piezo EMG with coherence analysis
  3. HRV during breath protocol
  4. Serum serotonin, BDNF

### 7.4. Discriminating power

Distinguishes TAP (Nami-ryu specifically trains the
spiral coupling) from generic exercise (which would
not specifically target the spirals). The selective
effect on the spirals (vs SBL/SFL) is the discriminating
signal.

---

## 8. Power and Resource Summary

| Prediction | n/group | Equipment | Cost | Time |
|------------|---------|-----------|------|------|
| P1 (opposite-direction) | 20×3 | Clinical lab + ATAC-seq | $$ | 1 yr |
| P2 (lymph flow) | 15×2 | Lymphangiography | $ | 6 mo |
| P3 (fidelity vs amp) | 15×3 | HD-EMG + ultrasound | $ | 6 mo |
| P4 (twin dragons) | 1 (rep) | SQUID MCG | $$$ | 1 yr |
| P5 (transgenerational) | 10-30×3 | ATAC-seq + small-RNA-seq | $$$ | 2 yr |
| P6 (Nami-ryu coherence) | 12×2 | Elastography + EMG | $ | 6 mo |

P1, P2, P3, P6 are tractable with current clinical
equipment. P4 and P5 require specialized equipment
or population access.

---

## 9. Recommended Order of Investigation

  1. **P3 first** (cheapest, fastest, most discriminating
     for the cascade-fidelity framing)
  2. **P1 second** (the v4.0.2 keystone prediction, well-powered
     with n=20/group)
  3. **P2 third** (the v5.0 keystone prediction, requires
     lymphangiography access)
  4. **P6 fourth** (the user can recruit from their own
     Nami-ryu community)
  5. **P4 fifth** (when MCG access is available)
  6. **P5 last** (when multi-generational cohort is recruited)

This sequence gives a falsifiable test of the cascade
fidelity framing (P3) and the v4.0.2 opposite-direction
prediction (P1) in the first year, with the other
predictions following as resources allow.

---

## 10. Falsification Criteria

A finding that *any* of the following would refute the
cascade sims:

  - P1: ayahuasca and tensegrity groups show similar (not
    opposite) cascade signatures
  - P2: tensegrity shows no lymph-flow increase
  - P3: tensegrity and stress show similar coherence (not
    the predicted inversion)
  - P4: spirals show no counter-phase, no breath modulation
  - P5: F1 ayahuasca = F1 control (no transgenerational
    signature)
  - P6: Nami-ryu shows no selective spiral effect

The cascade sims are **falsifiable**. A null result on
P1 or P3 alone would force a major revision. Null on
P5 would refute the transgenerational cascade claim.

This is the v5.0 commitment: the model is empirically
testable, the predictions are concrete, and the
predictions are not trivially consistent with null or
alternative models.
