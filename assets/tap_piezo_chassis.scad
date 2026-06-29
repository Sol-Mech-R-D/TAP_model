/*
 * tap_piezo_chassis.scad
 * =======================
 * Toolless Twist-Lock (Bayonet-Style) Clamping Chassis 
 * for the TAP 20mm Dual Piezo Acoustic Qubit.
 * 
 * Instructions:
 * 1. Open this file in OpenSCAD (https://openscad.org).
 * 2. Render (F6) and Export as STL (F7) for slicing and 3D printing.
 * 
 * Assembly Notes:
 * - Place Tx piezo in the Bottom Chassis, add your Mylar/Paper/Copper stackup.
 * - Place Rx piezo in the Top Cap.
 * - Align the three pins with the L-slots, press together, and twist clockwise.
 * - The built-in compression ramps will pull the halves together and clamp the sandwich.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;                      // Circle resolution

piezo_dia = 20.0;               // Nominal diameter of piezo disc (mm)
piezo_brass_thick = 0.25;       // Thickness of brass base plate (mm)
piezo_ceramic_dia = 15.0;       // Diameter of active ceramic area (mm)
piezo_ceramic_thick = 0.25;     // Extra thickness of ceramic layer + solder joints (mm)

clearance = 0.3;                // Print clearance (added to recesses for fit)
sleeve_clearance = 0.4;         // Clearance between mating parts (mm)

chassis_height = 8.0;           // Height of each main plate (mm)
pin_height = 2.0;               // Vertical size of locking pin (mm)
pin_width = 3.0;                // Angular width of locking pin (mm)
pin_depth = 1.2;                // Depth the pin protrudes (mm)

wire_channel_w = 3.5;           // Width of wire escape slot (mm)
wire_channel_d = 2.0;           // Depth of wire escape slot (mm)

// Calculated dimensions
inner_fit_dia = piezo_dia + clearance;
mate_inner_dia = inner_fit_dia + 4;
mate_outer_dia = mate_inner_dia + sleeve_clearance;
body_outer_dia = mate_outer_dia + 6;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
// Render both parts side-by-side for printing:
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
                cylinder(d=mate_inner_dia, h=7);
        }
        
        // 1. Recess for Tx Piezo Brass Flange
        translate([0, 0, chassis_height + 7 - piezo_brass_thick])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 1);
            
        // 2. Center relief pocket for fragile ceramic + solder joints
        translate([0, 0, chassis_height + 7 - piezo_brass_thick - piezo_ceramic_thick - 1.5])
            cylinder(d=piezo_ceramic_dia + clearance, h=piezo_ceramic_thick + 1.5);
            
        // 3. Central acoustic viewport / access hole through bottom
        translate([0, 0, -1])
            cylinder(d=piezo_ceramic_dia - 2.0, h=chassis_height + 10);
            
        // 4. Wire egress channel (runs down the collar and out the side)
        // Vertical slot in collar
        translate([-wire_channel_w/2, -mate_inner_dia/2 - 1, chassis_height])
            cube([wire_channel_w, mate_inner_dia + 2, 8]);
        // Radial channel in base
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, chassis_height - wire_channel_d])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d + 0.1]);
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
        cylinder(d=body_outer_dia, h=chassis_height + 9);
        
        // 1. Female socket to receive the bottom chassis collar
        translate([0, 0, -1])
            cylinder(d=mate_outer_dia, h=9.5);
            
        // 2. Recess for Rx Piezo Brass Flange (facing down toward Tx)
        translate([0, 0, 8.5])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 1);
            
        // 3. Center relief pocket for Rx ceramic element
        translate([0, 0, 8.5 + piezo_brass_thick])
            cylinder(d=piezo_ceramic_dia + clearance, h=piezo_ceramic_thick + 1.5);
            
        // 4. Central acoustic viewport through top of cap
        translate([0, 0, 8.5])
            cylinder(d=piezo_ceramic_dia - 2.0, h=chassis_height + 10);
            
        // 5. Wire egress channel in the cap
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, 8.5])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d]);
            
        // 6. 3x L-shaped Bayonet Entry Slots + Compression Ramps
        for (a = [0, 120, 240]) {
            rotate([0, 0, a]) {
                // Vertical entry slot from the bottom rim
                translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, -1.1])
                    cube([pin_depth + 0.4, pin_width + 0.6, 4.5]);
                
                // Horizontal locking slot with compression ramp
                // Sweeps 30 degrees to pull the pin tighter
                for (step = [0 : 3 : 30]) {
                    rotate([0, 0, step])
                        translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, 2.9 - (step * 0.02)])
                            cube([pin_depth + 0.4, pin_width + 0.6, pin_height + 0.4]);
                }
            }
        }
    }
}
