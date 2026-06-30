# TAP Integrated Cascade Circuit: Schematic & Breadboard Layout
## Dual-Excitation Phase Mixer, Schottky Ratchet, and Passive Reset Switch

This document defines the integrated hardware wiring for the 6-capacitor Tetrahedron bridge coupled to the DDC charge-accumulation and passive-reset cascade.

---

## 🗺️ 1. Complete System Schematic

```
   Arduino D3 (In A) ─── Node A ───[ Capacitor Tetrahedron ]
                                           │
   Arduino D5 (In B) ─── Node B ───[ Mixing Node C ]
                                           │
                                           ▼ (AC Mixed Wave)
                                    [ 1N5819 Schottky Ratchet ]
                                           │
                                           ▼ (DC Charge)
     Arduino A0 (Telemetry) ◄─────────── Node E (Reservoir / C_clock)
                                           │
                             ┌─────────────┴─────────────┐
                             ▼                           ▼
                     [ DDC2x1U202F Clock ]      [ DDC1X1U100F Reset Switch ]
                             │                           │
                            GND                         GND
```

---

## 🔌 2. Step-by-Step Breadboard Layout

### Step 1: The Tetrahedron Bridge (Nodes A, B, C, D)
Establish four separate columns/rows on your breadboard:
1.  **Row 1 (Node A):** Connect to **Arduino Pin D3**.
2.  **Row 2 (Node B):** Connect to **Arduino Pin D5**.
3.  **Row 3 (Node C):** The Output/Mixing Node.
4.  **Row 4 (Node D):** Connect to **GND** (shared reference).

**Capacitor Connections:**
*   **Boundary Loop ($27\text{ nF}$):**
    *   Connect one $27\text{ nF}$ cap between **Row 1 (Node A)** and **Row 2 (Node B)**.
    *   Connect one $27\text{ nF}$ cap between **Row 2 (Node B)** and **Row 3 (Node C)**.
    *   Connect one $27\text{ nF}$ cap between **Row 3 (Node C)** and **Row 1 (Node A)**.
*   **Ground Shunts ($10\text{ nF}$):**
    *   Connect one $10\text{ nF}$ cap between **Row 1 (Node A)** and **Row 4 (Node D/GND)**.
    *   Connect one $10\text{ nF}$ cap between **Row 2 (Node B)** and **Row 4 (Node D/GND)**.
    *   Connect one $10\text{ nF}$ cap between **Row 3 (Node C)** and **Row 4 (Node D/GND)**.

---

### Step 2: The Schottky Ratchet (The Charger)
1.  Choose a new column/row: **Row 5 (Node E / Reservoir)**.
2.  Connect the **Anode (no band)** of a `1N5819` Schottky diode to **Row 3 (Node C)**.
3.  Connect the **Cathode (banded side)** of this diode to **Row 5 (Node E)**.

---

### Step 3: The Capacitor Clock (`DDC2x1U202F`)
1.  Connect the positive legs of your parallel capacitor bank (2x $100\,\mu\text{F}$ electrolytic + 2x $1.0\,\mu\text{F}$ film caps) to **Row 5 (Node E)**.
2.  Connect the negative legs of the capacitor bank directly to **Row 4 (Node D/GND)**.
3.  Connect a jumper wire from **Row 5 (Node E)** to **Arduino Pin A0** (to monitor the charging and discharging voltage).

---

### Step 4: The Passive Reset Switch (`DDC1X1U100F`)
To trigger the spontaneous discharge when the clock saturates:
1.  Choose a blank row for the **Switch Gate (Node H)**.
2.  **Gate Diode:** Connect the Anode (no band) of a `1N5819` diode to **Row 5 (Node E)**, and the Cathode (banded side) to **Node H**.
3.  **Gate Capacitor:** Connect one leg of a $1.0\,\mu\text{F}$ film capacitor to **Row 5 (Node E)**, and the other leg to **Node H**.
4.  **Channel Diode (The Dump Switch):** Connect the Anode (no band) of a `1N5819` diode to **Node H**, and the Cathode (banded side) to **Row 4 (Node D/GND)**.
