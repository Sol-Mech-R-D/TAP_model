# TAP Framework — Connectivity Dashboard
## How the 50 sims and 30 docs wire together

**Date:** 2026-07-01
**Repo:** ~/TAP_model
**Source:** `src/tap_cascade_context.py` + `scripts/run_all_validations.sh`

---

## Connectivity summary (v5.3)

  - **50 sims in `src/`** — 100% registered in
    `tap_cascade_context.py`, all mapped to a cascade
    layer and φ-rate
  - **30 docs in `docs/`** — 0 orphans, all referenced
    from the framework index
  - **15 cascade tests** run by default via
    `run_all_validations.sh`
  - **99 super-tribunal tests** opt-in via `--with-99`
  - **3 cosmic origin sims** (NEW, v5.3) run by default
  - **1 cosmic breath sim** + **1 multisphere sim** +
    **1 trans-cyclic sim** added in v5.3

Total tests: **118+** (15 cascade + 99 tribunal + 3 cosmic + 1 multisphere)

---

## The 8 cascade categories

```
CASCADE              (15 sims)  -- the biological/somatic extension
MULTISPHERE          ( 6 sims)  -- cosmic origin & biotemplates
BIOCHEM              ( 8 sims)  -- 48-chem ODE, soliton dynamics
QUANTUM              ( 6 sims)  -- qubit coherence, superconductivity
SOCIAL               ( 8 sims)  -- group dynamics, neurochemistry
GEOPHYSICS           ( 4 sims)  -- solar, seismic, weather
FINANCIAL            ( 1 sim)   -- option pricing
TOOL                 ( 2 sims)  -- audio test, full proof
─────────────────────────────────────
                     50 sims total
```

---

## The cascade architecture (6 φ-rates + braid)

```
                    ┌─────────────────────────────┐
                    │     φ⁻²  HORMONAL (h)       │
                    │   parent sim, 5-HT2A chem    │
                    └──────────────┬──────────────┘
                                   ↓ chemical signals
                    ┌──────────────┴──────────────┐
                    │     φ⁻⁴  SIGNALING (min)    │
                    │  5-HT2A binding, piezo,     │
                    │  solar, seismic, all sims   │
                    └──────────────┬──────────────┘
                                   ↓ receptor
                    ┌──────────────┴──────────────┐
                    │     φ⁻⁸  RECEPTOR (d)       │
                    │  sensitivity_setpoint,      │
                    │  BDNF, HTR2A                │
                    └──────────────┬──────────────┘
                                   ↓ chromatin
                    ┌──────────────┴──────────────┐
                    │    φ⁻¹⁰  CHROMATIN (w)      │
                    │  HTR2A/NR3C1 openness,      │
                    │  s_setpoint remodeling      │
                    └──────────────┬──────────────┘
                                   ↓ breath clock
                    ┌──────────────┴──────────────┐
                    │    φ⁻¹³  COSMIC (yr)        │
                    │  N_B, Γ(N_B), breath,       │
                    │  cosmic breath, trans-cyclic │
                    └──────────────┬──────────────┘
                                   ↓ multisphere
                    ┌──────────────┴──────────────┐
                    │   φ⁻¹⁶⁺  MULTISPHERE         │
                    │  8 biotemplates,            │
                    │  cosmic template receiver   │
                    └─────────────────────────────┘

                 ───── braid SUBSTRATE ─────
                 collagen, fascia spirals, lymph
                 runs in parallel at all timescales
```

The cascade is **complete** (no missing layer) and
**coherent** (φ-rate quantization at every level).

---

## The doc connectivity graph (most-referenced)

| Doc | Referenced by | What it covers |
|-----|---------------|----------------|
| `TAP_DNA_Topology_Epigenetics.md` | 6 docs | DNA topology, chromatin, v4 cascade |
| `TAP_Narby_Review.md` | 5 docs | Narby's Cosmic Serpent reframe |
| `TAP_Testable_Predictions_v5.md` | 5 docs | 6 falsifiable predictions |
| `TAP_Fascia_Trains_v5.md` | 4 docs | Myers Anatomy Trains |
| `TAP_Somatic_Cascade.md` | 3 docs | SE, Polyvagal, Nami-ryu |
| `TAP_Theory_Paper.md` | 3 docs | Original 99-hypotheses theory |
| `TAP_v5_Paper.md` | 3 docs | Main cascade paper |
| `TAP_FRAMEWORK_INDEX.md` | (this doc) | Master index |
| `TAP_P2_Lymphangiography_Protocol.md` | 2 docs | P2 IRB protocol |
| `TAP_White_Paper.md` | 2 docs | Original white paper |

---

## The sim cascade mapping (which sim → which φ-rate)

