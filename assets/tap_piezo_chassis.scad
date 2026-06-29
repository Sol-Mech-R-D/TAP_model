/*
 * tap_piezo_chassis.scad
 * =======================
 * Toolless Closed-Chamber (Reverb Room) Acoustic Qubit Chassis 
 * for the TAP 20mm Dual Piezo.
 * 
 * Replaces the paper/Mylar spacer layers with a sealed 3D-printed air cavity.
 * Drives Tx directly from Arduino Pin 5, reads Rx on Pin A1.
 * 
 * Assembly Notes:
 * - Insert Tx piezo in the Bottom Chassis cup (wires out the side slot).
 * - Insert Rx piezo in the Top Cap cup (wires out the side slot).
 * - Align pins, push together, and twist clockwise to seal the acoustic chamber.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;                      // Circle resolution

piezo_dia = 20.0;               // Nominal diameter of piezo brass disc (mm)
piezo_brass_thick = 0.25;       // Thickness of brass base plate (mm)
piezo_ceramic_dia = 15.0;       // Diameter of active ceramic area (mm)
piezo_ceramic_thick = 0.25;     // Extra thickness of ceramic layer + solder joints (mm)

clearance = 0.3;                // Print clearance (added to recesses for fit)
sleeve_clearance = 0.4;         // Clearance between mating parts (mm)

chassis_height = 10.0;          // Height of each main plate (mm)
pin_height = 2.0;               // Vertical size of locking pin (mm)
pin_width = 3.0;                // Angular width of locking pin (mm)
pin_depth = 1.2;                // Depth the pin protrudes (mm)

wire_channel_w = 3.5;           // Width of wire escape slot (mm)
wire_channel_d = 2.0;           // Depth of wire escape slot (mm)

// Chamber spacing (air gap height between Tx and Rx piezos when locked)
chamber_air_gap = 4.0;          // Height of the reverb room cavity (mm)

// Calculated dimensions
inner_fit_dia = piezo_dia + clearance;
mate_inner_dia = inner_fit_dia + 4;
mate_outer_dia = mate_inner_dia + sleeve_clearance;
body_outer_dia = mate_outer_dia + 6;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
translate([-body_outer_dia/2 - 5, 0, 0]) bottom_chassis();
translate([body_outer_dia/2 + 5, 0, 0]) top_cap();

// ─── MODULES ────────────────────────────────────────────────────────────────

module bottom_chassis() {
    difference() {
        // Main base body + male alignment guide column
        union() {
            cylinder(d=body_outer_dia, h=chassis_height);
            // Alignment collar (male joint)
            translate([0, 0, chassis_height])
                cylinder(d=mate_inner_dia, h=6);
        }
        
        // 1. Recess for Tx Piezo Brass Flange (sits on the shelf)
        translate([0, 0, chassis_height + 6 - piezo_brass_thick])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 1);
            
        // 2. Sealed Acoustic Reverb Room Cavity (extends down below the shelf)
        // This forms the lower half of the closed speaker box
        translate([0, 0, chassis_height + 6 - piezo_brass_thick - chamber_air_gap/2])
            cylinder(d=piezo_ceramic_dia + clearance, h=chamber_air_gap/2 + 0.1);
            
        // 3. Radial wire egress channel in the base
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, chassis_height + 6 - wire_channel_d - piezo_brass_thick])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d + 1]);
    }
    
    // Add 3x Bayonet Locking Pins on the collar
    for (a = [0, 120, 240]) {
        rotate([0, 0, a]) {
            translate([mate_inner_dia/2 - 0.1, -pin_width/2, chassis_height + 2.0])
                cube([pin_depth + 0.1, pin_width, pin_height]);
        }
    }
}

module top_cap() {
    difference() {
        // Main body of the cap
        cylinder(d=body_outer_dia, h=chassis_height + 8);
        
        // 1. Female socket to receive the bottom chassis collar
        translate([0, 0, -1])
            cylinder(d=mate_outer_dia, h=8.5);
            
        // 2. Recess for Rx Piezo Brass Flange (facing down toward Tx)
        translate([0, 0, 7.5])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 1);
            
        // 3. Sealed Acoustic Reverb Room Cavity (extends up above the shelf)
        // This forms the upper half of the closed speaker box
        translate([0, 0, 7.5 - chamber_air_gap/2])
            cylinder(d=piezo_ceramic_dia + clearance, h=chamber_air_gap/2 + 0.1);
            
        // 4. Radial wire egress channel in the cap
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, 7.5])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d + 1]);
            
        // 5. 3x L-shaped Bayonet Entry Slots + Compression Ramps
        for (a = [0, 120, 240]) {
            rotate([0, 0, a]) {
                // Vertical entry slot from the bottom rim
                translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, -1.1])
                    cube([pin_depth + 0.4, pin_width + 0.6, 4.5]);
                
                // Horizontal locking slot with compression ramp
                for (step = [0 : 3 : 30]) {
                    rotate([0, 0, step])
                        translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, 2.9 - (step * 0.02)])
                            cube([pin_depth + 0.4, pin_width + 0.6, pin_height + 0.4]);
                }
            }
        }
    }
}
