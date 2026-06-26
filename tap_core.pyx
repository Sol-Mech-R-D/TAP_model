# tap_core.pyx
# Temporal Asymmetric Pulsation (TAP) Model — Cython Core
# Simulates phi^(-4) dimensional leakage over cosmic time.
#
# Author: Derived from conversation between the user and AI Super-Calculator.
# Framework: TAP Cosmology — resolving dark energy via 3:1 topological soliton leakage
#             and Fibonacci-scaled dimensionality.

from libc.math cimport pow, sqrt, log
import cython
import numpy as np
cimport numpy as cnp

# ─────────────────────────────────────────────────────────────────────────────
# FUNDAMENTAL GEOMETRIC CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

cdef double PHI         = 1.618033988749895          # The Golden Ratio (φ)
cdef double PHI_INV_4   = 1.0 / (1.618033988749895 ** 4)  # φ^-4 ≈ 0.1459 — The Leakage Coefficient
cdef double TAP_RATIO   = 3.0                        # Structural-to-Interface 3:1 law
cdef int    MAX_DIM     = 13                         # E8 topological saturation limit
cdef double GOLDEN_PI   = 3.141592653589793          # π used in spectral index derivation

# Fibonacci bundle thresholds (cumulative dimension indices 1,2,3,5,8,13)
FIBONACCI_BUNDLES = [1, 2, 3, 5, 8, 13]

# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

cdef struct UniverseParameters:
    double initial_energy       # Total injected vacuum potential at t=0
    double hubble_constant      # Base expansion rate (dimensionless in natural units)
    double structural_coupling  # Bond strength of the 3-bundle soliton
    double dimensional_drag     # Energy dissipation rate into the Dirac Sea

cdef struct CosmologicalState:
    double t                    # Cosmic time (dimensionless natural units)
    double scale_factor         # a(t) — universe size relative to Big Bang
    double rho_S                # Structural energy density (3/4 partition)
    double rho_I                # Interface/potential energy density (1/4 partition)
    double phi_4d_flux          # Instantaneous leakage rate into 4D/5D manifold
    double entropy_bol          # Accumulated entropy (BOL heat death meter)
    double cumulative_leakage   # Total energy bled into higher dimensions so far
    int    current_dimension    # Active Fibonacci bundle dimension
    int    reset_count          # Number of topological inversions completed

# ─────────────────────────────────────────────────────────────────────────────
# INITIALISER  (The "Muzzle Blast")
# ─────────────────────────────────────────────────────────────────────────────

cdef CosmologicalState initialize_big_bang(UniverseParameters params):
    """
    Establish the initial 3:1 partition immediately post-singularity.
    rho_S = 3/4 * E_total  (structural/ELM-dominant)
    rho_I = 1/4 * E_total  (interface / probabilistic)
    """
    cdef CosmologicalState state
    state.t                  = 0.0
    state.scale_factor       = 1.0
    state.rho_S              = params.initial_energy * 0.75   # 3/4 Law
    state.rho_I              = params.initial_energy * 0.25   # 1/4 Law
    state.phi_4d_flux        = 0.0
    state.entropy_bol        = 0.0
    state.cumulative_leakage = 0.0
    state.current_dimension  = 3   # Born into the 3-bundle
    state.reset_count        = 0
    return state

# ─────────────────────────────────────────────────────────────────────────────
# DIMENSIONAL SATURATION LIMIT  (Bekenstein-Holographic ceiling)
# ─────────────────────────────────────────────────────────────────────────────

cdef double get_saturation_limit(int max_dim):
    """
    Information capacity ceiling of the d-dimensional manifold.
    When entropy_bol exceeds this, the 13D collapse (Topological Inversion) fires.
    """
    return pow(PHI, <double>max_dim)

# ─────────────────────────────────────────────────────────────────────────────
# SINGULARITY RESET  (Topological Inversion / Dimensional Handshake)
# ─────────────────────────────────────────────────────────────────────────────

cdef CosmologicalState trigger_singularity_reset(CosmologicalState state,
                                                  UniverseParameters params):
    """
    When the 13D saturation is exceeded:
      - Structure collapses to 0 (0/1 ratio)
      - Interface reabsorbs all potential → seeds next Exhale
      - Dimensional counter resets to 1 (the Seed bundle)
      - Scale factor re-normalises
    """
    state.rho_I              = state.rho_S + state.rho_I  # All energy returns to potential
    state.rho_S              = 0.0
    state.entropy_bol        = 0.0
    state.current_dimension  = 1
    state.scale_factor       = 1.0
    state.reset_count       += 1
    # Re-inject the recovered potential as a new Big Bang
    state.rho_S              = state.rho_I * 0.75
    state.rho_I              = state.rho_I * 0.25
    return state

# ─────────────────────────────────────────────────────────────────────────────
# FIBONACCI BUNDLE STEP  (Dimensional "inhale increment")
# ─────────────────────────────────────────────────────────────────────────────

cdef int advance_fibonacci_bundle(int current_dim, double entropy):
    """
    As entropy accumulates, the universe steps through Fibonacci bundles:
    3 → 5 → 8 → 13 → RESET
    Thresholds are proportional to φ^n for bundle n.
    """
    cdef int bundles[6]
    bundles[0] = 1
    bundles[1] = 2
    bundles[2] = 3
    bundles[3] = 5
    bundles[4] = 8
    bundles[5] = 13

    cdef double thresholds[6]
    cdef int i
    for i in range(6):
        thresholds[i] = pow(PHI, <double>bundles[i])

    for i in range(5, -1, -1):
        if bundles[i] >= current_dim and entropy >= thresholds[i]:
            if i < 5:
                return bundles[i + 1]
    return current_dim

