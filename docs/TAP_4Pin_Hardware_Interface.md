# TAP 4-Pin Hardware Telemetry Interface Specification
## Microcontroller-to-Cascade Coupling Protocol

This document defines the 4-pin physical interface between the Arduino Nano controller and the autonomous analog cascade circuit. 

---

## 📐 1. The 4-Pin Interface Map

```
  ┌────────────────────────────────────────────────────────┐
  │                      ARDUINO NANO                      │
  └───────┬──────────────┬──────────────┬───────────┬──────┘
          │              │              │           │
          ▼ (D3)         ▼ (D5)         ▼ (GND)     ▼ (A0)
     [ Feeder 1 ]   [ Feeder 2 ]     [ Ground ]  [ Listener ]
          │              │              │           │
  ┌───────┼──────────────┼──────────────┼───────────┼──────┐
  │       ▼              ▼              ▼           ▼      │
  │                  AUTONOMOUS CASCADE CIRCUIT            │
  └────────────────────────────────────────────────────────┘
```

| Pin Name | Direction | Physical Role | Electrical Function |
|:---:|:---:|:---|:---|
| **D3** | Output (MCU to Circuit) | Feeder 1 | Phase-controlled AC wave excitation (Row 1 Tx) |
| **D5** | Output (MCU to Circuit) | Feeder 2 | Phase-controlled AC wave excitation (Row 5 Tx) |
| **GND** | Reference | Common Ground | System Ground reference for all capacitors and return paths |
| **A0** | Input (Circuit to MCU) | Listener | High-speed analog telemetry readout (Node 2 / C2 voltage) |

---

## ⚡ 2. Functional Roles

### A. The Feeders (D3 & D5)
*   **Signal Profile:** High-frequency square/sine waves (typically $2\text{ kHz}$ to $15\text{ kHz}$).
*   **Control Method:** The Arduino adjusts the frequency ($f$) and the phase delay ($\Delta \theta$) between D3 and D5 to inject energy constructively or destructively into the Schottky ratchets.
*   **Decoupled Operation:** The feeders do *not* act as the system clock. They only supply raw AC power and phase modulation to trigger the circuit's internal states.

### B. The Listener (A0)
*   **Readout Method:** Connected directly to the telemetry node of the DDC/ADC capacitor clock.
*   **Protection:** Clamped via a $1\text{ M}\Omega$ static drain resistor and a $5.1\text{ V}$ Zener diode to protect the ATmega328P input.
*   **ADC Tuning:** The Arduino ADC clock prescaler is set to 16, boosting the sampling speed to $\approx 77\text{ kHz}$ to prevent aliasing.

### C. The Ground (GND)
*   Connects the Arduino ground plane to the central ground node of the 6-capacitor tetrahedral bridge, shunting common-mode noise directly out of the analog calculation space.
