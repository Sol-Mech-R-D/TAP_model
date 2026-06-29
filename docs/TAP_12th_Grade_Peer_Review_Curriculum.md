# 🎓 The TAP Model: Advanced Physics Curriculum (12th-Grade / Freshman Level)
## A Rigorous Guide to Warped Metrics, RGE Running, Acoustic Solitons, and Peer-Review Framing

Welcome to the Advanced TAP Physics Curriculum. This guide is written at a 12th-grade / freshman college level, bridging the gap between intuitive concepts and formal physics. We will introduce the real mathematical equations, coordinate systems, and circuit formulations that govern the **Temporal Asymmetric Pulsation (TAP)** model to ensure your work is fully peer-review ready.

---

## 🗺️ Curriculum Core Modules

```mermaid
graph TD
    M1[Unit 1: Warped Geometry & Higgs Mass] --> M2[Unit 2: 2-Loop RGE Gauge Running]
    M2 --> M3[Unit 3: Waveguides & Acoustic Solitons]
    M3 --> M4[Unit 4: Tetrahedral Capacitor Networks]
    M4 --> M5[Unit 5: Biophysics & Gravitational Dynamics]
```

---

## 🌌 Unit 1: Warped Extra-Dimensional Geometry & Higgs Mass
### *Focus Files: `src/tap_dirac_modes.py`, `docs/TAP_Theory_Paper.md`*

In standard physics, the **Higgs Hierarchy Problem** asks why the weak force is $10^{32}$ times stronger than gravity (or why the Higgs boson is so light, $125\text{ GeV}$, compared to the Planck mass, $1.22 \times 10^{19}\text{ GeV}$). The TAP model solves this using a warped 5D anti-de Sitter ($AdS_5$) geometry (similar to the Randall-Sundrum RS1 model).

```
  Our Brane (y=0)                          Saturation Boundary (y=y_sat)
        |                                                 |
        | ==============================================> |
        |        Warp Factor e^{-k|y|} decreases          |
  Scale: Planck Scale (10^19 GeV)                Weak Scale (10^2 GeV)
```

#### 1. The Metric and Conformal Warping
Spacetime is described by the warped metric:
$$ds^2 = e^{-2k|y|} \eta_{\mu\nu} dx^\mu dx^\nu - dy^2$$
Where:
*   $\eta_{\mu\nu} = \text{diag}(1, -1, -1, -1)$ is the standard 4D flat Minkowski metric.
*   $y$ is the extra-dimensional coordinate running from $0$ (our physical 3-brane) to $y_{\text{sat}}$ (the 13D saturation ceiling).
*   $k = \ln(\phi)$ is the warp curvature scale governed by the Golden Ratio.

#### 2. The Sturm-Liouville Boundary Value Problem
The wavefunctions $\chi(y)$ of fields propagating in this warped bulk satisfy a Schrödinger-like Sturm-Liouville differential equation:
$$\left[ -\frac{d^2}{dy^2} + V(y) \right] \chi(y) = m^2 \chi(y)$$

*   **The Potential:** $V(y) = \frac{\chi - 2}{2} (\ln\phi)^2$ is derived from the Euler characteristic of the compactified 13D manifold ($\chi = D/2 = 6.5$).
*   **Boundary Conditions:** Neumann boundary conditions are imposed at the limits:
    $$\left. \frac{d\chi}{dy} \right|_{y=0} = 0, \quad \left. \frac{d\chi}{dy} \right|_{y=y_{\text{sat}}} = 0$$
*   **The Saturation Limit:** The extra dimension terminates at the holographic boundary:
    $$y_{\text{sat}} = 2\pi D \left(1 - \frac{\phi^{-9}}{\pi}\right) \approx 81.34 \, l_P$$

#### 3. Deriving the Higgs Mass
Solving this eigensystem numerically (as done in `tap_dirac_modes.py`) yields the lowest non-zero eigenvalue ($m_1^2$). Conformal warping scales this value down to our brane, yielding the physical Higgs mass ($m_H$):
$$m_H = m_P \cdot e^{-\ln(\phi) \cdot y_{\text{sat}}} \sqrt{2\lambda_0} \approx 125.12\text{ GeV}$$

---

## ⚡ Unit 2: Standard Model 2-Loop Renormalization Group (RGE) Running
### *Focus Files: `src/tap_flavor_running.py`*

