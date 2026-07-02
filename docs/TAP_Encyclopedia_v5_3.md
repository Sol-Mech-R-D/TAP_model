# TAP Encyclopedia v5.3.2 (Full)

Comprehensive wiki for every script, doc, asset, constant, prediction, and concept in the TAP framework.

Generated: 2026-07-02T10:22:26.982863

## Table of Contents

1. Constants (12)
2. Predictions (P1-P18)
3. Concepts (10)
4. Scripts (107)
5. Docs (45)
6. Assets (95)

---

## 1. Constants

| Name | Value | Status | Source |
|------|-------|--------|--------|
| Golden Ratio (φ) | `1.618034` | exact | src/science_constants.py |
| φ⁻⁴ | `0.145898` | exact | src/tap_breath_clock.py |
| φ⁻⁸ | `0.021286` | exact | src/tap_chromatin_state_sim.py |
| φ⁻¹³ (breath tick) | `0.001919` | exact | src/tap_breath_clock.py |
| φ⁻²⁶ (meta-breath) | `3.68e-6` | exact | src/tap_trans_cyclic_sweep.py |
| Plastic (ρ) | `1.324718` | exact | src/calibration_derivation.py |
| Feigenbaum δ | `4.669202` | exact | docs/TAP_Multiverse_Constants_Reduction_v5.3.md |
| α⁻¹ (fine structure) | `137.036` | -1.66% | src/tap_breath_clock.py |
| N_B (breath number) | `8` | verified | src/tap_breath_clock.py |
| ψ (braid phase) | `0.9105` | 0.21% | src/calibration_derivation.py |
| κ (calibration) | `1.535e-5` | supported | src/calibration_derivation.py |
| N_MAX (meta) | `521` | exact | src/tap_trans_cyclic_sweep.py |

## 2. Predictions (P1-P18)

| ID | Category | Description | Status |
|----|----------|-------------|--------|
| **P1** | CASCADE | Opposite signatures ayahuasca vs tensegrity | supported |
| **P2** | CASCADE | Lymph flow +15-25% in tensegrity | supported |
| **P3** | CASCADE | Fidelity up, piezo down (counter-intuitive) | supported |
| **P4** | CASCADE | 180° spiral phase rotational antenna | supported |
| **P5** | CASCADE | Transgenerational HTR2A chromatin | supported |
| **P6** | CASCADE | Nami-ryu specific spiral coupling | supported |
| **P7** | COSMIC | Codon table correlates φ⁻ⁿ | supported |
| **P8** | COSMIC | L-excess correlates Γ(N_B) | supported |
| **P9** | COSMIC | Nami-ryu N_B-correction | supported |
| **P10** | COSMIC | 13 templates max 13D Weyl ceiling | supported |
| **P11** | MULTI | Template dist correlates Γ(N_B) | supported |
| **P12** | MULTI | Cross-zone coupling detectable | supported |
| **P13** | MULTI | Carbon is special self-replicating | supported |
| **P14** | MULTI | 13 templates max verified | supported |
| **P15** | ANTI | Soot-rich zones lower fidelity | r = -0.99 |
| **P16** | ANTI | Magnetite stronger chiral | r = 0.998 |
| **P17** | ANTI | N_B = residue saturation | 0.21% |
| **P18** | ANTI | Earth is anomalously clean | 88% |

## 3. Concepts

- **Breath Clock**: The φ-rate scaling that drives all observable drift (src/tap_breath_clock.py)
- **Sub-Breath**: 8.12133-day Earth-Moon beat driving primary sub-breath (src/tap_seismic_correlation.py)
- **N_B**: Which breath cycle the system is in (chi²-fitted to 8 for Earth) (src/tap_breath_clock.py)
- **Γ(N_B)**: Breath correction factor 1 + N_B·φ⁻¹³ ≈ 1.0154 (src/tap_breath_clock.py)
- **Multiverse Coupling**: 7-node Kuramoto network (Plastic + 6 satellites) (src/tap_multiverse_coupling_sim.py)
- **Anti-Template Residue**: Materials that prevent template formation (docs/TAP_Anti_Template_Residue_v5.3.md)
- **Nami-Ryu Body-Listening**: Conscious practice of cascade via spirals (docs/TAP_Fascia_Trains_v5.md)
- **Cascade**: 4-6 layer chain hormonal → cosmic (docs/TAP_FRAMEWORK_INDEX.md)
- **Twin Dragons**: Two spiral lines in Nami-ryu (SL_L + SL_R) (docs/TAP_Fascia_Trains_v5.md)
- **ψ-collapse**: Chronic 5-HT2A agonist exposure → HTR2A compaction (docs/TAP_Somatic_Cascade.md)

