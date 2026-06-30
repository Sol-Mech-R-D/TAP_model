# -*- coding: utf-8 -*-
"""
tap_option_arbitrage.py
=======================
TAP Option Arbitrage & Volatility Screener.
Compares standard Black-Scholes option pricing (representing HNS / historical models)
against the TAP Model's phase-locked volatility modulation during sub-breath crossings.
Identifies underpriced and overpriced option contracts for key operational energy assets:
  1. WTI Crude Oil (CL)
  2. Henry Hub Natural Gas (NG)
  3. Energy Select Sector SPDR Fund (XLE)
  4. ERCOT Power Futures Proxy
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import math
import json
from datetime import datetime, timedelta
from scipy.stats import norm

# ─── TAP Constants ──────────────────────────────────────────────────────────
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV4 = PHI ** -4  # ≈ 0.14590 (TAP Volatility Coupling Coefficient)
PHI_INV13 = PHI ** -13

# ─── Earth Orbit / Crossing Constants ────────────────────────────────────────
SOLSTICE_2026 = datetime(2026, 6, 21, 19, 46)
T_YEAR = 365.256
V_MEAN = 29.78
E = 0.0167

# ─── Target Assets ───────────────────────────────────────────────────────────
ASSETS = {
    "WTI_Crude": {"price": 78.50, "hist_vol": 0.28, "sector": "Logistics & Shipping"},
    "Henry_Hub": {"price": 2.45, "hist_vol": 0.45, "sector": "Power Generation"},
    "XLE_ETF": {"price": 91.20, "hist_vol": 0.22, "sector": "Energy Equities"},
    "ERCOT_Proxy": {"price": 45.00, "hist_vol": 0.65, "sector": "Grid Power Markets"}
}

def get_earth_velocity(days_since_perihelion):
    mean_anomaly = (2.0 * math.pi * days_since_perihelion) / T_YEAR
    return V_MEAN * (1.0 + E * math.cos(mean_anomaly))

def get_crossing_times():
    current_date = SOLSTICE_2026
    days_from_peri = 169.0
    crossings = []
    # Generate 15 crossings ahead to cover upcoming maturities
    for step in range(15):
        v = get_earth_velocity(days_from_peri)
        interval = 8.12 * (V_MEAN / v)
        crossings.append({
            "step": step,
            "date": current_date
        })
        current_date += timedelta(days=interval)
        days_from_peri += interval
    return crossings

def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """Standard Black-Scholes pricing (HNS baseline)."""
    if T <= 0:
        return max(0.0, S - K) if option_type == "call" else max(0.0, K - S)
    if sigma <= 0:
        return max(0.0, S - K) if option_type == "call" else max(0.0, K - S)
        
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
    return max(0.0, price)

def get_integrated_tap_vol(t_start, T_days, crossings, sigma_base):
    """
    Integrates the phase-dependent TAP volatility over the option's duration:
    σ_TAP(t) = σ_base * (1 + φ⁻⁴ * cos(2π * ψ_t))
    """
    total_vol = 0.0
    steps = 100
    dt = T_days / steps
    
    for step in range(steps):
        t_current = t_start + timedelta(days=step * dt)
        
        # Find closest sub-breath crossing node
        closest = min(crossings, key=lambda c: abs((t_current - c["date"]).total_seconds()))
        diff_days = (t_current - closest["date"]).total_seconds() / 86400.0
        phase = (diff_days / 8.12) * 2.0 * math.pi
        
        # Volatility is excited near the crossing boundaries (phase = 0)
        vol_t = sigma_base * (1.0 + PHI_INV4 * math.cos(phase))
        total_vol += vol_t
        
    return max(0.01, total_vol / steps)

def main():
    print("=" * 80)
    print("  TAP OPTION ARBITRAGE & VOLATILITY SCREENER")
    print("  Comparing Black-Scholes (HNS) vs. Phase-Locked TAP Pricing")
    print("=" * 80)
    
    crossings = get_crossing_times()
    t_today = datetime(2026, 6, 30) # Anchor at today's date
    risk_free_rate = 0.045 # 4.5% risk free rate
    
    screen_results = []
    
    print(f"  [RUN DATE] {t_today.strftime('%Y-%m-%d')} (Sub-Breath Node Transition)")
    print(f"  [VOLATILITY COUPLING] φ⁻⁴ = {PHI_INV4*100:.3f}%\n")
    
    # Generate Option chain (Strikes: -10%, -5%, ATM, +5%, +10%)
    # Maturities: 2 days, 3 days, 5 days, 7 days, 14 days, 30 days
    maturities = [2, 3, 5, 7, 14, 30]
    strike_offsets = [0.90, 0.95, 1.00, 1.05, 1.10]
    
    for asset_name, info in ASSETS.items():
        S = info["price"]
        sigma_base = info["hist_vol"]
        print(f"  [ASSET] {asset_name:12s} | Spot: ${S:.2f} | Base Vol: {sigma_base*100:.1f}%")
        
        for days in maturities:
            T = days / 365.25
            tap_vol = get_integrated_tap_vol(t_today, days, crossings, sigma_base)
            
            for offset in strike_offsets:
                K = round(S * offset, 2)
                
                # Price calls
                bs_call = black_scholes_price(S, K, T, risk_free_rate, sigma_base, "call")
                tap_call = black_scholes_price(S, K, T, risk_free_rate, tap_vol, "call")
                call_yield = ((tap_call - bs_call) / bs_call * 100.0) if bs_call > 0.01 else 0.0
                
                # Price puts
                bs_put = black_scholes_price(S, K, T, risk_free_rate, sigma_base, "put")
                tap_put = black_scholes_price(S, K, T, risk_free_rate, tap_vol, "put")
                put_yield = ((tap_put - bs_put) / bs_put * 100.0) if bs_put > 0.01 else 0.0
                
                # Classify recommendations
                # If TAP price is significantly higher, standard options are underpriced (BUY)
                # If TAP price is significantly lower, standard options are overpriced (WRITE/SELL)
                call_rec = "HOLD"
                if call_yield > 12.0:
                    call_rec = "BUY (Underpriced)"
                elif call_yield < -12.0:
                    call_rec = "SELL/WRITE (Overpriced)"
                    
                put_rec = "HOLD"
                if put_yield > 12.0:
                    put_rec = "BUY (Underpriced)"
                elif put_yield < -12.0:
                    put_rec = "SELL/WRITE (Overpriced)"
                
                screen_results.append({
                    "asset": asset_name,
                    "maturity_days": days,
                    "strike": K,
                    "type": "Call",
                    "bs_price": round(bs_call, 3),
                    "tap_price": round(tap_call, 3),
                    "integrated_vol_pct": round(tap_vol * 100, 2),
                    "arbitrage_yield_pct": round(call_yield, 2),
                    "recommendation": call_rec
                })
                
                screen_results.append({
                    "asset": asset_name,
                    "maturity_days": days,
                    "strike": K,
                    "type": "Put",
                    "bs_price": round(bs_put, 3),
                    "tap_price": round(tap_put, 3),
                    "integrated_vol_pct": round(tap_vol * 100, 2),
                    "arbitrage_yield_pct": round(put_yield, 2),
                    "recommendation": put_rec
                })

    # Print summary of key high-yield buy opportunities
    print(f"\n  {'Asset':12s} | {'Type':4s} | {'Maturity':8s} | {'Strike':6s} | {'BS ($)':6s} | {'TAP ($)':7s} | {'Yield (%)':9s} | {'Action'}")
    print(f"  {'-'*12}-+-{'-'*4}-+-{'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}-+-{'-'*9}-+-{'-'*25}")
    
    # Filter for interesting arbitrage actions (Yield > 8% or Yield < -8%)
    actions = [r for r in screen_results if abs(r["arbitrage_yield_pct"]) > 8.0]
    for act in actions[::3]: # Print selection to keep stdout clean
        print(f"  {act['asset']:12s} | {act['type']:4s} | {act['maturity_days']:3d} days | ${act['strike']:5.2f} | ${act['bs_price']:5.2f} | ${act['tap_price']:5.2f} | {act['arbitrage_yield_pct']:+8.2f}% | {act['recommendation']}")
        
    # Export results to assets
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tap_option_arbitrage_results.json")
    
    with open(out_path, "w") as f:
        json.dump(screen_results, f, indent=2)
        
    print(f"\n  [EXPORT] Option arbitrage results saved -> {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
