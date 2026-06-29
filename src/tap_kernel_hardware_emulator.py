# -*- coding: utf-8 -*-
"""
tap_kernel_hardware_emulator.py
===============================
Emulates the three pillars of TAP-based kernel/hardware abstractions:
1. Algebraic Hierarchical Weyl Scheduler.
2. Topological Brane Boundary Memory Isolation.
3. Phinary ALU Unified Arithmetic.
All simulations are live-wired to the VEV cascade.
Now fully implements the Logicfalls ALU containing 20 distinct physical
and logical fall modes mapping directly to the physical PASSA+ architecture.
"""

import math
import numpy as np
from science_constants import PHI, PI, HIGGS_VEV_GEV
from tap_dirac_modes import solve_dirac_spectrum

# -------------------------------------------------------------------------
# 1. HIERARCHICAL WEYL PROCESS SCHEDULER
# -------------------------------------------------------------------------
class WeylTask:
    def __init__(self, pid, name, group_class):
        self.pid = pid
        self.name = name
        self.group_class = group_class  # 'RT', 'Interactive', 'Batch'

class WeylOS_Scheduler:
    def __init__(self, v_ratio):
        self.v_ratio = v_ratio
        self.state = 0.0
        # Allocate sub-intervals using golden-ratio partitions
        self.intervals = {
            'RT': (0.0, PHI ** -1),                             # [0.0, 0.618)
            'Interactive': (PHI ** -1, PHI ** -1 + PHI ** -2),   # [0.618, 0.900)
            'Batch': (PHI ** -1 + PHI ** -2, 1.0)               # [0.900, 1.0)
        }

    def schedule_tick(self, task_list, ticks=100):
        scheduled_pids = []
        for n in range(ticks):
            # Advance lowest-discrepancy Weyl sequence
            self.state = (self.state + PHI) % 1.0
            
            # Determine which process class interval the state lands in
            assigned_class = 'Batch'
            for grp, (low, high) in self.intervals.items():
                if low <= self.state < high:
                    assigned_class = grp
                    break
            
            # Filter tasks in that class
            eligible = [t for t in task_list if t.group_class == assigned_class]
            if not eligible:
                # Fallback to any task if the group is empty
                eligible = task_list
                
            # O(1) index mapping using state
            idx = int(len(eligible) * ((self.state * 13) % 1.0)) % len(eligible)
            scheduled_pids.append(eligible[idx].pid)
            
        return scheduled_pids

# -------------------------------------------------------------------------
# 2. BRANE BOUNDARY POINTER ISOLATION
# -------------------------------------------------------------------------
class BraneMemoryBus:
    def __init__(self, v_ratio):
        # Dirichlet potential barrier width
        self.barrier_width = 1.0 + (PHI ** -4) * v_ratio
        
    def access_pointer(self, address_offset):
        # Dirichlet potential at boundary
        # If boundary violated, potential climbs to infinity, blocking leakage
        if abs(address_offset) > self.barrier_width:
            potential = float('inf')
            success = False
        else:
            potential = math.sin(PI * address_offset / (2.0 * self.barrier_width))
            success = True
        return success, potential

# -------------------------------------------------------------------------
# 3. BASE CLASS FOR LOGICFALLS
# -------------------------------------------------------------------------
class LogicFall:
    """Base class for all Logicfalls in the TAP-PASSA+ ALU."""
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def evaluate(self, state):
        """
        Evaluates if the physical/logical fall triggers.
        Returns (triggered, probability, status_message)
        """
        raise NotImplementedError