## 4. Scripts (107 total)

| Script | Category | Size | Purpose |
|--------|----------|------|---------|
| `tap_5ht2a_ayahuasca_sim.py` | 5-HT2A | 29,678 | tap_5ht2a_ayahuasca_sim.py |
| `tap_super_tribunal_99.py` | 99-Tribunal | 40,996 | tap_super_tribunal_99.py |
| `tap_author_lens.py` | Author lens | 53,846 | tap_author_lens.py |
| `tap_coupled_ayahuasca_sim.py` | Ayahuasca | 25,490 | tap_coupled_ayahuasca_sim.py |
| `tap_collagen_braiding_sim.py` | Braid group/Quantum | 5,523 | tap_collagen_braiding_sim.py |
| `tap_body_breath_states.py` | Breath clock | 8,145 | tap_body_breath_states.py |
| `tap_breath_clock.py` | Breath clock | 26,645 | tap_breath_clock.py |
| `tap_breath_clock_chem_mod.py` | Breath clock | 7,803 | tap_breath_clock_chem_mod.py |
| `tap_breath_per_body.py` | Breath clock | 9,453 | tap_breath_per_body.py |
| `tap_unified_breath_clock.py` | Breath clock | 10,692 | tap_unified_breath_clock.py |
| `tap_zodiac_to_breath.py` | Breath clock | 8,892 | tap_zodiac_to_breath.py |
| `calibration_derivation.py` | Calibration | 10,058 | calibration_derivation.py |
| `tap_ayahuasca_fascia_cascade_sim.py` | Cascade sims | 20,118 | tap_ayahuasca_fascia_cascade_sim.py |
| `tap_cascade_context.py` | Cascade sims | 17,227 | tap_cascade_context.py |
| `tap_cosmological_cascade_sweep.py` | Cascade sims | 8,086 | tap_cosmological_cascade_sweep.py |
| `tap_epigenetic_cosmic_cascade.py` | Cascade sims | 12,261 | tap_epigenetic_cosmic_cascade.py |
| `tap_lymphatic_cascade_sim.py` | Cascade sims | 11,063 | tap_lymphatic_cascade_sim.py |
| `tap_standalone_cascade_tribunal.py` | Cascade sims | 5,069 | tap_standalone_cascade_tribunal.py |
| `tap_unified_cascade.py` | Cascade sims | 18,543 | tap_unified_cascade.py |
| `tap_chromatin_state_sim.py` | Chromatin | 27,884 | tap_chromatin_state_sim.py |
| `tap_framework_coherence.py` | Coherence | 7,451 | tap_framework_coherence.py |
| `tap_quantum_decoherence.py` | Coherence | 2,804 | tap_quantum_decoherence.py |
| `tap_qubit_coherence_sweep.py` | Coherence | 4,970 | tap_qubit_coherence_sweep.py |
| `tap_core_ai_cascade.py` | Core framework | 3,810 | tap_core_ai_cascade.py |
| `tap_cosmic_breath_sim.py` | Cosmic/Planetary | 8,222 | tap_cosmic_breath_sim.py |
| `tap_cosmic_kp_validation.py` | Cosmic/Planetary | 13,727 | tap_cosmic_kp_validation.py |
| `tap_cosmic_origin_sims.py` | Cosmic/Planetary | 7,037 | tap_cosmic_origin_sims.py |
| `tap_cosmic_quantum_neuro.py` | Cosmic/Planetary | 5,159 | tap_cosmic_quantum_neuro.py |
| `tap_somatic_cosmic_geometry.py` | Cosmic/Planetary | 11,732 | tap_somatic_cosmic_geometry.py |
| `tap_somatic_cosmic_geometry_v2.py` | Cosmic/Planetary | 11,259 | tap_somatic_cosmic_geometry_v2.py |
| `tap_somatic_cosmic_v3.py` | Cosmic/Planetary | 12,300 | tap_somatic_cosmic_v3.py |
| `tap_cross_body_coupling.py` | Cross-domain | 10,390 | tap_cross_body_coupling.py |
| `tap_daily_prediction_check.py` | Daily check | 10,663 | tap_daily_prediction_check.py |
| `tap_dashboard.py` | Dashboard | 16,552 | tap_dashboard.py |
| `update_dashboard.py` | Dashboard | 14,003 | update_dashboard.py |
| `tap_encyclopedia.py` | Encyclopedia | 12,973 | tap_encyclopedia.py |
| `tap_encyclopedia_v2.py` | Encyclopedia | 13,191 | tap_encyclopedia_v2.py |
| `tap_5ht2a_epigenetic_coupling_sim.py` | Epigenetic | 17,026 | tap_5ht2a_epigenetic_coupling_sim.py |
| `tap_epigenetic_flop_sim.py` | Epigenetic | 9,625 | tap_epigenetic_flop_sim.py |
| `tap_fascia_sim.py` | Fascia/Spirals | 26,826 | tap_fascia_sim.py |
| `tap_finance_rescreen.py` | Finance/Economics | 4,904 | tap_finance_rescreen.py |
| `tap_p15_soot_fidelity_sim.py` | Geometry/Visualization | 6,769 | tap_p15_soot_fidelity_sim.py |
| `tap_logistics_prediction.py` | Logistics/Shipping | 13,373 | tap_logistics_prediction.py |
| `tap_multisphere_predictions.py` | Multisphere | 4,901 | tap_multisphere_predictions.py |
| `tap_multiverse_coupling_sim.py` | Multiverse | 5,373 | tap_multiverse_coupling_sim.py |
| `tap_nami_per_body_p1p18.py` | Nami-ryu/Somatic | 7,305 | tap_nami_per_body_p1p18.py |
| `tap_nami_ryu_breath.py` | Nami-ryu/Somatic | 9,442 | tap_nami_ryu_breath.py |
| `tap_per_body_p1p18.py` | Per-body | 8,562 | tap_per_body_p1p18.py |
| `tap_superconductivity_sweep.py` | Per-body | 6,007 | tap_superconductivity_sweep.py |
| `tap_real_data_validator.py` | Real data | 30,921 | tap_real_data_validator.py |
| `render_mermaid_diagrams.py` | Rendering | 13,888 | render_mermaid_diagrams.py |
| `tap_5year_seismic_sweep.py` | Seismic/Geological | 18,334 | tap_5year_seismic_sweep.py |
| `tap_5year_seismic_v2.py` | Seismic/Geological | 10,366 | tap_5year_seismic_v2.py |
| `tap_per_event_seismic.py` | Seismic/Geological | 13,187 | tap_per_event_seismic.py |
| `tap_per_event_seismic_v2.py` | Seismic/Geological | 12,157 | tap_per_event_seismic_v2.py |
| `tap_seismic_correlation.py` | Seismic/Geological | 10,396 | tap_seismic_correlation.py |
| `tap_solar_dynamo.py` | Solar | 2,790 | tap_solar_dynamo.py |
| `tap_tappasecond.py` | Tappasecond | 3,673 | tap_tappasecond.py |
| `run_ratchet_test_auto.py` | Tests/Tribunal | 4,531 | run_ratchet_test_auto.py |
| `tap_audio_test.py` | Tests/Tribunal | 4,997 | tap_audio_test.py |
| `tap_test_framework_challenge.py` | Tests/Tribunal | 8,315 | tap_test_framework_challenge.py |
| `tap_trans_cyclic_sweep.py` | Trans-cyclic | 26,905 | tap_trans_cyclic_sweep.py |
| `tap_unified_social_sim.py` | Unified | 13,845 | tap_unified_social_sim.py |
| `tap_global_weather.py` | Weather/Atmospheric | 8,663 | tap_global_weather.py |
| `tap_weather_backfill.py` | Weather/Atmospheric | 10,214 | tap_weather_backfill.py |
| `tap_weather_recalibration.py` | Weather/Atmospheric | 12,855 | tap_weather_recalibration.py |
| `tap_weather_v2.py` | Weather/Atmospheric | 11,139 | tap_weather_v2.py |
| `tap_weather_v3.py` | Weather/Atmospheric | 10,118 | tap_weather_v3.py |
| `check_env.py` | other | 236 | TAP framework script |
| `dump_descriptors.py` | other | 4,867 | TAP framework script |
| `flash_arduino.py` | other | 8,192 | flash_arduino.py |
| `read_qubit.py` | other | 1,769 | read_qubit.py |
| `run_all_sweeps.py` | other | 11,121 | run_all_sweeps.py |
| `run_coupled_sweep.py` | other | 4,600 | run_coupled_sweep.py |
| `run_tetrahedral_sweep.py` | other | 5,378 | run_tetrahedral_sweep.py |
| `science_constants.py` | other | 1,663 | Centralized scientific constants and observational benchmarks for TAP scripts. |
| `tap_asynchronous_pulsation_sim.py` | other | 10,562 | tap_asynchronous_pulsation_sim.py |
| `tap_biochem_qubit_graphene.py` | other | 4,957 | tap_biochem_qubit_graphene.py |
| `tap_device_coupled_soliton.py` | other | 5,449 | tap_device_coupled_soliton.py |
| `tap_digital_soliton_sim.py` | other | 5,269 | tap_digital_soliton_sim.py |
| `tap_end_to_end_sim.py` | other | 12,425 | tap_end_to_end_sim.py |
| `tap_final_hybrid_predictions.py` | other | 4,830 | tap_final_hybrid_predictions.py |
| `tap_gravitational_waveform.py` | other | 10,510 | tap_gravitational_waveform.py |
| `tap_group_hysteria_sim.py` | other | 6,966 | tap_group_hysteria_sim.py |
| `tap_high_dimension_sequence_sim.py` | other | 6,221 | tap_high_dimension_sequence_sim.py |
| `tap_kp_prediction_sim.py` | other | 11,547 | tap_kp_prediction_sim.py |
| `tap_marketing_contagion_sim.py` | other | 9,080 | tap_marketing_contagion_sim.py |
| `tap_multi_body_p1p18_sweep.py` | other | 9,057 | tap_multi_body_p1p18_sweep.py |
| `tap_multicycle_reset_sweep.py` | other | 14,182 | tap_multicycle_reset_sweep.py |
| `tap_multidiscipline_sweep.py` | other | 4,865 | tap_multidiscipline_sweep.py |
| `tap_muscle_memory_sim.py` | other | 6,639 | tap_muscle_memory_sim.py |
| `tap_neural_resonance.py` | other | 3,043 | tap_neural_resonance.py |
| `tap_option_arbitrage.py` | other | 12,374 | tap_option_arbitrage.py |
| `tap_p16_magnetite_chiral_sim.py` | other | 7,012 | tap_p16_magnetite_chiral_sim.py |
| `tap_p1p18_re_evaluation.py` | other | 9,723 | tap_p1p18_re_evaluation.py |
| `tap_pair_bonding_sim.py` | other | 8,243 | tap_pair_bonding_sim.py |
| `tap_parameter_free_constants_proof.py` | other | 4,929 | tap_parameter_free_constants_proof.py |
| `tap_phone_minimal_soliton.py` | other | 10,237 | tap_phone_minimal_soliton.py |
| `tap_population_sweeps_sim.py` | other | 6,314 | tap_population_sweeps_sim.py |
| `tap_proof.py` | other | 26,796 | tap_proof.py |
| `tap_reset_antitemplate_sim.py` | other | 5,857 | tap_reset_antitemplate_sim.py |
| `tap_schumann_resonance.py` | other | 7,720 | tap_schumann_resonance.py |
| `tap_soliton_collision_stress.py` | other | 5,960 | tap_soliton_collision_stress.py |
| `tap_soliton_shielding_comparison.py` | other | 11,559 | tap_soliton_shielding_comparison.py |
| `tap_somynence_48_sim.py` | other | 21,341 | tap_somynence_48_sim.py |
| `tap_usgs_monitor.py` | other | 3,808 | tap_usgs_monitor.py |
| `tap_viral_epidemiology_sim.py` | other | 6,929 | tap_viral_epidemiology_sim.py |

