# -*- coding: utf-8 -*-
"""
git_push_cascade.py
===================
Orchestrates the split push mechanism between:
  1. Public Repo (Sol-Mech-R-D/TAP_model): Core science, weather, and agriculture files.
  2. Private Repo (bigcaker/TAP_model): Full codebase including finance, grid, and politics.

Algorithm:
  1. Add private remote if not present.
  2. Commit and push the public subset to origin/master.
  3. Commit and push the entire codebase (including private files) to private/master.
"""

import subprocess
import sys
import os

PUBLIC_FILES = [
    # Core Science
    "src/science_constants.py",
    "src/tap_proof.py",
    "src/tap_super_tribunal_99.py",
    "src/tap_tappasecond.py",
    "src/tap_trans_cyclic_sweep.py",
    "src/tap_breath_clock.py",
    "src/generate_chunks_14_26.py",
    "src/generate_chunks_27_29.py",
    "src/tap_massive_fibonacci_sweep.py",
    "src/tap_high_dimension_sweep.py",
    "src/update_dashboard.py",
    "README.md",
    
    # Weather & Geophysics
    "src/tap_fresno_weather.py",
    "src/tap_seismic_correlation.py",
    "src/tap_geophysics_brainstorm.py",
    "src/tap_core_ai_cascade.py",
    
    # Documents
    "docs/TAP_Tappasecond.md",
    "docs/TAP_Dynasty6_TransCyclic.md",
    "docs/TAP_Fresno_July2026_Weather.md",
    "docs/TAP_Geophysics_Weather_Brainstorm.md",
    "docs/TAP_SubBreaths_Conversions.md",
    "docs/TAP_Mandela_Effect_Conformal_Overlaps.md",
    "docs/TAP_Model_Explanation.md",
    "docs/TAP_Master_Map_Dynasties.md",
    "docs/TAP_Cross_Chunk_Interactions.md",
    "docs/TAP_Warp_and_Time_Travel.md",
    "docs/TAP_PlanetaryCores_AI_Energy_Brainstorm.md",
    
    # Assets / Public Data
    "assets/tap_fresno_july2026.json",
    "assets/tap_geophysics_timeline.json",
    "assets/tap_seismic_predictions_1year.json",
    "assets/tap_super_tribunal_99_results.json",
    "assets/tap_universe_dashboard.html",
    "assets/dashboard.html",
    "assets/tap_parameter_sweep.png",
    "assets/tap_proof_plots.png",
    "assets/tap_core_ai_coupling.json",
    "src/tap_usgs_monitor.py",
    "src/tap_solar_dynamo.py",
    "src/tap_quantum_decoherence.py",
    "src/tap_neural_resonance.py",
    "src/tap_cosmic_quantum_neuro.py",
    "src/tap_biochem_qubit_graphene.py",
    "src/tap_qubit_driver.ino",
    "src/read_qubit.py",
    "src/flash_arduino.py",
    "src/tap_superconductivity_sweep.py",
    "docs/TAP_Cosmic_Quantum_Neuro_Brainstorm.md",
    "docs/TAP_Biochem_Qubit_Graphene_Brainstorm.md",
    "docs/TAP_Macro_Qubit_Graphene_Schematic.md",
    "assets/tap_usgs_monitor_results.json",
    "assets/tap_solar_dynamo_results.json",
    "assets/tap_quantum_decoherence_results.json",
    "assets/tap_neural_resonance_results.json",
    "assets/tap_cosmic_quantum_neuro_results.json",
    "assets/tap_biochem_qubit_graphene_results.json",
    "assets/tap_qubit_driver.hex",
    "assets/tap_superconductivity_sweep.png",
    "assets/tap_piezo_chassis.scad",
    "assets/tap_octahedral_cabinet.scad",
    "docs/TAP_Theory_Paper.md",
    "docs/TAP_White_Paper.md",
    "docs/TAP_Hardware_Bill_of_Materials.md",
    "docs/TAP_Capacitor_and_Diode_Inventory.md",
    "docs/TAP_8th_Grade_Fundamentals_Curriculum.md",
    "docs/TAP_12th_Grade_Peer_Review_Curriculum.md",
    "docs/TAP_Superconductivity_Sweep_Results.md",
    "TERMUX_NOTE.md",
    "PXL_20260620_152100745.jpg",
    "PXL_20260620_152104825.jpg",
    "PXL_20260620_152109446.jpg",
    "PXL_20260621_042227933.jpg",
    "PXL_20260621_045224611.jpg",
    "PXL_20260621_045228411.jpg",
    "PXL_20260621_045237400.jpg",
    "PXL_20260621_045250728.jpg",
    "PXL_20260621_045256350.jpg",
    "PXL_20260621_045329709.jpg",
    "PXL_20260621_045410932.jpg",
    "PXL_20260621_045419627.jpg",
    "PXL_20260621_045421777.jpg",
    "PXL_20260621_053056488.jpg",
    "PXL_20260621_053059523.jpg",
    "PXL_20260621_053111213.jpg"
]

