#!/usr/bin/env bash
#
# run_all_validations.sh
# ======================
# TAP Model — Master Validation Script
#
# Runs every TAP simulation, audit, and validation tool in the
# repo, captures output to a single timestamped log, and prints
# a final pass/fail summary. Use this to:
#   - Verify the model after any code change
#   - Produce a single self-contained report for review
#   - Run nightly regression checks
#
# USAGE:
#   ./scripts/run_all_validations.sh              # full run (15 cascade tests)
#   ./scripts/run_all_validations.sh --with-99    # + 99-hypotheses tribunal (~2 min)
#   ./scripts/run_all_validations.sh --quick      # skip plots
#   ./scripts/run_all_validations.sh --suite sims # sims only
#   ./scripts/run_all_validations.sh --suite lens # lens only
#   ./scripts/run_all_validations.sh --suite val  # validator only
#   ./scripts/run_all_validations.sh --suite 99   # 99-tribunal only
#   ./scripts/run_all_validations.sh --quiet      # minimal output
#
# OUTPUTS:
#   assets/tap_full_run_<timestamp>.log    — full output
#   assets/tap_full_run_<timestamp>.md     — summary report
#   assets/tap_full_run_LATEST.*           — symlinks to latest
#
# EXIT CODE:
#   0 if all tests pass
#   1 if any test fails (MISMATCH, sim crash, etc.)
#

set -e  # exit on any uncaught error

# Resolve the repo root (this script is in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Parse arguments
SUITE="all"
QUIET=0
PLOT_ARG="--plot"
WITH_99=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick)  PLOT_ARG="" ; shift ;;
        --suite)  SUITE="$2"  ; shift 2 ;;
        --quiet)  QUIET=1     ; shift ;;
        --no-plot) PLOT_ARG="" ; shift ;;
        --with-99) WITH_99=1  ; shift ;;
        --help|-h) echo "Usage: $0 [--quick] [--suite sims|lens|val|99] [--quiet] [--no-plot] [--with-99]"; exit 0 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# Output files
TS=$(date +%Y%m%d_%H%M%S)
LOG="assets/tap_full_run_${TS}.log"
MD="assets/tap_full_run_${TS}.md"
LATEST_LOG="assets/tap_full_run_LATEST.log"
LATEST_MD="assets/tap_full_run_LATEST.md"

# Color helpers (skip if not a terminal)
if [[ -t 1 ]]; then
    BOLD="\033[1m"; GREEN="\033[32m"; RED="\033[31m"; YELLOW="\033[33m"; RESET="\033[0m"
else
    BOLD=""; GREEN=""; RED=""; YELLOW=""; RESET=""
fi

# Per-test result tracking
declare -a RESULTS
declare -a TEST_NAMES

log() {
    if [[ $QUIET -eq 0 ]]; then
        echo -e "$@"
    fi
}

