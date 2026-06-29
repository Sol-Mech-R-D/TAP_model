# -*- coding: utf-8 -*-
"""
organize_repo.py
================
Reorganizes the TAP_model repository files into clean subfolders:
- src/ for Python/Cython source files
- docs/ for LaTeX/Markdown documentation (except README.md)
- assets/ for images, JSON data, and web dashboard files
"""

import os
import shutil

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define subdirectories
    dirs = {
        "src": os.path.join(root_dir, "src"),
        "docs": os.path.join(root_dir, "docs"),
        "assets": os.path.join(root_dir, "assets")
    }
    
    # Create directories
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
        
    # File mappings
    # We keep setup.py and README.md at the root as per standard Git conventions.
    src_extensions = [".py", ".pyx", ".c", ".pyx", ".pyd"]
    doc_extensions = [".md", ".tex"]
    asset_extensions = [".png", ".json", ".js", ".html"]
    
    exclusions = ["setup.py", "organize_repo.py", "README.md"]
    
    for filename in os.listdir(root_dir):
        file_path = os.path.join(root_dir, filename)
        
        # Skip directories and excluded files
        if os.path.isdir(file_path) or filename in exclusions:
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        
        target_dir = None
        if ext in src_extensions:
            target_dir = dirs["src"]
        elif ext in doc_extensions:
            target_dir = dirs["docs"]
        elif ext in asset_extensions:
            target_dir = dirs["assets"]
            
        if target_dir:
            dest_path = os.path.join(target_dir, filename)
            try:
                # If destination exists, remove it first to avoid collision
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)
                shutil.move(file_path, target_dir)
                print(f"[MOVE] {filename} -> {os.path.basename(target_dir)}/")
            except Exception as e:
                print(f"[ERROR] Failed to move {filename}: {e}")

if __name__ == "__main__":
    main()
