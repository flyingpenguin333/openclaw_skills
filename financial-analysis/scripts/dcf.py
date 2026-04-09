#!/usr/bin/env python3
"""
DCF Valuation Model
Discounted Cash Flow analysis with sensitivity tables.
"""
import pandas as pd
import numpy as np
import argparse

def dcf_valuation(
    fcf_projections: list,
    wacc: float = 0.10,
    terminal_growth: float = 0.025,
    net_debt: float = 0,
    shares_outstanding: float = 1.0
) -> dict:
    """
    Calculate DCF valuation.
    
    Args:
        fcf_projections: List of projected free cash flows
        wacc: Weighted Average Cost of Capital
        terminal_growth: Terminal growth rate
        net_debt: Net debt position
        shares_outstanding: Shares outstanding (millions)
    
    Returns:
        Dictionary with valuation results
    """
    # Calculate present value of projected FCFs
    pv_fcf = []
    for i, fcf in enumerate(fcf_projections, 1):
        pv = fcf / ((1 + wacc) ** i)
        pv_fcf.append(pv)
    
    # Terminal value (perpetuity growth method)
    last_fcf = fcf_projections[-1]
    terminal_value = last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** len(fcf_projections))
    
    # Enterprise value
    enterprise_value = sum(pv_fcf) + pv_terminal
    
    # Equity value
    equity_value = enterprise_value - net_debt
    
    # Per share value
    value_per_share = equity_value / shares_outstanding
    
    results = {
        'pv_projected_fcf': sum(pv_fcf),
        'pv_terminal_value': pv_terminal,
        'enterprise_value': enterprise_value,
        'net_debt': net_debt,
        'equity_value': equity_value,
        'value_per_share': value_per_share,
        'wacc': wacc,
        'terminal_growth': terminal_growth
    }
    
    return results

def sensitivity_analysis(base_results: dict, fcf_projections: list, net_debt: float, shares: float) -> pd.DataFrame:
    """
    Create sensitivity table for WACC and terminal growth.
    """
    wacc_range = np.arange(0.07, 0.13, 0.01)
    growth_range = np.arange(0.01, 0.04, 0.005)
    
    sensitivity = pd.DataFrame(index=growth_range, columns=wacc_range)
    
    for g in growth_range:
        for w in wacc_range:
            result = dcf_valuation(fcf_projections, w, g, net_debt, shares)
            sensitivity.loc[g, w] = result['value_per_share']
    
    return sensitivity

def main():
    parser = argparse.ArgumentParser(description='DCF valuation model')
    parser.add_argument('--company', '-c', required=True, help='Company ticker')
    parser.add_argument('--wacc', type=float, default=0.10, help='WACC (default: 0.10)')
    parser.add_argument('--terminal-growth', type=float, default=0.025, help='Terminal growth (default: 0.025)')
    parser.add_argument('--years', type=int, default=5, help='Projection years (default: 5)')
    
    args = parser.parse_args()
    
    print(f"DCF Model for {args.company}")
    print(f"WACC: {args.wacc:.1%}")
    print(f"Terminal Growth: {args.terminal_growth:.1%}")
    print(f"\nNote: This is a template. Implement data fetching for actual projections.")

if __name__ == '__main__':
    main()
