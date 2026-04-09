# Financial Modeling Conventions

## Color Coding

Standard financial modeling color scheme:

| Color | Meaning | Example |
|-------|---------|---------|
| **Blue** | Hard-coded input | Historical data, assumptions |
| **Black** | Formula/calculation | =A1+B1 |
| **Green** | Link to another sheet | =Sheet2!A1 |
| **Red** | Error flag | Conditional formatting for errors |

## Formula Structure

### Best Practices
1. **One formula per row** - Copy across, don't rewrite
2. **No hard-coding in formulas** - Reference input cells
3. **Consistent signs** - Revenue positive, expenses negative (or vice versa, but be consistent)
4. **Error checking** - Add checksums: Assets = Liabilities + Equity

### Example Structure
```
Revenue          = [Blue: Historical] / [Black: Growth formula]
COGS             = [Black: % of Revenue]
Gross Profit     = [Black: Revenue - COGS]
```

## Model Structure

### Tabs/Sections
1. **Assumptions** - All blue inputs
2. **Income Statement** - Revenue to Net Income
3. **Balance Sheet** - Assets, Liabilities, Equity
4. **Cash Flow** - Operating, Investing, Financing
5. **Supporting Schedules** - D&A, Working Capital, Debt
6. **Outputs** - Summary metrics, charts

### Time Periods
- Historical: Actual data (blue)
- Projected: Model output (black/green)
- Clearly separate with a column or formatting

## Quality Checks

### Balance Sheet
- Assets = Liabilities + Equity
- Cash from BS = Cash from CF statement

### Cash Flow
- Net Change in Cash = Ending Cash - Beginning Cash
- Beginning Cash (Year 2) = Ending Cash (Year 1)

### Income Statement
- EPS = Net Income / Shares Outstanding
- Verify against reported EPS

## Units

- Always consistent (millions, billions, etc.)
- Label clearly in headers
- Example: "($ in millions, except per share data)"

## Circular References

Avoid circular references (e.g., interest expense based on average debt, which depends on interest). If necessary:
- Use Excel's iterative calculation
- Or approximate with beginning-of-period debt
