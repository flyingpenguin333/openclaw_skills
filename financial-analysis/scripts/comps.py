#!/usr/bin/env python3
"""
Comparable Company Analysis (Comps)
Build peer comparison tables with trading multiples.
"""
import pandas as pd
import argparse
from typing import List, Dict

def build_comps(target: str, peers: List[str], data_source: str = "yahoo") -> pd.DataFrame:
    """
    Build comparable company analysis table.
    
    Args:
        target: Target company ticker
        peers: List of peer company tickers
        data_source: Data source ('yahoo' for free, or premium provider)
    
    Returns:
        DataFrame with comps table
    """
    # TODO: Implement data fetching based on data_source
    # For now, returns template structure
    
    all_companies = [target] + peers
    
    metrics = [
        'Company', 'Price', 'Market Cap', 'EV', 
        'P/E', 'EV/EBITDA', 'EV/Revenue', 'P/B',
        'Revenue Growth', 'EBITDA Margin', 'Net Margin',
        'ROE', 'ROIC', 'Debt/EBITDA'
    ]
    
    # Template DataFrame
    df = pd.DataFrame(index=all_companies, columns=metrics)
    df.index.name = 'Ticker'
    
    print(f"Comps Table Template")
    print(f"Target: {target}")
    print(f"Peers: {', '.join(peers)}")
    print(f"\n{df}")
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Build comparable company analysis')
    parser.add_argument('--company', '-c', required=True, help='Target company ticker')
    parser.add_argument('--peers', '-p', required=True, help='Comma-separated peer tickers')
    parser.add_argument('--output', '-o', help='Output file path (Excel)')
    
    args = parser.parse_args()
    
    peers = [p.strip() for p in args.peers.split(',')]
    df = build_comps(args.company, peers)
    
    if args.output:
        df.to_excel(args.output)
        print(f"\nSaved to: {args.output}")

if __name__ == '__main__':
    main()
