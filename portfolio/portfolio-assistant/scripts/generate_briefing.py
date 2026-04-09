import sys
sys.path.insert(0, r'C:\Users\KYQ20\.openclaw\workspace\skills\portfolio-assistant\scripts')
from data_manager import DataManager

dm = DataManager()
portfolios = dm.get_portfolios()
keywords = dm.get_keyword_list()

# Generate simple briefing
print('INVESTMENT BRIEFING')
print('=' * 60)
print('Date: 2026-03-06')
print('')

# Market Overview (placeholder)
print('[Market Overview]')
print('  NASDAQ: -- (API not configured)')
print('  S&P 500: --')
print('  VIX: --')
print('')

# Portfolio Summary
print('[Your Portfolios]')
for name, p in portfolios.items():
    total_cost = sum(a.quantity * a.avg_cost for a in p.assets)
    print('  ' + name + ':')
    for asset in p.assets:
        print('    - ' + asset.ticker + ': ' + str(asset.quantity) + ' shares')
    print('    Total Cost: $' + str(total_cost))
    print('')

# Watchlist
print('[Watchlist]')
for kw in keywords:
    kw_name = kw['keyword']
    kw_freq = kw['frequency']
    print('  - ' + kw_name + ' (' + kw_freq + ')')
print('')

# News placeholder
print('[News Radar]')
print('  (News search requires API configuration)')
print('  - Configure Brave/Tavily API for news monitoring')
print('')

print('=' * 60)
print('End of Briefing')