# -------------------------------------------------------------------------
# THE 20 SPECIFIC LOGICFALL SUBCLASSES
# -------------------------------------------------------------------------
class RegFall(LogicFall):
    def __init__(self):
        super().__init__("RegFall", "Register State Thermal Decay")
    def evaluate(self, state):
        t_hold = state.get("t_hold", 0.0)
        v_ratio = state.get("v_ratio", 1.0)
        tau = 0.5 * v_ratio  # register cooling rate scale
        prob = 1.0 - math.exp(-t_hold / tau) if tau > 0 else 1.0
        triggered = prob > state.get("rand_val", 0.5)
        msg = f"Thermal relaxation of Peltier-TEG registers after {t_hold:.3f}s (P_fall={prob:.3f})"
        return triggered, prob, msg

class MemFall(LogicFall):
    def __init__(self):
        super().__init__("MemFall", "Capacitor Charge Leakage")
    def evaluate(self, state):
        t = state.get("t_active", 0.0)
        c_sig = 0.1e-6  # 0.1 uF signal capacitor
        r_leak = state.get("r_leak", 10.0e6)  # 10 MOhm leakage path
        tau = r_leak * c_sig
        prob = 1.0 - math.exp(-t / tau) if tau > 0 else 1.0
        triggered = prob > state.get("rand_val", 0.5)
        msg = f"Signal capacitor Cs charge leak to reservoir Cr (P_fall={prob:.3f})"
        return triggered, prob, msg

class ImpFall(LogicFall):
    def __init__(self):
        super().__init__("ImpFall", "Impedance Mismatch")
    def evaluate(self, state):
        v_ratio = state.get("v_ratio", 1.0)
        z_std = 376.73
        phi_inv4 = PHI ** -4
        z_tap_expected = z_std * (1.0 + phi_inv4 * v_ratio)
        z_actual = state.get("z_actual", z_tap_expected)
        deviation = abs(z_actual - z_tap_expected)
        prob = min(1.0, deviation / 50.0)
        triggered = deviation > 10.0
        msg = f"VEV-coupled impedance mismatch: |Z_actual - Z_TAP| = {deviation:.2f} Ohm (P_fall={prob:.3f})"
        return triggered, prob, msg

class ResFall(LogicFall):
    def __init__(self):
        super().__init__("ResFall", "Resonance Lock Loss")
    def evaluate(self, state):
        f_meas = state.get("f_measured", 40000.0)
        f_pred = state.get("f_predicted", 40000.0)
        deviation = abs(f_meas - f_pred)
        prob = min(1.0, deviation / 100.0)
        triggered = deviation > 15.0
        msg = f"Loss of zero-crossing resonant frequency lock: df = {deviation:.1f} Hz"
        return triggered, prob, msg

class AcFall(LogicFall):
    def __init__(self):
        super().__init__("AcFall", "Acoustic Attenuation")
    def evaluate(self, state):
        temp = state.get("temp", 20.0)
        dist = state.get("waveguide_length", 0.05)  # 50 mm
        alpha_att = 0.5 * (1.0 + 0.01 * temp)
        amp_loss = 1.0 - math.exp(-alpha_att * dist)
        prob = amp_loss
        triggered = amp_loss > 0.15
        msg = f"Acoustic wave attenuation along alumina waveguide (Loss={amp_loss:.1%})"
        return triggered, prob, msg

class ThermFall(LogicFall):
    def __init__(self):
        super().__init__("ThermFall", "Thermal Gradient Collapse")
    def evaluate(self, state):
        delta_t = state.get("delta_t", 14.0)  # nominal 14 C
        prob = max(0.0, 1.0 - (delta_t / 14.0))
        triggered = delta_t < 5.0
        msg = f"Thermal gradient collapse between grip and cold core: dT = {delta_t:.1f} C"
        return triggered, prob, msg

class PiezFall(LogicFall):
    def __init__(self):
        super().__init__("PiezFall", "Piezoelectric Depolarization")
    def evaluate(self, state):
        temp = state.get("temp", 20.0)
        v_drive = state.get("v_drive", 3.3)
        prob_t = min(1.0, max(0.0, (temp - 120.0) / 230.0))
        prob_v = min(1.0, max(0.0, (v_drive - 6.0) / 4.0))
        prob = max(prob_t, prob_v)
        triggered = temp > 150.0 or v_drive > 8.0
        msg = f"Piezoelectric PZT-5H depolarization (T={temp:.1f}C, V={v_drive:.1f}V)"
        return triggered, prob, msg

