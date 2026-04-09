#!/usr/bin/env python3
"""
全球实时行情面板 - Clawdbot Edition
支持：A股、港股、美股 实时行情
"""

import requests
import time
import os
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style

# 初始化颜色
init(autoreset=True)

# ============== 配置区域 ==============
# 在这里修改你关注的股票代码
WATCH_LIST = {
    # A股 (代码.交易所: sh=上海, sz=深圳)
    'A': [
        '000001.SH',  # 上证指数
        '399001.SZ',  # 深证成指
        '399006.SZ',  # 创业板指
        '600519.SH',  # 贵州茅台
        '000651.SZ',  # 格力电器
    ],
    # 港股
    'HK': [
        'HSI',        # 恒生指数
        '09618.HK',   # 恒生科技
        '00700.HK',   # 腾讯
    ],
    # 美股
    'US': [
        '^IXIC',      # 纳斯达克
        '^DJI',       # 道琼斯
        '^GSPC',      # S&P 500
        'AAPL',       # 苹果
        'NVDA',       # 英伟达
        'TSLA',       # 特斯拉
    ]
}

# 刷新间隔（秒）
REFRESH_INTERVAL = 10

# ============== 数据源 ==============

def get_a_stock(code):
    """获取A股实时行情 - 新浪财经"""
    try:
        url = f"http://hq.sinajs.cn/list={code}"
        headers = {'Referer': 'http://finance.sina.com.cn'}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.text
        if len(data) > 30:
            parts = data.split('=')[1].split(',')
            return {
                'name': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': int(parts[5]),
                'time': parts[31] if len(parts) > 31 else '',
            }
    except Exception as e:
        pass
    return None

def get_hk_stock(code):
    """获取港股实时行情 - 腾讯"""
    try:
        # 腾讯港股接口
        url = f"http://qt.gtimg.cn/q={code}"
        r = requests.get(url, timeout=5)
        data = r.text
        parts = data.split('~')
        if len(parts) > 30:
            return {
                'name': parts[1],
                'price': float(parts[3]),
                'change': float(parts[32]),
                'change_pct': float(parts[33]),
            }
    except Exception as e:
        pass
    return None

def get_us_stock(code):
    """获取美股实时行情 - Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}"
        r = requests.get(url, timeout=5)
        data = r.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        quote = result['indicators']['quote'][0]
        return {
            'name': code,
            'price': meta.get('regularMarketPrice', 0),
            'change': meta.get('regularMarketChange', 0),
            'change_pct': meta.get('regularMarketChangePercent', 0),
        }
    except Exception as e:
        pass
    return None

# ============== 显示函数 ==============

def fmt_num(num):
    """格式化数字"""
    if num >= 1e8:
        return f"{num/1e8:.2f}亿"
    elif num >= 1e4:
        return f"{num/1e4:.2f}万"
    else:
        return str(num)

def fmt_price(price):
    """格式化价格颜色"""
    return f"{Fore.WHITE}{price:.2f}"

def draw_separator(length=80):
    """画分隔线"""
    print(f"{Fore.BLUE}{'─' * length}{Style.RESET_ALL}")

def get_color(val, inverse=False):
    """获取涨跌颜色"""
    if inverse:
        return Fore.RED if val < 0 else Fore.GREEN
    return Fore.GREEN if val > 0 else Fore.RED

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time():
    """格式化当前时间"""
    return datetime.now().strftime("%H:%M:%S")

# ============== 主循环 ==============

def main():
    clear_screen()
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║           🦾 CLAWDBOT 全球实时行情面板 🦾                      ║
║                    装X利器 刷屏无价                             ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    draw_separator()
    print(f"{Fore.YELLOW}📡 连接数据源中...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⏰ 刷新间隔: {REFRESH_INTERVAL}秒{Style.RESET_ALL}")
    draw_separator()
    time.sleep(1)

    while True:
        clear_screen()
        timestamp = format_time()
        
        # 标题
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════╗
║ 🦾 CLAWDBOT 实时行情  [{timestamp}]                       ║
╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        
        total_change = 0
        stock_count = 0
        
        # A股
        print(f"{Fore.YELLOW}【 A股 】{Style.RESET_ALL}")
        draw_separator()
        for code in WATCH_LIST['A']:
            data = get_a_stock(code)
            if data:
                name = data.get('name', code)[:6]
                price = data.get('close', data.get('price', 0))
                high = data.get('high', 0)
                low = data.get('low', 0)
                
                # 计算涨跌
                prev_close = data.get('close', data.get('price', 0))
                open_price = data.get('open', 0)
                change = price - open_price
                change_pct = (change / open_price * 100) if open_price else 0
                
                color = get_color(change)
                sign = '+' if change >= 0 else ''
                
                print(f"  {name:8} │ {price:8.2f} │ {color}{sign}{change:+.2f}{Style.RESET_ALL} ({color}{sign}{change_pct:+.2f}%{Style.RESET_ALL}) │ H:{high:.2f} L:{low:.2f}")
            else:
                print(f"  {code:8} │ {Fore.RED}数据获取失败{Style.RESET_ALL}")
        
        print()
        
        # 港股
        print(f"{Fore.YELLOW}【 港股 】{Style.RESET_ALL}")
        draw_separator()
        for code in WATCH_LIST['HK']:
            data = get_hk_stock(code)
            if data:
                name = data.get('name', code)[:8]
                price = data.get('price', 0)
                change = data.get('change', 0)
                change_pct = data.get('change_pct', 0)
                
                color = get_color(change)
                sign = '+' if change >= 0 else ''
                
                print(f"  {name:10} │ {price:8.2f} │ {color}{sign}{change:+.2f}{Style.RESET_ALL} ({color}{sign}{change_pct:+.2f}%{Style.RESET_ALL})")
            else:
                print(f"  {code:10} │ {Fore.RED}数据获取失败{Style.RESET_ALL}")
        
        print()
        
        # 美股
        print(f"{Fore.YELLOW}【 美股 】{Style.RESET_ALL}")
        draw_separator()
        for code in WATCH_LIST['US']:
            data = get_us_stock(code)
            if data:
                name = data.get('name', code)[:10]
                price = data.get('price', 0)
                change = data.get('change', 0)
                change_pct = data.get('change_pct', 0)
                
                color = get_color(change)
                sign = '+' if change >= 0 else ''
                
                print(f"  {name:10} │ {price:8.2f} │ {color}{sign}{change:+.2f}{Style.RESET_ALL} ({color}{sign}{change_pct:+.2f}%{Style.RESET_ALL})")
            else:
                print(f"  {code:10} │ {Fore.RED}数据获取失败{Style.RESET_ALL}")
        
        print()
        draw_separator()
        print(f"{Fore.WHITE}💡 按 Ctrl+C 退出 | 数据来源: 新浪财经/腾讯/Yahoo Finance{Style.RESET_ALL}")
        draw_separator()
        
        try:
            time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}👋 下次见！{Style.RESET_ALL}")
            sys.exit(0)

if __name__ == "__main__":
    main()
