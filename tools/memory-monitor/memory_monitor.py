#!/usr/bin/env python3
"""
💾 内存条价格监控器
监控 DRAM/CPU 内存条市场价格，支持多数据源
"""

import requests
import time
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style
import re

# 初始化颜色
init(autoreset=True)

# ============== 配置区域 ==============
REFRESH_INTERVAL = 300  # 刷新间隔（秒），默认5分钟

# 关注的内存条型号
WATCH_LIST = {
    'DDR5': [
        'DDR5 16GB 4800/5600',
        'DDR5 32GB 4800/5600',
        'DDR5 8GB SO-DIMM',
        'DDR5 16GB SO-DIMM',
    ],
    'DDR4': [
        'DDR4 16GB 3200',
        'DDR4 8GB 3200',
        'DDR4 16GB SO-DIMM',
        'DDR4 8GB SO-DIMM',
    ],
    'LPDDR': [
        'LPDDR5X 16GB',
        'LPDDR5X 12GB',
        'LPDDR5X 8GB',
        'LPDDR4X 8GB',
    ]
}

# ============== 数据源 ==============

def fetch_dramx_prices():
    """获取 dramx.com 内存价格"""
    try:
        url = "https://www.dramx.com/Price/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {}
        
        text = response.text
        prices = {}
        
        # 解析 DDR5/DDR4 价格
        patterns = {
            'DDR5 16Gb (2Gx8) 4800/5600': r'DDR5 16Gb \(2Gx8\) 4800/5600.*?盘平均.*?([\d.]+)',
            'DDR4 16Gb (2Gx8) 3200': r'DDR4 16Gb \(2Gx8\) 3200.*?盘平均.*?([\d.]+)',
            'DDR4 8Gb (1Gx8) 3200': r'DDR4 8Gb \(1Gx8\) 3200.*?盘平均.*?([\d.]+)',
            'DDR5 UDIMM 16GB': r'DDR5 UDIMM 16GB.*?盘平均.*?([\d.]+)',
            'DDR5 RDIMM 32GB': r'DDR5 RDIMM 32GB.*?盘平均.*?([\d.]+)',
            'DDR4 UDIMM 16GB': r'DDR4 UDIMM 16GB.*?盘平均.*?([\d.]+)',
        }
        
        for name, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                prices[name] = float(match.group(1))
        
        return prices
        
    except Exception as e:
        print(f"❌ 获取dramx数据失败: {e}")
        return {}

# ============== 显示函数 ==============

def draw_separator():
    print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")

def get_color(value, inverse=False):
    """获取涨跌颜色"""
    if inverse:
        return Fore.RED if value < 0 else Fore.GREEN
    return Fore.GREEN if value > 0 else Fore.RED

def format_time():
    return datetime.now().strftime("%H:%M:%S")

def print_header():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════╗
║              💾 内存条价格监控器 🖥️                             ║
║                    实时追踪市场价格                              ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)

def print_price_table(prices):
    """打印价格表格"""
    print(f"{Fore.YELLOW}📊 DRAM 晶圆价格 (美元){Style.RESET_ALL}")
    draw_separator()
    print(f"{'型号':<35} {'价格':>10} {'状态':>10}")
    draw_separator()
    
    key_prices = {
        'DDR5 16Gb (2Gx8) 4800/5600': prices.get('DDR5 16Gb (2Gx8) 4800/5600', 0),
        'DDR4 16Gb (2Gx8) 3200': prices.get('DDR4 16Gb (2Gx8) 3200', 0),
        'DDR4 8Gb (1Gx8) 3200': prices.get('DDR4 8Gb (1Gx8) 3200', 0),
    }
    
    for name, price in key_prices.items():
        if price > 0:
            trend = "📈 上涨" if price > 30 else "📉 下跌" if price < 20 else "➡️ 持平"
            print(f"{name:<35} ${price:>8.2f} {trend}")
    
    draw_separator()
    print()

def print_retail_guide(prices):
    """打印零售价格参考"""
    print(f"{Fore.YELLOW}🏪 模组零售价格参考 (美元){Style.RESET_ALL}")
    draw_separator()
    
    retail_items = [
        ('DDR5 UDIMM 16GB', 'DDR5 16GB 台式机'),
        ('DDR5 RDIMM 32GB', 'DDR5 32GB 服务器'),
        ('DDR4 UDIMM 16GB', 'DDR4 16GB 台式机'),
    ]
    
    for key, name in retail_items:
        price = prices.get(key, 0)
        if price > 0:
            print(f"{name:<30} ${price:>8.2f}")
    
    draw_separator()
    print()

# ============== 主程序 ==============

def main():
    print_header()
    print(f"{Fore.WHITE}⏰ 刷新间隔: {REFRESH_INTERVAL}秒 | 数据源: dramx.com{Style.RESET_ALL}")
    print(f"{Fore.WHITE}💡 按 Ctrl+C 退出{Style.RESET_ALL}")
    draw_separator()
    
    while True:
        try:
            timestamp = format_time()
            
            print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════╗
║ 💾 价格监控 [{timestamp}]                          ║
╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
            """)
            
            # 获取价格
            prices = fetch_dramx_prices()
            
            if prices:
                print_price_table(prices)
                print_retail_guide(prices)
                
                # 简单的价格提醒逻辑
                ddr5_price = prices.get('DDR5 16Gb (2Gx8) 4800/5600', 0)
                if ddr5_price > 50:
                    print(f"{Fore.RED}⚠️  注意：DDR5 晶圆价格较高，可能影响零售价格{Style.RESET_ALL}")
                elif ddr5_price < 30:
                    print(f"{Fore.GREEN}✅ DDR5 价格回落，是入手的好时机！{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 无法获取价格数据，请检查网络连接{Style.RESET_ALL}")
            
            print()
            draw_separator()
            print(f"{Fore.WHITE}🕐 下次刷新: {REFRESH_INTERVAL}秒后...{Style.RESET_ALL}")
            draw_separator()
            
            time.sleep(REFRESH_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}👋 下次见！{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}❌ 错误: {e}{Style.RESET_ALL}")
            time.sleep(10)

if __name__ == "__main__":
    main()
