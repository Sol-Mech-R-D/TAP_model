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
    "assets/tap_core_ai_coupling.json"
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

    # 2. Stage and commit only PUBLIC files to a temp public branch
    print("\n  [STEP 1] Staging public files subset...")
    run_git(["checkout", "-b", "temp-public"])
    run_git(["reset"]) # clear staging area
    
    staged_count = 0
    for f in PUBLIC_FILES:
        if os.path.exists(f):
            run_git(["add", f])
            staged_count += 1
            
    print(f"  Staged {staged_count} public files.")
    
    commit_msg = "feat(public): update core science, weather, and agriculture models"
    print(f"  [COMMIT] Committing public files to temp branch...")
    run_git(["commit", "-m", commit_msg])
    
    print("  [PUSH] Pushing public branch to origin/master (Sol-Mech R&D)...")
    push_res = run_git(["push", "origin", "temp-public:master", "--force"])
    if push_res.returncode == 0:
        print("  ✅ Public push successful!")
    else:
        print("  ⚠️ Public push failed. Check remote credentials.")

    # 3. Stage and commit ALL files to master and push to private
    print("\n  [STEP 2] Preparing full repository push (bigcaker)...")
    run_git(["checkout", "master"])
    run_git(["branch", "-D", "temp-public"]) # cleanup temp branch
    
    run_git(["add", "."]) # stage everything
    commit_msg_all = "feat(private): update full macro-economic, grid stress, and core dynamos cascade"
    run_git(["commit", "-am", commit_msg_all])
    
    print("  [PUSH] Pushing entire repository to private/master (bigcaker)...")
    push_priv_res = run_git(["push", "private", "master", "--force"])
    if push_priv_res.returncode == 0:
        print("  ✅ Private push successful!")
    else:
        print("  ⚠️ Private push failed. Check remote credentials or configure URL.")
        print("     Ensure bigcaker repo exists at the designated address.")
        
    print("=" * 80)
    print("  REPOSITORY SPLIT PUSH CASCADE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
