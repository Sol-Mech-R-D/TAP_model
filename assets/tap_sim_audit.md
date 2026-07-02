# TAP Sim Audit — Cascade Primitive Coverage

## 10 sims audited

| Sim | Cascade layer | Primitives | Chemicals | Verdict |
|-----|---------------|------------|-----------|---------|
| tap_epigenetic_flop_sim | hormonal (φ⁻²) + epigenetic setpoint (φ⁻¹⁰) | 100% | 100% | TAP-AUGMENTED |
| tap_5ht2a_ayahuasca_sim | signaling (φ⁻⁴) + receptor (φ⁻⁸) + setpoint (φ⁻¹⁰) | 100% | 100% | TAP-AUGMENTED |
| tap_chromatin_state_sim | chromatin (φ⁻¹⁰) | 100% | 100% | TAP-AUGMENTED |
| tap_coupled_ayahuasca_sim | 5-HT2A ↔ chromatin (φ⁻⁸ ↔ φ⁻¹⁰) | 100% | 100% | TAP-AUGMENTED |
| tap_epigenetic_cosmic_cascade | epigenetic (φ⁻¹⁰) → cosmic (φ⁻¹³) | 100% | 100% | TAP-AUGMENTED |
| tap_5ht2a_epigenetic_coupling_sim | 5-HT2A ↔ parent sim (bidirectional) | 100% | 100% | TAP-AUGMENTED |
| tap_fascia_sim | substrate (fascia, φ⁻¹⁰ + braid) | 92% | 100% | TAP-AUGMENTED |
| tap_lymphatic_cascade_sim | epigenetic → substrate → lymph (φ⁻¹⁰) | 100% | 100% | TAP-AUGMENTED |
| tap_ayahuasca_fascia_cascade_sim | all layers (5-HT2A → chromatin → parent → fascia) | 100% | 100% | TAP-AUGMENTED |
| tap_collagen_braiding_sim | substrate (collagen braid, local quantum) | 86% | 100% | TAP-AUGMENTED |

## Verdict summary

- TAP-AUGMENTED: 10
- TAP-LEGAL:     0
- TAP-ILLEGAL:   0
- TAP-SILENT:    0
- Mean coverage: 0.98

## Per-sim details

### tap_epigenetic_flop_sim

- **Cascade layer:** hormonal (φ⁻²) + epigenetic setpoint (φ⁻¹⁰)
- **Real substrate:** HPA axis, steroidogenesis, epigenetics
- **Tests passed:** v4.0.1: s_setpoint 0.5→0.582 in 30d
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_5ht2a_ayahuasca_sim

- **Cascade layer:** signaling (φ⁻⁴) + receptor (φ⁻⁸) + setpoint (φ⁻¹⁰)
- **Real substrate:** 5-HT2A receptor, MAO inhibition
- **Tests passed:** Riba 2.05% err, Callaway 7.14% err
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_chromatin_state_sim

- **Cascade layer:** chromatin (φ⁻¹⁰)
- **Real substrate:** Chromatin state, 3D genome, TADs
- **Tests passed:** 6/6 modelable biomarkers MATCH
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_coupled_ayahuasca_sim

- **Cascade layer:** 5-HT2A ↔ chromatin (φ⁻⁸ ↔ φ⁻¹⁰)
- **Real substrate:** Receptor-chromatin coupling
- **Tests passed:** Coupled sim 2.19% err
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_epigenetic_cosmic_cascade

- **Cascade layer:** epigenetic (φ⁻¹⁰) → cosmic (φ⁻¹³)
- **Real substrate:** Epigenetic-cosmic timing coupling
- **Tests passed:** Tensegrity shifts cosmic breath tick 14%
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_5ht2a_epigenetic_coupling_sim

- **Cascade layer:** 5-HT2A ↔ parent sim (bidirectional)
- **Real substrate:** Receptor-epigenetic bidirectional coupling
- **Tests passed:** Tensegrity 0.58, ayahuasca 0.38, opposite
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_fascia_sim

- **Cascade layer:** substrate (fascia, φ⁻¹⁰ + braid)
- **Real substrate:** Myofascial network, piezo collagen, lymph
- **Tests passed:** 4/4 verifications PASS, 12 trains modeled
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 0.92
- **Chemicals coverage:** 1.00
- **Missing primitives:** twin_dragons

### tap_lymphatic_cascade_sim

- **Cascade layer:** epigenetic → substrate → lymph (φ⁻¹⁰)
- **Real substrate:** Lymphatic circulation in tensegrity state
- **Tests passed:** Both verifications PASS
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_ayahuasca_fascia_cascade_sim

- **Cascade layer:** all layers (5-HT2A → chromatin → parent → fascia)
- **Real substrate:** Full ayahuasca pathway through substrate
- **Tests passed:** 7/7 PASS, cosmic breath +67%
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 1.00
- **Chemicals coverage:** 1.00

### tap_collagen_braiding_sim

- **Cascade layer:** substrate (collagen braid, local quantum)
- **Real substrate:** Collagen triple helix, anyonic qubit
- **Tests passed:** 100% coherence modulation by somatic state
- **Verdict:** TAP-AUGMENTED
- **Primitives coverage:** 0.86
- **Chemicals coverage:** 1.00
- **Missing primitives:** gate_fidelity

