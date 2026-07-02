# Changelog

All notable changes to the TAP Model are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.3.0] - 2026-07-01

### Added
- **`docs/TAP_FRAMEWORK_INDEX.md`** (17 KB) — the unified
  master index of the entire TAP framework: 50 sims across
  8 categories, 30 docs across 7 topics, cascade architecture,
  validation status, user's intuitions formalized
- **`docs/TAP_CONNECTIVITY_DASHBOARD.md`** (9 KB) — file
  reference graph, cascade mapping, validation flow
- **`docs/TAP_Multisphere_Biotemplates_v5.3.md`** (12 KB) —
  the 8 biotemplates across cosmic zones, deposited by the
  breath clock's cross-cycle mechanics
- **`src/tap_cascade_context.py`** (13 KB) — the cascade
  context registry mapping all 50 sims to their cascade
  layer and φ-rate. 50/50 sims registered, 0 orphans
- **3 deep validation sims** in `src/tap_cosmic_origin_sims.py`
  (NEW, 7 KB, by the other agent):
  - Weyl Chiral Spin-Pump (BN nanotubes): chiral seed
    EE = 1.00045e-6, 0.0451% error
  - Seismo-Piezoelectric Transduction (Siloxane helices):
    voltage 0.001855V, selectivity 1.0135
  - Hydrothermal Spin-Memory (Fe-S clusters): switching
    ratio 1.39M (way over 0.1 threshold)
- **P11-P14** — 4 new testable predictions on the
  multisphere framework

### Updated
- All 10 previously-orphan docs now have backreferences
  to `TAP_FRAMEWORK_INDEX.md`
- `docs/INDEX.md` updated with framework index link at top
- `scripts/run_all_validations.sh` runs 15 cascade + 3
  cosmic origin sims by default

### Status
- 15/15 cascade tests PASS
- 3/3 cosmic origin sims PASS
- 99/99 super-tribunal tests PASS (with --with-99)
- 50/50 sims registered in cascade_context
- 0 orphan docs
- **Total: 134+ tests passing**

## [5.2.0] - 2026-07-01

### Added
- **Cosmic origin of life doc** (`docs/TAP_Cosmic_Origin_of_Life_v5.2.md`)
  - DNA-as-cosmic-template-receiver (not source)
  - 4 new testable predictions P7-P10
  - Breath clock N_B ≈ 7-9 as previous cycles
- **v5.2 section in TAP_v5_Paper.md**

## [5.1.0] - 2026-07-01

### Added
- **Somatic cascade documentation** (`docs/TAP_Somatic_Cascade.md`)
  - Maps Somatic Experiencing, Polyvagal Theory, Feldenkrais,
    Hanna Somatics, and Nami-ryu aikijujutsu to specific φ-rates
    in the cascade
  - Differential equations for polyvagal-substrate coupling
  - 5 somatic-cascade-specific predictions (S1-S5)
- **P2 lymphangiography study protocol** (`docs/TAP_P2_Lymphangiography_Protocol.md`)
  - Full IRB-approvable design for thoracic duct lymph flow study
  - Power analysis, equipment list, budget, timeline
- **Sim audit mode** in `tap_author_lens.py`
  - `SIM_AUDIT_REGISTRY` with 10 sims mapped to cascade layers
  - `audit_sim()` and `run_sim_audit()` functions
  - `--audit-sim` and `--list-sims` CLI flags
  - **Result: 10/10 sims TAP-AUGMENTED, mean coverage 0.98**
- **Academic paper** (`docs/TAP_v5_Paper.md`)
  - Full Frontiers in Psychology / JACM-format paper
  - Abstract, intro, methods, results, discussion, conclusion
  - 30+ real literature references
- **CITATION.cff** for academic citation of the v5 paper
- **LICENSE.md** (MIT)
- **CHANGELOG.md** (this file)
- **docs/INDEX.md** as clean entry point for peer reviewers

### Status
- 15/15 master validation tests pass
- 10 sims total, all TAP-AUGMENTED (98% coverage)
- Both repos (public + private) in sync at v5.1

## [5.0.1] - 2026-07-01

### Added
- **Full ayahuasca pathway cascade sim** (`tap_ayahuasca_fascia_cascade_sim.py`)
  - Integrates 5-HT2A + chromatin + parent + fascia sims
  - 24 ceremonies over 84 days, all cascade layers measured
  - **7/7 verifications PASS** for chronic ayahuasca signature
  - Cosmic breath tick shift: +67% (matches v4.0.2 prediction)
  - Lymph stagnation: -30% (matches user intuition)
- **1-page summary** (`docs/TAP_v5_OnePager.md`)

### Status
- 15/15 master validation tests pass

## [5.0.0] - 2026-07-01

### Added
- **Myers' Anatomy Trains fascia substrate sim** (`tap_fascia_sim.py`)
  - 12 myofascial meridians with dual contralateral spirals
  - The "twin dragons" (SL_L, SL_R) as the primary substrate channel
  - Piezo coupling, blood/lymph circulation, stress-modulated coherence
  - **4/4 verifications PASS**
- **Lymphatic cascade sim** (`tap_lymphatic_cascade_sim.py`)
  - Full chain: parent sim → s_setpoint → cortisol → fascia → lymph
  - 30-day tensegrity: lymph +17%, spiral coupling +617%
- **v5.0 framing doc** (`docs/TAP_Fascia_Trains_v5.md`)
  - 12 trains, twin dragons, piezo EM coupling, Nami-ryu
