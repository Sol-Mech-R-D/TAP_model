# Design Specification: The Double-DDCFET Regenerative Cascade Reset (TAP Breath Clock)

## The Concept: Two-Transistor Avalanche Emulation
In classical solid-state physics, an **SCR (Silicon Controlled Rectifier)** or thyristor triggers an instant, latching avalanche discharge using a **regenerative feedback loop formed by two interconnected transistors (one NPN and one PNP)**. 

To build a **fully self-contained, passive cascade reset** on our breadboard without active semiconductors (silicon transistors) or microcontroller trigger pins, we construct a **Double-DDCFET (Diode-Capacitor FET) regenerative loop**. This creates a physical **TAP Breath Clock**—a circuit that charges up, reaches a threshold, and then spontaneously triggers its own collapse (reset) back to the ground state.

```
       Pins D3/D5 (AC Drive)
              │
              ▼
       [ DDCFET 1: Timer ] (202uF Gate) ───► Threshold Node F
              │                                      │
              ▼                                      ▼
       [ Schottky Ratchet ] (C2) ◄───────── [ DDCFET 2: Switch ] (1uF Gate)
              │
             GND
```

---

## Circuit Architecture

We have already built **DDCFET 1 (The Timer)** using the $202\,\mu\text{F}$ parallel capacitor clock. Now, we wire in **DDCFET 2 (The Reset Switch)**.

### DDCFET 1 (The Timer):
*   **Gate Capacitance:** $202\,\mu\text{F}$ parallel bank.
*   **Inputs:** Pin D3 and D5 driven through the Schottky OR gate ($D_A, D_B$) to Node E.
*   **Channel Diode ($D_C$):** Connected from Node F to Row 5 (Ratchet input).

### DDCFET 2 (The Reset Switch):
*   **Gate Capacitance:** $1.0\,\mu\text{F}$ film capacitor (marked `105`).
*   **Gate Diode ($D_{\text{gate2}}$):** Connects from Node F to a new empty row (**Node H**).
*   **Channel Diode ($D_{\text{switch}}$):** Connects Node 2 (C2 / A0) to GND via the switch node.

---

## 🔌 Step-by-Step Wiring for DDCFET 2 (The Reset Gate)

Grab **2x 1N5819 Schottky diodes** and **1x $1.0\,\mu\text{F}$ film capacitor** (marked `105`):

1.  **Establish Node H (The Switch Node):** Choose an empty row on your breadboard.
2.  **Gate Diode ($D_{\text{gate2}}$):**
    *   Connect the **Anode (No Band)** to **Row 5 (Ratchet Node 1)**.
    *   Connect the **Cathode (Banded side)** to **Node H**.
3.  **Gate Capacitor ($C_{\text{switch}}$):**
    *   Connect one leg of the **$1.0\,\mu\text{F}$ film capacitor** to **Row 6 (Node 2 / Pin A0)**.
    *   Connect the other leg of this capacitor to **Node H**.
4.  **Channel Diode ($D_{\text{switch}}$):**
    *   Connect the **Anode (No Band)** to **Node H**.
    *   Connect the **Cathode (Banded side)** directly to **Row 7 (GND)**.

---

## 🔬 The Regenerative Avalanche Dynamics (How it Resets Passively)

When you run this Double-DDCFET loop, the circuit governs its own "breathing" cycle:

1.  **The Accumulation Phase (Inhalation):**
    *   As D3 and D5 pulse, they pump charge through the Tetrahedron. The Ratchet rectifies this and builds up voltage on C2 (Row 6).
    *   Simultaneously, the $202\,\mu\text{F}$ clock bank (DDCFET 1) charges up slowly.
2.  **The Trigger Point (The Hold):**
    *   As DDCFET 1's voltage rises, it reaches the Schottky threshold of DDCFET 2 ($D_{\text{gate2}}$).
    *   This forces current into Node H, charging the $1.0\,\mu\text{F}$ gate capacitor ($C_{\text{switch}}$).
3.  **The Spontaneous Collapse (Exhalation):**
    *   The moment the drive pulses stop (or the phase shifts to destructive), the voltage at Node F drops.
    *   This drop pulls Node H negative via $C_{\text{switch}}$.
    *   Because Node H goes negative, it forward-biases the channel diode ($D_{\text{switch}}$), creating a low-resistance short-circuit that instantly dumps C2's energy straight to Ground!
    *   **Result:** The stored voltage on A0 instantly collapses to $0\text{V}$ without any software trigger!

---

## Next Steps: Telemetry and Readout
In this fully passive setup, the Arduino does **not** control D6. We keep D6 completely disconnected. The Arduino simply:
1.  Sends the pulse train (D3/D5).
2.  Monitors A0.
3.  We will observe a **self-driven saw-tooth oscillator waveform** at A0 as the circuit naturally pumps itself up and triggers its own cascade collapses over time!
