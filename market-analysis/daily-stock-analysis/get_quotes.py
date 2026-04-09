import sys
sys.path.insert(0, r'C:\Users\KYQ20\.openclaw\workspace\daily_stock_analysis-main')
from data_provider.base import DataFetcherManager

manager = DataFetcherManager()
stocks = ['600519', '300750', '002594']

print('实时行情数据：')
print('=' * 60)

for code in stocks:
    data = manager.get_realtime_quote(code)
    if data:
        name = data.get('name', code)
        price = data.get('price', 0)
        change = data.get('change_pct', 0)
        vol_ratio = data.get('volume_ratio', 0)
        turnover = data.get('turnover_rate', 0)
        print(f"\n股票: {name} ({code})")
        print(f"  当前价格: {price:.2f}")
        print(f"  涨跌幅: {change:+.2f}%")
        print(f"  量比: {vol_ratio:.2f}")
        print(f"  换手率: {turnover:.2f}%")
    else:
        print(f"{code}: 获取失败")
