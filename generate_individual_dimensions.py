# -*- coding: utf-8 -*-
"""
generate_individual_dimensions.py
=================================
Generates a stunning 16-panel grid diagram (4x4) extracting each of the 13
dimensions as individual, discrete geometric shapes.
Saves to tap_dimensions_discrete.png.
"""

import os
import math
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Set dark theme style
    plt.style.use('dark_background')
    fig, axes = plt.subplots(4, 4, figsize=(12, 12), dpi=300)
    fig.patch.set_facecolor('#030308')
    
    dims = [
        {"d": 1, "name": "Spatial Point", "color": "#ff6b6b"},
        {"d": 2, "name": "Temporal Phase", "color": "#ff8e53"},
        {"d": 3, "name": "Spatial Brane", "color": "#ffd93d"},
        {"d": 4, "name": "Spacetime Brane", "color": "#a8ff3d"},
        {"d": 5, "name": "AdS Bulk Channel", "color": "#4ecdc4"},
        {"d": 6, "name": "Calabi-Yau Base", "color": "#4e96cd"},
        {"d": 7, "name": "M-Theory 7-Sphere", "color": "#7c6af7"},
        {"d": 8, "name": "Boundary Width", "color": "#a26af7"},
        {"d": 9, "name": "Weyl Curvature", "color": "#c96af7"},
        {"d": 10, "name": "Superstring Base", "color": "#f06af7"},
        {"d": 11, "name": "M-Theory Bulk", "color": "#f76ae2"},
        {"d": 12, "name": "F-Theory Projection", "color": "#f76abd"},
        {"d": 13, "name": "Saturation Ceiling", "color": "#f76a9a"}
    ]
    
    for idx in range(16):
        row = idx // 4
        col = idx % 4
        ax = axes[row, col]
        ax.set_facecolor('#030308')
        ax.axis('off')
        
        if idx < 13:
            d = dims[idx]
            num_sides = d["d"]
            color = d["color"]
            
            ax.set_title(f"D = {num_sides}", color='#ffffff', fontsize=11, fontweight='black', pad=8)
            ax.text(0, -1.3, d["name"], color='#8f8fa3', fontsize=7, ha='center', fontweight='medium')
            
            # Draw individual shapes
            if num_sides == 1:
                # D=1: Single glowing point
                ax.scatter(0, 0, color=color, s=250, zorder=5, edgecolors='#ffffff', linewidths=1.2)
                ax.scatter(0, 0, color=color, s=700, zorder=4, alpha=0.35)
            elif num_sides == 2:
                # D=2: Line segment
                ax.plot([-0.6, 0.6], [0, 0], color=color, linewidth=3, solid_capstyle='round')
                ax.scatter([-0.6, 0.6], [0, 0], color='#ffffff', s=40, zorder=5)
            elif num_sides == 4:
                # D=4: Projected 3D Tetrahedron
                angles = [2 * math.pi * i / 3 - math.pi/6 for i in range(3)]
                x_outer = [0.85 * math.cos(a) for a in angles]
                y_outer = [0.85 * math.sin(a) for a in angles]
                
                # Draw outer triangle
                for i in range(3):
                    next_idx = (i + 1) % 3
                    ax.plot([x_outer[i], x_outer[next_idx]], [y_outer[i], y_outer[next_idx]], color=color, linewidth=2)
                # Connect to center node
                for i in range(3):
                    ax.plot([x_outer[i], 0], [y_outer[i], 0], color=color, linestyle='--', linewidth=1.2, alpha=0.8)
                    
                ax.scatter(x_outer + [0], y_outer + [0], color=color, s=60, zorder=5, edgecolors='#ffffff')
            else:
                # Regular polygons for D=3 and D>=5
                angles = [2 * math.pi * i / num_sides + math.pi/2 for i in range(num_sides)]
                x_pts = [0.85 * math.cos(a) for a in angles]
                y_pts = [0.85 * math.sin(a) for a in angles]
                
                # Draw polygon lines
                for i in range(num_sides):
                    next_idx = (i + 1) % num_sides
                    ax.plot([x_pts[i], x_pts[next_idx]], [y_pts[i], y_pts[next_idx]], color=color, linewidth=2)
                    
                ax.scatter(x_pts, y_pts, color=color, s=60, zorder=5, edgecolors='#ffffff', linewidths=0.8)
                
            ax.set_xlim(-1.4, 1.4)
            ax.set_ylim(-1.4, 1.4)
            
        else:
            # Aesthetic placeholder boxes for the last 3 cells (symmetrical grid layout)
            ax.set_xlim(-1.4, 1.4)
            ax.set_ylim(-1.4, 1.4)
            
            if idx == 13:
                ax.text(0, 0.2, "TAP MODEL\nUNIFIED\nGEOMETRY", color='#7c6af7', fontsize=9, fontweight='black', ha='center', va='center')
                ax.text(0, -0.6, "13D Manifold", color='#4ecdc4', fontsize=7, ha='center')
            elif idx == 14:
                ax.text(0, 0.2, "DELTA VECTOR'S\n99\nHYPOTHESES", color='#ffd93d', fontsize=9, fontweight='black', ha='center', va='center')
                ax.text(0, -0.6, "David Baker", color='#8f8fa3', fontsize=7, ha='center')
            elif idx == 15:
                # Draw small aesthetic 13D star logo in the last box
                N = 13
                angles = [2 * math.pi * i / N for i in range(N)]
                x_star = [0.65 * math.cos(a) for a in angles]
                y_star = [0.65 * math.sin(a) for a in angles]
                for i in range(N):
                    next_idx = (i + 5) % N
                    ax.plot([x_star[i], x_star[next_idx]], [y_star[i], y_star[next_idx]], color='#ffd93d', linewidth=0.5, alpha=0.3)
                ax.text(0, -0.8, "Axiomatic Proofs", color='#8f8fa3', fontsize=6, ha='center')
                
    plt.tight_layout(pad=3.0)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tap_dimensions_discrete.png")
    plt.savefig(out_path, facecolor='#030308', edgecolor='none')
    plt.close()
    print(f"[EXPORT] Discrete dimensions grid generated -> {out_path}")

if __name__ == "__main__":
    main()
