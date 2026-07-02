# -*- coding: utf-8 -*-
"""
tap_finance_rescreen.py
========================
TAP v5.3 Finance re-screen with lower threshold.

The original tap_option_arbitrage.py uses a 12% threshold
for BUY/SELL signals, which only triggers on 34/960 contracts.
This script re-screens the same data with a 5% threshold
to surface more actionable signals.

Strategy: if a TAP option price differs from Black-Scholes
by > 5%, the framework flags it as either:
  - BUY (TAP says it's underpriced vs BS)
  - SELL (TAP says it's overpriced vs BS)

The lower threshold surfaces more signals, but they have
smaller expected yields.
"""

import os
import json
import statistics
from collections import Counter

ASSETS_PATH = '/data/data/com.termux/files/home/TAP_model/assets/tap_option_arbitrage_results.json'
OUTPUT_PATH = '/data/data/com.termux/files/home/TAP_model/assets/tap_finance_rescreen_results.json'

THRESHOLDS = [3, 5, 7, 10, 12, 15, 20, 30, 50]


def load_results() -> list:
    with open(ASSETS_PATH) as f:
        return json.load(f)


def rescreen(contracts: list, threshold: float) -> dict:
    """Re-screen with a given threshold."""
    buy = [r for r in contracts if r['arbitrage_yield_pct'] > threshold]
    sell = [r for r in contracts if r['arbitrage_yield_pct'] < -threshold]

    # Stats
    buy_yields = [r['arbitrage_yield_pct'] for r in buy]
    sell_yields = [r['arbitrage_yield_pct'] for r in sell]

    # Per-asset counts
    asset_counts = Counter(r['asset'] for r in buy + sell)
    asset_buy = Counter(r['asset'] for r in buy)
    asset_sell = Counter(r['asset'] for r in sell)

    # Per-maturity counts
    mat_counts = Counter(r['maturity_days'] for r in buy + sell)

    return {
        'threshold_pct': threshold,
        'n_buy': len(buy),
        'n_sell': len(sell),
        'n_total': len(buy) + len(sell),
        'buy_yield_mean': round(statistics.mean(buy_yields), 2) if buy_yields else 0,
        'buy_yield_max': round(max(buy_yields), 2) if buy_yields else 0,
        'sell_yield_mean': round(statistics.mean(sell_yields), 2) if sell_yields else 0,
        'sell_yield_min': round(min(sell_yields), 2) if sell_yields else 0,
        'top_assets': dict(asset_counts.most_common(10)),
        'top_buy_assets': dict(asset_buy.most_common(5)),
        'top_sell_assets': dict(asset_sell.most_common(5)),
        'top_maturities': dict(mat_counts.most_common(5)),
    }


def main():
    print("=" * 80)
    print("  TAP FINANCE RE-SCREEN")
    print("  Threshold sensitivity analysis")
    print("=" * 80)
    print()

    contracts = load_results()
    print(f"  Loaded {len(contracts)} contracts from {ASSETS_PATH.split('/')[-1]}")
    print()

    # Re-screen at multiple thresholds
    results = {
        'total_contracts': len(contracts),
        'thresholds': {},
    }

    print(f"  {'Threshold':12s} | {'BUY':>5s} | {'SELL':>5s} | {'TOTAL':>5s} | {'Mean BUY':>9s} | {'Max BUY':>8s}")
    print("  " + "-" * 65)
    for thresh in THRESHOLDS:
        r = rescreen(contracts, thresh)
        results['thresholds'][thresh] = r
        print(f"  {thresh:>10.1f}% | {r['n_buy']:>5d} | {r['n_sell']:>5d} | {r['n_total']:>5d} | {r['buy_yield_mean']:>8.2f}% | {r['buy_yield_max']:>+7.1f}%")
    print()

    # Default 5% threshold - full analysis
    default_threshold = 5
    default_results = rescreen(contracts, default_threshold)
    results['default_5pct'] = default_results
    print(f"  === DETAILED @ {default_threshold}% THRESHOLD ===")
    print(f"  Total actionable: {default_results['n_total']}")
    print(f"    BUY signals:  {default_results['n_buy']} (avg yield {default_results['buy_yield_mean']:+.2f}%)")
    print(f"    SELL signals: {default_results['n_sell']} (avg yield {default_results['sell_yield_mean']:+.2f}%)")
    print()
    print(f"  Top BUY assets: {default_results['top_buy_assets']}")
    print(f"  Top SELL assets: {default_results['top_sell_assets']}")
    print(f"  Top maturities: {default_results['top_maturities']}")
    print()

    # Top 10 actionable at 5% threshold
    actionable = [r for r in contracts if abs(r['arbitrage_yield_pct']) > 5.0]
    actionable.sort(key=lambda r: -abs(r['arbitrage_yield_pct']))

    print(f"  === TOP 15 SIGNALS @ 5% THRESHOLD ===")
    print(f"  {'Asset':12s} | {'Type':4s} | {'Days':4s} | {'Strike':>7s} | {'BS':>6s} | {'TAP':>6s} | {'Yield':>7s} | Action")
    print("  " + "-" * 90)
    for r in actionable[:15]:
        action = "BUY" if r['arbitrage_yield_pct'] > 0 else "SELL"
        print(f"  {r['asset']:12s} | {r['type']:4s} | {r['maturity_days']:3d}d | ${r['strike']:6.2f} | ${r['bs_price']:5.3f} | ${r['tap_price']:5.3f} | {r['arbitrage_yield_pct']:+6.1f}% | {action}")
    print()

    # Export
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  [EXPORT] -> {OUTPUT_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
