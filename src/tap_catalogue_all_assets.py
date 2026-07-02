# -*- coding: utf-8 -*-
"""
tap_catalogue_all_assets.py
================================
TAP v5.3.2 — Catalogue All Assets (non-JSON).

Extends the encyclopedia to include:
  - 79 .log files
  - 50 .md files
  - 26 .png files
  - 4 .html files
  - 2 .wav files
  - 2 .m4a files
  - 1 .txt file
  - 1 .hex file
  - 1 .cad file

For each: type, size, modified time, sample content.
"""

import os
import json
from datetime import datetime


def main():
    print("=" * 80)
    print("  TAP CATALOGUE ALL ASSETS")
    print("  Adding 165 non-JSON assets to encyclopedia")
    print("=" * 80)
    print()

    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    assets_dir = os.path.join(repo_root, 'assets')

    # Type-specific handlers
    HANDLERS = {
        ".png": ("image", "PNG image", "Mermaid/visualization output"),
        ".html": ("html", "HTML file", "Generated report/dashboard"),
        ".md": ("markdown", "Markdown doc", "Documentation"),
        ".log": ("log", "Log file", "Validation/tribunal log"),
        ".wav": ("audio", "WAV audio", "Voice memo or sim audio"),
        ".m4a": ("audio", "M4A audio", "Voice memo"),
        ".txt": ("text", "Text file", "Notes/observations"),
        ".hex": ("hex", "Hex dump", "Binary data dump"),
        ".cad": ("cad", "CAD data", "Geometry/3D data"),
    }

    # Group by extension
    by_ext = {}
    for f in sorted(os.listdir(assets_dir)):
        ext = os.path.splitext(f)[1]
        if ext in HANDLERS and ext != ".json":
            by_ext.setdefault(ext, []).append(f)

    # Print summary
    print("  ASSET TYPES DISCOVERED:")
    for ext, files in sorted(by_ext.items()):
        type_name, type_desc, _ = HANDLERS[ext]
        total_size = sum(os.path.getsize(os.path.join(assets_dir, f)) for f in files)
        print(f"    .{ext:6s} ({type_name:8s}): {len(files):3d} files, {total_size:,} bytes total")
    print(f"    {'TOTAL':12s}: {sum(len(f) for f in by_ext.values())} non-JSON files")
    print()

    # Build catalogue
    catalogue = {
        "timestamp": datetime.now().isoformat(),
        "n_total": sum(len(f) for f in by_ext.values()),
        "by_type": {},
    }
    for ext, files in sorted(by_ext.items()):
        type_name, type_desc, type_purpose = HANDLERS[ext]
        entries = []
        for f in files:
            filepath = os.path.join(assets_dir, f)
            size = os.path.getsize(filepath)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            entries.append({
                "name": f,
                "size_bytes": size,
                "modified": mtime,
                "type": type_name,
                "description": type_desc,
                "purpose": type_purpose,
            })
        catalogue["by_type"][type_name] = {
            "extension": ext,
            "description": type_desc,
            "purpose": type_purpose,
            "n_files": len(files),
            "total_size": sum(e["size_bytes"] for e in entries),
            "files": entries,
        }

    # Sample analysis: count discipline lines in logs
    print("  [1/3] SAMPLE ANALYSIS OF LOG FILES:")
    log_count = 0
    tribunal_count = 0
    for f in by_ext.get(".log", []):
        filepath = os.path.join(assets_dir, f)
        log_count += 1
        try:
            with open(filepath, 'r', errors='ignore') as fp:
                head = fp.read(500)
            if "DISCIPLINE" in head or "tribunal" in head.lower():
                tribunal_count += 1
        except (IOError, UnicodeDecodeError):
            pass
    print(f"    Total .log files: {log_count}")
    print(f"    Tribunal logs: {tribunal_count}")
    print()

    # Sample analysis of PNGs
    print("  [2/3] SAMPLE ANALYSIS OF PNG FILES:")
    png_files = by_ext.get(".png", [])
    print(f"    Total .png files: {len(png_files)}")
    # Categorize PNGs by name
    categories = {"mermaid": 0, "cascade": 0, "diagram": 0, "graph": 0, "other": 0}
    for f in png_files:
        if "mermaid" in f.lower():
            categories["mermaid"] += 1
        elif "cascade" in f.lower():
            categories["cascade"] += 1
        elif "diagram" in f.lower():
            categories["diagram"] += 1
        elif "graph" in f.lower():
            categories["graph"] += 1
        else:
            categories["other"] += 1
    for cat, n in categories.items():
        print(f"      {cat}: {n}")
    print()

    # Sample analysis of MDs
    print("  [3/3] SAMPLE ANALYSIS OF MD FILES:")
    md_files = by_ext.get(".md", [])
    print(f"    Total .md files: {len(md_files)}")
    # Get titles
    sample = []
    for f in md_files[:5]:
        filepath = os.path.join(assets_dir, f)
        try:
            with open(filepath, 'r', errors='ignore') as fp:
                head = fp.read(200)
            import re
            match = re.search(r'^#\s+(.+?)$', head, re.MULTILINE)
            if match:
                sample.append(f"    {f}: {match.group(1).strip()[:60]}")
            else:
                sample.append(f"    {f}")
        except (IOError, UnicodeDecodeError):
            sample.append(f"    {f}")
    for s in sample:
        print(s)
    print()

    # Save catalogue
    out_path = os.path.join(assets_dir, 'tap_full_asset_catalogue.json')
    with open(out_path, 'w') as f:
        json.dump(catalogue, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print(f"  Total assets documented: {catalogue['n_total']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
