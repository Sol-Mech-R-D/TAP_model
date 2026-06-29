/*
 * tap_octahedral_cabinet.scad
 * ============================
 * 3D-Printable 8-Channel Fibonacci Octahedral Qubit Cabinet.
 * Designed for David Baker (Delta Vector)
 * 
 * Splits along the equator into two square pyramids (Bottom and Top Cap).
 * Holds 8x 20mm Piezo Brass Discs (4 Tx, 4 Rx) facing a shared central cavity.
 * Uses a toolless twist-lock bayonet ring at the equator to seal the chamber.
 * 
 * Assembly Notes:
 * - Insert 4 piezos into the Bottom Pyramid faces (routes wires down).
 * - Insert 4 piezos into the Top Pyramid faces (routes wires up).
 * - Align the equatorial collar pins, push together, and twist clockwise to lock.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;                      // Resolution

piezo_dia = 20.0;               // Nominal piezo diameter (mm)
piezo_brass_thick = 0.25;       // Brass plate thickness (mm)
piezo_ceramic_dia = 15.0;       // Active ceramic area (mm)
piezo_ceramic_thick = 0.25;     // Ceramic + solder joint clearance (mm)

clearance = 0.3;                // Tolerances for piezo seats
sleeve_clearance = 0.4;         // Mating collar tolerance

face_thickness = 4.0;           // Thickness of the pyramid walls (mm)
pyramid_size = 42.0;            // Base size of the square pyramid (mm)

pin_height = 2.0;               // Bayonet pin size
pin_width = 3.0;                
pin_depth = 1.2;                

wire_channel_w = 3.0;           // Wire slot width
wire_channel_d = 1.5;           // Wire slot depth

// Octahedron Angles
tilt_angle = 35.264;            // Angle of faces relative to horizontal (90 - 54.736)
face_height = pyramid_size * sqrt(3)/2; 

// Mating collar dimensions
mate_inner_dia = pyramid_size - 4;
mate_outer_dia = mate_inner_dia + sleeve_clearance;
body_outer_dia = pyramid_size + 8;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
// Render both halves side-by-side for printing:
translate([-body_outer_dia/2 - 5, 0, 0]) bottom_pyramid();
translate([body_outer_dia/2 + 5, 0, 0]) top_pyramid();

// ─── MODULES ────────────────────────────────────────────────────────────────

module bottom_pyramid() {
    difference() {
        union() {
            // Main square pyramid shell (truncated at the bottom base)
            pyramid_shell(pyramid_size, face_thickness);
            
            // Circular male mating collar rising from base
            translate([0, 0, 0])
                difference() {
                    cylinder(d=mate_inner_dia, h=5);
                    cylinder(d=mate_inner_dia - 4, h=6);
                }
        }
        
        // Subtract 4x Piezo Pockets on the tilted faces
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
                translate([0, pyramid_size/4 + 1, pyramid_size/4])
                    rotate([tilt_angle, 0, 0])
                        piezo_pocket_subtraction();
        }
        
        // Hollow out center chamber
        translate([0, 0, -1])
            cylinder(d=mate_inner_dia - 4, h=pyramid_size);
    }
    
    // Add 4x Bayonet Pins on the circular collar (90 deg spacing)
    for (a = [0, 90, 180, 270]) {
        rotate([0, 0, a]) {
            translate([mate_inner_dia/2 - 0.1, -pin_width/2, 1.5])
                cube([pin_depth + 0.1, pin_width, pin_height]);
        }
    }
}

module top_pyramid() {
    difference() {
        // Main square pyramid shell
        pyramid_shell(pyramid_size, face_thickness);
        
        // Subtract 4x Piezo Pockets on the tilted faces
        for (i = [0:3]) {
            rotate([0, 0, i * 90])
                translate([0, pyramid_size/4 + 1, pyramid_size/4])
                    rotate([tilt_angle, 0, 0])
                        piezo_pocket_subtraction();
        }
        
        // Hollow out center chamber
        translate([0, 0, -1])
            cylinder(d=mate_inner_dia - 4, h=pyramid_size);
            
        // Female socket to receive the bottom collar
        translate([0, 0, -0.1])
            cylinder(d=mate_outer_dia, h=4.0);
            
        // 4x L-shaped Bayonet Entry Slots + Compression Ramps
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a]) {
                // Vertical entry
                translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, -1.1])
                    cube([pin_depth + 0.4, pin_width + 0.6, 3.0]);
                
                // Horizontal locking slot with compression ramp
                for (step = [0 : 3 : 24]) {
                    rotate([0, 0, step])
                        translate([mate_outer_dia/2 - 0.1, -pin_width/2 - 0.3, 1.9 - (step * 0.02)])
                            cube([pin_depth + 0.4, pin_width + 0.6, pin_height + 0.4]);
                }
            }
        }
    }
}

// Helper to draw a square pyramid shell
module pyramid_shell(size, wall) {
    difference() {
        // Outer Solid Pyramid
        cylinder(r1=size/sqrt(2), r2=0, h=size/sqrt(2), $fn=4);
        
        // Inner Truncated Pyramid (hollow)
        translate([0, 0, -0.1])
            cylinder(r1=size/sqrt(2) - wall, r2=0, h=size/sqrt(2) - wall/2, $fn=4);
    }
}

// Subtraction module for each face's piezo slot and wire channels
module piezo_pocket_subtraction() {
    inner_fit_dia = piezo_dia + clearance;
    
    // 1. Viewport / Acoustic path into inner chamber
    translate([0, 0, -10])
        cylinder(d=piezo_ceramic_dia - 2.0, h=20);
        
    // 2. Recess for Brass Plate flange
    translate([0, 0, -piezo_brass_thick])
        cylinder(d=inner_fit_dia, h=piezo_brass_thick + 0.1);
        
    // 3. Relief pocket for Ceramic element + solder connections
    translate([0, 0, -piezo_brass_thick - piezo_ceramic_thick])
        cylinder(d=piezo_ceramic_dia + clearance, h=piezo_ceramic_thick + 0.1);
        
    // 4. Wire Egress Channel leading down the face to the equator
    translate([-wire_channel_w/2, -inner_fit_dia/2 - 15, -wire_channel_d])
        cube([wire_channel_w, 20, wire_channel_d + 0.1]);
}
