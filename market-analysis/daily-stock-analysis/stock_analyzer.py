#!/usr/bin/env python3
"""
Daily Stock Analysis Skill - Simple Wrapper
Calls daily_stock_analysis project directly
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Project paths
SKILL_DIR = Path(__file__).parent
WORKSPACE = Path("C:/Users/KYQ20/.openclaw/workspace")
DSA_PROJECT = WORKSPACE / "daily_stock_analysis-main"
REPORTS_DIR = DSA_PROJECT / "reports"

def run_dsa_command(args):
    """Run daily_stock_analysis command"""
    cmd = [sys.executable, "main.py"] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=DSA_PROJECT,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='ignore'
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "执行超时", 1
    except Exception as e:
        return "", str(e), 1

def show_latest_report():
    """Show latest analysis report"""
    if not REPORTS_DIR.exists():
        print("报告目录不存在")
        return
    
    reports = sorted(REPORTS_DIR.glob("report_*.md"), reverse=True)
    if not reports:
        print("暂无分析报告")
        return
    
    latest = reports[0]
    print(f"最新报告: {latest.name}")
    print("=" * 50)
    try:
        content = latest.read_text(encoding='utf-8')
        print(content)
    except Exception as e:
        print(f"读取报告失败: {e}")

def quick_analyze(stock_code: str):
    """Quick analysis without full AI (faster)"""
    print(f"正在分析 {stock_code}...")
    print("(完整分析需要配置 AI API Key)")
    print()
    
    # Show latest report if exists
    show_latest_report()

def main():
    parser = argparse.ArgumentParser(
        description='Daily Stock Analysis Skill',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --report              查看最新报告
  %(prog)s --project-path        显示项目路径
        """
    )
    
    parser.add_argument('--report', '-r', action='store_true',
                        help='查看最新分析报告')
    parser.add_argument('--project-path', '-p', action='store_true',
                        help='显示 daily_stock_analysis 项目路径')
    parser.add_argument('--run', action='store_true',
                        help='运行完整分析（需要 AI API Key）')
    
    args = parser.parse_args()
    
    # Check if project exists
    if not DSA_PROJECT.exists():
        print(f"项目不存在: {DSA_PROJECT}")
        print("请先安装 daily_stock_analysis 项目")
        return 1
    
    if args.project_path:
        print(f"项目路径: {DSA_PROJECT}")
        print(f"配置文件: {DSA_PROJECT / '.env'}")
        return 0
    
    if args.report:
        show_latest_report()
        return 0
    
    if args.run:
        print("启动完整分析...")
        stdout, stderr, code = run_dsa_command([])
        if stdout:
            print(stdout)
        if stderr:
            print("错误:", stderr)
        return code
    
    # Default: show help + latest report
    parser.print_help()
    print()
    show_latest_report()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
