# -*- coding: utf-8 -*-
"""
tap_graph_visualization_v2.py
=================================
TAP v5.3.2 — SM-HNSW Graph Visualization v2.

Builds an interactive HTML page with SVG force-directed
graph visualization of the SM-HNSW combined index.

Features v2:
  - Force-directed layout
  - Color-coded by node type
  - Edge color by RelationType
  - **Zoom & pan** (mouse wheel + drag)
  - **Search-in-graph** (type to highlight)
  - Click to highlight neighborhood
  - Self-contained HTML
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


def force_layout(nodes, edges, iterations=100):
    """Simple force-directed layout."""
    random.seed(42)
    for n in nodes:
        n['x'] = random.uniform(-300, 300)
        n['y'] = random.uniform(-300, 300)

    area = 600 * 600
    k = math.sqrt(area / max(1, len(nodes)))
    k2 = k * k

    for it in range(iterations):
        # Repulsive
        for i, ni in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                nj = nodes[j]
                dx = ni['x'] - nj['x']
                dy = ni['y'] - nj['y']
                d2 = dx * dx + dy * dy + 0.01
                d = math.sqrt(d2)
                f = k2 / d
                ni['x'] += f * dx / d * 0.1
                ni['y'] += f * dy / d * 0.1
                nj['x'] -= f * dx / d * 0.1
                nj['y'] -= f * dy / d * 0.1

        # Attractive (edges)
        for e in edges:
            ni = nodes[e['source']]
            nj = nodes[e['target']]
            dx = ni['x'] - nj['x']
            dy = ni['y'] - nj['y']
            d2 = dx * dx + dy * dy + 0.01
            d = math.sqrt(d2)
            f = d2 / k
            ni['x'] -= f * dx / d * 0.01
            ni['y'] -= f * dy / d * 0.01
            nj['x'] += f * dx / d * 0.01
            nj['y'] += f * dy / d * 0.01

        # Clamp
        for n in nodes:
            if n['x'] > 500: n['x'] = 500
            if n['x'] < -500: n['x'] = -500
            if n['y'] > 500: n['y'] = 500
            if n['y'] < -500: n['y'] = -500

    return nodes


def main():
    print("=" * 80)
    print("  TAP SM-HNSW GRAPH VIZ v2 (zoom, pan, search)")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')
    combined_path = os.path.join(assets_dir, 'tap_combined_index.json')

    with open(combined_path, 'r') as f:
        combined = json.load(f)

    raw_nodes = combined.get("nodes", [])
    print(f"  [1/4] LOAD INDEX: {len(raw_nodes)} nodes")

    tap_nodes = [n for n in raw_nodes if not n.get("label", "").startswith("cythos:")]
    cythos_nodes = [n for n in raw_nodes if n.get("label", "").startswith("cythos:")][:50]
    all_nodes = tap_nodes + cythos_nodes
    print(f"    Visualized: {len(all_nodes)}")

    nodes = []
    id_to_idx = {}
    for i, n in enumerate(all_nodes):
        label = n.get("label", "")
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

    edges = []
    for n in all_nodes:
        src_id = n.get("id")
        if src_id not in id_to_idx:
            continue
        for e in n.get("edges", []):
            target_id = e["target"]
            if target_id in id_to_idx:
                edges.append({
                    'source': id_to_idx[src_id],
                    'target': id_to_idx[target_id],
                    'relation': e.get("relation", 0),
                })
    print(f"    Edges: {len(edges)}")

    print(f"  [2/4] FORCE LAYOUT:")
    nodes = force_layout(nodes, edges, iterations=80)
    print(f"    Layout complete")
    print()

    print(f"  [3/4] BUILD HTML:")

    sampled_edges = edges[::max(1, len(edges) // 1500)]
    sampled_nodes = nodes

    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TAP SM-HNSW Graph Visualization v2</title>
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
  #graph { background: #14141f; border: 1px solid #333; border-radius: 5px; cursor: grab; }
  #graph:active { cursor: grabbing; }
  .node { cursor: pointer; }
  .link { opacity: 0.3; }
  .label { font-size: 0.7em; fill: #fff; pointer-events: none; }
  .info { color: #aaa; font-size: 0.8em; margin: 10px 0; padding: 8px; background: #14141f; border-radius: 3px; }
  .search-box { background: #1a1a2e; color: #ffd700; border: 1px solid #333; padding: 8px; border-radius: 3px; font-family: inherit; font-size: 0.95em; width: 100%; margin: 10px 0; }
  .search-box:focus { outline: 1px solid #ffd700; }
  .controls { color: #888; font-size: 0.8em; margin: 5px 0; }
</style>
</head>
<body>
<h1>TAP SM-HNSW Graph Visualization v2</h1>
<div class="subtitle">303-node semantic memory graph (TAP + CythOS) with zoom, pan, and search</div>
<div class="stats" id="stats"></div>
<div class="legend" id="legend"></div>
<input type="text" id="search" class="search-box" placeholder="Search nodes (type to highlight)...">
<div class="controls">Mouse wheel: zoom | Drag: pan | Click node: highlight neighborhood</div>
<div class="info" id="info">Click on any node to highlight its neighborhood. Type to search. Use mouse wheel to zoom, drag to pan.</div>
<svg id="graph" width="100%" height="700"></svg>
<script>
""")
    html_parts.append(f"const NODES = {json.dumps(sampled_nodes)};")
    html_parts.append(f"const EDGES = {json.dumps(sampled_edges)};")
    html_parts.append(f"const REL_NAMES = {json.dumps(REL_NAMES)};")
    html_parts.append(f"const REL_COLORS = {json.dumps(REL_COLORS)};")
    html_parts.append(f"const NODE_COLORS = {json.dumps(NODE_COLORS)};")

    html_parts.append("""
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

// SVG
const svg = document.getElementById('graph');
const W = svg.clientWidth || 1200;
const H = 700;

// Scale positions
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
  circle.setAttribute('data-label', n.label.toLowerCase());
  circle.addEventListener('click', () => {
    document.querySelectorAll('.link').forEach(l => l.setAttribute('opacity', '0.05'));
    document.querySelectorAll(`.link[data-source="${i}"]`).forEach(l => l.setAttribute('opacity', '1'));
    document.querySelectorAll(`.link[data-target="${i}"]`).forEach(l => l.setAttribute('opacity', '1'));
    document.getElementById('info').innerHTML = `<b>${n.label}</b><br>Type: ${n.type}, Edges: ${n.n_edges}`;
  });
  nodesGroup.appendChild(circle);
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', n.sx + 10);
  text.setAttribute('y', n.sy + 4);
  text.setAttribute('class', 'label');
  text.textContent = n.label.split(': ', 1)[1] || n.label;
  nodesGroup.appendChild(text);
});
svg.appendChild(nodesGroup);

// ZOOM & PAN
let viewBox = { x: 0, y: 0, w: W, h: H };
function updateViewBox() {
  svg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.w} ${viewBox.h}`);
}
svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

let isPanning = false;
let startX, startY;
svg.addEventListener('mousedown', (e) => {
  isPanning = true;
  startX = e.clientX;
  startY = e.clientY;
});
svg.addEventListener('mousemove', (e) => {
  if (!isPanning) return;
  const dx = (e.clientX - startX) * viewBox.w / W;
  const dy = (e.clientY - startY) * viewBox.h / H;
  viewBox.x -= dx;
  viewBox.y -= dy;
  startX = e.clientX;
  startY = e.clientY;
  updateViewBox();
});
svg.addEventListener('mouseup', () => isPanning = false);
svg.addEventListener('mouseleave', () => isPanning = false);

svg.addEventListener('wheel', (e) => {
  e.preventDefault();
  const scale = e.deltaY > 0 ? 1.1 : 0.9;
  const rect = svg.getBoundingClientRect();
  const px = (e.clientX - rect.left) / W * viewBox.w + viewBox.x;
  const py = (e.clientY - rect.top) / H * viewBox.h + viewBox.y;
  viewBox.w *= scale;
  viewBox.h *= scale;
  viewBox.x = px - (px - viewBox.x) * scale;
  viewBox.y = py - (py - viewBox.y) * scale;
  updateViewBox();
});

// SEARCH-IN-GRAPH
const searchBox = document.getElementById('search');
searchBox.addEventListener('input', (e) => {
  const q = e.target.value.toLowerCase();
  if (!q) {
    document.querySelectorAll('.node').forEach(n => {
      n.setAttribute('opacity', '1');
      n.setAttribute('stroke', 'none');
    });
    document.querySelectorAll('.label').forEach(n => n.setAttribute('opacity', '1'));
    document.querySelectorAll('.link').forEach(l => l.setAttribute('opacity', '0.3'));
    return;
  }
  document.querySelectorAll('.node').forEach(n => {
    const lbl = n.getAttribute('data-label');
    if (lbl && lbl.includes(q)) {
      n.setAttribute('opacity', '1');
      n.setAttribute('stroke', '#fff');
      n.setAttribute('stroke-width', '2');
    } else {
      n.setAttribute('opacity', '0.15');
      n.setAttribute('stroke', 'none');
    }
  });
  document.querySelectorAll('.label').forEach(n => {
    const lbl = n.textContent.toLowerCase();
    if (lbl && lbl.includes(q)) {
      n.setAttribute('opacity', '1');
    } else {
      n.setAttribute('opacity', '0.15');
    }
  });
});
""")

    html_parts.append("</script>")
    html_parts.append("</body></html>")

    out_path = os.path.join(assets_dir, 'tap_graph_visualization_v2.html')
    with open(out_path, 'w') as f:
        f.write('\n'.join(html_parts))
    print(f"    [EXPORT] -> {out_path}")
    print(f"    HTML size: {os.path.getsize(out_path):,} bytes")
    print(f"    Nodes: {len(sampled_nodes)}, Edges: {len(sampled_edges)}")
    print()

    print(f"  [4/4] STATS:")
    print(f"    v2 features: zoom, pan, search-in-graph")
    print(f"    Wheel: zoom in/out")
    print(f"    Drag: pan")
    print(f"    Type in search: highlight matches")
    print(f"    Click node: highlight neighborhood")
    print()
    print("  Open in browser:")
    print(f"    file://{out_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
