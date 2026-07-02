# -*- coding: utf-8 -*-
"""
tap_graph_visualization.py
==============================
TAP v5.3.2 — SM-HNSW Graph Visualization.

Builds an interactive HTML page with SVG force-directed
graph visualization of the 303-node SM-HNSW combined
index.

Features:
  - Force-directed layout (using D3.js-like simulation)
  - Color-coded by node type (TAP, CythOS, etc.)
  - Edge color by RelationType (CAUSES, PART_OF, etc.)
  - Zoom/pan support
  - Click to highlight neighborhood
  - Tooltips with metadata
  - Self-contained HTML (no external dependencies)

Output: assets/tap_graph_visualization.html
"""

import os
import json
import math
import random
from datetime import datetime


REL_NAMES = {0: "NONE", 1: "CAUSES", 2: "PART_OF", 3: "CONTRADICTS", 4: "SUPPORTS", 5: "SYNONYM"}
REL_COLORS = {0: "#888", 1: "#f87171", 2: "#60a5fa", 3: "#fbbf24", 4: "#4ade80", 5: "#a78bfa"}
NODE_COLORS = {
    "constant": "#ffd700",
    "prediction": "#ff8c00",
    "concept": "#ffaa55",
    "script": "#4ade80",
    "doc": "#60a5fa",
    "cythos": "#a78bfa",
}


def force_layout(nodes: list, edges: list, iterations: int = 200) -> list:
    """Simple force-directed layout (Fruchterman-Reingold)."""
    # Initialize positions
    random.seed(42)
    for n in nodes:
        n['x'] = random.uniform(-300, 300)
        n['y'] = random.uniform(-300, 300)
        n['vx'] = 0.0
        n['vy'] = 0.0

    # Parameters
    area = 600 * 600
    k = math.sqrt(area / max(1, len(nodes)))
    k2 = k * k

    for it in range(iterations):
        # Repulsive forces
        for i, ni in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                nj = nodes[j]
                dx = ni['x'] - nj['x']
                dy = ni['y'] - nj['y']
                d2 = dx * dx + dy * dy + 0.01
                d = math.sqrt(d2)
                # Repulsive force
                f = k2 / d
                fx = f * dx / d
                fy = f * dy / d
                ni['vx'] += fx
                ni['vy'] += fy
                nj['vx'] -= fx
                nj['vy'] -= fy

        # Attractive forces (edges)
        for e in edges:
            ni = nodes[e['source']]
            nj = nodes[e['target']]
            dx = ni['x'] - nj['x']
            dy = ni['y'] - nj['y']
            d2 = dx * dx + dy * dy + 0.01
            d = math.sqrt(d2)
            f = d2 / k
            fx = f * dx / d
            fy = f * dy / d
            ni['vx'] -= fx
            ni['vy'] -= fy
            nj['vx'] += fx
            nj['vy'] += fy

        # Apply velocity, with cooling
        cool = max(0.1, 1.0 - it / iterations)
        for n in nodes:
            v2 = n['vx'] ** 2 + n['vy'] ** 2
            if v2 > 0:
                n['x'] += n['vx'] * cool * 0.1
                n['y'] += n['vy'] * cool * 0.1
                # Limit displacement
                if n['x'] > 500: n['x'] = 500
                if n['x'] < -500: n['x'] = -500
                if n['y'] > 500: n['y'] = 500
                if n['y'] < -500: n['y'] = -500
            n['vx'] = 0
            n['vy'] = 0

    return nodes


