/*
 * tap_piezo_chassis.scad
 * =======================
 * Parametric 3D-Printable Clamping Chassis for the TAP 20mm Dual Piezo Acoustic Qubit.
 * Designed for David Baker (Delta Vector)
 * 
 * Instructions:
 * 1. Open this file in OpenSCAD (https://openscad.org).
 * 2. Adjust parameters in the section below if using different piezo sizes or bolt diameters.
 * 3. Render (F6) and Export as STL (F7) for slicing and 3D printing.
 * 
 * Assembly Notes:
 * - Use non-conductive Nylon M3 bolts and nuts to prevent electrical shorting or signal coupling.
 * - Place Tx piezo in the Bottom Chassis, add Mylar/Paper/Copper stackup, then align Top Chassis.
 * - Tighten bolts lightly and evenly to avoid cracking the ceramic piezo coatings.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;                      // Resolution of circles

piezo_dia = 20.0;               // Nominal diameter of piezo disc (mm)
piezo_brass_thick = 0.25;       // Thickness of brass base plate (mm)
piezo_ceramic_dia = 15.0;       // Diameter of active ceramic area (mm)
piezo_ceramic_thick = 0.25;     // Extra thickness of ceramic layer + solder joints (mm)

clearance = 0.3;                // Print clearance (added to recesses for fit)
wall_thickness = 4.0;           // Outer structural wall thickness (mm)
chassis_height = 8.0;           // Total thickness of each chassis half (mm)

screw_dia = 3.2;                // Hole diameter for M3 bolts (mm)
screw_head_dia = 6.0;           // Pocket diameter for screw head / nut (mm)
screw_head_depth = 3.5;         // Pocket depth for screw head / nut recess (mm)
screw_offset = 14.5;            // Distance from center to bolt holes (mm)

wire_channel_w = 3.5;           // Width of wire escape slot (mm)
wire_channel_d = 2.0;           // Depth of wire escape slot (mm)

// Calculated dimensions
inner_fit_dia = piezo_dia + clearance;
outer_dia = (screw_offset + screw_head_dia/2 + wall_thickness) * 2;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
// Render both parts side-by-side for printing:
translate([-outer_dia/2 - 5, 0, 0]) bottom_chassis();
translate([outer_dia/2 + 5, 0, 0]) top_chassis();

// ─── MODULES ────────────────────────────────────────────────────────────────

module bottom_chassis() {
    difference() {
        // Main body + male alignment guide ring
        union() {
            cylinder(d=outer_dia, h=chassis_height);
            // Alignment collar (male joint)
            translate([0, 0, chassis_height])
                difference() {
                    cylinder(d=inner_fit_dia + 4, h=3);
                    cylinder(d=inner_fit_dia, h=4);
                }
        }
        
        // 1. Recess for Tx Piezo Brass Flange
        translate([0, 0, chassis_height - piezo_brass_thick])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 4);
            
        // 2. Center relief pocket for fragile ceramic + solder joints
        translate([0, 0, chassis_height - piezo_brass_thick - piezo_ceramic_thick - 1.5])
            cylinder(d=piezo_ceramic_dia + clearance, h=piezo_ceramic_thick + 1.5);
            
        // 3. Central acoustic viewport / transducer access hole
        translate([0, 0, -1])
            cylinder(d=piezo_ceramic_dia - 2.0, h=chassis_height + 2);
            
        // 4. Radial wire egress channel
        translate([0, -wire_channel_w/2, chassis_height - wire_channel_d - piezo_brass_thick])
            cube([outer_dia/2 + 5, wire_channel_w, wire_channel_d + 10]);
            
        // 5. 3x Bolt Holes with nut recesses
        bolt_pattern();
    }
}

module top_chassis() {
    difference() {
        // Main body
        cylinder(d=outer_dia, h=chassis_height);
        
        // 1. Recess for Rx Piezo Brass Flange (facing up)
        translate([0, 0, chassis_height - piezo_brass_thick])
            cylinder(d=inner_fit_dia, h=piezo_brass_thick + 4);
            
        // 2. Center relief pocket for Rx ceramic element
        translate([0, 0, chassis_height - piezo_brass_thick - piezo_ceramic_thick - 1.5])
            cylinder(d=piezo_ceramic_dia + clearance, h=piezo_ceramic_thick + 1.5);
            
        // 3. Central acoustic viewport
        translate([0, 0, -1])
            cylinder(d=piezo_ceramic_dia - 2.0, h=chassis_height + 2);
            
        // 4. Radial wire egress channel
        translate([0, -wire_channel_w/2, chassis_height - wire_channel_d - piezo_brass_thick])
            cube([outer_dia/2 + 5, wire_channel_w, wire_channel_d + 10]);
            
        // 5. Female alignment ring recess
        translate([0, 0, chassis_height - 3])
            difference() {
                cylinder(d=inner_fit_dia + 4.5, h=4);
                cylinder(d=inner_fit_dia - 0.2, h=5);
            }
            
        // 6. 3x Bolt Holes with screw head recesses
        bolt_pattern();
    }
}

module bolt_pattern() {
    for (a = [0, 120, 240]) {
        rotate([0, 0, a]) {
            // Main screw shaft
            translate([screw_offset, 0, -1])
                cylinder(d=screw_dia, h=chassis_height + 15);
                
            // Recess for head / locknut
            translate([screw_offset, 0, -0.1])
                cylinder(d=screw_head_dia, h=screw_head_depth + 0.1);
        }
    }
}
