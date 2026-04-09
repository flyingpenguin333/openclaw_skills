#!/usr/bin/env python3
"""
Daily Stock Analysis Skill - Core Interface
Integrates with daily_stock_analysis project
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Daily stock analysis project path
DSA_PROJECT = Path("C:/Users/KYQ20/.openclaw/workspace/daily_stock_analysis-main")

def ensure_env():
    """Ensure environment variables are set"""
    env_file = DSA_PROJECT / ".env"
    if env_file.exists():
        # Load .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if value and value not in ['your_key_here', '']:
                        os.environ[key] = value

def analyze_stock(stock_code: str):
    """Analyze a single stock"""
    ensure_env()
    
    # Change to project directory
    os.chdir(DSA_PROJECT)
    
    # Run single stock analysis
    cmd = [
        sys.executable, "-c",
        f"""
import sys
sys.path.insert(0, str({DSA_PROJECT!r}))

from data_provider.base import DataFetcherManager
from src.core.pipeline import StockAnalysisPipeline
import asyncio

async def analyze():
    manager = DataFetcherManager()
    pipeline = StockAnalysisPipeline()
    
    # Fetch data
    data = await manager.fetch_stock_data('{stock_code}')
    if data:
        print(f"股票: {{data.get('name', '{stock_code}')}}")
        print(f"当前价格: {{data.get('price', 'N/A')}}")
        print(f"涨跌幅: {{data.get('change_pct', 'N/A')}}%")
        print(f"成交量: {{data.get('volume', 'N/A')}}")
    else:
        print("数据获取失败")

asyncio.run(analyze())
"""
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except Exception as e:
        print(f"执行失败: {e}")

def get_watchlist():
    """Get current watchlist from .env"""
    env_file = DSA_PROJECT / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('STOCK_LIST='):
                    stocks = line.split('=', 1)[1].strip()
                    return [s.strip() for s in stocks.split(',') if s.strip()]
    return ['600519', '300750', '002594']  # defaults

def update_watchlist(stocks: list):
    """Update watchlist in .env"""
    env_file = DSA_PROJECT / ".env"
    if not env_file.exists():
        print("配置文件不存在")
        return False
    
    content = env_file.read_text(encoding='utf-8')
    stock_line = f"STOCK_LIST={','.join(stocks)}"
    
    if 'STOCK_LIST=' in content:
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('STOCK_LIST='):
                new_lines.append(stock_line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    else:
        content += f"\n{stock_line}"
    
    env_file.write_text(content, encoding='utf-8')
    print(f"自选股已更新: {','.join(stocks)}")
    return True

def show_help():
    """Show help message"""
    help_text = """
📊 Daily Stock Analysis Skill

用法:
  python analyze.py <command> [args]

命令:
  analyze <code>      分析单只股票 (e.g., 600519, AAPL)
  batch [codes]       批量分析 (默认分析自选股)
  watchlist           显示当前自选股
  watchlist add <code>    添加自选股
  watchlist remove <code> 移除自选股
  report              查看最新分析报告

示例:
  python analyze.py analyze 600519
  python analyze.py batch 600519,300750
  python analyze.py watchlist add 000001
    """
    print(help_text)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'analyze':
        if len(sys.argv) < 3:
            print("错误: 请提供股票代码")
            print("示例: python analyze.py analyze 600519")
            return
        analyze_stock(sys.argv[2])
    
    elif command == 'batch':
        stocks = sys.argv[2] if len(sys.argv) > 2 else None
        print(f"批量分析: {stocks or '自选股'}")
        # TODO: Implement batch analysis
    
    elif command == 'watchlist':
        if len(sys.argv) < 3:
            stocks = get_watchlist()
            print(f"当前自选股: {', '.join(stocks)}")
        else:
            action = sys.argv[2].lower()
            if action in ['add', 'remove'] and len(sys.argv) > 3:
                code = sys.argv[3]
                current = get_watchlist()
                if action == 'add':
                    if code not in current:
                        current.append(code)
                        update_watchlist(current)
                    else:
                        print(f"{code} 已在列表中")
                else:  # remove
                    if code in current:
                        current.remove(code)
                        update_watchlist(current)
                    else:
                        print(f"{code} 不在列表中")
            else:
                print("用法: watchlist [add|remove] <code>")
    
    elif command == 'report':
        report_dir = DSA_PROJECT / "reports"
        if report_dir.exists():
            reports = sorted(report_dir.glob("*.md"), reverse=True)
            if reports:
                print(f"最新报告: {reports[0]}")
                print(reports[0].read_text(encoding='utf-8'))
            else:
                print("暂无报告")
        else:
            print("报告目录不存在")
    
    else:
        show_help()

if __name__ == "__main__":
    main()
