// TAP Integrated Standalone Chassis & Waveguide
// Optimized for stable CGAL rendering with localized $fn scaling

module tetrahedron_frame(side_length = 50, thickness = 4) {
    // Vertices of a regular tetrahedron centered at origin
    h = side_length * sqrt(6) / 3;
    r = side_length * sqrt(3) / 6;
    
    v0 = [0, -2*r, -h/4];
    v1 = [-side_length/2, r, -h/4];
    v2 = [side_length/2, r, -h/4];
    v3 = [0, 0, 3*h/4];
    
    // Draw 3D edges (struts) with slots for capacitors
    module strut(p1, p2) {
        hull() {
            translate(p1) sphere(d=thickness, $fn=12);
            translate(p2) sphere(d=thickness, $fn=12);
        }
    }
    
    color("Gold") {
        strut(v0, v1);
        strut(v1, v2);
        strut(v2, v0);
        strut(v0, v3);
        strut(v1, v3);
        strut(v2, v3);
    }
}

module fintenna_blade(angle, length = 25, thickness = 1.5, height = 15) {
    // Vertical radiating fins to route wire leads and act as planar antennas
    rotate([0, 0, angle])
    translate([10, 0, -2.5]) {
        difference() {
            // The planar fin/blade
            translate([length/2, 0, height/2])
            cube([length, thickness, height], center = true);
            
            // Micro-groove (0.8mm channel) along the top edge for wire routing
            translate([length/2, 0, height - 0.4])
            cube([length + 2, 0.8, 1.02], center = true);
            
            // Compression lock sockets (tapered holes for locking pins)
            translate([length/3, 0, height/2])
            rotate([90, 0, 0])
            cylinder(h = thickness + 2, d = 2.0, center = true, $fn=12);
            
            translate([2*length/3, 0, height/2])
            rotate([90, 0, 0])
            cylinder(h = thickness + 2, d = 2.0, center = true, $fn=12);
        }
    }
}

module compression_pin(d_base = 2.2, height = 6) {
    // Tapered locking pin to squeeze overlapping leads inside the blade sockets
    cylinder(h = height, d1 = d_base, d2 = d_base - 0.4, center = true, $fn=12);
}

module helmholtz_pocket(angle) {
    // Tuned to 4.5 kHz (Neck: 2.2mm, Bulb: 5.0mm)
    rotate([0, 0, angle])
    translate([8, 0, 2.5]) {
        // Neck channel (with slight 0.02mm overlap)
        rotate([0, 90, 0])
        cylinder(h = 3.02, d = 2.2, center = true, $fn=12);
        
        // Resonant bulb
        translate([2.5, 0, 0])
        sphere(d = 5.0, $fn=16);
    }
}

module helical_grooves(radius = 6.5, depth = 0.6) {
    // Spiral cuts for orbital angular momentum (OAM)
    for (theta = [0 : 15 : 360]) {
        r_val = radius * (theta / 360.0);
        rotate([0, 0, theta])
        translate([r_val, 0, 0])
        sphere(d = depth, $fn=12);
    }
}

module base_cradle(width = 80, length = 110, height = 15) {
    difference() {
        // Main block
        translate([0, 0, -height/2])
        cube([width, length, height], center = true);
        
        // Recess for USB-C Power breakout (left side)
        translate([-20, 0, 2])
        cube([30, 90, 15.02], center = true);
        
        // Recess for DCD Shift Registers (right side)
        translate([20, 0, 2])
        cube([30, 90, 15.02], center = true);
    }
}

module main_chassis() {
    difference() {
        union() {
            // 1. Base cradle
            base_cradle();
            
            // 2. Rising Waveguide Chamber Wall (smooth outer surface)
            translate([0, 0, 7.5])
            cylinder(h = 10, d = 25, center = true, $fn=40);
            
            // 3. Fintenna Blades (4 radiating channels)
            fintenna_blade(0);
            fintenna_blade(90);
            fintenna_blade(180);
            fintenna_blade(270);
            
            // 4. 3D Simplex Circuit Cage
            translate([0, 0, 15])
            scale([1, 1, 1.2])
            tetrahedron_frame(side_length = 60, thickness = 5);
        }
        
        // 5. Closed Reverb Chamber (13mm diameter, 5mm height - with 0.02mm overlap)
        translate([0, 0, 7.5])
        cylinder(h = 5.02, d = 13, center = true, $fn=40);
        
        // 6. Helical diffusers (Floor & Ceiling of chamber)
        translate([0, 0, 5.0])
        helical_grooves();
        
        translate([0, 0, 10.0])
        helical_grooves();
        
        // 7. Helmholtz Resonance Pockets
        helmholtz_pocket(45);
        helmholtz_pocket(165);
        helmholtz_pocket(285);
        
        // 8. Piezo Mount slots (Tx on bottom, Rx on top)
        translate([0, 0, 4.0])
        cylinder(h = 1.22, d = 20.2, center = true, $fn=40);
        
        translate([0, 0, 11.0])
        cylinder(h = 1.22, d = 20.2, center = true, $fn=40);
    }
}

main_chassis();

// Render standalone compression pins off to the side for printing
translate([45, 45, -7.5]) compression_pin();
translate([45, 35, -7.5]) compression_pin();
translate([45, 25, -7.5]) compression_pin();
translate([45, 15, -7.5]) compression_pin();
