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
