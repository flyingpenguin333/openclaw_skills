from data_manager import DataManager, Asset

# 测试数据管理器
dm = DataManager()

# 测试添加持仓
print('=== Testing Add Holdings ===')
dm.add_asset('Tech Portfolio', Asset(ticker='TSLA', name='Tesla Inc', quantity=1000, avg_cost=120.0))
dm.add_asset('Tech Portfolio', Asset(ticker='NVDA', name='NVIDIA Corp', quantity=100, avg_cost=450.0))
print('Add successful')

# 测试查看组合
print('\n=== Portfolio Summary ===')
summary = dm.get_portfolio_summary('Tech Portfolio')
print(f"Portfolio: {summary['name']}")
print(f"Assets: {summary['asset_count']}")
print(f"Total Cost: ${summary['total_cost']:,.2f}")
for asset in summary['assets']:
    print(f"  - {asset['ticker']}: {asset['quantity']} shares @ ${asset['avg_cost']}")

# 测试添加关键词
print('\n=== Testing Add Keywords ===')
dm.add_keyword('Solid State Battery', related_stocks=['QS', 'SLDP'])
dm.add_keyword('AI Chips', frequency='real-time', related_stocks=['NVDA', 'AMD'])
print('Keywords added')

# 测试查看关键词
print('\n=== Keyword List ===')
for kw in dm.get_keyword_list():
    stocks = ', '.join(kw['related_stocks']) if kw['related_stocks'] else 'None'
    print(f"  - {kw['keyword']}: {kw['frequency']} ({stocks})")

print('\nAll tests passed!')
