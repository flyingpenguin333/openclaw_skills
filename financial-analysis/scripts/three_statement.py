#!/usr/bin/env python3
"""
3-Statement Financial Model
Integrated income statement, balance sheet, and cash flow statement.
"""
import pandas as pd
import argparse

def build_three_statement_model(years: int = 5) -> dict:
    """
    Build 3-statement financial model structure.
    
    Args:
        years: Number of projection years
    
    Returns:
        Dictionary with DataFrames for each statement
    """
    periods = [f'Year {i+1}' for i in range(years)]
    
    # Income Statement structure
    income_statement = pd.DataFrame(index=[
        'Revenue',
        'COGS',
        'Gross Profit',
        'SG&A',
        'EBITDA',
        'D&A',
        'EBIT',
        'Interest Expense',
        'EBT',
        'Taxes',
        'Net Income'
    ], columns=periods)
    
    # Balance Sheet structure
    balance_sheet = pd.DataFrame(index=[
        'Cash',
        'Accounts Receivable',
        'Inventory',
        'Other Current Assets',
        'Total Current Assets',
        'PP&E',
        'Intangibles',
        'Other Long-term Assets',
        'Total Assets',
        '',
        'Accounts Payable',
        'Accrued Expenses',
        'Short-term Debt',
        'Total Current Liabilities',
        'Long-term Debt',
        'Other Long-term Liabilities',
        'Total Liabilities',
        '',
        'Common Stock',
        'Retained Earnings',
        'Total Equity',
        'Total Liabilities & Equity'
    ], columns=periods)
    
    # Cash Flow Statement structure
    cash_flow = pd.DataFrame(index=[
        'Net Income',
        'D&A',
        'Change in Working Capital',
        'Operating Cash Flow',
        '',
        'CapEx',
        'Acquisitions',
        'Investing Cash Flow',
        '',
        'Debt Issued/(Repaid)',
        'Equity Issued/(Repurchased)',
        'Dividends',
        'Financing Cash Flow',
        '',
        'Net Change in Cash',
        'Beginning Cash',
        'Ending Cash'
    ], columns=periods)
    
    return {
        'income_statement': income_statement,
        'balance_sheet': balance_sheet,
        'cash_flow': cash_flow
    }

def main():
    parser = argparse.ArgumentParser(description='3-Statement Financial Model')
    parser.add_argument('--company', '-c', required=True, help='Company ticker')
    parser.add_argument('--years', '-y', type=int, default=5, help='Projection years')
    parser.add_argument('--output', '-o', help='Output Excel file')
    
    args = parser.parse_args()
    
    model = build_three_statement_model(args.years)
    
    print(f"3-Statement Model for {args.company}")
    print(f"Years: {args.years}")
    print(f"\nIncome Statement:\n{model['income_statement']}")
    
    if args.output:
        with pd.ExcelWriter(args.output, engine='openpyxl') as writer:
            model['income_statement'].to_excel(writer, sheet_name='Income Statement')
            model['balance_sheet'].to_excel(writer, sheet_name='Balance Sheet')
            model['cash_flow'].to_excel(writer, sheet_name='Cash Flow')
        print(f"\nSaved to: {args.output}")

if __name__ == '__main__':
    main()
