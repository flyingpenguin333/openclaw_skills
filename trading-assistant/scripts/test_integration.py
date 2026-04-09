#!/usr/bin/env python3
"""
Trading Assistant - 快速测试脚本
"""

import os
import sys
from pathlib import Path

# 设置路径
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

# 设置 API Key
os.environ['QVERIS_API_KEY'] = 'sk-wHXgrRI3Naqmj92Meknakwrv4DFeRCzi-YnCVs3mpoA'

from qveris_data_fetcher import QVerisDataFetcher

print("=" * 70)
print("Trading Assistant - QVeris Integration Test")
print("=" * 70)

fetcher = QVerisDataFetcher()

# 测试1: 获取A股行情
print("\n[Test 1] A-Share Quotes: 000001.SZ + 600519.SH")
try:
    quotes = fetcher.get_realtime_quote_a_share(['000001.SZ', '600519.SH'])
    if quotes:
        for q in quotes:
            print(f"  {q.get('symbol')}: Price={q.get('price')}, Change={q.get('change_pct'):.2f}%")
    else:
        print("  No data returned")
except Exception as e:
    print(f"  Error: {e}")

# 测试2: 获取热点板块
print("\n[Test 2] Hot Sectors")
try:
    sectors = fetcher.get_sector_hot(top_n=3)
    if sectors:
        for s in sectors:
            print(f"  {s.get('sector_name')}: Change={s.get('change_pct'):.2f}%, Score={s.get('hot_score'):.1f}")
    else:
        print("  No data returned")
except Exception as e:
    print(f"  Error: {e}")

# 测试3: 获取美股
print("\n[Test 3] US Stock: AAPL")
try:
    quotes = fetcher.get_realtime_quote_us(['AAPL'])
    if quotes:
        for q in quotes:
            print(f"  {q.get('symbol')}: Price=${q.get('price')}, Change={q.get('change_pct'):.2f}%")
    else:
        print("  No data returned")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("Test completed!")
print("=" * 70)
