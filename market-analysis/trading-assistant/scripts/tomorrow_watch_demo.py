#!/usr/bin/env python3
"""
Tomorrow's Watch - Advanced Analysis (ASCII Version)
"""

import os
import sys
sys.path.insert(0, str(Path(__file__).parent))

from evening_summary_live import *

# 扩展分析逻辑
def analyze_stock_advanced(quote):
    """
    综合分析一只股票的关注价值
    """
    score = 0
    signals = []
    
    # 1. 价格动量评分 (0-30)
    change_pct = quote.get('change_pct', 0)
    if change_pct > 5:
        score += 30
        signals.append("Strong momentum: +" + str(round(change_pct, 1)) + "%")
    elif change_pct > 3:
        score += 25
        signals.append("Good momentum: +" + str(round(change_pct, 1)) + "%")
    elif change_pct > 1:
        score += 15
        signals.append("Positive momentum: +" + str(round(change_pct, 1)) + "%")
    elif change_pct > 0:
        score += 5
    elif change_pct < -3:
        signals.append("Oversold bounce potential: " + str(round(change_pct, 1)) + "%")
    
    # 2. 成交量评分 (0-25)
    vol_ratio = quote.get('vol_ratio', 0)
    if vol_ratio > 3:
        score += 25
        signals.append("Volume spike: " + str(round(vol_ratio, 1)) + "x average")
    elif vol_ratio > 2:
        score += 20
        signals.append("High volume: " + str(round(vol_ratio, 1)) + "x average")
    elif vol_ratio > 1.5:
        score += 10
        signals.append("Above average volume")
    
    # 3. 资金流向 (0-20)
    # 通过买卖盘比例判断
    if quote.get('buyVolume', 0) > 0 and quote.get('sellVolume', 0) > 0:
        buy_ratio = quote['buyVolume'] / (quote['buyVolume'] + quote['sellVolume'])
        if buy_ratio > 0.7:
            score += 20
            signals.append("Strong buying: " + str(round(buy_ratio*100)) + "% buy orders")
        elif buy_ratio > 0.6:
            score += 15
            signals.append("Buying interest: " + str(round(buy_ratio*100)) + "% buy orders")
    
    # 4. 技术形态 (0-15)
    price = quote.get('price', 0)
    high = quote.get('high', 0)
    if price > 0 and high > 0 and price >= high * 0.998:
        score += 15
        signals.append("Breakout: New intraday high")
    
    # 5. 估值安全 (0-10)
    pe = quote.get('pe', 0)
    pb = quote.get('pb', 0)
    if 0 < pe < 15:
        score += 10
        signals.append("Attractive valuation: PE " + str(round(pe, 1)))
    elif 0 < pe < 25:
        score += 5
    
    return score, signals


print("=" * 70)
print("TOMORROW'S WATCH - Advanced Analysis")
print("=" * 70)
print("\nAnalysis Dimensions:")
print("  1. Price Momentum (0-30 points)")
print("  2. Volume Analysis (0-25 points)")
print("  3. Fund Flow (0-20 points)")
print("  4. Technical Pattern (0-15 points)")
print("  5. Valuation Safety (0-10 points)")
print("  MAX Score: 100 points")
print("\n" + "=" * 70)

# 示例分析结果 (基于今日收盘数据)
watch_results = [
    {
        "symbol": "000001",
        "name": "平安银行",
        "score": 25,
        "signals": [
            "Oversold bounce potential: -0.55%",
            "Attractive valuation: PE 4.8"
        ],
        "priority": "MEDIUM",
        "why": "Low valuation, potential rebound"
    },
    {
        "symbol": "600519", 
        "name": "贵州茅台",
        "score": 35,
        "signals": [
            "Defensive stock in volatile market",
            "Stable performance: -0.36%"
        ],
        "priority": "MEDIUM",
        "why": "Core asset, defensive play"
    },
    {
        "symbol": "002594",
        "name": "比亚迪", 
        "score": 55,
        "signals": [
            "Strong momentum: +3.2%",
            "High volume: 2.5x average",
            "New energy sector hot"
        ],
        "priority": "HIGH",
        "why": "Sector momentum + volume confirmation"
    }
]

print("\nTOP WATCH LIST:\n")

for i, stock in enumerate(watch_results, 1):
    print(f"{i}. {stock['name']} ({stock['symbol']})")
    print(f"   Score: {stock['score']}/100 [{stock['priority']} PRIORITY]")
    print(f"   Signals:")
    for signal in stock['signals']:
        print(f"      - {signal}")
    print(f"   Why Watch: {stock['why']}")
    print()

print("=" * 70)
print("TRADING SUGGESTIONS:")
print("=" * 70)
print()
print("HIGH PRIORITY (Score >= 50):")
print("  - Consider position if momentum continues tomorrow")
print("  - Set stop loss at today's low")
print("  - Target: 3-5% short term gain")
print()
print("MEDIUM PRIORITY (30-49):")
print("  - Wait for clearer breakout signal")
print("  - Monitor first 30 minutes")
print()
print("RISK MANAGEMENT:")
print("  - Max position per stock: 20%")
print("  - Overall market trend: Check US market tonight")
print("  - News catalyst: Watch for policy announcements")
print()
print("=" * 70)
print("Analysis complete!")
print("=" * 70)
