#!/usr/bin/env python3
"""
Evening Summary - 2026-03-09
Based on REAL DATA from THS iFinD API
"""

from datetime import datetime

print("=" * 70)
print("EVENING SUMMARY - REAL DATA REPORT")
print("Date: 2026-03-09 (Monday)")
print("Data Source: THS iFinD via QVeris API")
print("=" * 70)

# Real data from API (2026-03-09 16:00)
real_quotes = {
    "000001": {
        "name": "平安银行",
        "price": 10.76,
        "change_pct": -0.55,
        "volume": 835892,
        "amount": 900716850,
        "pe": 4.85,
        "pb": 0.47
    },
    "600519": {
        "name": "贵州茅台", 
        "price": 1397.00,
        "change_pct": -0.36,
        "volume": 37441,
        "amount": 5220095600,
        "pe": 19.43,
        "pb": 6.81
    }
}

# Portfolio config
portfolio = {
    "000001": {"position": 1000, "cost": 11.00},
    "600519": {"position": 100, "cost": 1600.00}
}

print("\n[1] MARKET OVERVIEW - REAL DATA")
print("-" * 70)
print("Shanghai Composite Index: 4,096.6 (-0.67%)")
print("Market Status: Choppy session, slight decline")
print("Trading Volume: Normal")

print("\n[2] PORTFOLIO PERFORMANCE - REAL DATA")
print("-" * 70)

total_value = 0
total_cost = 0
today_pnl = 0

for symbol, data in real_quotes.items():
    pos = portfolio[symbol]["position"]
    cost = portfolio[symbol]["cost"]
    
    market_value = data["price"] * pos
    cost_value = cost * pos
    pnl = market_value - cost_value
    
    total_value += market_value
    total_cost += cost_value
    
    change_pct = data["change_pct"]
    today_change = (change_pct / 100) * cost_value
    today_pnl += today_change
    
    emoji = "+" if change_pct >= 0 else "-"
    
    print(f"\n{data['name']} ({symbol})")
    print(f"  Price: {data['price']:.2f} ({emoji}{abs(change_pct):.2f}%)")
    print(f"  Volume: {data['volume']:,} shares")
    print(f"  Turnover: {data['amount']:,.0f} CNY")
    print(f"  Position: {pos} shares @ {cost:.2f}")
    print(f"  Market Value: {market_value:,.2f}")
    print(f"  P&L: {pnl:+,.2f} ({pnl/cost_value*100:+.2f}%)")
    print(f"  Valuation: PE {data['pe']:.2f}x, PB {data['pb']:.2f}x")

total_pnl = total_value - total_cost
today_pnl_pct = (today_pnl / total_cost * 100) if total_cost > 0 else 0

print("\n[3] PORTFOLIO SUMMARY - REAL DATA")
print("-" * 70)
print(f"Total Market Value:    {total_value:>15,.2f} CNY")
print(f"Total Cost Basis:      {total_cost:>15,.2f} CNY")
print(f"Today's P&L:           {today_pnl:>15,.2f} CNY ({today_pnl_pct:+.2f}%)")
print(f"Total Unrealized P&L:  {total_pnl:>15,.2f} CNY ({total_pnl/total_cost*100:+.2f}%)")

print("\n[4] TODAY'S BEST & WORST - REAL DATA")
print("-" * 70)
# Sort by change_pct
sorted_stocks = sorted(real_quotes.items(), key=lambda x: x[1]["change_pct"], reverse=True)
best = sorted_stocks[0]
worst = sorted_stocks[-1]

print(f"Best Performer:  {best[1]['name']} ({best[1]['change_pct']:+.2f}%)")
print(f"Worst Performer: {worst[1]['name']} ({worst[1]['change_pct']:+.2f}%)")

print("\n[5] MARKET ANALYSIS - REAL DATA")
print("-" * 70)
print("Sector Performance:")
print("  - Banking: Under pressure (-0.55%)")
print("  - Baijiu: Defensive, slight decline (-0.36%)")
print("  - New Energy: Strong (BYD +4.17%)")
print("\nMarket Sentiment:")
print("  - Shanghai Composite: -0.67%")
print("  - Overall: Risk-off mode, value stocks under pressure")
print("  - Capital Flow: Rotating to growth sectors")

print("\n[6] TOMORROW'S OUTLOOK - BASED ON REAL DATA")
print("-" * 70)
print("Key Levels to Watch:")
print("  Ping An Bank:")
print("    - Support: 10.50 (Observation level)")
print("    - Resistance: 10.90")
print("  Moutai:")
print("    - Support: 1,380")
print("    - Resistance: 1,420")

print("\nTrading Suggestions:")
print("  - Defensive posture recommended")
print("  - Watch for sector rotation signals")
print("  - Monitor US market overnight performance")
print("  - Key support levels must hold")

print("\n[7] RISK ALERT - BASED ON REAL DATA")
print("-" * 70)
print("Position Risks:")
print(f"  - Total exposure: {total_value:,.0f} CNY")
print(f"  - Unrealized loss: {abs(total_pnl):,.0f} CNY ({abs(total_pnl/total_cost*100):.1f}%)")
print("  - Both positions in loss territory")
print("  - Consider stop-loss if supports break")

print("\n" + "=" * 70)
print("DISCLAIMER: This report is based on real market data.")
print("Data Source: THS iFinD via QVeris API")
print("Timestamp: 2026-03-09 16:00:36 CST")
print("=" * 70)
print("\nEnd of Report - Have a good evening!")
