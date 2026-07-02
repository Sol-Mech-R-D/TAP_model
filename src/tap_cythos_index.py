# -*- coding: utf-8 -*-
"""
tap_cythos_index.py
======================
TAP v5.3.2 — CythOS Code Index.

Catalogs and indexes the 800+ C/Python files in
the CythOS codebase (/data/data/com.termux/files/home/CythOS)
and adds them to the encyclopedia index.

The CythOS codebase contains the CyGemm inference
engine, SM-HNSW (already indexed), CCP compiler,
and other infrastructure that the TAP framework
relies on.

Each file becomes an entry with:
  - Path
  - Language (.c, .h, .py)
  - Size
  - First line / description
  - Key functions (for .c files)
  - Category (bridge, alloc, runtime, etc.)
"""

import os
import json
import re
import sys
import subprocess
from datetime import datetime
from collections import defaultdict


def extract_c_functions(filepath: str, max_funcs: int = 10) -> list:
    """Extract function signatures from a C file."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        # Find function definitions
        # Pattern: return_type name(args) { ... }
        matches = re.findall(r'^[\w\s\*]+?\s+(\w+)\s*\([^)]*\)\s*\{', content, re.MULTILINE)
        # Filter out keywords
        keywords = {'if', 'for', 'while', 'switch', 'return', 'else'}
        return [m for m in matches if m not in keywords][:max_funcs]
    except (IOError, UnicodeDecodeError):
        return []


def extract_python_docstring(filepath: str) -> str:
    """Extract module docstring from a Python file."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        match = re.match(r'^[\s]*"""([\s\S]*?)"""', content)
        if match:
            return match.group(1).strip().split('\n')[0][:200]
        match = re.match(r"^[\s]*'''([\s\S]*?)'''", content)
        if match:
            return match.group(1).strip().split('\n')[0][:200]
        return ""
    except (IOError, UnicodeDecodeError):
        return ""


def categorize(path: str) -> str:
    """Categorize a CythOS file by path."""
    if 'bridge' in path:
        return 'bridge'
    if 'alloc' in path.lower() or 'memory' in path.lower():
        return 'memory'
    if 'runtime' in path.lower():
        return 'runtime'
    if 'cygemm' in path.lower() or 'gemm' in path.lower():
        return 'gemm'
    if 'cascade' in path.lower():
        return 'cascade'
    if 'hnsw' in path.lower():
        return 'hnsw'
    if 'moe' in path.lower() or 'expert' in path.lower():
        return 'moe'
    if 'kernel' in path.lower() or 'dispatch' in path.lower():
        return 'kernel'
    if 'core' in path.lower():
        return 'core'
    if 'ccp' in path.lower():
        return 'ccp'
    if 'alternative' in path.lower():
        return 'alternative-vibration-network'
    if 'sim' in path.lower():
        return 'sim'
    if 'test' in path.lower():
        return 'test'
    return 'other'


def main():
    print("=" * 80)
    print("  TAP CYTHOS CODE INDEX")
    print("  Indexing 800+ CythOS source files")
    print("=" * 80)
    print()

    cythos_root = "/data/data/com.termux/files/home/CythOS"
    if not os.path.exists(cythos_root):
        print(f"  CythOS not found at {cythos_root}")
        return

    # Find all C, H, Python files
    print("  [1/4] DISCOVER CYTHOS FILES:")
    files = []
    for ext in ['.c', '.h', '.py']:
        for root, dirs, fs in os.walk(cythos_root):
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in fs:
                if f.endswith(ext):
                    filepath = os.path.join(root, f)
                    relpath = os.path.relpath(filepath, cythos_root)
                    size = os.path.getsize(filepath)
                    files.append({
                        'path': filepath,
                        'relpath': relpath,
                        'name': f,
                        'ext': ext,
                        'size_bytes': size,
                    })

    # Group by extension
    by_ext = defaultdict(list)
    for f in files:
        by_ext[f['ext']].append(f)

    for ext, fs in sorted(by_ext.items()):
        total_size = sum(f['size_bytes'] for f in fs)
        print(f"    .{ext:3s}: {len(fs):4d} files, {total_size:>12,} bytes total")
    print(f"    TOTAL: {len(files)} files")
    print()

    # Sample some files
    print("  [2/4] SAMPLE FILE ANALYSIS:")
    sample_files = [
        'cygemm/hnsw_sm.c',
        'cygemm/hnsw_sm.h',
        'cygemm/cygemm_hnsw.c',
    ]
    for s in sample_files:
        for f in files:
            if f['relpath'] == s:
                funcs = extract_c_functions(f['path']) if s.endswith('.c') else []
                print(f"    {f['relpath']}:")
                print(f"      Size: {f['size_bytes']:,} bytes")
                if funcs:
                    print(f"      Functions: {', '.join(funcs[:8])}")
                break
    print()

    # Categorize
    print("  [3/4] CATEGORIZE ALL FILES:")
    by_category = defaultdict(list)
    for f in files:
        cat = categorize(f['relpath'])
        f['category'] = cat
        by_category[cat].append(f)
    for cat, fs in sorted(by_category.items(), key=lambda x: -len(x[1])):
        total_size = sum(f['size_bytes'] for f in fs)
        print(f"    {cat:30s}: {len(fs):4d} files, {total_size:>12,} bytes")
    print()

    # Build catalogue
    print("  [4/4] BUILD INDEX:")
    # Add category, functions, docstring to each file
    for f in files:
        if f['ext'] == '.c':
            f['functions'] = extract_c_functions(f['path'])
        elif f['ext'] == '.py':
            f['docstring'] = extract_python_docstring(f['path'])
        else:
            f['functions'] = []

    # Save the index
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    out_dir = os.path.join(repo_root, 'assets')
    out_path = os.path.join(out_dir, 'tap_cythos_index.json')
    output = {
        'timestamp': datetime.now().isoformat(),
        'n_total': len(files),
        'n_by_ext': {ext: len(fs) for ext, fs in by_ext.items()},
        'n_by_category': {cat: len(fs) for cat, fs in by_category.items()},
        'files': files,
    }
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  [EXPORT] -> {out_path}")
    print(f"  Index size: {os.path.getsize(out_path):,} bytes")
    print()

    # Now also rebuild the SM-HNSW index with the CythOS entries
    print("  [5/5] REBUILDING COMBINED SM-HNSW INDEX WITH CYTHOS ENTRIES:")
    sys_path = os.path.dirname(os.path.abspath(__file__))
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from tap_sm_hnsw import HNSWGraph, text_to_vector

    g = HNSWGraph(dim=64)
    n_added = 0

    # Add TAP entries
    enc_path = os.path.join(out_dir, 'tap_encyclopedia_full.json')
    with open(enc_path, 'r') as fp:
        encyclopedia = json.load(fp)
    for k, c in encyclopedia.get("constants", {}).items():
        label = f"constant: {c['name']}"
        text = f"{c['name']} {c.get('formula', '')}"
        g.add_node(text_to_vector(text, dim=64), label=label)
        n_added += 1
    for k, p in encyclopedia.get("predictions", {}).items():
        label = f"prediction: {k}"
        g.add_node(text_to_vector(f"{k} {p['name']}", dim=64), label=label)
        n_added += 1
    for s in encyclopedia.get("scripts", []):
        label = f"script: {s['name']}"
        g.add_node(text_to_vector(f"{s['name']} {s.get('purpose', '')}", dim=64), label=label)
        n_added += 1
    for d in encyclopedia.get("docs", []):
        label = f"doc: {d['name']}"
        g.add_node(text_to_vector(f"{d['name']} {d.get('title', '')}", dim=64), label=label)
        n_added += 1

    # Add CythOS entries (sampled to avoid bloat)
    cythos_added = 0
    for f in files:
        if cythos_added > 150:  # cap
            break
        label = f"cythos: {f['relpath']}"
        text = f"{f['name']} {f.get('functions', [''])[0] if f.get('functions') else ''} {f.get('docstring', '')}"
        g.add_node(text_to_vector(text, dim=64), label=label)
        cythos_added += 1
        n_added += 1

    print(f"    Added: {n_added} nodes ({cythos_added} CythOS + {n_added - cythos_added} TAP)")
    print(f"    Max layer: {g.max_level}")

    # Save combined index
    combined_path = os.path.join(out_dir, 'tap_combined_index.json')
    out_data = g.to_dict()
    out_data["n_tap"] = n_added - cythos_added
    out_data["n_cythos"] = cythos_added
    with open(combined_path, 'w') as f:
        json.dump(out_data, f, indent=2, default=str)
    print(f"    [EXPORT] -> {combined_path}")
    print(f"    Combined index: {os.path.getsize(combined_path):,} bytes")
    print()

    print("  CYTHOS INDEX BUILT:")
    print(f"    Files: {len(files)}")
    print(f"    Categories: {len(by_category)}")
    print(f"    Combined SM-HNSW: {n_added} nodes")
    print("=" * 80)


if __name__ == "__main__":
    main()
