/*
 * tap_piezo_droplet_mount.scad
 * =============================
 * 3D-Printable Surface Acoustic Wave (SAW) Droplet Mount for 20mm Piezo.
 * Designed for David Baker (Delta Vector)
 * 
 * Holds a 20mm piezo disc horizontally with the ceramic side facing UP.
 * Features a shallow retaining ring to hold a drop of water directly 
 * on the piezo face for visual resonance tests at 4.5 kHz.
 * 
 * ⚠️ WATERPROOFING NOTE:
 * You MUST paint a thin layer of clear nail polish, silicone, or hot glue over 
 * the solder joints and exposed copper wires before adding water to prevent 
 * the water drop from shorting the Tx signal to GND.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;

piezo_dia = 20.0;               // Nominal brass disc diameter (mm)
piezo_brass_thick = 0.25;       // Brass plate thickness (mm)
clearance = 0.2;                // Fit clearance (mm)

base_dia = 32.0;                // Outer base diameter (mm)
base_height = 8.0;              // Total height of the base mount (mm)
lip_height = 1.0;               // Height of the water retention dam (mm)

wire_egress_w = 3.0;            // Wire slot width
wire_egress_d = 2.0;            // Wire slot depth

// Calculated dimensions
inner_fit_dia = piezo_dia + clearance;
ceramic_well_dia = 15.0;        // Open diameter exposing the active area

// ─── MODEL ──────────────────────────────────────────────────────────────────
difference() {
    // Main solid cylinder (base + raised lip)
    cylinder(d=base_dia, h=base_height + lip_height);
    
    // 1. Recess for the 20mm Piezo Brass Flange
    translate([0, 0, base_height])
        cylinder(d=inner_fit_dia, h=lip_height + 0.1);
        
    // 2. Central well to expose the ceramic area to the water drop
    translate([0, 0, base_height - 1.5])
        cylinder(d=ceramic_well_dia, h=2.0);
        
    // 3. Under-shelf relief for solder joints and wires
    translate([0, 0, 1.5])
        cylinder(d=inner_fit_dia - 2, h=base_height - 3.0);
        
    // 4. Wire egress slot running out the bottom side
    translate([-wire_egress_w/2, -base_dia/2 - 1, -0.1])
        cube([wire_egress_w, base_dia/2 + 2, wire_egress_d + 0.1]);
        
    // 5. Central wire pass-through hole leading to the under-shelf relief
    translate([0, 0, -1])
        cylinder(d=4.0, h=base_height + 2);
}