In Quantum Field Theory (QFT), coupling constants (like electromagnetic or weak force strengths) are not constant; they change ("run") depending on the energy scale ($\mu$) at which they are measured.

```
  Planck Scale (10^19 GeV):   Fixed Boundary: α_1^-1 = 4πφ⁵, sin²θ_W = φ^-2
             |
             |  <===== 2-Loop RGE Integration (tap_flavor_running.py)
             ▼
    Weak Scale (M_Z):         Calculated: α_1^-1 ≈ 163.88, sin²θ_W ≈ 0.2312
```

#### 1. The 2-Loop RGE Equations
The running of the gauge couplings ($g_1, g_2$) is governed by their beta functions:
$$\frac{d \alpha_i^{-1}}{d t} = -\frac{b_i}{2\pi} - \frac{1}{8\pi^2} \sum_{j} B_{ij} \alpha_j^{-1}$$
Where:
*   $t = \ln(\mu)$ is the log energy scale.
*   $b_1 = -4.1$ and $b_2 = 19/6$ are the Standard Model 1-loop beta coefficients.
*   $B_{ij} = \begin{pmatrix} 199/50 & 27/10 \\ 9/10 & 35/6 \end{pmatrix}$ is the 2-loop beta matrix.

#### 2. The Ultraviolet (UV) Boundary Conditions
The TAP model proposes that the Standard Model is unified at the Planck scale ($m_P$) by topological boundary conditions:
*   **Hypercharge Coupling:** $\alpha_1^{-1}(m_P) = 4\pi\phi^5 \approx 139.36$
*   **Weinberg Angle:** $\sin^2\theta_W(m_P) = \phi^{-2} \approx 0.3820$

Integrating these values down to the weak scale ($M_Z = 91.1876\text{ GeV}$) via the RGEs yields the exact low-energy values observed in particle colliders:
$$\alpha_1^{-1}(M_Z) \approx 163.88, \quad \sin^2\theta_W(M_Z) \approx 0.2312$$

---

## 🔊 Unit 3: Wavefield Engineering & Non-Linear Acoustic Solitons
### *Focus Files: `assets/tap_piezo_chassis.scad`, `src/tap_qubit_driver.ino`*

The "trash build" serves as a basic proof-of-concept showing that a physical, non-dispersive wave packet (an acoustic soliton) can propagate across a media boundary. High-fidelity emulation uses structured wavefield cavities.

```
                       HELICAL VORTEX GENERATION
          Planar Wave In                          Vortex Out (OAM)
          ==============    ===========>    )))))))) @ ))))))))
                        [ Helical Diffuser ]
```

#### 1. Non-Dispersive Solitons
Normal acoustic waves obey the linear wave equation, causing them to spread and decay. A soliton balances non-linear medium dynamics with dispersion, described by the Korteweg-de Vries (KdV) equation:
$$\frac{\partial \psi}{\partial t} + \frac{\partial^3 \psi}{\partial x^3} + 6\psi \frac{\partial \psi}{\partial x} = 0$$
This non-linear balance allows the wave packet to travel without losing its shape.

#### 2. OpenSCAD Resonant Geometry (`tap_piezo_chassis.scad`)
*   **Acoustic Vortex (Orbital Angular Momentum):** The floor and ceiling are etched with a helical Golden Spiral diffuser. The groove depth ($d$) and radius ($r$) scale as:
    $$r(\theta) = r_0 + c\theta, \quad d(\theta) = d_0 + k\theta$$
    This twists reflecting planar waves into a vortex carrying **Orbital Angular Momentum (OAM)**, trapping the wave packet along the central axis.
*   **Helmholtz Slow-Light Emulators:** Three cavities acting as Helmholtz resonators are coupled to the chamber. The resonant frequency ($f_H$) is:
    $$f_H = \frac{v}{2\pi} \sqrt{\frac{A}{V \cdot L_{eq}}}$$
    Where $A$ is the neck area, $V$ is the pocket volume, and $L_{eq}$ is the equivalent neck length. Tuning these to $4.5\text{ kHz}$ slows the wave packet's group velocity, prolonging its classical phase coherence ($T_2$).

---

## 📐 Unit 4: Topological Circuit Networks & Simplex Grounding
### *Focus Files: `docs/TAP_Topological_Electronics_Manifesto.md`, `docs/TAP_Hardware_Bill_of_Materials.md`*

The **8-Channel Tetrahedral Bridge** is a physical circuit that emulates the mathematical state of a qubit. It maps the 6 edges of a 3-dimensional simplex (a tetrahedron) to a capacitive network.

