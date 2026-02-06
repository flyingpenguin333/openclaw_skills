# 🦾 Clawdbot 全球实时行情面板

> 装X利器，看盘必备。零成本，5分钟上线。

---

## 📊 效果预览

```
╔══════════════════════════════════════════════════════════════════════════╗
║ 🦾 CLAWDBOT 实时行情  [14:32:05]                             ║
╚══════════════════════════════════════════════════════════════════════════╝

【 A股 】
───────────────────────────────────────────────────────────────────────────────
  上证指数    │  3421.00  │ 🟢 +15.23 (+0.45%)  │ H:3425.00 L:3402.00
  贵州茅台    │  1780.50  │ 🔴 -8.20 (-0.46%)   │ H:1792.00 L:1775.00

【 港股 】
───────────────────────────────────────────────────────────────────────────────
  恒生指数    │  19250.00 │ 🟢 +120.50 (+0.63%)
  腾讯        │  365.20   │ 🟢 +5.80 (+1.61%)

【 美股 】
───────────────────────────────────────────────────────────────────────────────
  纳斯达克    │  15200.00 │ 🟢 +250.00 (+1.67%)
  英伟达      │  950.00   │ 🔴 -12.50 (-1.30%)
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests colorama
```

### 2. 创建文件

创建 `market_panel.py`，粘贴以下代码：

```python
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
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════╗
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
```

### 3. 运行

```bash
python market_panel.py
```

---

## ⚙️ 自定义配置

编辑 `WATCH_LIST` 区域，修改你关注的股票：

```python
WATCH_LIST = {
    'A': [
        '000001.SH',  # 上证指数
        '600519.SH',  # 贵州茅台
        '300750.SZ',  # 宁德时代
    ],
    'HK': [
        '00700.HK',   # 腾讯
        '09988.HK',   # 阿里巴巴
    ],
    'US': [
        'AAPL',       # 苹果
        'NVDA',       # 英伟达
        'TSLA',       # 特斯拉
    ]
}
```

### 股票代码说明

| 市场 | 代码示例 | 说明 |
|-----|---------|------|
| A股-上海 | `600519.SH` | 贵州茅台 |
| A股-深圳 | `000001.SZ` | 深证成指 |
| 港股 | `00700.HK` | 腾讯 |
| 美股 | `AAPL` | 苹果 |
| 指数 | `^IXIC` | 纳斯达克 |

---

## 📦 数据源

| 市场 | 来源 | 实时性 |
|-----|------|-------|
| A股 | 新浪财经 | ⏱️ 延迟几秒 |
| 港股 | 腾讯 | ⏱️ 延迟几秒 |
| 美股 | Yahoo Finance | ⏱️ 延迟几秒 |

---

## 🔧 常见问题

**Q: 报错 "数据获取失败"**
> 检查网络连接，免费API可能临时抽风

**Q: 能加自选股吗**
> 直接改 `WATCH_LIST` 配置即可

**Q: 怎么改刷新频率**
> 修改 `REFRESH_INTERVAL = 10`（秒）

---

## 📝 更新日志

- **v1.0** - 基础功能，支持 A股/港股/美股
- **v1.1** - 增加红绿配色，装X效果+100%

---

> 🦾 Made with Clawdbot
