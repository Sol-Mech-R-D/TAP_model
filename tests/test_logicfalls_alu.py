# -*- coding: utf-8 -*-
"""
test_logicfalls_alu.py
======================
Unit tests for the Logicfalls ALU and the 20 distinct fall subclasses.
"""

import os
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from tap_kernel_hardware_emulator import LogicfallsALU, PhinaryALU, run_emulator
from science_constants import PHI

def test_nominal_behavior():
    alu = LogicfallsALU()
    nominal_env = {
        "v_ratio": 1.0,
        "t_hold": 0.001,
        "t_active": 0.001,
        "z_actual": 376.73 * (1.0 + (PHI ** -4) * 1.0),
        "f_measured": 40000.0,
        "f_predicted": 40000.0,
        "temp": 20.0,
        "waveguide_length": 0.05,
        "delta_t": 14.0,
        "v_drive": 3.3,
        "phase_drift": 0.0,
        "scheduler_discrepancy": 0.0,
        "pulse_jitter_us": 0.1,
        "octave_drift_hz": 5.0,
        "casimir_gap_nm": 100.0,
        "f_clock_mhz": 1.0,
        "hbridge_temp": 30.0,
        "snr_db": 30.0,
        "v_piezo_burst": 1.2,
        "leyline_distance": 10.0,
        "rand_val": 0.99
    }
    report = alu.evaluate_falls(nominal_env)
    active_falls = [name for name, details in report.items() if details["triggered"]]
    assert len(active_falls) == 0
    
    # Test phinary calculation
    res = alu.phinary_add(2.0, 3.0)
    assert "ERROR" not in res
    assert "2" not in res

def test_stressed_tldfall():
    alu = LogicfallsALU()
    stressed_env = {
        "v_ratio": 1.0,
        "t_hold": 0.001,
        "t_active": 0.001,
        "z_actual": 376.73,
        "f_measured": 40000.0,
        "f_predicted": 40000.0,
        "temp": 20.0,
        "waveguide_length": 0.05,
        "delta_t": 14.0,
        "v_drive": 3.3,
        "phase_drift": 0.0,
        "scheduler_discrepancy": 0.0,
        "pulse_jitter_us": 0.1,
        "octave_drift_hz": 5.0,
        "casimir_gap_nm": 100.0,
        "f_clock_mhz": 1.0,
        "hbridge_temp": 30.0,
        "snr_db": 2.0,  # low SNR -> triggers TldFall
        "v_piezo_burst": 1.2,
        "leyline_distance": 10.0,
        "rand_val": 0.99
    }
    report = alu.evaluate_falls(stressed_env)
    assert report["TldFall"]["triggered"] is True
    res = alu.phinary_add(2.0, 3.0)
    assert res == "ERROR: COMMAND_CORRUPTED"

def test_stressed_phinaryfall():
    alu = LogicfallsALU()
    stressed_env = {
        "v_ratio": 1.0,
        "t_hold": 0.001,
        "t_active": 0.001,
        "z_actual": 376.73,
        "f_measured": 40000.0,
        "f_predicted": 40000.0,
        "temp": 20.0,
        "waveguide_length": 0.05,
        "delta_t": 14.0,
        "v_drive": 3.3,
        "phase_drift": 0.0,
        "scheduler_discrepancy": 0.0,
        "pulse_jitter_us": 0.1,
        "octave_drift_hz": 5.0,
        "casimir_gap_nm": 100.0,
        "f_clock_mhz": 15.0,  # high frequency clock -> triggers PhinaryFall
        "hbridge_temp": 30.0,
        "snr_db": 30.0,
        "v_piezo_burst": 1.2,
        "leyline_distance": 10.0,
        "rand_val": 0.99
    }
    report = alu.evaluate_falls(stressed_env)
    assert report["PhinaryFall"]["triggered"] is True
    res = alu.to_phinary(5.0)
    assert "2" in res or "011" in res

def test_run_emulator_nominal():
    results = run_emulator()
    assert results["v_ratio"] > 0
    assert len(results["nominal_active_falls"]) == 0
    assert "ERROR" not in results["nominal_phinary_sum_5"]
    assert "ERROR" in results["stressed_phinary_sum_5"] or len(results["stressed_active_falls"]) > 0