class OuroFall(LogicFall):
    def __init__(self):
        super().__init__("OuroFall", "Ouroboros Desynchronization")
    def evaluate(self, state):
        phase_drift = state.get("phase_drift", 0.0)
        prob = min(1.0, phase_drift / (math.pi / 2))
        triggered = phase_drift > (math.pi / 8)
        msg = f"Ouroboros loop desynchronization: drift = {phase_drift:.3f} rad"
        return triggered, prob, msg

class WeylFall(LogicFall):
    def __init__(self):
        super().__init__("WeylFall", "Weyl Scheduler Jitter")
    def evaluate(self, state):
        discrepancy = state.get("scheduler_discrepancy", 0.0)
        limit = PHI ** -8
        prob = min(1.0, discrepancy / (2.0 * limit))
        triggered = discrepancy > limit
        msg = f"Weyl task scheduling jitter: discrepancy = {discrepancy:.5f} (limit = {limit:.5f})"
        return triggered, prob, msg

class ConfFall(LogicFall):
    def __init__(self):
        super().__init__("ConfFall", "Holographic Cutoff Leakage")
    def evaluate(self, state):
        v_ratio = state.get("v_ratio", 1.0)
        y_sat = 2.0 * math.pi * 13.0 * (1.0 - (PHI ** -9) / math.pi)
        lambda_c = 15.0
        prob = math.exp(-y_sat / lambda_c) * v_ratio
        triggered = prob > state.get("rand_val", 0.5)
        msg = f"Holographic cutoff leakage across 13D boundary (P_leak={prob:.4f})"
        return triggered, prob, msg

class StutFall(LogicFall):
    def __init__(self):
        super().__init__("StutFall", "StutterHammer Glitch")
    def evaluate(self, state):
        jitter = state.get("pulse_jitter_us", 0.0)
        prob = min(1.0, jitter / 10.0)
        triggered = jitter > 2.0
        msg = f"StutterHammer pulse train timing glitch: jitter = {jitter:.2f} us"
        return triggered, prob, msg

class SpecFall(LogicFall):
    def __init__(self):
        super().__init__("SpecFall", "Octave Drift")
    def evaluate(self, state):
        drift = state.get("octave_drift_hz", 0.0)
        prob = min(1.0, drift / 500.0)
        triggered = drift > 150.0
        msg = f"Py-Sonic octave frequency band drift: drift = {drift:.1f} Hz"
        return triggered, prob, msg

class CasimirFall(LogicFall):
    def __init__(self):
        super().__init__("CasimirFall", "Casimir Vacuum Leak")
    def evaluate(self, state):
        d_gap = state.get("casimir_gap_nm", 100.0)
        force = (1.0e-24) / (d_gap ** 4) if d_gap > 0 else float('inf')
        prob = min(1.0, force * 1e16)
        triggered = d_gap < 20.0
        msg = f"Casimir vacuum leakage fluctuations at gap = {d_gap:.1f} nm"
        return triggered, prob, msg

class PhinaryFall(LogicFall):
    def __init__(self):
        super().__init__("PhinaryFall", "Phinary Reduction Error")
    def evaluate(self, state):
        f_clock = state.get("f_clock_mhz", 1.0)
        prob = min(1.0, max(0.0, (f_clock - 5.0) / 15.0))
        triggered = f_clock > 8.0
        msg = f"Phinary local carry reduction delay at clock = {f_clock:.1f} MHz"
        return triggered, prob, msg

class HBFall(LogicFall):
    def __init__(self):
        super().__init__("HBFall", "H-Bridge Thermal Overload")
    def evaluate(self, state):
        temp_h = state.get("hbridge_temp", 30.0)
        prob = min(1.0, max(0.0, (temp_h - 70.0) / 80.0))
        triggered = temp_h > 120.0
        msg = f"H-Bridge lane thermal overload: Temp = {temp_h:.1f} C"
        return triggered, prob, msg

