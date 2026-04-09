#!/usr/bin/env python3
"""
LBO Model
Leveraged Buyout analysis with returns calculation.
"""
import pandas as pd
import numpy as np
import argparse

def lbo_model(
    entry_ebitda: float,
    entry_multiple: float,
    debt_ratio: float = 0.60,
    interest_rate: float = 0.08,
    exit_multiple: float = None,
    holding_period: int = 5,
    ebitda_growth: float = 0.05
) -> dict:
    """
    Calculate LBO returns.
    
    Args:
        entry_ebitda: Entry EBITDA
        entry_multiple: Entry EV/EBITDA multiple
        debt_ratio: Debt as % of purchase price
        interest_rate: Interest rate on debt
        exit_multiple: Exit EV/EBITDA (defaults to entry_multiple)
        holding_period: Years held
        ebitda_growth: Annual EBITDA growth rate
    
    Returns:
        Dictionary with LBO results
    """
    if exit_multiple is None:
        exit_multiple = entry_multiple
    
    # Purchase price
    purchase_price = entry_ebitda * entry_multiple
    
    # Sources & Uses
    debt = purchase_price * debt_ratio
    equity = purchase_price - debt
    
    # Project EBITDA and cash flows
    ebitda_schedule = [entry_ebitda * ((1 + ebitda_growth) ** i) for i in range(holding_period + 1)]
    
    # Simplified: Assume all EBITDA goes to debt paydown
    debt_schedule = [debt]
    for i in range(holding_period):
        fcf = ebitda_schedule[i+1] * 0.5  # Simplified FCF assumption
        new_debt = max(0, debt_schedule[-1] - fcf)
        debt_schedule.append(new_debt)
    
    # Exit
    exit_ebitda = ebitda_schedule[-1]
    exit_enterprise_value = exit_ebitda * exit_multiple
    exit_debt = debt_schedule[-1]
    exit_equity_value = exit_enterprise_value - exit_debt
    
    # Returns
    total_return = exit_equity_value - equity
    moic = exit_equity_value / equity
    irr = (moic ** (1 / holding_period)) - 1
    
    results = {
        'purchase_price': purchase_price,
        'debt': debt,
        'equity': equity,
        'exit_enterprise_value': exit_enterprise_value,
        'exit_debt': exit_debt,
        'exit_equity_value': exit_equity_value,
        'total_return': total_return,
        'moic': moic,
        'irr': irr,
        'holding_period': holding_period
    }
    
    return results

def main():
    parser = argparse.ArgumentParser(description='LBO Model')
    parser.add_argument('--company', '-c', required=True, help='Company ticker')
    parser.add_argument('--ebitda', type=float, required=True, help='Entry EBITDA (millions)')
    parser.add_argument('--multiple', '-m', type=float, required=True, help='Entry EV/EBITDA')
    parser.add_argument('--debt-ratio', type=float, default=0.60, help='Debt ratio (default: 0.60)')
    parser.add_argument('--years', '-y', type=int, default=5, help='Holding period')
    
    args = parser.parse_args()
    
    results = lbo_model(
        args.ebitda,
        args.multiple,
        debt_ratio=args.debt_ratio,
        holding_period=args.years
    )
    
    print(f"LBO Model for {args.company}")
    print(f"\nSources & Uses:")
    print(f"  Purchase Price: ${results['purchase_price']:.1f}M")
    print(f"  Debt: ${results['debt']:.1f}M")
    print(f"  Equity: ${results['equity']:.1f}M")
    print(f"\nReturns:")
    print(f"  Exit Equity Value: ${results['exit_equity_value']:.1f}M")
    print(f"  MOIC: {results['moic']:.2f}x")
    print(f"  IRR: {results['irr']:.1%}")

if __name__ == '__main__':
    main()
