#!/bin/bash
# TAP daily prediction wrapper
# Runs all 5 daily checks + recalibration

set -e

REPO="/data/data/com.termux/files/home/TAP_model"
cd "$REPO"

echo "==================================="
echo "  TAP DAILY CHECK — $(date)"
echo "==================================="
echo

# 1. Daily prediction check (fetches live data)
echo "[1/4] Daily prediction check..."
python3 src/tap_daily_prediction_check.py 2>&1 | tail -30
echo

# 2. Weather recalibration (re-runs every day as new actuals come in)
echo "[2/4] Weather recalibration..."
python3 src/tap_weather_recalibration.py 2>&1 | tail -15
echo

# 3. Kp prediction
echo "[3/4] Kp prediction..."
python3 src/tap_kp_prediction_sim.py 2>&1 | tail -20
echo

# 4. Finance re-screen at multiple thresholds
echo "[4/4] Finance re-screen..."
python3 src/tap_finance_rescreen.py 2>&1 | tail -15
echo

echo "==================================="
echo "  DAILY CHECK COMPLETE"
echo "==================================="