class TldFall(LogicFall):
    def __init__(self):
        super().__init__("TldFall", "Tilde Command Malfunction")
    def evaluate(self, state):
        snr = state.get("snr_db", 30.0)
        prob = 1.0 - min(1.0, snr / 15.0) if snr >= 0 else 1.0
        triggered = snr < 10.0
        msg = f"Tilde-Lock command packet noise corruption: SNR = {snr:.1f} dB"
        return triggered, prob, msg

class LoomFall(LogicFall):
    def __init__(self):
        super().__init__("LoomFall", "Loom Charge Decay")
    def evaluate(self, state):
        t = state.get("t_active", 0.0)
        c_loom = 100e-6  # 100 uF Loom capacitor
        r_loom = state.get("r_loom_leak", 1.0e6)
        tau = r_loom * c_loom
        prob = 1.0 - math.exp(-t / tau) if tau > 0 else 1.0
        triggered = prob > state.get("rand_val", 0.5)
        msg = f"Loom parallel distribution register charge decay (P_fall={prob:.3f})"
        return triggered, prob, msg

class DripFall(LogicFall):
    def __init__(self):
        super().__init__("DripFall", "Acoustic Drip Rectification Loss")
    def evaluate(self, state):
        v_piezo = state.get("v_piezo_burst", 1.0)
        v_diode = 0.24 * 2 # two Schottky diodes
        prob = 1.0 if v_piezo < v_diode else max(0.0, 1.0 - (v_piezo / 1.5))
        triggered = v_piezo < v_diode
        msg = f"Acoustic Drip rectification loss: V_piezo = {v_piezo:.2f}V < V_diode = {v_diode:.2f}V"
        return triggered, prob, msg

class SolFall(LogicFall):
    def __init__(self):
        super().__init__("SolFall", "Pilot Wave Dissipation")
    def evaluate(self, state):
        dist = state.get("leyline_distance", 50.0)
        v_ratio = state.get("v_ratio", 1.0)
        l_coherence = 100.0 * (1.0 - (PHI ** -4) * v_ratio)
        prob = min(1.0, dist / l_coherence) if l_coherence > 0 else 1.0
        triggered = dist > l_coherence
        msg = f"Phase-conjugate pilot wave dissipation at distance = {dist:.1f} m"
        return triggered, prob, msg

class IsoFall(LogicFall):
    def __init__(self):
        super().__init__("IsoFall", "Isospin Perturbation")
    def evaluate(self, state):
        v_ratio = state.get("v_ratio", 1.0)
        epsilon = (PHI ** -8) * v_ratio
        prob = min(1.0, epsilon / 0.05)
        triggered = epsilon > 0.025
        msg = f"Isospin shell boundary perturbation: epsilon = {epsilon:.5f}"
        return triggered, prob, msg

# -------------------------------------------------------------------------
# 4. PHINARY ALU & LOGICFALLS ALU EXTENSION
# -------------------------------------------------------------------------
class PhinaryALU:
    def __init__(self):
        pass

    def to_phinary(self, val, max_digits=8):
        """Converts positive float/int to base-phi representation."""
        if val == 0:
            return "0"
            
        digits = {}
        # Greedy search over powers of phi
        remaining = val
        for p in range(max_digits, -max_digits - 1, -1):
            power_val = PHI ** p
            if remaining >= power_val - 1e-9:
                digits[p] = 1
                remaining -= power_val
            else:
                digits[p] = 0
                
        # Format string
        high_pow = max(digits.keys())
        low_pow = min(digits.keys())
        
        integral = []
        fractional = []
        for p in range(high_pow, -1, -1):
            integral.append(str(digits.get(p, 0)))
        for p in range(-1, low_pow - 1, -1):
            fractional.append(str(digits.get(p, 0)))
            
        res = "".join(integral)
        if fractional:
            res += "." + "".join(fractional)
        return res

    def phinary_add(self, a_val, b_val):
        # In hardware, this is carry-less XOR + local reduction rules
        # Emulated via standard phinary transformation of the sum
        return self.to_phinary(a_val + b_val)