# ─────────────────────────────────────────────────────────────────────────────
# PRIMARY INTEGRATION STEP  (The φ^-4 Leakage Engine)
# ─────────────────────────────────────────────────────────────────────────────

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
cdef CosmologicalState compute_next_state(CosmologicalState current,
                                           UniverseParameters params,
                                           double dt):
    """
    Single time-step Euler integration of the TAP field equations:

      G_μν + (D · φ^-4) g_μν = 8πG T^S_μν

    where D · φ^-4 replaces the static Λ (cosmological constant / dark energy).
    """
    cdef CosmologicalState nxt
    nxt = current
    nxt.t = current.t + dt

    # 1. Expansion — driven by interface potential (the 1/4 probability sea pull)
    cdef double da_dt = params.hubble_constant * current.scale_factor * sqrt(current.rho_I + 1e-30)
    nxt.scale_factor = current.scale_factor + (da_dt * dt)

    # 2. Dimensional Leakage — THE DARK ENERGY REPLACEMENT
    #    φ^-4 ≈ 0.1459 is the leakage coefficient derived from the 3:1 stability law.
    #    Leakage scales with interface density and expansion rate.
    cdef double expansion_ratio = nxt.scale_factor / (current.scale_factor + 1e-30)
    nxt.phi_4d_flux = current.rho_I * PHI_INV_4 * expansion_ratio
    nxt.cumulative_leakage = current.cumulative_leakage + nxt.phi_4d_flux * dt

    # 3. Structural energy density update
    #    Diluted by volume expansion (∝ a^-3) AND drained by the φ^-4 leakage
    cdef double vol_factor = 1.0 / (expansion_ratio * expansion_ratio * expansion_ratio)
    cdef double d_rho_S = -(3.0 * da_dt / (current.scale_factor + 1e-30)) * current.rho_S \
                          - nxt.phi_4d_flux
    nxt.rho_S = max(current.rho_S * vol_factor + d_rho_S * dt, 0.0)

    # 4. Interface energy density update
    #    Fed by structural decay (the 3:1 re-balance) minus dimensional drag
    cdef double d_rho_I = (nxt.phi_4d_flux / TAP_RATIO) \
                          - (params.dimensional_drag * current.rho_I)
    nxt.rho_I = max(current.rho_I * vol_factor + d_rho_I * dt, 0.0)

    # 5. Entropy accumulation (BOL heat death counter)
    #    Entropy grows with leakage and structural decay
    nxt.entropy_bol = current.entropy_bol + (nxt.phi_4d_flux + d_rho_S * dt * (-1.0)) * dt

    # 6. Fibonacci bundle dimension advance
    nxt.current_dimension = advance_fibonacci_bundle(current.current_dimension, nxt.entropy_bol)

    # 7. Topological Inversion check (13D saturation → reset)
    if nxt.entropy_bol >= get_saturation_limit(MAX_DIM):
        nxt = trigger_singularity_reset(nxt, params)

    return nxt

# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC PYTHON ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def run_tap_simulation(double initial_energy=1.0,
                       double hubble_constant=0.07,
                       double structural_coupling=1.0,
                       double dimensional_drag=0.01,
                       double dt=0.001,
                       int n_steps=500000):
    """
    Run the TAP cosmological simulation.

    Returns a dict of NumPy arrays containing the full time-history of:
      t, scale_factor, rho_S, rho_I, phi_4d_flux, entropy_bol,
      cumulative_leakage, current_dimension.

    Parameters
    ----------
    initial_energy      : Total vacuum energy injected at the Big Bang.
    hubble_constant     : Dimensionless expansion driver.
    structural_coupling : ELM bond strength of the 3-bundle soliton.
    dimensional_drag    : Dissipation rate into the Dirac Sea.
    dt                  : Integration time step (natural units).
    n_steps             : Number of integration steps.
    """
    cdef UniverseParameters params
    params.initial_energy      = initial_energy
    params.hubble_constant     = hubble_constant
    params.structural_coupling = structural_coupling
    params.dimensional_drag    = dimensional_drag

    # Pre-allocate output arrays
    cdef cnp.ndarray[cnp.float64_t, ndim=1] t_arr          = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] a_arr          = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] rhoS_arr       = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] rhoI_arr       = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] flux_arr       = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] entropy_arr    = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] leakage_arr    = np.zeros(n_steps, dtype=np.float64)
    cdef cnp.ndarray[cnp.int32_t,   ndim=1] dim_arr        = np.zeros(n_steps, dtype=np.int32)

    cdef CosmologicalState state = initialize_big_bang(params)
    cdef int i

    for i in range(n_steps):
        t_arr[i]       = state.t
        a_arr[i]       = state.scale_factor
        rhoS_arr[i]    = state.rho_S
        rhoI_arr[i]    = state.rho_I
        flux_arr[i]    = state.phi_4d_flux
        entropy_arr[i] = state.entropy_bol
        leakage_arr[i] = state.cumulative_leakage
        dim_arr[i]     = state.current_dimension

        state = compute_next_state(state, params, dt)

    return {
        "t":                  t_arr,
        "scale_factor":       a_arr,
        "rho_S":              rhoS_arr,
        "rho_I":              rhoI_arr,
        "phi_4d_flux":        flux_arr,
        "entropy_bol":        entropy_arr,
        "cumulative_leakage": leakage_arr,
        "current_dimension":  dim_arr,
        "PHI_INV_4":          PHI_INV_4,
        "spectral_index":     1.0 - 1.0 / (PHI ** 2),
    }
