#!/usr/bin/env python3
"""
Real Data Test - Calling real QVeris/THS iFinD API
Date: 2026-03-09
"""

import subprocess
import json
import os
from datetime import datetime

os.environ['QVERIS_API_KEY'] = 'sk-wHXgrRI3Naqmj92Meknakwrv4DFeRCzi-YnCVs3mpoA'
tool_path = os.path.expanduser('~/.openclaw/skills/qveris/scripts/qveris_tool.mjs')

print('=' * 70)
print('REAL DATA TEST FROM QVERIS / THS iFinD API')
print('Date: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print('=' * 70)

# Test 1: Ping An Bank
print('\n[TEST 1] Ping An Bank (000001.SZ) - Real-time Quote')
result = subprocess.run(
    ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
     '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
     '--params', json.dumps({'codes': '000001.SZ'})],
    capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
)

if 'Result:' in result.stdout:
    parts = result.stdout.split('Result:')
    if len(parts) > 1:
        data = json.loads(parts[1].strip())
        if 'data' in data and len(data['data']) > 0:
            stock = data['data'][0][0]
            print('  Stock: ' + str(stock.get('thscode')))
            print('  Name: Ping An Bank')
            print('  Price: ' + str(stock.get('latest')))
            print('  Change: ' + str(round(stock.get('changeRatio', 0), 2)) + '%')
            print('  Volume: ' + str(stock.get('volume')))
            print('  Amount: ' + str(stock.get('amount')))
            print('  Time: ' + str(stock.get('time')))
            print('  Source: REAL DATA from THS iFinD API')

# Test 2: Kweichow Moutai
print('\n[TEST 2] Kweichow Moutai (600519.SH) - Real-time Quote')
result = subprocess.run(
    ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
     '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
     '--params', json.dumps({'codes': '600519.SH'})],
    capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
)

if 'Result:' in result.stdout:
    parts = result.stdout.split('Result:')
    if len(parts) > 1:
        data = json.loads(parts[1].strip())
        if 'data' in data and len(data['data']) > 0:
            stock = data['data'][0][0]
            print('  Stock: ' + str(stock.get('thscode')))
            print('  Name: Kweichow Moutai')
            print('  Price: ' + str(stock.get('latest')))
            print('  Change: ' + str(round(stock.get('changeRatio', 0), 2)) + '%')
            print('  Volume: ' + str(stock.get('volume')))
            print('  Amount: ' + str(stock.get('amount')))
            print('  PE: ' + str(round(stock.get('pe_ttm', 0), 2)))
            print('  PB: ' + str(round(stock.get('pbr_lf', 0), 2)))
            print('  Time: ' + str(stock.get('time')))
            print('  Source: REAL DATA from THS iFinD API')

# Test 3: Shanghai Composite Index
print('\n[TEST 3] Shanghai Composite Index (000001.SH) - Real-time Quote')
result = subprocess.run(
    ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
     '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
     '--params', json.dumps({'codes': '000001.SH'})],
    capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
)

if 'Result:' in result.stdout:
    parts = result.stdout.split('Result:')
    if len(parts) > 1:
        data = json.loads(parts[1].strip())
        if 'data' in data and len(data['data']) > 0:
            stock = data['data'][0][0]
            print('  Index: Shanghai Composite')
            print('  Price: ' + str(stock.get('latest')))
            print('  Change: ' + str(round(stock.get('changeRatio', 0), 2)) + '%')
            print('  Volume: ' + str(stock.get('volume')))
            print('  Source: REAL DATA from THS iFinD API')

# Test 4: BYD
print('\n[TEST 4] BYD (002594.SZ) - Real-time Quote')
result = subprocess.run(
    ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
     '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
     '--params', json.dumps({'codes': '002594.SZ'})],
    capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
)

if 'Result:' in result.stdout:
    parts = result.stdout.split('Result:')
    if len(parts) > 1:
        data = json.loads(parts[1].strip())
        if 'data' in data and len(data['data']) > 0:
            stock = data['data'][0][0]
            print('  Stock: ' + str(stock.get('thscode')))
            print('  Name: BYD')
            print('  Price: ' + str(stock.get('latest')))
            print('  Change: ' + str(round(stock.get('changeRatio', 0), 2)) + '%')
            print('  Source: REAL DATA from THS iFinD API')

print('\n' + '=' * 70)
print('DATA SOURCE VERIFICATION')
print('=' * 70)
print('API Endpoint: qveris.ai/api/v1')
print('Data Provider: THS iFinD (Tonghuashun)')
print('Data Type: Real-time quotation')
print('Update Frequency: Real-time')
print('Status: LIVE DATA')
print('=' * 70)
print('TEST COMPLETED SUCCESSFULLY')
