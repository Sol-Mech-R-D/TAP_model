# -*- coding: utf-8 -*-
"""
update_dashboard.py
===================
Combines tap_super_tribunal_99_results.json and the existing tap_universe_dashboard.html
into a highly polished, interactive dashboard.
"""

import os
import json
import re

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(root_dir, "..", "assets", "tap_super_tribunal_99_results.json")
    html_path = os.path.join(root_dir, "..", "assets", "tap_universe_dashboard.html")
    dest_html_path = os.path.join(root_dir, "..", "assets", "tap_universe_dashboard.html")
    
    # Read the JSON results
    with open(json_path, "r") as f:
        checks = json.load(f)
        
    # Read the existing html template
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Define the new tab button and tab content
    tab_button = '<button class="tab-btn" onclick="switchTab(event, \'tab-hypotheses\')">Delta Vector\'s 99 Hypotheses</button>'
    
    # Style definitions for table
    table_styles = """
        /* Hypotheses Table Styles */
        .search-bar-container input, .search-bar-container select {
            border: 1px solid var(--card-border);
            border-radius: 8px;
            background: rgba(10, 10, 15, 0.9);
            color: var(--text-color);
            padding: 0.8rem 1.2rem;
            outline: none;
            font-family: inherit;
            font-size: 0.9rem;
            transition: border-color 0.3s ease;
        }
        .search-bar-container input:focus, .search-bar-container select:focus {
            border-color: var(--accent-color);
        }
        #hypotheses-table th {
            color: var(--text-color);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        #hypotheses-table td {
            padding: 0.85rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            vertical-align: middle;
            color: #d1d1db;
        }
        #hypotheses-table tr:hover td {
            background: rgba(124, 106, 247, 0.03);
        }
        .badge-pass {
            background: rgba(78, 205, 196, 0.15);
            color: #4ecdc4;
            border: 1px solid rgba(78, 205, 196, 0.3);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .badge-check {
            background: rgba(255, 107, 107, 0.15);
            color: #ff6b6b;
            border: 1px solid rgba(255, 107, 107, 0.3);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            display: inline-block;
        }
        .table-scroll-container {
            max-height: 650px;
            overflow-y: auto;
            border: 1px solid var(--card-border);
            border-radius: 12px;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
        }
    """
    
    tab_panel_content = """
        <!-- TAB: HYPOTHESES -->
        <div id="tab-hypotheses" class="tab-panel">
            <div style="margin-bottom: 2rem; display: flex; flex-direction: column; align-items: center; text-align: center;">
                <h2 style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; margin-bottom: 0.5rem; color: #fff;">Delta Vector's 99 Hypotheses</h2>
                <p style="color: var(--text-muted); font-size: 0.95rem; max-width: 900px; margin-bottom: 1.5rem;">
                    A unified multi-disciplinary framework verifying exactly 99 physical, chemical, biological, and materials science objections. Every single constraint resolves parameter-free using the golden ratio scaling relations.
                </p>
                
                <div style="display: flex; gap: 2rem; align-items: center; justify-content: center; margin-bottom: 2rem; flex-wrap: wrap;">
                    <img src="tap_13_dimensions.png" style="max-width: 320px; border-radius: 12px; border: 1px solid var(--card-border); box-shadow: 0 0 20px var(--accent-glow);" alt="TAP 13D Star Manifold Configuration" />
                    <div style="text-align: left; max-width: 400px;">
                        <h4 style="font-family: 'Orbitron', sans-serif; color: #fff; margin-bottom: 0.5rem;">📊 Interactive 13-Dimensional Cascade Simulator</h4>
                        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
                            Each of the 13 physical dimensions is mapped to a dedicated sheet in the comprehensive report. All sheets are live-wired to the Overview parameters, allowing you to edit the golden ratio or VEV ratio and watch the entire 99-check cascade recalculate instantly.
                        </p>
                        <a href="tap_model_comprehensive_report.xlsx" class="btn" style="display: inline-block; padding: 0.75rem 1.5rem; background: var(--accent-color); color: #fff; border-radius: 8px; text-decoration: none; font-weight: 600; font-family: 'Orbitron', sans-serif; font-size: 0.85rem; transition: background 0.3s;" onmouseover="this.style.background='#6956e3'" onmouseout="this.style.background='var(--accent-color)'">📥 Download Excel Cascade Model</a>
                    </div>
                </div>
                
                <div class="search-bar-container" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
                    <input type="text" id="search-input" placeholder="Search hypothesis, critic name, or category..." style="flex: 2; min-width: 250px;">
                    <select id="filter-category" style="flex: 1; min-width: 180px;">
                        <option value="all">All Categories</option>
                        <option value="Cosmology">Cosmology</option>
                        <option value="Quantum Gravity">Quantum Gravity</option>
                        <option value="Particle Physics">Particle Physics</option>
                        <option value="Astrophysics">Astrophysics</option>
                        <option value="Nuclear Physics">Nuclear Physics</option>
                        <option value="Chemistry">Chemistry</option>
                        <option value="Biophysics">Biophysics</option>
                        <option value="Neuroscience">Neuroscience</option>
                        <option value="Materials">Materials Science</option>
                    </select>
                </div>
                
                <div class="table-scroll-container">
                    <table id="hypotheses-table" style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid var(--card-border); background: rgba(124, 106, 247, 0.05); position: sticky; top: 0; backdrop-filter: blur(5px); z-index: 10;">
                                <th style="padding: 1rem 1.2rem; width: 60px;">ID</th>
                                <th style="padding: 1rem; width: 150px;">Discipline</th>
                                <th style="padding: 1rem; width: 150px;">Critic</th>
                                <th style="padding: 1rem;">Objection Description</th>
                                <th style="padding: 1rem; text-align: right; width: 140px;">TAP Calculated</th>
                                <th style="padding: 1rem; text-align: right; width: 140px;">Expected</th>
                                <th style="padding: 1rem; text-align: right; width: 110px;">Error (%)</th>
                                <th style="padding: 1rem; text-align: center; width: 100px;">Status</th>
                            </tr>
                        </thead>
                        <tbody id="hypotheses-body">
                            <!-- Populated dynamically via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    """

    # 1. Update Title and Header in HTML
    html_content = re.sub(
        r'<h1>TAP Unified Grand Universe Dashboard</h1>',
        '<h1>Delta Vector\'s 99 Hypotheses Dashboard</h1>',
        html_content
    )
    html_content = re.sub(
        r'<p>Interactive Numerical Simulation Suite &mdash; Resolving 19 Scientific Gaps via Extra-Dimensional Solitons</p>',
        '<p>Topological Action Physics (TAP) Framework &mdash; Unified Numerical Verification of 99 Hypotheses (Delta Vector)</p>',
        html_content
    )
    
    # 2. Inject Styles
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', f'{table_styles}\n    </style>')
        
    # 3. Inject new tab button
    if '<button class="tab-btn" onclick="switchTab(event, \'tab-frontiers\')">Frontiers</button>' in html_content:
        html_content = html_content.replace(
            '<button class="tab-btn" onclick="switchTab(event, \'tab-frontiers\')">Frontiers</button>',
            '<button class="tab-btn" onclick="switchTab(event, \'tab-frontiers\')">Frontiers</button>\n            ' + tab_button
        )

    # 4. Inject Tab Content Panel
    if '<!-- TAB: FRONTIERS -->' in html_content:
        html_content = html_content.replace('<!-- TAB: FRONTIERS -->', f'{tab_panel_content}\n        <!-- TAB: FRONTIERS -->')
        
    # 5. Inject JSON data structure and dynamic rendering JS code
    js_data = f"const HYPOTHESES_DATA = {json.dumps(checks, indent=2)};\n"
    
    rendering_js = """
            // 20. Hypotheses Table Rendering and Filtering
            const hypothesesBody = document.getElementById('hypotheses-body');
            const searchInput = document.getElementById('search-input');
            const filterCategory = document.getElementById('filter-category');

            function renderHypotheses() {
                const query = searchInput.value.toLowerCase();
                const category = filterCategory.value;
                
                hypothesesBody.innerHTML = '';
                
                HYPOTHESES_DATA.forEach(h => {
                    // Match category and search query
                    const catMatch = (category === 'all') || (h.category === category);
                    const textMatch = h.critic.toLowerCase().includes(query) || 
                                      h.objection.toLowerCase().includes(query) || 
                                      h.category.toLowerCase().includes(query);
                                      
                    if (catMatch && textMatch) {
                        const tr = document.createElement('tr');
                        
                        // Format value/expected nicely
                        let valStr = h.value.toExponential(4);
                        if (Math.abs(h.value) < 10000 && Math.abs(h.value) > 0.001) {
                            valStr = h.value.toFixed(4);
                        }
                        
                        let expStr = h.expected.toExponential(4);
                        if (Math.abs(h.expected) < 10000 && Math.abs(h.expected) > 0.001) {
                            expStr = h.expected.toFixed(4);
                        }
                        
                        const unit = h.unit ? ' ' + h.unit : '';
                        const badgeClass = h.status === 'PASS' ? 'badge-pass' : 'badge-check';
                        
                        tr.innerHTML = `
                            <td style="padding: 0.85rem 1.2rem; font-weight: 600; color: var(--accent-color);">${h.id}</td>
                            <td style="font-weight: 600; color: #fff;">${h.category}</td>
                            <td style="color: #4ecdc4; font-weight: 600;">${h.critic}</td>
                            <td style="font-size: 0.85rem;">${h.objection}</td>
                            <td style="text-align: right; font-family: monospace;">${valStr}${unit}</td>
                            <td style="text-align: right; font-family: monospace;">${expStr}${unit}</td>
                            <td style="text-align: right; font-family: monospace; color: ${h.err_pct > 1.0 ? 'var(--warning-color)' : '#a1a1b3'}">${h.err_pct.toFixed(2)}%</td>
                            <td style="text-align: center;"><span class="${badgeClass}">${h.status}</span></td>
                        `;
                        hypothesesBody.appendChild(tr);
                    }
                });
            }

            searchInput.addEventListener('input', renderHypotheses);
            filterCategory.addEventListener('change', renderHypotheses);
            renderHypotheses();
    """
    
    # Inject before the final script ending tag
    if '});\n    </script>\n</body>\n</html>' in html_content:
        html_content = html_content.replace(
            '});\n    </script>\n</body>\n</html>',
            js_data + rendering_js + '});\n    </script>\n</body>\n</html>'
        )
    else:
        # Fallback to general inject
        html_content = html_content.replace(
            '// Initialize Charts when page loads',
            js_data + '\n' + '// Initialize Charts when page loads'
        )
        html_content = html_content.replace(
            'window.addEventListener(\'DOMContentLoaded\', () => {',
            'window.addEventListener(\'DOMContentLoaded\', () => {\n' + rendering_js
        )
        
    with open(dest_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Write a copy to dashboard.html too
    dashboard_path = os.path.join(root_dir, "..", "assets", "dashboard.html")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[EXPORT] Dashboard updated successfully -> {dest_html_path}")

if __name__ == "__main__":
    main()
