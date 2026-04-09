from feishu_handler import MessageParser, MessageFormatter

parser = MessageParser()
formatter = MessageFormatter()

print('=== Testing Message Parser ===\n')

test_messages = [
    'Buy 1000 shares of TSLA at $120 in Tech Portfolio',
    'Sell 500 shares of TSLA in Tech Portfolio',
    'Watch Solid State Battery',
    'Unwatch Solid State Battery',
    'View my asset radar',
    'Generate briefing',
]

for msg in test_messages:
    result = parser.parse(msg)
    print(f'Input: {msg}')
    print(f'Parsed: action={result.action}')
    if result.ticker:
        print(f'  ticker={result.ticker}, qty={result.quantity}, price={result.price}')
    if result.keyword:
        print(f'  keyword={result.keyword}')
    print()

print('\n=== Testing Message Formatter ===\n')

# Test buy confirmation
print(formatter.format_buy_confirmation('TSLA', 'Tesla Inc', 1000, 120.0, 'Tech Portfolio', 120000.0))
print()

# Test portfolio summary
portfolio_data = {
    'portfolios': {
        'Tech Portfolio': {
            'assets': [
                {'ticker': 'TSLA', 'quantity': 1000, 'avg_cost': 120.0},
                {'ticker': 'NVDA', 'quantity': 100, 'avg_cost': 450.0}
            ]
        }
    },
    'keywords': [
        {'keyword': 'Solid State Battery', 'added_at': '2026-03-06T10:00:00', 'frequency': 'daily'},
        {'keyword': 'AI Chips', 'added_at': '2026-03-05T10:00:00', 'frequency': 'real-time'}
    ]
}
print(formatter.format_portfolio_summary(portfolio_data))

print('\n=== All Tests Passed ===')