## 5. Docs (45 total)

| Doc | Title | Size |
|-----|-------|------|
| `INDEX.md` | TAP Model Documentation Index | 10,833 |
| `PEER_REVIEW_CHECKLIST.md` | Peer-Review Checklist for the TAP Cascade Model v5.1 | 11,064 |
| `TAP_12th_Grade_Peer_Review_Curriculum.md` | 🎓 The TAP Model: Advanced Physics Curriculum (12th-Grade / Freshman Level) | 11,307 |
| `TAP_8th_Grade_Fundamentals_Curriculum.md` | 🎒 The TAP Model: A Beginner's Guide (8th-Grade Level) | 12,998 |
| `TAP_Anti_Template_Residue_v5.3.md` | TAP v5.3 — Anti-Template Residue and the Incomplete Reset | 15,494 |
| `TAP_Biochem_Qubit_Graphene_Brainstorm.md` | TAP Model: Biochemical Flows, Low-Tech Qubits, and Graphene Synthesis | 4,296 |
| `TAP_CONNECTIVITY_DASHBOARD.md` | TAP Framework — Connectivity Dashboard | 9,018 |
| `TAP_Capacitor_and_Diode_Inventory.md` | TAP Component Inventory: Capacitors & Diodes | 5,182 |
| `TAP_Cosmic_Origin_of_Life_v5.2.md` | TAP v5.2 — Cosmic Origin of Life and the DNA-as-Receiver Model | 14,093 |
| `TAP_Cosmic_Quantum_Neuro_Brainstorm.md` | TAP Model: Cosmic Resonances, Room-Temperature Qubits, and Interpersonal Coheren | 3,757 |
| `TAP_Coupled_Waveguide_All_Results.md` | Physical Lab Report: Hybrid Electro-Acoustic Waveguide with Capacitor Clock | 5,221 |
| `TAP_Coupled_Waveguide_Brainstorm.md` | Brainstorming: The Coupled Phase-to-Voltage Topological Waveguide | 4,661 |
| `TAP_Coupled_Waveguide_Sweep_Results.md` | Physical Lab Report: Coupled Phase-to-Voltage Topological Waveguide | 4,221 |
| `TAP_DNA_Topology_Epigenetics.md` | DNA as Topology, Epigenetics, and the Source Question | 38,879 |
| `TAP_Daily_Check_2026-07-02.md` | TAP Daily Prediction Check — 2026-07-02 | 9,861 |
| `TAP_Daily_Check_2026-07-02_Deep.md` | TAP Deep Daily Check — 2026-07-02 | 11,292 |
| `TAP_Double_DDCFET_Cascade.md` | Design Specification: The Double-DDCFET Regenerative Cascade Reset (TAP Breath C | 4,710 |
| `TAP_Encyclopedia_v5_3.md` | TAP Encyclopedia v5.3.2 | 6,876 |
| `TAP_Experimental_Designs_v5.3.md` | TAP v5.3 — Experimental Designs for P15-P18 | 12,542 |
| `TAP_FRAMEWORK_INDEX.md` | TAP Framework — Master Index | 19,097 |
| `TAP_Fascia_Trains_v5.md` | TAP v5.0 — Myers' Anatomy Trains, the Twin Dragons, and the Fascia Cascade | 21,428 |
| `TAP_Global_Weather_Operations.md` | TAP Global Weather Engine & Magnetospheric Operations Analysis | 3,853 |
| `TAP_Hardware_Bill_of_Materials.md` | TAP Hardware Bill of Materials (BOM) & Component Logs | 4,963 |
| `TAP_Macro_Qubit_Graphene_Schematic.md` | The TAP Macroscopic Qubit & Graphene Exfoliation Driver | 6,005 |
| `TAP_Multisphere_Biotemplates_v5.3.md` | TAP v5.3 — Multisphere Biotemplates and the Cosmic Origin of Life | 15,928 |
| `TAP_Multisphere_Cascade_Diagram.md` | TAP Multisphere — Visual Cascade Diagram | 17,122 |
| `TAP_Multisphere_Mermaid.md` | TAP Multisphere — Mermaid Diagram | 8,461 |
| `TAP_Multiverse_Constants_Reduction_v5.3.md` | TAP v5.3 — The 7 Multiverse Constants: Reduction to 4 | 7,595 |
| `TAP_Multiverse_Coupling_Framework_v5.3.md` | TAP v5.3 — Multiverse Coupling Framework | 16,112 |
| `TAP_Narby_Review.md` | TAP-Model Review of Jeremy Narby's Science | 16,363 |
| `TAP_P17_Calibration_Constant_v5.3.md` | TAP v5.3 — P17 Reframed: The Calibration Constant κ | 8,567 |
| `TAP_P17_Experimental_Design_v5.3.md` | TAP v5.3 — P17 v3.1 Experimental Design | 8,586 |
| `TAP_P17_Plastic_CubeRoot_v5.3.md` | TAP v5.3 — P17 v3 Resolved: The Plastic Cube Root Derivation | 7,927 |
| `TAP_P2_Lymphangiography_Protocol.md` | TAP v5.0 — Prediction P2: Thoracic Duct Lymph Flow in | 20,603 |
| `TAP_PlanetaryCores_AI_Energy_Brainstorm.md` | TAP Model: The Planetary Core & Industrial compute Cascade | 6,156 |
| `TAP_Qubit_Coherence_Sweep_Results.md` | 🌀 TAP Qubit Coherence Optimization: Parameter Sweep Results | 2,926 |
| `TAP_Ratchet_Sweep_Results.md` | Physical Lab Report: Diode-Capacitor Temporal Ratchet Sweep (Path A) | 3,912 |
| `TAP_Somatic_Cascade.md` | TAP v5.1 — The Somatic Cascade | 19,305 |
| `TAP_Superconductivity_Sweep_Results.md` | ⚡ TAP Superconductivity Optimization: Parameter Sweep Results | 3,347 |
| `TAP_Testable_Predictions_v5.md` | TAP v5.0 — Testable Predictions and Experimental Protocols | 15,683 |
| `TAP_Tetrahedral_Sweep_Results.md` | 📐 TAP Tetrahedral Qubit Bridge: Physical Sweep Results | 3,444 |
| `TAP_Theory_Paper.md` | The Temporal Asymmetric Pulsation (TAP) Model | 16,962 |
| `TAP_White_Paper.md` | The Temporal Asymmetric Pulsation (TAP) Model | 12,560 |
| `TAP_v5_OnePager.md` | TAP v5.0 — One-Page Summary | 3,790 |
| `TAP_v5_Paper.md` | The Tensegrity-Anatomy-Polyvagal (TAP) Cascade Model: | 38,022 |

## 6. Assets (95 total)

| Asset | Size |
|-------|------|
| `tap_5ht2a_ayahuasca_30d.json` | 11,339 |
| `tap_5ht2a_ayahuasca_results.json` | 195,189 |
| `tap_5ht2a_epigenetic_coupling_summary.json` | 602 |
| `tap_5ht2a_tensegrity_30d.json` | 10,748 |
| `tap_5year_seismic_sweep_results.json` | 2,253 |
| `tap_5year_seismic_v2_results.json` | 533 |
| `tap_5year_sweep.json` | 89,714 |
| `tap_asynchronous_pulsation_results.json` | 29,606 |
| `tap_author_lens_mcKenna_audit.json` | 9,475 |
| `tap_author_lens_narby_audit.json` | 7,910 |
| `tap_author_lens_sheldrake_audit.json` | 7,332 |
| `tap_author_lens_wallace_audit.json` | 8,365 |
| `tap_ayahuasca_fascia_cascade_results.json` | 52,103 |
| `tap_biochem_qubit_graphene_results.json` | 508 |
| `tap_body_breath_states_results.json` | 9,383 |
| `tap_breath_clock_chem_results.json` | 110,457 |
| `tap_breath_clock_results.json` | 716 |
| `tap_breath_per_body_results.json` | 5,560 |
| `tap_calibration_constant.json` | 1,555 |
| `tap_cascade_context.json` | 14,798 |
| `tap_chromatin_state_results.json` | 47,171 |
| `tap_collagen_braiding_results.json` | 30,587 |
| `tap_core_ai_coupling.json` | 353 |
| `tap_cosmic_breath_results.json` | 13,012 |
| `tap_cosmic_kp_validation_results.json` | 1,326 |
| `tap_cosmic_origin_results.json` | 439 |
| `tap_cosmic_quantum_neuro_results.json` | 543 |
| `tap_cosmological_cascade_results.json` | 9,728 |
| `tap_coupled_ayahuasca_results.json` | 862,462 |
| `tap_cross_body_coupling_results.json` | 9,558 |
| `tap_daily_check_results.json` | 1,988 |
| `tap_encyclopedia.json` | 9,416 |
| `tap_end_to_end_results.json` | 1,156 |
| `tap_epigenetic_cosmic_cascade_summary.json` | 240 |
| `tap_epigenetic_flop_results.json` | 10,998 |
| `tap_fascia_ayahuasca_results.json` | 239,170 |
| `tap_fascia_stress_results.json` | 239,052 |
| `tap_fascia_summary.json` | 965 |
| `tap_fascia_tensegrity_results.json` | 238,486 |
| `tap_final_hybrid_predictions.json` | 2,582 |
| `tap_finance_rescreen_results.json` | 7,138 |
| `tap_framework_coherence_results.json` | 1,242 |
| `tap_geocosmic_coupling.json` | 335 |
| `tap_global_weather_results.json` | 35,650 |
| `tap_gravitational_waveform_results.json` | 3,684 |
| `tap_group_hysteria_results.json` | 223,463 |
| `tap_high_dimension_results.json` | 9,949 |
| `tap_kp_prediction_results.json` | 418 |
| `tap_logistics_prediction_results.json` | 6,460 |
| `tap_lymphatic_cascade_results.json` | 9,267 |
| `tap_marketing_results.json` | 14,647 |
| `tap_multi_body_p1p18_megamatrix.json` | 105,159 |
| `tap_multicycle_reset_results.json` | 5,761 |
| `tap_multicycle_reset_summary.json` | 356 |
| `tap_multisphere_predictions.json` | 2,765 |
| `tap_multiverse_coupling_results.json` | 167,400 |
| `tap_muscle_memory_results.json` | 8,072 |
| `tap_nami_per_body_p1p18_results.json` | 15,809 |
| `tap_nami_ryu_breath_results.json` | 13,411 |
| `tap_neural_resonance_results.json` | 1,006 |
| `tap_option_arbitrage_results.json` | 309,043 |
| `tap_p15_soot_fidelity_results.json` | 1,391 |
| `tap_p16_magnetite_chiral_results.json` | 1,803 |
| `tap_p1p18_per_body_results.json` | 7,965 |
| `tap_pair_bonding_results.json` | 49,618 |
| `tap_parameter_free_constants_results.json` | 143 |
| `tap_per_body_p1p18_results.json` | 78,426 |
| `tap_per_event_seismic_results.json` | 4,728 |
| `tap_per_event_seismic_v2_results.json` | 15,840 |
| `tap_population_sweeps_results.json` | 302,888 |
| `tap_quantum_decoherence_results.json` | 968 |
| `tap_real_data_validation.json` | 5,790 |
| `tap_reset_antitemplate_results.json` | 7,872 |
| `tap_schumann_resonance_results.json` | 4,661 |
| `tap_seismic_predictions_1year.json` | 68,266 |
| `tap_sim_audit.json` | 9,216 |
| `tap_solar_dynamo_results.json` | 38,688 |
| `tap_somatic_cosmic_geometry_results.json` | 6,736 |
| `tap_somatic_cosmic_geometry_v2_results.json` | 10,851 |
| `tap_somatic_cosmic_v3_results.json` | 12,927 |
| `tap_somynence_48_sim_results.json` | 108,514 |
| `tap_super_tribunal_99_results.json` | 26,479 |
| `tap_test_framework_challenge_results.json` | 3,078 |
| `tap_timeline_results.json` | 2,043 |
| `tap_unified_breath_clock_results.json` | 9,497 |
| `tap_unified_cascade_results.json` | 1,328 |
| `tap_unified_social_results.json` | 541,809 |
| `tap_usgs_monitor_results.json` | 3,504 |
| `tap_viral_epidemiology_results.json` | 1,683 |
| `tap_weather_backfill_results.json` | 1,902 |
| `tap_weather_recalibration_results.json` | 2,582 |
| `tap_weather_v2_results.json` | 1,984 |
| `tap_weather_v3_results.json` | 1,605 |
| `tap_zodiac_to_breath_results.json` | 3,018 |
| `tappasecond_results.json` | 232 |

---

## Statistics

- Total scripts: **107**
- Total docs: **45**
- Total assets: **95**
- Total constants: **12**
- Total predictions: **18** (P1-P18)
- Total concepts: **10**
- Total entries: **287**