def run_git(args):
    res = subprocess.run(["git"] + args, capture_output=True, text=True)
    if res.returncode != 0:
         print(f"  [GIT ERROR] Command 'git {' '.join(args)}' failed:")
         print(res.stderr)
    return res

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(root_dir, ".."))
    
    print("=" * 80)
    print("  TAP REPOSITORY SPLIT PUSH CASCADE")
    print("=" * 80)

    # 1. Check if private remote is configured
    remotes_res = run_git(["remote"])
    remotes = remotes_res.stdout.split()
    
    private_url = "https://github.com/thebigcaker/TAP_model.git" # use HTTPS to support token/credential helper
    if "private" not in remotes:
        print(f"  [CONFIG] Adding private remote pointing to: {private_url}")
        run_git(["remote", "add", "private", private_url])
    else:
        # Get actual configured private URL
        v_res = run_git(["remote", "-v"])
        print("  [CONFIG] Existing remotes:")
        for line in v_res.stdout.splitlines():
            print(f"    {line}")

    # Add all F-Levels sheets to public files dynamically
    docs_dir = "docs"
    if os.path.exists(docs_dir):
        for f in os.listdir(docs_dir):
            if f.startswith("TAP_F_Levels_") and f.endswith(".md"):
                PUBLIC_FILES.append(os.path.join(docs_dir, f))

    # 2. Stage and commit ALL files to master first to prevent loss of files
    print("\n  [STEP 1] Committing all files to master...")
    run_git(["add", "."])
    commit_msg_all = "feat(master): update full macro-economic, grid stress, and core dynamos cascade"
    run_git(["commit", "-m", commit_msg_all])

    # 3. Stage and commit only PUBLIC files to a temp public branch
    print("\n  [STEP 2] Preparing public files subset...")
    
    # Ensure any old temp-public branch is deleted
    run_git(["branch", "-D", "temp-public"])
    run_git(["checkout", "-b", "temp-public"])
    
    # Physically delete any untracked or private files to ensure they don't get committed
    staged_count = 0
    for root, dirs, files in os.walk("."):
        if ".git" in root.split(os.sep):
            continue
        for file in files:
            filepath = os.path.relpath(os.path.join(root, file), ".")
            filepath_norm = filepath.replace("\\", "/")
            if filepath_norm not in PUBLIC_FILES:
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    # Clean up empty directories
    for root, dirs, files in os.walk(".", topdown=False):
        if ".git" in root.split(os.sep):
            continue
        for d in dirs:
            dirpath = os.path.join(root, d)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
            except Exception:
                pass
                
    # Stage all modifications and deletions
    run_git(["add", "-A"])
    
    # Count actually staged files
    status_res = run_git(["status", "--porcelain"])
    staged_files = [line for line in status_res.stdout.splitlines() if not line.startswith("??")]
    print(f"  Staged {len(staged_files)} file changes for public release.")
    
    commit_msg = "feat(public): update core science, weather, and agriculture models"
    print(f"  [COMMIT] Committing public files to temp branch...")
    run_git(["commit", "-m", commit_msg])
    
    print("  [PUSH] Pushing public branch to origin/master (Sol-Mech R&D)...")
    push_res = run_git(["push", "origin", "temp-public:master", "--force"])
    if push_res.returncode == 0:
        print("  [SUCCESS] Public push successful!")
    else:
        print("  [WARNING] Public push failed. Check remote credentials.")

    # 4. Switch back to master and push to private
    print("\n  [STEP 3] Preparing full repository push (bigcaker)...")
    run_git(["checkout", "-f", "master"]) # force checkout to restore deleted private files
    run_git(["branch", "-D", "temp-public"]) # cleanup temp branch
    
    print("  [PUSH] Pushing entire repository to private/master (bigcaker)...")
    push_priv_res = run_git(["push", "private", "master", "--force"])
    if push_priv_res.returncode == 0:
        print("  [SUCCESS] Private push successful!")
    else:
        print("  [WARNING] Private push failed. Check remote credentials or configure URL.")
        print("     Ensure bigcaker repo exists at the designated address.")
        
    print("=" * 80)
    print("  REPOSITORY SPLIT PUSH CASCADE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