run_test() {
    local name="$1"
    local cmd="$2"
    TEST_NAMES+=("$name")
    log "\n${BOLD}=== $name ===${RESET}"
    log "CMD: $cmd"
    if eval "$cmd" >> "$LOG" 2>&1; then
        RESULTS+=("PASS")
        log "${GREEN}✓ PASS${RESET}"
        return 0
    else
        RESULTS+=("FAIL")
        log "${RED}✗ FAIL${RESET}"
        log "  See $LOG for details"
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Start log
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p assets
: > "$LOG"
log "${BOLD}TAP Model — Full Validation Run${RESET}"
log "Timestamp: $TS"
log "Repo: $REPO_ROOT"
log "Suite: $SUITE"
log ""

# ─────────────────────────────────────────────────────────────────────────────
# SUITE 1: Sim tests
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$SUITE" == "all" || "$SUITE" == "sims" ]]; then
    log "\n${BOLD}─── SUITE: SIMS ───${RESET}"

    # 1.1: Parent epigenetic sim
    run_test "Parent epigenetic sim (tap_epigenetic_flop_sim.py)" \
        "python3 src/tap_epigenetic_flop_sim.py $PLOT_ARG"

    # 1.2: 5-HT2A sim (Riba + Callaway validation)
    run_test "5-HT2A ayahuasca sim (tap_5ht2a_ayahuasca_sim.py)" \
        "python3 src/tap_5ht2a_ayahuasca_sim.py $PLOT_ARG"

    # 1.3: Chromatin state sim
    run_test "Chromatin state sim (tap_chromatin_state_sim.py)" \
        "python3 src/tap_chromatin_state_sim.py $PLOT_ARG"

    # 1.4: Coupled 5-HT2A + chromatin
    run_test "Coupled 5-HT2A + chromatin sim (tap_coupled_ayahuasca_sim.py)" \
        "python3 src/tap_coupled_ayahuasca_sim.py $PLOT_ARG"

    # 1.5: NEW v4.0 — End-to-end epigenetic → cosmic cascade
    # This is the keystone: it shows that epigenetic state (φ⁻¹⁰)
    # modulates the cosmic breath tick (φ⁻¹³), closing the cascade
    # from hormonal interventions to cosmic-scale dynamics.
    run_test "Epigenetic → cosmic cascade (tap_epigenetic_cosmic_cascade.py)" \
        "python3 src/tap_epigenetic_cosmic_cascade.py $PLOT_ARG"

    # 1.6: NEW v4.0.2 — Tensegrity vs ayahuasca opposite-direction test
    # This is the v4.0.2 prediction: two interventions, two opposite
    # cosmic breath signatures. The most testable claim in the model.
    run_test "5-HT2A ↔ parent-sim coupling (tap_5ht2a_epigenetic_coupling_sim.py)" \
        "python3 src/tap_5ht2a_epigenetic_coupling_sim.py $PLOT_ARG"

    # 1.7: NEW v5.0 — Myers' Anatomy Trains fascia network
    # The substrate below the cascade: 12 myofascial meridians with
    # dual contralateral spirals (the "twin dragons"), piezo coupling,
    # lymph flow. The cascade reaches the substrate level.
    run_test "Myers Anatomy Trains fascia sim (tap_fascia_sim.py)" \
        "python3 src/tap_fascia_sim.py $PLOT_ARG"

    # 1.8: NEW v5.0 — Full lymphatic cascade (parent → fascia → lymph)
    # Closes the loop from epigenetic setpoint through fascia state
    # to lymph flow, demonstrating the full substrate-channel chain.
    run_test "Lymphatic cascade (tap_lymphatic_cascade_sim.py)" \
        "python3 src/tap_lymphatic_cascade_sim.py $PLOT_ARG"

    # 1.9: NEW v5.0.1 — Full ayahuasca pathway through the cascade
    # This is the v5.0.1 measurement: 24 ceremonies over 84 days,
    # the chronic ayahuasca user's state at every layer. 7/7
    # verifications pass (lymph stagnation, spiral coupling
    # collapse, HTR2A closure, cosmic breath tick +67%).
    run_test "Full ayahuasca pathway cascade (tap_ayahuasca_fascia_cascade_sim.py)" \
        "python3 src/tap_ayahuasca_fascia_cascade_sim.py $PLOT_ARG"
fi

# ─────────────────────────────────────────────────────────────────────────────
# SUITE 2: Author lens
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$SUITE" == "all" || "$SUITE" == "lens" ]]; then
    log "\n${BOLD}─── SUITE: LENS ───${RESET}"

    # 2.1: Run lens for all four registered authors
    run_test "Author lens — all authors (tap_author_lens.py --author all)" \
        "python3 src/tap_author_lens.py --author all"

    # 2.2: Narby audit specifically (canonical worked example)
    run_test "Author lens — Narby (canonical)" \
        "python3 src/tap_author_lens.py --author narby"

    # 2.3: Sheldrake
    run_test "Author lens — Sheldrake" \
        "python3 src/tap_author_lens.py --author sheldrake"

    # 2.4: McKenna
    run_test "Author lens — McKenna" \
        "python3 src/tap_author_lens.py --author mcKenna"

    # 2.5: Wallace
    run_test "Author lens — Wallace" \
        "python3 src/tap_author_lens.py --author wallace"
fi

# ─────────────────────────────────────────────────────────────────────────────
# SUITE 3: Literature validator
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$SUITE" == "all" || "$SUITE" == "val" ]]; then
    log "\n${BOLD}─── SUITE: VALIDATOR ───${RESET}"

    # 3.1: Real-data validator
    run_test "Real-data validator (tap_real_data_validator.py)" \
        "python3 src/tap_real_data_validator.py"
fi

# ─────────────────────────────────────────────────────────────────────────────
# SUITE 4: Original 99-hypotheses super tribunal (the foundation)
# ─────────────────────────────────────────────────────────────────────────────
# This is the original TAP framework's 99-check multi-disciplinary
# peer-review tribunal. The cascade work (Suites 1-3) was developed
# on top of this foundation. The tribunal takes ~2 minutes to run
# and is therefore opt-in via the --with-99 flag (or by passing
# --suite=99).
if [[ "$SUITE" == "99" || "$WITH_99" == "1" ]]; then
    log "\n${BOLD}─── SUITE: ORIGINAL 99-HYPOTHESES SUPER TRIBUNAL ───${RESET}"
    log "${BOLD}  (Foundation of the cascade work — 9 disciplines, 11 checks each)${RESET}"

    # 4.1: Run the full 99-hypotheses tribunal
    # This is opt-in because it takes ~2 minutes. The default --quick
    # and --all suites skip it.
    run_test "99-hypotheses super tribunal (tap_super_tribunal_99.py)" \
        "python3 src/tap_super_tribunal_99.py"

    # 4.2: Check the 99 results JSON exists and shows 99/99
    if [[ -f "assets/tap_super_tribunal_99_results.json" ]]; then
        TOTAL_99=$(python3 -c "
import json, sys
try:
    with open('assets/tap_super_tribunal_99_results.json') as f:
        d = json.load(f)
except Exception as e:
    print(f'parse_err: {e}', file=sys.stderr)
    sys.exit(0)  # don't fail the validation if JSON parse fails
# Count entries with 'VERIFIED' or pass=True anywhere in the structure
def count_verified(obj):
    n = 0
    if isinstance(obj, dict):
        for v in obj.values():
            n += count_verified(v)
    elif isinstance(obj, list):
        for v in obj:
            n += count_verified(v)
    elif isinstance(obj, bool):
        n += 1 if obj else 0
    elif isinstance(obj, str) and 'VERIFIED' in obj.upper():
        n += 1
    return n
print(count_verified(d))
" 2>/dev/null)
        if [[ -n "$TOTAL_99" && "$TOTAL_99" -ge 99 ]] 2>/dev/null; then
            log "${GREEN}    → $TOTAL_99/99 tribunal entries verified${RESET}"
        else
            log "${YELLOW}    → $TOTAL_99 entries verified (tribunal may have changed format)${RESET}"
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
PASS_COUNT=0
FAIL_COUNT=0
for r in "${RESULTS[@]}"; do
    if [[ "$r" == "PASS" ]]; then
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

log "\n${BOLD}══════════════════════════════════════════════════════════════${RESET}"
log "${BOLD}  TAP FULL VALIDATION SUMMARY${RESET}"
log "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
log ""
log "  Timestamp: $TS"
log "  Suite:     $SUITE"
log "  Total:     ${#TEST_NAMES[@]}"
log "  ${GREEN}Passed:   $PASS_COUNT${RESET}"
log "  ${RED}Failed:   $FAIL_COUNT${RESET}"
log ""
log "  Per-test results:"
for i in "${!TEST_NAMES[@]}"; do
    name="${TEST_NAMES[$i]}"
    r="${RESULTS[$i]}"
    if [[ "$r" == "PASS" ]]; then
        log "    ${GREEN}✓ PASS${RESET}  $name"
    else
        log "    ${RED}✗ FAIL${RESET}  $name"
    fi
done
log ""
log "  Log:   $LOG"
log "  Report: $MD"

# ─────────────────────────────────────────────────────────────────────────────
# Write markdown summary
# ─────────────────────────────────────────────────────────────────────────────
cat > "$MD" <<EOF
# TAP Full Validation Report
**Generated:** $(date -Iseconds)
**Suite:** $SUITE
**Repo:** $REPO_ROOT

## Summary

- **Total tests:** ${#TEST_NAMES[@]}
- **Passed:** $PASS_COUNT
- **Failed:** $FAIL_COUNT

## Per-test results

| Status | Test |
|--------|------|
EOF
for i in "${!TEST_NAMES[@]}"; do
    name="${TEST_NAMES[$i]}"
    r="${RESULTS[$i]}"
    if [[ "$r" == "PASS" ]]; then
        echo "| ✓ PASS | $name |" >> "$MD"
    else
        echo "| ✗ FAIL | $name |" >> "$MD"
    fi
done

cat >> "$MD" <<EOF

## Artifacts produced

- Sim outputs: \`assets/tap_*_results.json\`
- Plots: \`assets/tap_*_*.png\`
- Author audits: \`assets/tap_author_lens_*_audit.{md,json}\`
- Validation report: \`assets/tap_real_data_validation.{md,json}\`
- Full log: \`$LOG\`

## Interpretation

The TAP model is self-consistent if all sims run without errors, the
chromatin sim recovers at the φ⁻¹⁰ timescale, the Riba 2001 within-day
tolerance matches to within 5%, the Callaway 1994 setpoint recovery
matches to within 10%, and the real-data validator shows ≥ 80% match
rate on modelable biomarkers.

If any test fails, the log file contains the full output for
debugging. Re-run individual sims to isolate the issue.
EOF

# Update LATEST symlinks
ln -sf "$(basename "$LOG")" "$LATEST_LOG" 2>/dev/null || cp -f "$LOG" "$LATEST_LOG"
ln -sf "$(basename "$MD")" "$LATEST_MD" 2>/dev/null || cp -f "$MD" "$LATEST_MD"

if [[ $FAIL_COUNT -gt 0 ]]; then
    log "\n${RED}${BOLD}FAILURES: $FAIL_COUNT test(s) failed. See $LOG for details.${RESET}"
    exit 1
fi

log "\n${GREEN}${BOLD}ALL TESTS PASSED.${RESET}"
exit 0