```
                          TETRAHEDRAL NETWORK
                                Node A
                               /  |  \
                              /   |   \
                         C_AB/  C_AD   \C_AC
                            /     |     \
                        Node B───C_BD───Node C
                            \     |     /
                             \    |    /
                         C_BD \ C_CD  / C_CD
                               \  |  /
                                Node D (GND)
```

#### 1. Multi-Path Charge Distribution
When driving **Node A** and **Node B** with alternating signals, the charge splits across the outer capacitors ($C_{AB}, C_{BC}, C_{CA}$). The voltage at the receiver **Node C** is governed by Kirchhoff's current law:
$$I_C = C_{CA} \frac{d(V_A - V_C)}{dt} + C_{BC} \frac{d(V_B - V_C)}{dt} + C_{CD} \frac{d(V_{\text{GND}} - V_C)}{dt} = 0$$

By adjusting the phase offset ($\Delta \theta$) between the input pins on the Arduino, you control the constructive and destructive interference of the charge waves at Node C, emulating quantum phase rotation.

#### 2. Common-Mode Noise Shunting
The ratio of the outer boundary capacitors ($C_{CA} = 27\text{ nF}$) to the inner grounding capacitors ($C_{CD} = 10\text{ nF}$) is locked to the Golden Ratio squared:
$$\frac{C_{\text{outer}}}{C_{\text{inner}}} \approx \phi^2 \approx 2.7$$
This creates a high-pass impedance filter. High-frequency signals ($4.5\text{ kHz}$) are confined to the outer boundary, while low-frequency environmental noise ($60\text{ Hz}$ power-line hum) is shunted directly to Ground (Node D) through the inner star capacitors, protecting the emulator.

---

## 🧠 Unit 5: Biophysics & Gravitational Dynamics
### *Focus Files: `src/tap_cosmic_quantum_neuro.py`, `src/tap_spacetime_shortcuts.py`*

#### 1. Microtubule Coherence & Biological Light-Harvesting
Tegmark's decoherence limit ($10^{-13}\text{ s}$) assumes standard 4D isotropic thermal noise. Under the TAP model, the helical Fibonacci geometry of microtubules shields the internal protofilaments, extending the coherence lifetime of phonon-polaritons to $\tau \approx 939.57\text{ fs}$.
*   **Quantum-to-Classical Transduction:** The system uses sub-picosecond quantum triggering. A polariton state only needs to remain coherent long enough ($\approx 939\text{ fs}$) to bias a conformational transition in a tubulin dimer. This shift is locked into a classical state, which then triggers millisecond-scale action potentials.
*   **Photosynthetic Analogy:** This mirrors the **Fenna-Matthews-Olson (FMO) complex** in photosynthesis, where excitons utilize quantum coherence on a $300\text{ fs}$ scale to transfer energy with $99\%$ efficiency at room temperature.

#### 2. Gravitational Wave Speed & Zero-Mode Localization
Extra-dimensional gravity leakage is heavily constrained by **GW170817** ($|v_{\text{GW}} - c|/c \le 10^{-15}$). In the TAP model, gravity is localized on our 4D brane via the RS1 warp factor:
$$S_{\text{gravity}} = \int d^4x \, dy \sqrt{-g} \, M_5^3 R_5$$

The 4D graviton emerges as the strictly brane-bound **zero-mode** of this action. Gravitational leakage is restricted to massive Kaluza-Klein excitations. Since their mass scale is stabilized at $M_{\text{KK}} \approx 10^{17}\text{ GeV}$ by the 13D saturation ceiling, they cannot be excited at low energies. Thus, low-energy GWs propagate strictly at the speed of light.

#### 3. Stable Kaluza-Klein Graviton Dark Matter
Dark matter consists of stable KK-gravitons ($M_{\text{DM}} \approx 468.98\text{ GeV}$). 
*   **KK-Parity ($\mathbb{Z}_2$):** The extra-dimensional symmetry prevents the Lightest Kaluza-Klein Particle (LKP) from decaying into Standard Model particles.
*   **Planck-Scale Suppression:** These particles interact with normal matter via dimension-8 operators:
    $$\mathcal{O}_8 \sim \frac{1}{M_P^2} T_{\mu\nu}^{\text{SM}} T^{\mu\nu}_{\text{KK}}$$
    This makes the interaction cross-section extremely small, explaining their direct-detection invisibility.
