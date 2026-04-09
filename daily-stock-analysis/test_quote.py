import sys
sys.path.insert(0, r'C:\Users\KYQ20\.openclaw\workspace\daily_stock_analysis-main')
from data_provider.base import DataFetcherManager

manager = DataFetcherManager()

print('测试获取实时行情...')
print('=' * 60)

# 获取茅台的实时行情
data = manager.get_realtime_quote('600519')
print(f"数据类型: {type(data)}")
print(f"数据内容: {data}")

# 尝试访问属性
if data:
    print(f"\n可用属性:")
    for attr in dir(data):
        if not attr.startswith('_'):
            try:
                val = getattr(data, attr)
                if not callable(val):
                    print(f"  {attr}: {val}")
            except:
                pass
