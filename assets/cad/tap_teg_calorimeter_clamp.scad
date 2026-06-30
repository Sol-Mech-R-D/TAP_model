/*
 * tap_teg_calorimeter_clamp.scad
 * ===============================
 * 3D-Printable 3-TEG Calorimeter Sandwich Clamp.
 * Designed for David Baker (Delta Vector)
 * 
 * Clamps a stack of three 40mm x 40mm thermoelectric modules (Peltier-Spacer-TEG-Peltier)
 * using a toolless twist-lock bayonet cap to ensure uniform thermal contact.
 * 
 * Assembly Stack:
 * 1. Peltier 1 (Heater) at the bottom.
 * 2. Your test material (e.g. 5mm 3D printed Fibonacci spacer).
 * 3. TEG 2 (Sensor) in the middle.
 * 4. Peltier 3 (Cooler) at the top.
 * 5. Slide the Plunger in, and twist the Bayonet Cap clockwise to compress the stack.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;

teg_size = 40.0;                // Nominal size of Peltier/TEG module (mm)
clearance = 0.6;                // Slide clearance (mm)
wall_thickness = 4.0;           // Outer housing wall thickness (mm)

stack_max_height = 25.0;        // Maximum height of the Peltier+Spacer stack (mm)
housing_height = 32.0;          // Total height of the outer casing (mm)

wire_slot_w = 12.0;             // Width of the side slot for wire egress (mm)

// Calculated dimensions
chamber_size = teg_size + clearance;
outer_dia = (chamber_size + wall_thickness * 2) * 1.15;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
// Render the three parts side-by-side for printing:
translate([-outer_dia/2 - 5, 0, 0]) calorimeter_housing();
translate([outer_dia/2 + 5, 0, 0]) pressure_plunger();
translate([0, outer_dia + 10, 0]) bayonet_cap();

// ─── MODULES ────────────────────────────────────────────────────────────────

module calorimeter_housing() {
    difference() {
        // Main cylindrical outer body
        cylinder(d=outer_dia, h=housing_height);
        
        // 1. Square chamber for the 40mm TEG modules
        translate([-chamber_size/2, -chamber_size/2, -0.1])
            cube([chamber_size, chamber_size, housing_height + 0.2]);
            
        // 2. Wide side slot for wire egress
        translate([-wire_slot_w/2, -outer_dia/2 - 1, -0.1])
            cube([wire_slot_w, outer_dia + 2, housing_height - 6.0]);
            
        // 3. 3x L-shaped Bayonet Slots on the outer rim (120 degree spacing)
        for (a = [0, 120, 240]) {
            rotate([0, 0, a]) {
                // Vertical entry from the top rim
                translate([outer_dia/2 - 1.5, -2.0, housing_height - 6.1])
                    cube([4.0, 4.0, 6.5]);
                
                // Horizontal locking slot with compression ramp
                for (step = [0 : 3 : 24]) {
                    rotate([0, 0, step])
                        translate([outer_dia/2 - 1.5, -2.0, housing_height - 9.0 - (step * 0.05)])
                            cube([4.0, 4.0, 3.2]);
                }
            }
        }
    }
}

module pressure_plunger() {
    // A square plunger block that slides down on top of the TEG stack
    // It has a circular top boss for the bayonet cap to push against
    union() {
        // Square slide plate
        cube([chamber_size - 0.6, chamber_size - 0.6, 5.0], center=true);
        // Circular contact boss
        translate([0, 0, 2.5])
            cylinder(d=28.0, h=4.0);
    }
}

module bayonet_cap() {
    // A twist-lock cap that pushes the plunger down
    difference() {
        union() {
            // Cap outer ring
            cylinder(d=outer_dia, h=8.0);
            
            // Central pressing plunger boss extending downwards
            translate([0, 0, -3.0])
                cylinder(d=26.0, h=3.1);
        }
        
        // Large hollow center (finger grip recess)
        translate([0, 0, 3.0])
            cylinder(d=outer_dia - 8.0, h=6.0);
            
        // Finger grip ribs
        for (i = [0:12:360]) {
            rotate([0, 0, i])
                translate([outer_dia/2 - 1, -1, 3.0])
                    cube([3, 2, 6]);
        }
    }
    
    // Add 3x Locking Pins pointing inwards from the cap rim
    for (a = [0, 120, 240]) {
        rotate([0, 0, a]) {
            translate([outer_dia/2 - 3.8, -1.5, -4.5])
                cube([2.2, 3.0, 2.0]);
        }
    }
}
