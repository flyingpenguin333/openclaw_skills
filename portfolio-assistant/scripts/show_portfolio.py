import sys
sys.path.insert(0, r'C:\Users\KYQ20\.openclaw\workspace\skills\portfolio-assistant\scripts')
from data_manager import DataManager
from feishu_handler import MessageFormatter

dm = DataManager()

# 获取组合数据
portfolios = dm.get_portfolios()
keywords = dm.get_keyword_list()

# 生成报告
print('Portfolio Asset Radar')
print('=' * 50)

if portfolios:
    print('')
    print('[Holdings]')
    for name, p in portfolios.items():
        print(f'  Portfolio: {name}')
        for asset in p.assets:
            print(f'    - {asset.ticker}: {asset.quantity} shares @ ${asset.avg_cost}')
        print('')

if keywords:
    print('[Watchlist Keywords]')
    for kw in keywords:
        stocks = ', '.join(kw['related_stocks']) if kw['related_stocks'] else 'None'
        print(f'  - {kw.keyword}: {kw.frequency} ({stocks})')

print('')
print('=' * 50)
print('Send "buy", "sell", "watch" commands to manage')
