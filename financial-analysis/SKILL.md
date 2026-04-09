---
name: financial-analysis
description: Financial analysis toolkit for investment banking, equity research, and corporate finance. Supports comparable company analysis (comps), DCF valuation, LBO modeling, 3-statement financial modeling, and presentation QC. Use when the user needs to perform financial analysis, valuation, build financial models, create pitch materials, or analyze companies. Triggers on phrases like "financial analysis", "DCF model", "comparable company", "LBO model", "3-statement model", "valuation", "financial modeling", "pitch deck", "investment banking", "equity research".
---

# Financial Analysis

## Overview

Professional financial analysis toolkit adapted from Anthropic's financial-services-plugins. Provides workflows for investment banking, equity research, and corporate finance tasks.

**Note**: This is an OpenClaw adaptation of the original Claude Code plugin. Some features (like MCP data connectors) require separate API configuration.

## Prerequisites

- Python 3.8+
- Required packages: `pandas`, `numpy`, `openpyxl`, `python-pptx` (for Excel/PowerPoint output)
- Optional: API keys for data providers (see references/data-providers.md)

## Quick Start

### Comparable Company Analysis (Comps)

```python
# Build a comps table
python scripts/comps.py --company AAPL --peers MSFT,GOOGL,AMZN
```

### DCF Valuation

```python
# Run DCF model
python scripts/dcf.py --company AAPL --wacc 0.08 --terminal-growth 0.025
```

### Financial Modeling

```python
# Build 3-statement model
python scripts/three_statement.py --company AAPL --years 5
```

## Core Capabilities

### 1. Comparable Company Analysis (Comps)

Build and analyze peer comparison tables:
- Trading multiples (P/E, EV/EBITDA, P/B)
- Growth metrics
- Margin analysis
- Returns (ROE, ROIC)

**Scripts**: `scripts/comps.py`

### 2. DCF Valuation

Discounted Cash Flow modeling:
- Projected free cash flows
- WACC calculation
- Terminal value (perpetuity growth or exit multiple)
- Sensitivity analysis

**Scripts**: `scripts/dcf.py`

### 3. LBO Modeling

Leveraged Buyout analysis:
- Sources & uses
- Debt schedule
- Returns analysis (IRR, MOIC)
- Exit scenarios

**Scripts**: `scripts/lbo.py`

### 4. 3-Statement Modeling

Integrated financial statements:
- Income statement
- Balance sheet
- Cash flow statement
- Supporting schedules

**Scripts**: `scripts/three_statement.py`

### 5. Presentation QC

Quality check for pitch materials:
- Format consistency
- Formula auditing
- Color coding (blue/black/green conventions)

**Scripts**: `scripts/presentation_qc.py`

## Workflow Patterns

### Research to Report

1. Gather company data (see references/data-sources.md)
2. Build comps (`/comps`)
3. Run valuation (`/dcf`)
4. Generate report (see references/report-templates.md)

### Spreadsheet Analysis

1. Load data (CSV/Excel)
2. Build model (`/three-statement`)
3. Add sensitivity tables
4. QC and format (`/presentation-qc`)

## References

### data-providers.md
Available data sources and API configuration:
- Free: Yahoo Finance, SEC EDGAR
- Premium: Daloopa, Morningstar, S&P Global, FactSet, etc.

### modeling-conventions.md
Financial modeling best practices:
- Color coding (blue = input, black = formula, green = link)
- Formula structure
- Error checking

### report-templates.md
Templates for common outputs:
- Equity research reports
- Pitch books
- IC memos
- One-pagers

## Slash Commands (Future)

Planned commands for interactive use:
- `/comps [company]` - Comparable company analysis
- `/dcf [company]` - DCF valuation
- `/lbo [company]` - LBO model
- `/earnings [company] [quarter]` - Earnings analysis
- `/one-pager [company]` - Company profile

## Limitations

- **Data Access**: Requires separate API keys for premium data providers
- **Real-time Data**: Not included; user must provide or use free sources
- **MCP Connectors**: Original Claude Code MCP connectors not available in OpenClaw

## Customization

To customize for your firm:
1. Edit `references/modeling-conventions.md` with your firm's standards
2. Add your templates to `references/report-templates.md`
3. Configure API keys in `scripts/config.py`

## Credits

Adapted from [Anthropic Financial Services Plugins](https://github.com/anthropics/financial-services-plugins).
Original plugins by Anthropic, adapted for OpenClaw by user.
