# TAP Multisphere — Mermaid Diagram
## GitHub-renderable visualization of the 22-template cascade

**Date:** 2026-07-01
**Source:** `src/tap_cosmological_cascade_sweep.py`

This doc uses **Mermaid** syntax for the multisphere
cascade. Mermaid renders natively in:
  - GitHub markdown (in `.md` files, in issues, in PRs)
  - GitLab markdown
  - VSCode with Mermaid extension
  - Obsidian
  - Most modern markdown editors

---

## Diagram 1: The 4 zones and 22 templates

```mermaid
graph TB
    BC[BREATH CLOCK<br/>N_B ≈ 7-9]
    BC -->|distributes via φ⁻¹³| Z1
    BC -->|distributes via φ⁻¹³| Z2
    BC -->|distributes via φ⁻¹³| Z3
    BC -->|distributes via φ⁻¹³| Z4
    BC -.->|residue| AT[ANTI-TEMPLATES<br/>soot, magnetite, L-D, glass]

    subgraph Z1[ZONE 1: HOT / ACCRETION - T 500-5000K]
        T1[Dusty Plasma Helices<br/>5000K]
        T2[Lanthanide Upconversion<br/>2000K]
        T3[SiC Whiskers<br/>1500K]
        T4[BN Tubes<br/>1200K]
        T5[BCN Braids<br/>900K]
    end

    subgraph Z2[ZONE 2: WARM - T 250-750K]
        T6[Thioester Matrices<br/>300K]
        T7[Ge-Sn Photonic Wafers<br/>320K]
        T8[Fe-S Grids<br/>400K]
        T9[Organosilicon Hybrids<br/>400K]
        T10[Siloxane Helices<br/>450K]
        T11[Carborane Cages<br/>550K]
    end

    subgraph Z3[ZONE 3: TEMPERATE - T 100-300K]
        T12["★ Carbon Biotemplates (DNA)<br/>150K - US"]
        T13[PNA Helices<br/>180K]
        T14[Quadruplet Codon DNA<br/>150K]
        T15[Metallo-Nucleic Wires<br/>200K]
        T16[Se-DNA<br/>200K]
        T17[Germoxane Gels<br/>200K]
        T18[Phosphazene Braids<br/>220K]
    end

    subgraph Z4[ZONE 4: COLD - T 0.5-220K]
        T19[Superfluid Vortex Braids<br/>3K]
        T20[Polythiazyl Helices<br/>8K]
        T21[Fluorocarbon Sleeves<br/>120K]
        T22[Phosphaalkene Ribbons<br/>130K]
    end

    AT -.->|biases| Z1
    AT -.->|biases| Z2
    AT -.->|biases| Z3
    AT -.->|biases| Z4

    style BC fill:#69db7c,stroke:#000,color:#000
    style Z1 fill:#ff6b6b,stroke:#000,color:#fff
    style Z2 fill:#ffa94d,stroke:#000,color:#000
    style Z3 fill:#69db7c,stroke:#000,color:#000
    style Z4 fill:#4dabf7,stroke:#000,color:#000
    style AT fill:#ff006e,stroke:#000,color:#fff
    style T12 fill:#ffd43b,stroke:#000,color:#000
```

---

## Diagram 2: The Bounce → Max Expansion cascade flow

```mermaid
graph LR
    subgraph S0[Step 0: BOUNCHE]
        A0[a=0.050<br/>5/22 active<br/>hot zone only]
    end
    subgraph S5[Step 5: Mid-Expansion 1]
        A5[a=0.189<br/>0/22 active<br/>sterile]
    end
    subgraph S10[Step 10: Mid-Expansion 2]
        A10[a=0.525<br/>0/22 active<br/>sterile]
    end
    subgraph S15[Step 15: Late Expansion]
        A15[a=0.861<br/>15/22 active<br/>temperate emerging]
    end
    subgraph S20[Step 20: MAX EXPANSION]
        A20["a=1.0<br/>17/22 active ★<br/>all cold + most temperate"]
    end

    S0 ==>|"universe expands<br/>T drops"| S5
    S5 ==>|"a=0.5"| S10
    S10 ==>|"a=0.86"| S15
    S15 ==>|"a=1.0"| S20
    S20 -.->|next Inhale| R[RESET]

    style S0 fill:#ff6b6b,color:#fff
    style S5 fill:#666,color:#fff
    style S10 fill:#666,color:#fff
    style S15 fill:#69db7c,color:#000
    style S20 fill:#ffd43b,color:#000
    style R fill:#ff006e,color:#fff
```

---

## Diagram 3: The anti-template contamination cycle

```mermaid
graph TB
    subgraph CYCLE[Exhale - biological activity]
        B0[Max expansion<br/>T=120K<br/>DNA: 1.0<br/>Soot: 0.26<br/>EM: 0.98<br/>Helix: 1.0]
    end
    subgraph CONT[Contraction - contamination]
        B5[Mid-contraction<br/>T=150K<br/>DNA: 1.0<br/>Soot: 0.50<br/>EM: 0.74<br/>Helix: 1.0]
    end
    subgraph CRIT[Critical - DNA denatures]
        B10[Critical<br/>T=182K<br/>DNA: 0.56<br/>Soot: 0.98<br/>EM: 0.55<br/>Helix: 0.79<br/>RACEMIZATION]
    end
    subgraph RESET[Reset complete - substrate dirty]
        B15[Reset<br/>T=200K<br/>DNA: 0.00<br/>Soot: 4.94<br/>EM: 0.13<br/>Helix: 0.07<br/>DIRTY]
    end
    subgraph AT[Anti-templates contaminate]
        AT_S[Soot/PAHs]
        AT_M[Magnetite]
        AT_LD[L-D antagonists]
        AT_G[Amorphous glass]
    end
    subgraph NEXT[Next Exhale - residue-biased]
        NEXT_E[New templates emerge<br/>biased by residue]
    end

    CYCLE ==> CONT
    CONT ==> CRIT
    CRIT ==> RESET
    RESET ==> AT
    AT -->|biases| NEXT
    NEXT ==> CYCLE

    style CYCLE fill:#69db7c,color:#000
    style CONT fill:#ffa94d,color:#000
    style CRIT fill:#ff6b6b,color:#fff
    style RESET fill:#ff006e,color:#fff
    style AT fill:#ff006e,color:#fff
    style NEXT fill:#69db7c,color:#000
    style AT_S fill:#000,color:#fff
    style AT_M fill:#000,color:#fff
    style AT_LD fill:#000,color:#fff
    style AT_G fill:#000,color:#fff
```

