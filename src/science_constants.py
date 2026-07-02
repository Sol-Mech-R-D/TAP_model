# -*- coding: utf-8 -*-
"""Centralized scientific constants and observational benchmarks for TAP scripts."""

import math
from scipy import constants as const

# Fundamental constants from SciPy
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

# Derived geometric constants used across the codebase
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4

# Centralized Breath Clock constants derived from the 99 Hypotheses Tribunal
N_BREATH = 7         # Current Breath number (chi²-minimised)
GAMMA_BREATH = 1.01343565  # Universal Breath correction factor
PSI_BREATH = 0.0265           # Breath phase (position in current Exhale)

# Alias names for compatibility with tap_tappasecond.py and tap_neural_resonance.py
DELTA_B_N = N_BREATH
DELTA_B_GAMMA = GAMMA_BREATH
DELTA_B_PSI = PSI_BREATH
DELTA_B_M = 0

# ─── Time Constants ──────────────────────────────────────────────────────────
PLANCK_TIME_SEC = math.sqrt((HBAR * G_NEWTON) / (C_LIGHT ** 5)) # ≈ 5.39124e-44 s

# TAPPASECOND (τ_Tappa): The fundamental bulk chronon scale
TAPPASECOND = PLANCK_TIME_SEC * (DELTA_B_GAMMA ** -PHI) * (PHI ** -DELTA_B_N) * ((1.0 - DELTA_B_PSI) ** (PHI ** -4))



