# -*- coding: utf-8 -*-
"""Centralized scientific constants and observational benchmarks for TAP scripts."""

import math
from scipy import constants as const

# Fundamental constants from SciPy
# (e.g. speed of light, planck's reduced constant, gravitational constant, alpha, m_p/m_e)
PI = const.pi
C_LIGHT = const.c
HBAR = const.hbar
G_NEWTON = const.G
ALPHA_OBSERVED = const.alpha
PROTON_ELECTRON_MASS_RATIO = const.m_p / const.m_e
PLANCK_MASS_KG = const.physical_constants['Planck mass'][0]
PLANCK_MASS_GEV = (PLANCK_MASS_KG * C_LIGHT**2) / (const.eV * 1e9)

# Observational benchmarks used by the TAP proof scripts
HIGGS_MASS_GEV = 125.10
HIGGS_VEV_GEV = 246.22
PLANCK_NS_OBSERVED = 0.9649
PLANCK_NS_ERROR = 0.0042

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4

# ─── ΔB (Delta Breaths) — Breath Clock Constants ────────────────────────────
DELTA_B_N     = 5                                 # ΔB: Current Breath # (nearest Fibonacci = 5)
DELTA_B_GAMMA = 1.0 + DELTA_B_N * PHI ** -13    # Γ(ΔB) = 1 + ΔB·φ⁻¹³ ≈ 1.009597
DELTA_B_PSI   = 0.0265                           # ψ(ΔB): Breath phase (2.6% through Exhale)
DELTA_B_M     = 0                                # M(ΔB): Meta-Breath = 0 (first Meta-cycle)

# ─── Time Constants ──────────────────────────────────────────────────────────
PLANCK_TIME_SEC = math.sqrt((HBAR * G_NEWTON) / (C_LIGHT ** 5)) # ≈ 5.39124e-44 s

# TAPPASECOND (τ_Tappa): The fundamental bulk chronon scale
TAPPASECOND = PLANCK_TIME_SEC * (DELTA_B_GAMMA ** -PHI) * (PHI ** -DELTA_B_N) * ((1.0 - DELTA_B_PSI) ** (PHI ** -4))
