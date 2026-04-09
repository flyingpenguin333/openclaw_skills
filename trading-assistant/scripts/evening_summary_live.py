#!/usr/bin/env python3
"""
Trading Assistant - 收盘总结 (实时版)
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 设置 API Key
os.environ['QVERIS_API_KEY'] = 'sk-wHXgrRI3Naqmj92Meknakwrv4DFeRCzi-YnCVs3mpoA'

tool_path = os.path.expanduser("~/.openclaw/skills/qveris/scripts/qveris_tool.mjs")

# 自选股配置
watchlist = [
    {"symbol": "000001", "name": "平安银行", "market": "A", "position": 1000, "cost_price": 11.00},
    {"symbol": "600519", "name": "贵州茅台", "market": "A", "position": 100, "cost_price": 1600.00},
]

print("=" * 70)
print("Trading Assistant - Evening Summary")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

# 获取股票行情
print("\n[1/3] Fetching stock quotes...")
quotes = []

for stock in watchlist:
    symbol = stock['symbol']
    if symbol.startswith('6'):
        symbol_with_suffix = f"{symbol}.SH"
    else:
        symbol_with_suffix = f"{symbol}.SZ"
    
    try:
        result = subprocess.run(
            ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
             '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
             '--params', json.dumps({'codes': symbol_with_suffix})],
            capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
        )
        
        if 'Result:' in result.stdout:
            parts = result.stdout.split('Result:')
            if len(parts) > 1:
                data = json.loads(parts[1].strip())
                if 'data' in data and len(data['data']) > 0:
                    stock_data = data['data'][0][0]
                    quote = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'price': stock_data.get('latest', 0),
                        'pre_close': stock_data.get('preClose', 0),
                        'change_pct': stock_data.get('changeRatio', 0),
                        'position': stock['position'],
                        'cost_price': stock['cost_price'],
                        'volume': stock_data.get('volume', 0),
                        'amount': stock_data.get('amount', 0),
                        'pe': stock_data.get('pe_ttm', 0),
                        'pb': stock_data.get('pbr_lf', 0),
                    }
                    quotes.append(quote)
                    print(f"  [OK] {stock['name']}: {quote['price']} ({quote['change_pct']:+.2f}%)")
    except Exception as e:
        print(f"  [FAIL] {stock['name']}: {e}")

if not quotes:
    print("\n  No data available.")
    sys.exit(1)

# 计算持仓收益
print("\n[2/3] Calculating portfolio...")
total_value = 0
total_cost = 0
today_pnl = 0

for quote in quotes:
    position = quote['position']
    current_price = quote['price']
    cost_price = quote['cost_price']
    pre_close = quote['pre_close']
    
    market_value = current_price * position
    cost_value = cost_price * position
    pnl = market_value - cost_value
    today_change = (current_price - pre_close) * position
    
    total_value += market_value
    total_cost += cost_value
    today_pnl += today_change
    
    quote['market_value'] = market_value
    quote['cost_value'] = cost_value
    quote['pnl'] = pnl
    quote['pnl_pct'] = (current_price - cost_price) / cost_price * 100 if cost_price > 0 else 0
    quote['today_pnl'] = today_change

# 排序
quotes.sort(key=lambda x: x['change_pct'], reverse=True)

total_pnl = total_value - total_cost
today_pnl_pct = (today_pnl / total_cost * 100) if total_cost > 0 else 0

# 生成报告
print("\n[3/3] Generating report...")
print("\n" + "=" * 70)
print("EVENING SUMMARY REPORT")
print("=" * 70)

print(f"\n[Money] Today's P&L")
print(f"  Total Value:    {total_value:>15,.2f}")
print(f"  Today's P&L:    {today_pnl:>15,.2f} ({today_pnl_pct:+.2f}%)")
print(f"  Total P&L:      {total_pnl:>15,.2f}")

print(f"\n[Chart] Holdings Performance")
print(f"  {'Name':<12} {'Price':>10} {'Change':>8} {'P&L':>12} {'Position':>10}")
print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*12} {'-'*10}")
for q in quotes:
    emoji = "+" if q['change_pct'] >= 0 else "-"
    print(f"  {q['name']:<12} {q['price']:>10.2f} {emoji}{abs(q['change_pct']):>6.2f}% {q['pnl']:>11,.0f} {q['position']:>10}")

print(f"\n[Best] Today's Best & Worst")
if quotes:
    best = quotes[0]
    worst = quotes[-1]
    print(f"  Best:  {best['name']} ({best['change_pct']:+.2f}%)")
    print(f"  Worst: {worst['name']} ({worst['change_pct']:+.2f}%)")

# 明日关注
print(f"\n[Watch] Tomorrow's Watchlist")
watch_list = []
for q in quotes:
    reasons = []
    if q['change_pct'] > 3:
        reasons.append(f"Up {q['change_pct']:.1f}%")
    if abs(q['change_pct']) > 5:
        reasons.append("High volatility")
    if q['volume'] > 1000000:  # 100万手
        reasons.append("High volume")
    
    if reasons:
        watch_list.append(f"  {q['name']}: {', '.join(reasons)}")

if watch_list:
    for item in watch_list:
        print(item)
else:
    print("  No special signals today.")

print("\n" + "=" * 70)
print("Summary completed! Have a good evening!")
print("=" * 70)
