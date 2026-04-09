import sys
sys.path.insert(0, r'C:\Users\KYQ20\.openclaw\workspace\daily_stock_analysis-main')
from data_provider.base import DataFetcherManager

manager = DataFetcherManager()
stocks = ['600519', '300750', '002594']

print('')
print('=' * 70)
print('  DAILY STOCK ANALYSIS - 实时行情')
print('=' * 70)

for code in stocks:
    data = manager.get_realtime_quote(code)
    if data:
        # Determine trend indicator
        trend = "上涨" if data.change_pct > 0 else "下跌" if data.change_pct < 0 else "平盘"
        change_str = f"{data.change_pct:+.2f}%"
        
        print(f"\n  {data.name} ({code})")
        print(f"  {'-' * 50}")
        print(f"  当前价格:  {data.price:.2f}  ({change_str})")
        print(f"  今日趋势:  {trend}")
        print(f"  成交量比:  {data.volume_ratio:.2f}")
        print(f"  换手率:    {data.turnover_rate:.2f}%")
        print(f"  市盈率:    {data.pe_ratio:.2f}")
        print(f"  市净率:    {data.pb_ratio:.2f}")
    else:
        print(f"\n  {code}: 数据获取失败")

print('\n' + '=' * 70)
print('  数据来源: 腾讯财经 / 东方财富')
print('  注意: AI 决策分析需要配置 API Key')
print('=' * 70)