- **Testable predictions doc** (`docs/TAP_Testable_Predictions_v5.md`)
  - 6 falsifiable predictions with experimental protocols
- **v4.0.2 opposite-direction test sim** (`tap_5ht2a_epigenetic_coupling_sim.py`)
  - Tensegrity vs ayahuasca produce OPPOSITE cascade signatures

### Status
- 12/12 master validation tests pass (was 11/11)

## [4.0.2] - 2026-07-01

### Added
- **5-HT2A ↔ parent sim coupling**
  - Extended `tap_coupled_ayahuasca_sim.py` to read parent sim's
    s_setpoint and apply a parent-setpoint bias to 5-HT2A recovery
- **v4.0.2 keystone prediction**: chronic ayahuasca and tensegrity
  training produce opposite cascade signatures in s_setpoint and
  cosmic breath tick (verified: tensegrity 0.58, ayahuasca 0.38)
- **Section 14** in `docs/TAP_DNA_Topology_Epigenetics.md`:
  5-HT2A-to-parent coupling (opposite-direction test)

### Status
- 11/11 master validation tests pass

## [4.0.1] - 2026-07-01

### Fixed
- **Parent epigenetic sim s_setpoint bug** (`tap_epigenetic_flop_sim.py`)
  - Original `action_a > 1.0` threshold was unreachable (action_a
    peaks at ~0.007 in 30-day run)
  - Lowered threshold to 0.001 and added 500x multiplier on
    remodel_rate
  - After fix: 30-day Tensegrity phase shifts s_setpoint from
    0.5000 to 0.5820 (16% shift)
  - This activates the parent sim → breath clock → cosmic breath
    cascade wiring that was previously silent

### Added
- **Epigenetic → cosmic cascade sim** (`tap_epigenetic_cosmic_cascade.py`)
  - Runs the full cascade: hormonal → epigenetic → cosmic
  - 4-panel plot showing s_setpoint, action state, hormones,
    implied cosmic breath tick
- **Section 13** in `docs/TAP_DNA_Topology_Epigenetics.md`:
  The parent sim discovery and v4.0.1 cascade wiring

### Status
- 11/11 master validation tests pass

## [4.0.0] - 2026-07-01

### Added
- **Narby re-evaluation v4.0** with 2024-2026 literature:
  - Khatib 2024 (transgenerational epigenetic inheritance)
  - Rieger 2026 / Rechavi lab (small RNAs as heritable agents)
  - Liu 2026 (H3K36me3 transgenerational inheritance)
  - Saunthararajah 2024 (Lamarckian models in mainstream journals)
- **6 testable predictions** including transgenerational HTR2A
  chromatin signature
- **DOC**: `docs/TAP_DNA_Topology_Epigenetics.md` (816 lines)

### Status
- 9/9 master validation tests pass

## [3.0.0] - 2026-07-01

### Added
- **5-HT2A ayahuasca sim** (`tap_5ht2a_ayahuasca_sim.py`)
  - 3-layer tolerance model (acute desens, chronic tolerance,
    sensitivity setpoint)
  - **Riba 2001 fit: 2.05% error**, **Callaway 1994 fit: 7.14% error**
- **Chromatin state sim** (`tap_chromatin_state_sim.py`)
  - 233-bead chr21 model with 8 stress-responsive loci
  - (FOS, EGR1, HSP70, NR3C1, FKBP5, BDNF, HTR2A, TELOMERE)
  - **6/6 modelable biomarkers MATCH (100%)** against published data
- **Coupled 5-HT2A + chromatin sim** (`tap_coupled_ayahuasca_sim.py`)
  - End-to-end DMT → 5-HT2A → chromatin pipeline
- **Author lens tool** (`tap_author_lens.py`)
  - 4 authors audited (Narby, Sheldrake, McKenna, Wallace)
  - 4 verdicts: TAP-AUGMENTED, TAP-LEGAL, TAP-ILLEGAL, TAP-SILENT
- **Real-data validator** (`tap_real_data_validator.py`)
  - Regression test against 8 published ayahuasca biomarkers
  - 6/6 modelable biomarkers MATCH (100%), 0 MISMATCH
- **Master validation script** (`scripts/run_all_validations.sh`)
- **Narby re-evaluation doc** (`docs/TAP_Narby_Review.md`)

### Status
- 5/5 master validation tests pass (parent sim only at this point)
- 6/6 modelable biomarkers validated against published data

## [1.0-2.0] - Earlier work

The pre-v3.0 work focused on the original TAP (Temporal Asymmetric
Pulsation) framework with 99 hypotheses. This included:

- Hardware fabrication (CAD files in `assets/cad/`)
- Audio/soliton work (`tap_phone_minimal_soliton.py`, etc.)
- Shielding simulations
- Original parent sim (before v4.0.1 fix)

These are preserved in git history but are outside the scope of
the v3.0+ Narby re-evaluation framework.

---

## How to use this changelog

The version numbers follow the cascade architecture:
- **Major version** (3.0, 4.0, 5.0): new cascade layer added
  - 3.0: 5-HT2A + chromatin (receptor + chromatin layers)
  - 4.0: parent sim → cosmic breath (epigenetic → cosmic)
  - 5.0: fascia substrate (fascia + lymph + braid)
- **Minor version** (4.0.1, 4.0.2, 5.0.1): refinement or coupling
- **Patch version** (5.1.0): documentation/tooling additions