---

## Diagram 4: The cascade architecture (φ-rate layers)

```mermaid
graph TB
    HORM["φ⁻² HORMONAL (hours)<br/>parent sim, 5-HT2A chem<br/>cortisol/serotonin baseline"]
    SIG["φ⁻⁴ SIGNALING (minutes)<br/>5-HT2A binding, piezo<br/>solar, seismic, all sims"]
    REC["φ⁻⁸ RECEPTOR (days)<br/>sensitivity_setpoint<br/>BDNF, HTR2A"]
    CHR["φ⁻¹⁰ CHROMATIN (weeks)<br/>HTR2A/NR3C1 openness<br/>s_setpoint remodeling"]
    COS["φ⁻¹³ COSMIC (years)<br/>N_B, Γ(N_B), breath clock<br/>cosmic breath, trans-cyclic"]
    MULT["φ⁻¹⁶⁺ MULTISPHERE<br/>22 biotemplates<br/>4 cosmic zones<br/>anti-template residue"]
    SUB["braid SUBSTRATE (parallel)<br/>collagen, fascia spirals<br/>lymph, piezo<br/>twin dragons"]

    HORM -->|"chemical signals"| SIG
    SIG -->|"receptor dynamics"| REC
    REC -->|"chromatin state"| CHR
    CHR -->|"breath clock mod"| COS
    COS -->|"multisphere dep"| MULT
    MULT -.->|"template #3<br/>carbon DNA"| HORM

    SUB -.->|parallel at all timescales| HORM
    SUB -.->|parallel| SIG
    SUB -.->|parallel| REC
    SUB -.->|parallel| CHR
    SUB -.->|parallel| COS
    SUB -.->|parallel| MULT

    style HORM fill:#ffd43b,color:#000
    style SIG fill:#69db7c,color:#000
    style REC fill:#4dabf7,color:#000
    style CHR fill:#cc5de8,color:#fff
    style COS fill:#ff6b6b,color:#fff
    style MULT fill:#ff006e,color:#fff
    style SUB fill:#adb5bd,color:#000
```

---

## Diagram 5: Testable predictions summary (P1-P18)

```mermaid
graph LR
    subgraph CASCADE["Cascade predictions (P1-P6)"]
        P1["P1: opposite signatures<br/>ayahuasca vs tensegrity"]
        P2["P2: lymph flow +15-25%<br/>in tensegrity"]
        P3["P3: fidelity up, piezo down<br/>(counter-intuitive)"]
        P4["P4: 180° spiral phase<br/>rotational antenna"]
        P5["P5: transgenerational<br/>HTR2A chromatin"]
        P6["P6: Nami-ryu specific<br/>spiral coupling"]
    end
    subgraph COSMIC["Cosmic origin (P7-P10)"]
        P7["P7: codon table<br/>correlates with φ⁻ⁿ"]
        P8["P8: L-excess<br/>correlates with Γ(N_B)"]
        P9["P9: Nami-ryu<br/>N_B-correction"]
        P10["P10: 13 templates max<br/>13D Weyl ceiling"]
    end
    subgraph MULTI["Multisphere (P11-P14)"]
        P11["P11: template dist<br/>correlates with Γ(N_B)"]
        P12["P12: cross-zone coupling<br/>detectable"]
        P13["P13: carbon is special<br/>only self-replicating"]
        P14["P14: 13 templates max<br/>verified"]
    end
    subgraph ANTI["Anti-template (P15-P18)"]
        P15["P15: soot-rich zones<br/>lower fidelity"]
        P16["P16: magnetite<br/>stronger chiral seed"]
        P17["P17: N_B = residue<br/>saturation threshold"]
        P18["P18: Earth is<br/>anomalously clean"]
    end

    style CASCADE fill:#69db7c,color:#000
    style COSMIC fill:#ff6b6b,color:#fff
    style MULTI fill:#ffa94d,color:#000
    style ANTI fill:#ff006e,color:#fff
```

---

## How to use this doc

1. **View in GitHub**: the Mermaid blocks render
   automatically when this `.md` file is viewed on
   github.com
2. **View in VSCode**: install the "Markdown Preview
   Mermaid Support" extension
3. **View in Obsidian**: Mermaid is supported natively
4. **Embed in academic papers**: convert to PNG via
   [mermaid.live](https://mermaid.live) and include as
   figures

The diagrams are also available in:
  - `assets/tap_multisphere_cascade.html` (interactive
    HTML)
  - `docs/TAP_Multisphere_Cascade_Diagram.md` (ASCII art)
  - `docs/TAP_Multisphere_Biotemplates_v5.3.md` (8-template
    v5.3 framing)
  - `docs/TAP_Anti_Template_Residue_v5.3.md` (anti-template
    finding)
  - `docs/TAP_FRAMEWORK_INDEX.md` (master index)
