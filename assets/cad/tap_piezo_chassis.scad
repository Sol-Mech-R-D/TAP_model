/*
 * tap_piezo_chassis.scad
 * =======================
 * Closed-Chamber (Reverb Room) Acoustic Qubit Chassis 
 * with 13:5 Fibonacci Aspect Ratio, Helical Golden Spiral Diffusers,
 * Helmholtz Reverb Pockets, and Curved Fibonacci Deflector Fins.
 * 
 * Height: 5.0mm (F5) | Diameter: 13.0mm (F7) | Ratio: 2.60 ≈ phi^2
 * Drives Tx directly from Arduino Pin 5, reads Rx on Pin A1.
 */

// ─── PARAMETERS ─────────────────────────────────────────────────────────────
$fn = 100;                      // Circle resolution

piezo_dia = 20.0;               // Nominal diameter of piezo brass disc (mm)
piezo_brass_thick = 0.25;       // Thickness of brass base plate (mm)
piezo_ceramic_dia = 15.0;       // Diameter of active ceramic area (mm)
piezo_ceramic_thick = 0.25;     // Extra thickness of ceramic layer + solder joints (mm)

clearance = 0.3;                // Print clearance (added to recesses for fit)
sleeve_clearance = 0.4;         // Clearance between mating parts (mm)

chassis_height = 11.0;          // Height of each main plate (mm)
pin_height = 2.0;               // Vertical size of locking pin (mm)
pin_width = 3.0;                // Angular width of locking pin (mm)
pin_depth = 1.2;                // Depth the pin protrudes (mm)

wire_channel_w = 3.5;           // Width of wire escape slot (mm)
wire_channel_d = 2.0;           // Depth of wire escape slot (mm)

// --- TAP Fibonacci-Locked Chamber Geometry ---
chamber_air_gap = 5.0;          // Height = 5.0mm (F5)
chamber_dia = 13.0;              // Diameter = 13.0mm (F7) -> Ratio = 13/5 = 2.60 ≈ phi^2

use_spiral_diffuser = true;     // Toggle helical Golden Spiral diffusers

// Calculated dimensions
inner_fit_dia = piezo_dia + clearance;
mate_inner_dia = inner_fit_dia + 4;
mate_outer_dia = mate_inner_dia + sleeve_clearance;
body_outer_dia = mate_outer_dia + 6;

// ─── RENDERING SELECTION ────────────────────────────────────────────────────
translate([-body_outer_dia/2 - 5, 0, 0]) bottom_chassis();
translate([body_outer_dia/2 + 5, 0, 0]) top_cap();

// ─── MODULES ────────────────────────────────────────────────────────────────

// Unified Chamber Cavity Module containing Helmholtz Reverb Pockets 
// and solid curved Fibonacci deflector fins.
module chamber_cavity(h_half) {
    difference() {
        union() {
            // Main cylinder cavity
            cylinder(d=chamber_dia, h=h_half + 0.1);
            
            // 3x Helmholtz Reverb Pockets (placed at 60, 180, 300 degrees to avoid bayonets)
            // Tuned as Helmholtz resonators to amplify and store the 4.5 kHz acoustic wave
            for (a = [60, 180, 300]) {
                rotate([0, 0, a]) {
                    // Resonant neck/throat
                    translate([chamber_dia/2 - 0.5, -0.6, 0])
                        cube([2.0, 1.2, h_half + 0.1]);
                    // Resonant volume chamber
                    translate([chamber_dia/2 + 2.0, 0, 0])
                        cylinder(d=3.5, h=h_half + 0.1);
                }
            }
        }
        
        // 3x Curved Fibonacci Deflector Fins (will render as solid plastic walls in the chamber)
        // Curves waves into a central vortex to prevent wall scattering (topological waveguide)
        for (a = [0, 120, 240]) {
            rotate([0, 0, a]) {
                intersection() {
                    cylinder(d=chamber_dia - 0.5, h=h_half + 0.2);
                    // Curved blade segment created by off-center ring subtraction
                    translate([2.5, 2.5, -0.1])
                        difference() {
                            cylinder(d=10.0, h=h_half + 0.4);
                            cylinder(d=8.4, h=h_half + 0.4);
                            // Angle cutout to restrict the blade to a 120-degree sector
                            translate([-6, -6, -0.1]) 
                                cube([12, 6, h_half + 0.6]);
                        }
                }
            }
        }
    }
}

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
            
        // 2. 13mm Resonant Cavity (lower half) with Fins & Reverb Pockets
        translate([0, 0, chassis_height + 6 - piezo_brass_thick - chamber_air_gap/2])
            chamber_cavity(chamber_air_gap/2);
            
        // 3. Radial wire egress channel in the base
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, chassis_height + 6 - wire_channel_d - piezo_brass_thick])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d + 1]);
            
        // 4. Helical Golden Spiral Diffuser on the bottom chamber floor
        if (use_spiral_diffuser) {
            translate([0, 0, chassis_height + 6 - piezo_brass_thick - chamber_air_gap/2])
                fibonacci_diffuser();
        }
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
            
        // 3. 13mm Resonant Cavity (upper half) with Fins & Reverb Pockets
        translate([0, 0, 7.5 - chamber_air_gap/2])
            chamber_cavity(chamber_air_gap/2);
            
        // 4. Radial wire egress channel in the cap
        translate([-wire_channel_w/2, -body_outer_dia/2 - 1, 7.5])
            cube([wire_channel_w, body_outer_dia + 2, wire_channel_d + 1]);
            
        // 5. Helical Golden Spiral Diffuser on the top chamber ceiling
        if (use_spiral_diffuser) {
            translate([0, 0, 7.5 - chamber_air_gap/2])
                rotate([180, 0, 0])
                    fibonacci_diffuser();
        }
            
        // 6. 3x L-shaped Bayonet Entry Slots + Compression Ramps
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

// Generates a helical Golden Spiral groove winding outwards
module fibonacci_diffuser() {
    for (a = [0 : 6 : 720]) {
        r = 1.0 + (a / 720) * 5.0;
        d = 0.3 + (a / 720) * 0.7;
        
        rotate([0, 0, a])
            translate([r, 0, -d])
                cylinder(d=1.5, h=d + 0.1); // 1.5mm wide spiral cut
    }
}
