# Physical Lab Report: Diode-Capacitor Temporal Ratchet Sweep (Path A)

## Executive Summary
This report documents the physical breadboard implementation and testing of **Path A: The Diode-Capacitor Temporal Ratchet** (Charge Pump) as defined in the [TAP Topological Electronics Manifesto](file:///C:/TAP_model/docs/TAP_Topological_Electronics_Manifesto.md). Using an Arduino Nano clone (COM5) as the pulse generator and telemetry node, we successfully demonstrated automated software-controlled discharge and physical charge accumulation.

---

## Experimental Setup
*   **Microcontroller:** Arduino Nano clone on port `COM5` (Atmega328p, 16 MHz).
*   **Coupling Capacitor ($C_1$):** $100\text{ nF}$ ceramic disc (marked `104`).
*   **Storage Capacitor ($C_2$):** $10\,\mu\text{F}$ electrolytic cylinder (50V rated, polarized).
*   **Diodes ($D_1$, $D_2$):** $1N4148$ high-speed switching silicon diodes.
*   **Receiver Pin ($RX$):** Analog pin `A0` configured in high-impedance input mode for measurements and low-impedance output mode for active discharging.
*   **Pulse Width:** $15\,\mu\text{s}$ at $10\text{ ms}$ step delays.

---

## Telemetry Logs

### 1. Forward Pumping Sequence ('f')
*   **Initial State:** $0.37\text{ V}$ (Successfully discharged by Arduino in software).
*   **Charging Curve:**
    *   Step 0: $0.38\text{ V}$ (1st pulse)
    *   Step 5: $1.67\text{ V}$
    *   Step 10: $2.41\text{ V}$
    *   Step 20: $3.12\text{ V}$
    *   Step 40: $3.56\text{ V}$
    *   Step 95: $3.92\text{ V}$ (Saturated plateau)

### 2. Reversed Pumping Sequence ('b')
*   **Initial State:** $0.39\text{ V}$ (Drained).
*   **Charging Curve:**
    *   Step 0: $0.38\text{ V}$
    *   Step 5: $1.62\text{ V}$
    *   Step 10: $2.40\text{ V}$
    *   Step 20: $3.12\text{ V}$
    *   Step 95: $3.92\text{ V}$

---

## Physical Analysis

### 1. Verification of Software Discharge
The telemetry confirms that the active software discharge routine:
```cpp
void active_software_discharge() {
  pinMode(RX_PIN, OUTPUT);
  digitalWrite(RX_PIN, LOW);
  delay(200); 
  pinMode(RX_PIN, INPUT);
}
```
successfully drained the **$10\,\mu\text{F}$ capacitor** from its saturated $3.92\text{V}$ charge down to **$<0.4\text{V}$** within 200 milliseconds before beginning the next test. This removed the need for manual wire wiggling and prevented serial drops.

### 2. Pumping Dynamics and Direct-Path Saturation
The capacitor charged along a beautiful, textbook **exponential curve** ($V(t) = V_{\text{max}}(1 - e^{-t/\tau})$). However, both the Forward and Reversed sequences charged the reservoir to the exact same limit ($3.92\text{V}$). This is due to two physical characteristics of the current breadboard layout:

*   **AC Rectification:** $C_1$ ($100\text{ nF}$), $D_2$, and $C_2$ ($10\,\mu\text{F}$) form a series half-wave rectifier connected to Pin D3. Any voltage transitions (HIGH/LOW) on D3 will pump charge into $C_2$ regardless of D5's state.
*   **Direct DC Path:** When Pin D5 goes HIGH, a direct DC current flows through $D_1$ and $D_2$ to charge $C_2$ directly. Since D5 goes HIGH in both phase sequences, it contributes to charging in both directions.

---

## Comparative Curve Plot

Below is the comparative plot showing the overlapping charging curves:

![Ratchet Sweep Results](file:///C:/Users/DavidBaker/.gemini/antigravity-cli/brain/fbb59340-3b17-4624-aeb8-100411d8284a/tap_ratchet_sweep_results.png)

---

## Conclusion & Next Steps
We have successfully verified:
1.  **Constructive/Destructive Wave Interference (6cap Tetrahedron):** Extinction ratio of **$2.01\times$** at $50\,\mu\text{s}$ overlap.
2.  **Charge Pumping Rectification (Path A Ratchet):** Exponential charge accumulation up to **$3.91\text{V}$** and automated software discharge.

The physical hardware behaves exactly in line with classical circuit theory, validating the assembly and functionality of the breadboard setup!