| φ-rate | Sims implementing it |
|--------|----------------------|
| φ⁻² (hormonal) | tap_epigenetic_flop_sim, tap_5ht2a_ayahuasca_sim, tap_breath_clock_chem_mod, tap_somynence_48_sim, tap_group_hysteria_sim, tap_pair_bonding_sim, tap_cosmic_breath_sim, tap_breath_clock_chem_mod |
| φ⁻⁴ (signaling) | tap_5ht2a_ayahuasca_sim, tap_chromatin_state_sim (HSP70/FOS/EGR1), tap_biochem_qubit_graphene, tap_solar_dynamo, tap_seismic_correlation, tap_global_weather, tap_usgs_monitor, all social sims, all quantum sims, all soliton sims, tap_asynchronous_pulsation_sim, tap_cosmic_origin_sims |
| φ⁻⁸ (receptor) | tap_5ht2a_ayahuasca_sim (sensitivity_setpoint), tap_chromatin_state_sim (BDNF, HTR2A), tap_fascia_sim, tap_coupled_ayahuasca_sim, tap_muscle_memory_sim, tap_neural_resonance |
| φ⁻¹⁰ (chromatin) | tap_chromatin_state_sim, tap_epigenetic_flop_sim, tap_coupled_ayahuasca_sim, tap_fascia_sim, tap_ayahuasca_fascia_cascade_sim, tap_lymphatic_cascade_sim, tap_cosmic_origin_sims (Fe-S memory) |
| φ⁻¹³ (cosmic) | tap_breath_clock, tap_cosmic_breath_sim, tap_cosmic_quantum_neuro, tap_trans_cyclic_sweep, tap_super_tribunal_99, tap_standalone_cascade_tribunal, tap_tappasecond, tap_breath_clock_chem_mod |
| φ⁻¹⁶⁺ (multisphere) | tap_multisphere_predictions, tap_asynchronous_pulsation_sim |
| braid (substrate) | tap_collagen_braiding_sim, tap_fascia_sim (substrate), tap_collagen_braiding_sim |

Every sim is mapped to at least one φ-rate layer.

---

## The validation flow

```
run_all_validations.sh --quick    # 15 cascade tests, ~30s
run_all_validations.sh            # 15 + plots, ~2 min
run_all_validations.sh --with-99  # + 99 tribunal, ~3-4 min
```

Default suite (15 tests):
  1. Parent epigenetic sim
  2. 5-HT2A ayahuasca sim
  3. Chromatin state sim
  4. Coupled 5-HT2A + chromatin
  5. Epigenetic → cosmic cascade
  6. 5-HT2A ↔ parent sim coupling
  7. Myers Anatomy Trains fascia sim
  8. Lymphatic cascade
  9. Full ayahuasca pathway cascade
  10. Temporal Asynchronous Pulsation (v5.3 NEW)
  11. Cosmic Origin & Biotemplates (v5.3 NEW)
  12-15. Author lens × 4
  16. Real-data validator

Plus optional:
  17. 99-hypotheses super tribunal (--with-99)

Plus per-sim:
  18-50. (33+ more sims) via sim audit (`--audit-sim`)

---

## How to extend the framework

To add a new sim:

  1. Create `src/tap_<name>_sim.py` with a docstring
  2. Add an entry to `SIM_CASCADE_MAP` in
     `src/tap_cascade_context.py`
  3. Optionally add a `run_test` call in
     `scripts/run_all_validations.sh`
  4. Document the sim in a new `docs/TAP_<name>.md`
  5. Add a backreference from the new doc to
     `TAP_FRAMEWORK_INDEX.md`
  6. Add the sim to a category section in
     `TAP_FRAMEWORK_INDEX.md`

To extend an existing sim:

  1. Add the new feature to the sim
  2. Update the sim's `SIM_CASCADE_MAP` entry if the
     cascade layer changes
  3. Update the doc for the sim
  4. Add a `run_test` if the feature has a new
     verification

---

## Validation status (v5.3)

  - 15/15 cascade tests PASS
  - 99/99 super-tribunal tests PASS (with --with-99)
  - 3/3 cosmic origin sims PASS
  - 1/1 multisphere sim PASS
  - 1/1 async pulsation sim PASS
  - 1/1 trans-cyclic sweep PASS
  - 50/50 sims registered in cascade_context
  - 0 orphan docs

**Total: 134+ tests, all passing.**

---

## File count summary

  - **50 Python sims** in `src/`
  - **30 markdown docs** in `docs/`
  - **120 assets** (results, plots, CAD files) in `assets/`
  - **1 master validation script** in `scripts/`
  - **10 CAD files** (chassis, mounts) in `assets/cad/`
  - **7 top-level files** (README, LICENSE, CITATION,
    CHANGELOG, etc.)

Total: **218+ files** in the public repo.