class LogicfallsALU(PhinaryALU):
    """
    Enhanced Phinary ALU that simulates the effects of 20 distinct
    Logicfalls under varying environmental stress factors.
    """
    def __init__(self):
        super().__init__()
        # Instantiate all 20 falls
        self.falls = [
            RegFall(), MemFall(), ImpFall(), ResFall(), AcFall(),
            ThermFall(), PiezFall(), OuroFall(), WeylFall(), ConfFall(),
            StutFall(), SpecFall(), CasimirFall(), PhinaryFall(), HBFall(),
            TldFall(), LoomFall(), DripFall(), SolFall(), IsoFall()
        ]
        self.active_falls = {}

    def evaluate_falls(self, state_dict):
        """
        Evaluates all 20 logicfalls based on the operational environment state.
        Saves active falls and returns the details.
        """
        self.active_falls = {}
        report = {}
        for fall in self.falls:
            triggered, prob, msg = fall.evaluate(state_dict)
            if triggered:
                self.active_falls[fall.name] = {
                    "probability": prob,
                    "message": msg
                }
            report[fall.name] = {
                "triggered": triggered,
                "probability": prob,
                "message": msg
            }
        return report

    def to_phinary(self, val, max_digits=8):
        # MemFall degrades max_digits resolution
        if "MemFall" in self.active_falls:
            max_digits = max(2, max_digits - 3)
        
        res = super().to_phinary(val, max_digits)
        
        # PhinaryFall fails to reduce adjacent '11's or '2's
        if "PhinaryFall" in self.active_falls:
            if "." in res:
                int_part, frac_part = res.split(".")
                if len(int_part) >= 3:
                    int_part = int_part[:-3] + "011"
                else:
                    int_part = int_part + "2"
                res = int_part + "." + frac_part
            else:
                res = res + "2"
                
        # ConfFall flips bits due to boundary cutoff leak
        if "ConfFall" in self.active_falls:
            chars = list(res)
            for idx in range(len(chars)):
                if chars[idx] in ('0', '1'):
                    chars[idx] = '1' if chars[idx] == '0' else '0'
            res = "".join(chars)
            
        return res

    def phinary_add(self, a_val, b_val):
        # TldFall or HBFall breaks the parser/circuit completely
        if "TldFall" in self.active_falls:
            return "ERROR: COMMAND_CORRUPTED"
        if "HBFall" in self.active_falls:
            return "ERROR: LANE_POWER_OVERLOAD"
            
        sum_val = a_val + b_val
        
        # ImpFall reduces output due to reflection losses
        if "ImpFall" in self.active_falls:
            sum_val *= 0.95
            
        return self.to_phinary(sum_val)

