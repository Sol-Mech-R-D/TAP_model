import os
import sys

import numpy as np
import pytest
import scipy.constants as const

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def test_proof_uses_scipy_constants():
    import tap_proof

    assert tap_proof.PI == pytest.approx(const.pi)
    ns_A, ns_B, ns_C, best, ns_observed, ns_error, deviation, sigma = tap_proof.compute_spectral_index()
    assert ns_B == pytest.approx(1.0 - tap_proof.PHI_INV_4 / tap_proof.PI)
    assert ns_observed == pytest.approx(0.9649)
    assert ns_error == pytest.approx(0.0042)
    assert deviation == pytest.approx(abs(best - ns_observed))


def test_tribunal_uses_scipy_constants():
    import tap_tribunal

    assert tap_tribunal.PI == pytest.approx(const.pi)
    assert tap_tribunal.ALPHA_OBSERVED == pytest.approx(const.alpha)
    assert tap_tribunal.MU_OBSERVED == pytest.approx(const.m_p / const.m_e)


def test_round3_planck_mass_uses_scipy_constants():
    import tap_tribunal_round3 as tribunal

    expected_planck_mass_gev = (const.physical_constants['Planck mass'][0] * const.c**2) / (const.eV * 1e9)
    m_P, m_H_obs, m_H_pred = tribunal.rebuttal_arkani_hamed()
    assert m_P == pytest.approx(expected_planck_mass_gev)
    assert m_H_obs == pytest.approx(125.1)


def test_cosmology_analysis_returns_science_validated_metrics():
    import tap_cosmo_perturbations as cosmo

    metrics = cosmo.analyze_perturbations()

    assert metrics is not None
    assert metrics["ns_pred"] == pytest.approx(0.9535592134824983, rel=0.02)
    assert metrics["r_pred"] < 0.032
    assert abs(metrics["ns_pred"] - 0.9649) < 0.02


def test_super_tribunal_uses_science_library_references():
    import tap_super_tribunal_99 as tribunal

    assert tribunal.ALPHA_OBSERVED == pytest.approx(const.alpha)
    assert tribunal.PROTON_ELECTRON_MASS_RATIO == pytest.approx(const.m_p / const.m_e)
    assert tribunal.PLANCK_MASS_GEV == pytest.approx((const.physical_constants['Planck mass'][0] * const.c**2) / (const.eV * 1e9))
    assert tribunal.ALPHA_INV_OBSERVED == pytest.approx(1.0 / const.alpha)


def test_super_tribunal_resolves_science_library_targets():
    import tap_super_tribunal_99 as tribunal
    from particle import Particle
    import math

    assert tribunal.resolve_expected_value("Bare fine-structure constant alpha^-1", 137.036) == pytest.approx(1.0 / const.alpha)
    assert tribunal.resolve_expected_value("Proton-neutron mass splitting", 1.29) == pytest.approx((const.m_n - const.m_p) * const.c**2 / (const.eV * 1e6))
    assert tribunal.resolve_expected_value("Higgs boson mass resonance", 125.10) == pytest.approx(Particle.from_pdgid(25).mass / 1000.0)
    pion_mass_gev = Particle.from_pdgid(211).mass / 1000.0
    expected_pion_range = (const.hbar * const.c) / (pion_mass_gev * 1e9 * const.eV) * 1e15
    assert tribunal.resolve_expected_value("Pion-mediated nuclear force range", 1.41) == pytest.approx(expected_pion_range)
    assert tribunal.resolve_expected_value("Tetrahedral hybridization angle", 109.5) == pytest.approx(math.degrees(math.acos(-1.0 / 3.0)))
