# Data Providers

## Free Data Sources

### Yahoo Finance (yfinance)
- **Coverage**: US and international equities
- **Data**: Prices, fundamentals, financial statements
- **Usage**: `pip install yfinance`
- **Limitations**: 15-minute delay, rate limits

### SEC EDGAR
- **Coverage**: US public companies
- **Data**: 10-K, 10-Q, 8-K filings
- **Usage**: `sec-edgar-downloader` or direct API
- **Limitations**: US only, XBRL parsing required

### FRED (Federal Reserve)
- **Coverage**: Economic data
- **Data**: Interest rates, GDP, inflation
- **Usage**: `pip install fredapi`
- **API Key**: Required (free)

## Premium Data Providers

### Daloopa
- **Focus**: Historical financial data, modeling-ready
- **MCP Server**: `https://mcp.daloopa.com/server/mcp`
- **Note**: Requires subscription

### Morningstar
- **Focus**: Global equities, funds
- **MCP Server**: `https://mcp.morningstar.com/mcp`
- **Note**: Requires subscription

### S&P Global (Capital IQ)
- **Focus**: Comprehensive financial data
- **MCP Server**: `https://kfinance.kensho.com/integrations/mcp`
- **Note**: Requires subscription

### FactSet
- **Focus**: Institutional-grade data
- **MCP Server**: `https://mcp.factset.com/mcp`
- **Note**: Requires subscription

### Moody's
- **Focus**: Credit ratings, risk data
- **MCP Server**: `https://api.moodys.com/genai-ready-data/m1/mcp`
- **Note**: Requires subscription

### LSEG (Refinitiv)
- **Focus**: Fixed income, FX, equities
- **MCP Server**: `https://api.analytics.lseg.com/lfa/mcp`
- **Note**: Requires subscription

### PitchBook
- **Focus**: Private markets, VC/PE
- **MCP Server**: `https://premium.mcp.pitchbook.com/mcp`
- **Note**: Requires subscription

## Configuration

Create a `config.py` file in the scripts directory:

```python
# Data provider API keys
API_KEYS = {
    'yahoo': None,  # Free, no key needed
    'fred': 'YOUR_FRED_API_KEY',
    'daloopa': 'YOUR_DALOOPA_KEY',
    'morningstar': 'YOUR_MORNINGSTAR_KEY',
    # ... etc
}

# Default data source
DEFAULT_SOURCE = 'yahoo'
```

## Implementation Notes

Since OpenClaw doesn't support MCP connectors like Claude Code, you'll need to:
1. Install provider SDKs separately
2. Configure API keys manually
3. Modify scripts to use your preferred data source