# -------------------------------------------------------------------------
# GLOBAL ENTRYPOINT
# -------------------------------------------------------------------------
def run_emulator():
    # Solve cascade VEV ratio
    _, _, _, _, m_H, _ = solve_dirac_spectrum(n_grid=1000)
    v_ratio = (2.0 * m_H) / HIGGS_VEV_GEV
    
    # 1. Scheduler Simulation
    tasks = [
        WeylTask(1, "kernel_main", "RT"),
        WeylTask(2, "audio_driver", "RT"),
        WeylTask(3, "ui_shell", "Interactive"),
        WeylTask(4, "background_download", "Batch")
    ]
    scheduler = WeylOS_Scheduler(v_ratio)
    schedule = scheduler.schedule_tick(tasks, ticks=1000)
    
    # Calculate group resource distributions (%)
    rt_count = sum(1 for pid in schedule if pid in [1, 2])
    inter_count = sum(1 for pid in schedule if pid == 3)
    batch_count = sum(1 for pid in schedule if pid == 4)
    
    # 2. Brane Pointer Access
    bus = BraneMemoryBus(v_ratio)
    ok_access, pot_ok = bus.access_pointer(0.5)
    bad_access, pot_bad = bus.access_pointer(2.5)
    
    # 3. Phinary & Logicfalls ALU Simulation
    # Define operational environments
    nominal_env = {
        "v_ratio": v_ratio,
        "t_hold": 0.001,
        "t_active": 0.001,
        "z_actual": 376.73 * (1.0 + (PHI ** -4) * v_ratio),
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
        "rand_val": 0.99  # prevent random triggers in nominal run
    }

    stressed_env = {
        "v_ratio": v_ratio,
        "t_hold": 2.5,                # Trigger RegFall
        "t_active": 1.5,              # Trigger MemFall
        "z_actual": 450.0,            # Trigger ImpFall
        "f_measured": 40085.0,        # Trigger ResFall
        "f_predicted": 40000.0,
        "temp": 160.0,                # Trigger AcFall, PiezFall
        "waveguide_length": 0.05,
        "delta_t": 3.0,               # Trigger ThermFall
        "v_drive": 9.0,               # Trigger PiezFall
        "phase_drift": 1.2,           # Trigger OuroFall
        "scheduler_discrepancy": 0.1, # Trigger WeylFall
        "pulse_jitter_us": 4.5,       # Trigger StutFall
        "octave_drift_hz": 280.0,     # Trigger SpecFall
        "casimir_gap_nm": 12.0,       # Trigger CasimirFall
        "f_clock_mhz": 12.0,          # Trigger PhinaryFall
        "hbridge_temp": 135.0,        # Trigger HBFall
        "snr_db": 6.5,                # Trigger TldFall
        "v_piezo_burst": 0.35,        # Trigger DripFall
        "leyline_distance": 95.0,      # Trigger SolFall
        "rand_val": 0.01  # encourage random triggers in stressed run
    }

    alu = LogicfallsALU()
    
    # Run nominal arithmetic
    nominal_report = alu.evaluate_falls(nominal_env)
    nominal_phi_2 = alu.to_phinary(2.0)
    nominal_phi_3 = alu.to_phinary(3.0)
    nominal_phi_sum = alu.phinary_add(2.0, 3.0)

    # Run stressed arithmetic
    stressed_report = alu.evaluate_falls(stressed_env)
    stressed_phi_2 = alu.to_phinary(2.0)
    stressed_phi_3 = alu.to_phinary(3.0)
    stressed_phi_sum = alu.phinary_add(2.0, 3.0)
    
    active_nominal_falls = [name for name, details in nominal_report.items() if details["triggered"]]
    active_stressed_falls = [name for name, details in stressed_report.items() if details["triggered"]]
    
    return {
        "v_ratio": v_ratio,
        "scheduler_rt_pct": (rt_count / 1000.0) * 100.0,
        "scheduler_interactive_pct": (inter_count / 1000.0) * 100.0,
        "scheduler_batch_pct": (batch_count / 1000.0) * 100.0,
        "valid_ptr_potential": pot_ok,
        "invalid_ptr_blocked": not bad_access,
        # Nominal ALU Results
        "nominal_active_falls": active_nominal_falls,
        "nominal_phinary_2": nominal_phi_2,
        "nominal_phinary_3": nominal_phi_3,
        "nominal_phinary_sum_5": nominal_phi_sum,
        # Stressed ALU Results
        "stressed_active_falls": active_stressed_falls,
        "stressed_phinary_sum_5": stressed_phi_sum
    }

if __name__ == "__main__":
    res = run_emulator()
    print("TAP Kernel Hardware Emulator Results:")
    for k, v in res.items():
        print(f"  {k:<30}: {v}")
