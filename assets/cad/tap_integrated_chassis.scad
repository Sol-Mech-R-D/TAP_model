// TAP Integrated Standalone Chassis & Waveguide
// Features: Nested Octahedron (Outer Shell) & Tetrahedron (Inner Core) Waveguide
// Solderless compression slots, Fintenna blades, and 4 coaxial bus tunnels.

$fn = 24;

module octahedron(side = 28) {
    // Generates a regular 3D octahedron (6 vertices)
    hull() {
        translate([side, 0, 0]) sphere(d=0.1);
        translate([-side, 0, 0]) sphere(d=0.1);
        translate([0, side, 0]) sphere(d=0.1);
        translate([0, -side, 0]) sphere(d=0.1);
        translate([0, 0, side]) sphere(d=0.1);
        translate([0, 0, -side]) sphere(d=0.1);
    }
}

module tetrahedron(side_length = 16, thickness = 3) {
    // Generates a regular 3D tetrahedron (4 vertices)
    h = side_length * sqrt(6) / 3;
    r = side_length * sqrt(3) / 6;
    
    v0 = [0, -2*r, -h/4];
    v1 = [-side_length/2, r, -h/4];
    v2 = [side_length/2, r, -h/4];
    v3 = [0, 0, 3*h/4];
    
    module strut(p1, p2) {
        hull() {
            translate(p1) sphere(d=thickness, $fn=12);
            translate(p2) sphere(d=thickness, $fn=12);
        }
    }
    
    // Draw the 6 edges of the inner core
    strut(v0, v1);
    strut(v1, v2);
    strut(v2, v0);
    strut(v0, v3);
    strut(v1, v3);
    strut(v2, v3);
    
    // 4 Suspension struts linking the core to the outer shell
    hull() { translate(v0) sphere(d=1.5); translate([0, -25, 0]) sphere(d=1.5); }
    hull() { translate(v1) sphere(d=1.5); translate([-20, 20, 0]) sphere(d=1.5); }
    hull() { translate(v2) sphere(d=1.5); translate([20, 20, 0]) sphere(d=1.5); }
    hull() { translate(v3) sphere(d=1.5); translate([0, 0, 25]) sphere(d=1.5); }
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

module base_cradle(width = 80, length = 110, height = 15) {
    difference() {
        // Main block
        translate([0, 0, -height/2])
        cube([width, length, height], center = true);
        
        // 1. Cable entry port (5.5mm tunnel from back of the chassis for 16-wire USB-C cable)
        translate([0, length/2, -height/2])
        rotate([90, 0, 0])
        cylinder(h = 30, d = 5.5, center = true, $fn=12);
        
        // 2. Internal wire-distribution cavity where discrete power/CC/data wires split
        translate([0, length/4, -height/2 + 2])
        cube([20, 25, 10.02], center = true);
        
        // 3. Register Recess (Right side - holds DCD Shift Registers & Program ROM)
        translate([22, -10, 2])
        cube([25, 70, 15.02], center = true);
        
        // 4. ALU Recess (Left side - holds 1-Bit Full Adder & Carry Latch)
        translate([-22, -10, 2])
        cube([25, 70, 15.02], center = true);
        
        // 5. 4x Coaxial Bus Tunnels (2.0mm tunnels linking Register Recess to ALU Recess)
        for (y = [-25, -10, 5, 20]) {
            translate([0, y, 2.5])
            rotate([0, 90, 0])
            cylinder(h = 22, d = 2.0, center = true, $fn=12);
        }
    }
}

module nested_waveguide_chamber() {
    difference() {
        // Outer Octahedron shell
        translate([0, 0, 12])
        octahedron(side = 28);
        
        // Subtract inner cavity (slightly smaller octahedron to create 3mm walls)
        translate([0, 0, 12])
        octahedron(side = 25);
        
        // Cut the chamber in half at the horizontal split-plane (Z = 12)
        // This makes it printable and allows toolless loading of the core
        translate([0, 0, 26])
        cube([60, 60, 28], center = true);
    }
    
    // Suspend the inner Tetrahedron core in the geometric center of the cavity
    translate([0, 0, 12])
    scale([1, 1, 1.1])
    tetrahedron(side_length = 16, thickness = 3);
}

module main_chassis() {
    difference() {
        union() {
            // 1. Base cradle
            base_cradle();
            
            // 2. Nested Waveguide chamber (Outer Octahedron wall + Inner Core)
            nested_waveguide_chamber();
            
            // 3. Fintenna Blades (4 radiating channels)
            fintenna_blade(0);
            fintenna_blade(90);
            fintenna_blade(180);
            fintenna_blade(270);
        }
        
        // 4. Piezo Mount slots in the bottom face of the octahedron
        translate([0, 0, 1.5])
        cylinder(h = 1.22, d = 20.2, center = true, $fn=24);
        
        // 5. Helmholtz resonance pockets inside the bottom shell
        // neck = 2.2mm, bulb = 5.0mm
        for (angle = [45, 165, 285]) {
            rotate([0, 0, angle])
            translate([8, 0, 4.0]) {
                rotate([0, 90, 0]) cylinder(h = 3.02, d = 2.2, center = true, $fn=12);
                translate([2.5, 0, 0]) sphere(d = 5.0, $fn=16);
            }
        }
    }
}

main_chassis();

// Render standalone compression pins off to the side for printing
translate([45, 45, -7.5]) compression_pin();
translate([45, 35, -7.5]) compression_pin();
translate([45, 25, -7.5]) compression_pin();
translate([45, 15, -7.5]) compression_pin();
