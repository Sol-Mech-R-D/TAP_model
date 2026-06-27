# -*- coding: utf-8 -*-
"""
generate_13_dimensions_diagram.py
=================================
Generates a stunning, high-resolution vector visualization of the 13 dimensions
of the TAP model as a 13-pointed star (tridecagram) with detailed nodes.
Saves to tap_13_dimensions.png.
"""

import os
import math
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Set dark theme style
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    fig.patch.set_facecolor('#030308')
    ax.set_facecolor('#030308')
    
    # 13 dimensions details
    dims = [
        {"d": 1, "name": "Spatial Point", "desc": "Seed/compaction", "color": "#7c6af7"},
        {"d": 2, "name": "Temporal Phase", "desc": "Time flow/entropy", "color": "#8b6af7"},
        {"d": 3, "name": "Spatial Brane", "desc": "Observable 3D space", "color": "#9a6af7"},
        {"d": 4, "name": "Relativistic Spacetime", "desc": "4D spacetime brane", "color": "#a96af7"},
        {"d": 5, "name": "AdS Bulk Channel", "desc": "5D gravity leakage", "color": "#b86af7"},
        {"d": 6, "name": "Calabi-Yau Base", "desc": "Fermion spin states", "color": "#c76af7"},
        {"d": 7, "name": "M-Theory 7-Sphere", "desc": "Supergravity coords", "color": "#d66af7"},
        {"d": 8, "name": "Boundary Width", "desc": "Fibonacci F_6 scale", "color": "#e56af7"},
        {"d": 9, "name": "Weyl Curvature", "desc": "Gravity KK modes", "color": "#4ecdc4"},
        {"d": 10, "name": "Superstring Base", "desc": "Anomaly cancellation", "color": "#4ecda5"},
        {"d": 11, "name": "M-Theory Bulk", "desc": "11D supergravity", "color": "#4ecd86"},
        {"d": 12, "name": "F-Theory Projection", "desc": "Gauge group bundles", "color": "#4ecd67"},
        {"d": 13, "name": "Saturation Ceiling", "desc": "Holographic entropy", "color": "#ffd93d"}
    ]
    
    N = 13
    angles = [2 * math.pi * i / N + math.pi/2 for i in range(N)]
    x = [math.cos(a) for a in angles]
    y = [math.sin(a) for a in angles]
    
    # Draw tridecagram star lines (step = 5)
    step = 5
    for i in range(N):
        next_idx = (i + step) % N
        ax.plot([x[i], x[next_idx]], [y[i], y[next_idx]], color=(124/255, 106/255, 247/255, 0.35), 
                linestyle='-', linewidth=1.2, alpha=0.35)
        
    # Draw outer tridecagon boundary
    for i in range(N):
        next_idx = (i + 1) % N
        ax.plot([x[i], x[next_idx]], [y[i], y[next_idx]], color='#4ecdc4', 
                linestyle='-', linewidth=1.5, alpha=0.5)
        
    # Draw nodes and add text
    for i, d in enumerate(dims):
        # Glow effect
        ax.scatter(x[i], y[i], color=d["color"], s=180, zorder=5, edgecolors='#ffffff', linewidths=1.2, alpha=0.9)
        ax.scatter(x[i], y[i], color=d["color"], s=450, zorder=4, alpha=0.3)
        
        # Calculate label offset direction
        ox = math.cos(angles[i])
        oy = math.sin(angles[i])
        
        # Label placement details
        lx = 1.25 * ox
        ly = 1.25 * oy
        
        # Alignments
        ha = 'left' if ox > 0.1 else ('right' if ox < -0.1 else 'center')
        va = 'bottom' if oy > 0.1 else ('top' if oy < -0.1 else 'center')
        
        label_text = f"D={d['d']}: {d['name']}\n({d['desc']})"
        ax.text(lx, ly, label_text, color='#f0f0f5', fontsize=8, fontweight='semibold',
                ha=ha, va=va, zorder=6,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0d0d1e', edgecolor='#7c6af7', alpha=0.85, lw=1))
        
    # Center text
    ax.text(0, 0, "TAP\n13D\nMANIFOLD", color='#ffffff', fontsize=18, fontweight='black',
            fontfamily='sans-serif', ha='center', va='center', zorder=10,
            bbox=dict(boxstyle='circle,pad=0.4', facecolor='#06060f', edgecolor='#ffd93d', alpha=0.95, lw=2))
            
    # Aesthetic circle guidelines
    circle1 = plt.Circle((0, 0), 1.0, color='#7c6af7', fill=False, linestyle='--', linewidth=0.8, alpha=0.25)
    circle2 = plt.Circle((0, 0), 1.2, color='#4ecdc4', fill=False, linestyle=':', linewidth=0.8, alpha=0.15)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.axis('off')
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tap_13_dimensions.png")
    plt.savefig(out_path, facecolor='#030308', edgecolor='none', pad_inches=0.1)
    plt.close()
    print(f"[EXPORT] 13 dimensions diagram generated -> {out_path}")

if __name__ == "__main__":
    main()
