/*
 * tap_graphene_exfoliation_mount.scad
 * ====================================
 * 3D-Printable 50mm Ultrasonic Transducer Graphene Exfoliation Mount.
 * Designed for David Baker (Delta Vector)
 * 
 * Securely holds a 50mm 40kHz ultrasonic piezo transducer and centers 
 * a standard 20mm (or 16mm) glass vial or test tube directly on its active face.
 * Uses a twist-lock cap to clamp the vial base against the transducer.
 * 
 * 💡 ACOUSTIC COUPLING TIP:
 * Put a small drop of water or mineral oil on the face of the transducer 
 * before sliding the vial in. This liquid coupling agent prevents air gaps, 
 * ensuring maximum 40kHz acoustic shear wave transmission into the liquid!
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;

transducer_dia = 50.0;          // Nominal diameter of ultrasonic transducer (mm)
transducer_recess_d = 5.0;      // Depth of transducer mounting seat (mm)
clearance = 0.5;                // Print clearance (mm)

vial_dia = 20.0;                // Diameter of the test tube / vial (mm)
vial_clearance = 0.4;           // Clearance for the vial slide
sleeve_clearance = 0.4;         // Mating cap tolerance clearance (mm)

sleeve_height = 40.0;           // Height of the vertical sleeve guide (mm)
wall_thickness = 4.0;           // Wall thickness of guide sleeve (mm)

pin_height = 2.0;               // Bayonet locking pin parameters
pin_width = 3.0;
pin_depth = 1.2;

// Calculated dimensions
inner_fit_trans = transducer_dia + clearance;
inner_fit_vial = vial_dia + vial_clearance;
outer_dia = inner_fit_trans + wall_thickness * 2;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
// Render both parts side-by-side for printing:
translate([-outer_dia/2 - 5, 0, 0]) base_mount();
translate([outer_dia/2 + 5, 0, 0]) top_clamp_cap();

// ─── MODULES ────────────────────────────────────────────────────────────────

module base_mount() {
    difference() {
        // Main outer cylindrical guide housing
        cylinder(d=outer_dia, h=sleeve_height);
        
        // 1. Bottom pocket to seat the 50mm Transducer
        translate([0, 0, -0.1])
            cylinder(d=inner_fit_trans, h=transducer_recess_d + 0.1);
            
        // 2. Central vertical guide hole for the vial
        translate([0, 0, transducer_recess_d - 0.1])
            cylinder(d=inner_fit_vial, h=sleeve_height - transducer_recess_d + 0.2);
            
        // 3. Side slot for wire connections to the transducer face
        translate([-10/2, -outer_dia/2 - 1, -0.1])
            cube([10, outer_dia/2 + 2, transducer_recess_d + 1]);
            
        // 4. Acoustic viewports (3 slots cut in side to monitor liquid cavitation)
        for (a = [60, 180, 300]) {
            rotate([0, 0, a])
                translate([0, 0, sleeve_height/2])
                    cube([outer_dia + 2, 6.0, 15.0], center=true);
        }
    }
    
    // Add 3x Bayonet locking pins on the outer top rim
    for (a = [0, 120, 240]) {
        rotate([0, 0, a]) {
            translate([outer_dia/2 - 0.1, -pin_width/2, sleeve_height - 6.0])
                cube([pin_depth + 0.1, pin_width, pin_height]);
        }
    }
}

module top_clamp_cap() {
    // Sliding cap that slips over the vial neck and twist-locks onto base
    difference() {
        // Cap body
        cylinder(d=outer_dia + sleeve_clearance + 3.0, h=10.0);
        
        // 1. Internal socket to slip over the base housing
        translate([0, 0, -1])
            cylinder(d=outer_dia + 0.4, h=8.5);
            
        // 2. Central clearance hole for the vial neck / cap
        translate([0, 0, -2])
            cylinder(d=inner_fit_vial + 2.0, h=15);
            
        // 3. 3x L-shaped Bayonet Entry Slots + Compression Ramps
        for (a = [0, 120, 240]) {
            rotate([0, 0, a]) {
                // Vertical entry from the bottom rim
                translate([(outer_dia + 0.4)/2 - 0.1, -pin_width/2 - 0.3, -1.1])
                    cube([pin_depth + 0.4, pin_width + 0.6, 5.0]);
                
                // Horizontal locking slot with compression ramp
                for (step = [0 : 3 : 24]) {
                    rotate([0, 0, step])
                        translate([(outer_dia + 0.4)/2 - 0.1, -pin_width/2 - 0.3, 3.9 - (step * 0.03)])
                            cube([pin_depth + 0.4, pin_width + 0.6, pin_height + 0.4]);
                }
            }
        }
    }
}