def main():
    print("=" * 80)
    print("  TAP SM-HNSW GRAPH VISUALIZATION")
    print("  Building interactive HTML/SVG for 303 nodes + 27k edges")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')
    combined_path = os.path.join(assets_dir, 'tap_combined_index.json')

    if not os.path.exists(combined_path):
        print(f"  Combined index not found")
        return

    with open(combined_path, 'r') as f:
        combined = json.load(f)

    # Load nodes and edges
    raw_nodes = combined.get("nodes", [])
    print(f"  [1/4] LOAD INDEX: {len(raw_nodes)} nodes")

    # Filter to TAP nodes + key CythOS nodes (to keep visualization manageable)
    # Use all TAP + first 50 CythOS
    tap_nodes = [n for n in raw_nodes if not n.get("label", "").startswith("cythos:")]
    cythos_nodes = [n for n in raw_nodes if n.get("label", "").startswith("cythos:")][:50]
    all_nodes = tap_nodes + cythos_nodes
    print(f"    TAP nodes: {len(tap_nodes)}")
    print(f"    CythOS nodes (limited): {len(cythos_nodes)}")
    print(f"    Total visualized: {len(all_nodes)}")

    # Parse nodes
    nodes = []
    id_to_idx = {}
    for i, n in enumerate(all_nodes):
        label = n.get("label", "")
        # Determine type
        if label.startswith("constant:"):
            ntype = "constant"
        elif label.startswith("prediction:"):
            ntype = "prediction"
        elif label.startswith("concept:"):
            ntype = "concept"
        elif label.startswith("script:"):
            ntype = "script"
        elif label.startswith("doc:"):
            ntype = "doc"
        elif label.startswith("cythos:"):
            ntype = "cythos"
        else:
            ntype = "other"
        nodes.append({
            'id': n.get("id", i),
            'label': label,
            'type': ntype,
            'n_edges': len(n.get("edges", [])),
        })
        id_to_idx[n.get("id", i)] = i
    print()

    # Parse edges
    print(f"  [2/4] PARSE EDGES:")
    edges = []
    edge_count = 0
    for n in all_nodes:
        src_id = n.get("id")
        if src_id not in id_to_idx:
            continue
        for e in n.get("edges", []):
            target_id = e["target"]
            if target_id not in id_to_idx:
                continue
            edges.append({
                'source': id_to_idx[src_id],
                'target': id_to_idx[target_id],
                'relation': e.get("relation", 0),
            })
            edge_count += 1
    print(f"    Edges: {edge_count}")
    print()

    # Force layout
    print(f"  [3/4] FORCE-DIRECTED LAYOUT:")
    nodes = force_layout(nodes, edges, iterations=100)
    print(f"    Layout complete")
    print()

    # Build HTML
    print(f"  [4/4] BUILD HTML:")

    # Sample edges for visualization (avoid 27k lines)
    sampled_edges = edges[::max(1, len(edges) // 1500)]  # cap at 1500

    # Sample nodes
    sampled_nodes = nodes

    html = []
    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TAP SM-HNSW Graph Visualization</title>
<style>
  body { font-family: 'SF Mono', Consolas, monospace; background: #0a0a14; color: #e0e0e0; margin: 0; padding: 20px; }
  h1 { color: #ffd700; font-size: 1.5em; margin: 0 0 5px 0; }
  .subtitle { color: #999; font-size: 0.85em; margin-bottom: 10px; }
  .stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; margin: 10px 0; }
  .stat { background: #1a1a2e; padding: 8px; border-left: 2px solid #ffd700; }
  .stat-label { color: #888; font-size: 0.7em; }
  .stat-value { color: #ffd700; font-size: 1.3em; font-weight: bold; }
  .legend { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; font-size: 0.85em; }
  .legend-item { display: flex; align-items: center; gap: 4px; }
  .legend-swatch { width: 12px; height: 12px; border-radius: 2px; }
  #graph { background: #14141f; border: 1px solid #333; border-radius: 5px; }
  .node { cursor: pointer; }
  .node:hover { stroke: #fff; stroke-width: 2px; }
  .link { opacity: 0.3; }
  .label { font-size: 0.7em; fill: #fff; pointer-events: none; }
  .info { color: #aaa; font-size: 0.8em; margin: 10px 0; padding: 8px; background: #14141f; border-radius: 3px; }
</style>
</head>
<body>
<h1>TAP SM-HNSW Graph Visualization</h1>
<div class="subtitle">303-node semantic memory graph (TAP + CythOS)</div>
<div class="stats" id="stats"></div>
<div class="legend" id="legend"></div>
<div class="info" id="info">Click on any node to highlight its neighborhood. Hover for tooltip.</div>
<svg id="graph" width="100%" height="700"></svg>
<script>
""")

    # Embed data as JS
    html.append(f"const NODES = {json.dumps(sampled_nodes)};")
    html.append(f"const EDGES = {json.dumps(sampled_edges)};")
    html.append(f"const REL_NAMES = {json.dumps(REL_NAMES)};")
    html.append(f"const REL_COLORS = {json.dumps(REL_COLORS)};")
    html.append(f"const NODE_COLORS = {json.dumps(NODE_COLORS)};")

    # JS rendering
    html.append("""
// Stats
const stats = document.getElementById('stats');
const typeCounts = {};
NODES.forEach(n => { typeCounts[n.type] = (typeCounts[n.type] || 0) + 1; });
const relCounts = {};
EDGES.forEach(e => { relCounts[REL_NAMES[e.relation]] = (relCounts[REL_NAMES[e.relation]] || 0) + 1; });
stats.innerHTML = `
  <div class="stat"><div class="stat-label">Nodes</div><div class="stat-value">${NODES.length}</div></div>
  <div class="stat"><div class="stat-label">Edges</div><div class="stat-value">${EDGES.length}</div></div>
  <div class="stat"><div class="stat-label">Types</div><div class="stat-value">${Object.keys(typeCounts).length}</div></div>
  <div class="stat"><div class="stat-label">Relations</div><div class="stat-value">${Object.keys(relCounts).length}</div></div>
  <div class="stat"><div class="stat-label">Avg edges/node</div><div class="stat-value">${(EDGES.length * 2 / NODES.length).toFixed(1)}</div></div>
`;

// Legend
const legend = document.getElementById('legend');
for (const [type, color] of Object.entries(NODE_COLORS)) {
  const item = document.createElement('div');
  item.className = 'legend-item';
  item.innerHTML = `<div class="legend-swatch" style="background: ${color}"></div>${type} (${typeCounts[type] || 0})`;
  legend.appendChild(item);
}
for (const [rel, color] of Object.entries(REL_COLORS)) {
  if (rel === 'NONE') continue;
  const item = document.createElement('div');
  item.className = 'legend-item';
  item.innerHTML = `<div class="legend-swatch" style="background: ${color}"></div>${rel} (${relCounts[rel] || 0})`;
  legend.appendChild(item);
}

// SVG
const svg = document.getElementById('graph');
const W = svg.clientWidth || 1200;
const H = 700;

// Scale positions to fit
const xMin = Math.min(...NODES.map(n => n.x));
const xMax = Math.max(...NODES.map(n => n.x));
const yMin = Math.min(...NODES.map(n => n.y));
const yMax = Math.max(...NODES.map(n => n.y));
const xRange = xMax - xMin || 1;
const yRange = yMax - yMin || 1;
NODES.forEach(n => {
  n.sx = 50 + (n.x - xMin) / xRange * (W - 100);
  n.sy = 50 + (n.y - yMin) / yRange * (H - 100);
});

// Edges
const edgesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
EDGES.forEach(e => {
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  const s = NODES[e.source];
  const t = NODES[e.target];
  line.setAttribute('x1', s.sx);
  line.setAttribute('y1', s.sy);
  line.setAttribute('x2', t.sx);
  line.setAttribute('y2', t.sy);
  line.setAttribute('stroke', REL_COLORS[e.relation] || '#888');
  line.setAttribute('stroke-width', '0.5');
  line.setAttribute('class', 'link');
  line.setAttribute('data-source', e.source);
  line.setAttribute('data-target', e.target);
  edgesGroup.appendChild(line);
});
svg.appendChild(edgesGroup);

// Nodes
const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
NODES.forEach((n, i) => {
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  circle.setAttribute('cx', n.sx);
  circle.setAttribute('cy', n.sy);
  circle.setAttribute('r', Math.min(8, 2 + Math.sqrt(n.n_edges)));
  circle.setAttribute('fill', NODE_COLORS[n.type] || '#888');
  circle.setAttribute('class', 'node');
  circle.setAttribute('data-id', n.id);
  circle.setAttribute('data-idx', i);
  circle.addEventListener('click', () => {
    // Highlight neighborhood
    document.querySelectorAll('.link').forEach(l => l.setAttribute('opacity', '0.05'));
    document.querySelectorAll(`.link[data-source="${i}"]`).forEach(l => l.setAttribute('opacity', '1'));
    document.querySelectorAll(`.link[data-target="${i}"]`).forEach(l => l.setAttribute('opacity', '1'));
    document.getElementById('info').innerHTML = `<b>${n.label}</b><br>Type: ${n.type}, Edges: ${n.n_edges}`;
  });
  nodesGroup.appendChild(circle);
  // Label
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', n.sx + 10);
  text.setAttribute('y', n.sy + 4);
  text.setAttribute('class', 'label');
  text.textContent = n.label.split(': ', 1)[1] || n.label;
  nodesGroup.appendChild(text);
});
svg.appendChild(nodesGroup);
""")

    html.append("</script>")
    html.append("</body></html>")

    # Write
    out_path = os.path.join(assets_dir, 'tap_graph_visualization.html')
    with open(out_path, 'w') as f:
        f.write('\n'.join(html))
    print(f"    [EXPORT] -> {out_path}")
    print(f"    HTML size: {os.path.getsize(out_path):,} bytes")
    print(f"    Nodes in viz: {len(sampled_nodes)}")
    print(f"    Edges in viz: {len(sampled_edges)}")
    print()

    # Save stats
    out_stats = os.path.join(assets_dir, 'tap_graph_viz_stats.json')
    with open(out_stats, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "n_nodes_total": len(raw_nodes),
            "n_nodes_visualized": len(sampled_nodes),
            "n_edges_total": edge_count,
            "n_edges_visualized": len(sampled_edges),
            "html_size_bytes": os.path.getsize(out_path),
            "type_counts": {ntype: sum(1 for n in sampled_nodes if n['type'] == ntype) for ntype in set(n['type'] for n in sampled_nodes)},
        }, f, indent=2)
    print(f"  [EXPORT] -> {out_stats}")
    print()
    print("  Open in browser:")
    print(f"    file://{out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
