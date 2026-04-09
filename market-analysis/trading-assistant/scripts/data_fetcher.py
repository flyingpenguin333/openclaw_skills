#!/usr/bin/env python3
"""
Trading Assistant Data Fetcher
集成 QVeris API 获取 A股市场数据
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加父目录到路径以导入模块
SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

# 导入 QVerisDataFetcher
from qveris_data_fetcher import QVerisDataFetcher


class TradingDataFetcher:
    """交易助手数据获取器 - 基于 QVeris"""

    def __init__(self):
        self.skill_root = SKILL_ROOT
        self.config_path = self.skill_root / "config.json"
        self.data_source_config_path = self.skill_root / "data_source.json"
        self.cache_dir = self.skill_root / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        # 加载配置
        self.config = self._load_json(self.config_path)
        self.data_source_config = self._load_json(self.data_source_config_path)

        # 初始化 QVeris 数据获取器
        api_key = os.getenv('QVERIS_API_KEY')
        if not api_key:
            print("⚠️  Warning: QVERIS_API_KEY not set")
        self.qveris_fetcher = QVerisDataFetcher(api_key=api_key)

    def _load_json(self, path: Path) -> Dict:
        """加载 JSON 配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

    def _save_json(self, path: Path, data: Dict):
        """保存 JSON 配置文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving {path}: {e}")

    def _get_cache_path(self, cache_type: str) -> Path:
        """获取缓存文件路径"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.cache_dir / f"{cache_type}_{date_str}.json"

    def _load_cache(self, cache_type: str, max_age_minutes: int = 5) -> Optional[Dict]:
        """从缓存加载数据"""
        cache_path = self._get_cache_path(cache_type)

        if not cache_path.exists():
            return None

        # 检查缓存是否过期
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - cache_time > timedelta(minutes=max_age_minutes):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache {cache_path}: {e}")
            return None

    def _save_cache(self, cache_type: str, data: Dict):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(cache_type)
        self._save_json(cache_path, data)

    def get_market_indices(self) -> Dict[str, Any]:
        """获取主要市场指数"""
        # 先尝试从缓存获取
        cached = self._load_cache("market_indices", max_age_minutes=5)
        if cached:
            return cached

        # 使用 QVeris 获取上证指数
        try:
            quote = self.qveris_fetcher.get_realtime_quote_a_share(['000001.SH'])
            if quote and len(quote) > 0:
                data = quote[0]
                result = {
                    "shanghai": {
                        "code": "000001.SH",
                        "name": "上证指数",
                        "price": data.get('price', 0),
                        "change": data.get('change', 0),
                        "change_pct": data.get('change_pct', 0),
                        "volume": data.get('volume', 0)
                    },
                    "fetched_at": datetime.now().isoformat()
                }
            else:
                result = {
                    "shanghai": {"code": "000001.SH", "name": "上证指数", "price": 0, "change": 0, "change_pct": 0},
                    "fetched_at": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching market indices: {e}")
            result = {
                "shanghai": {"code": "000001.SH", "name": "上证指数", "price": 0, "change": 0, "change_pct": 0},
                "fetched_at": datetime.now().isoformat(),
                "error": str(e)
            }

        # 缓存结果
        self._save_cache("market_indices", result)
        return result

    def get_hot_sectors(self, top_n: int = 5) -> List[Dict]:
        """获取热点板块"""
        # 从缓存获取
        cached = self._load_cache("hot_sectors", max_age_minutes=15)
        if cached:
            return cached.get("sectors", [])[:top_n]

        # 使用 QVeris 获取板块数据
        sectors = self.qveris_fetcher.get_sector_hot(top_n=top_n)

        # 格式化结果
        formatted_sectors = []
        for sector in sectors:
            formatted_sectors.append({
                "name": sector.get('sector_name', ''),
                "change_pct": sector.get('change_pct', 0),
                "fund_flow": sector.get('main_inflow', 0),
                "hot_score": sector.get('hot_score', 0)
            })

        result = {"sectors": formatted_sectors, "fetched_at": datetime.now().isoformat()}
        self._save_cache("hot_sectors", result)
        return formatted_sectors[:top_n]

    def get_watchlist_quotes(self, symbols: List[str] = None) -> List[Dict]:
        """获取自选股实时报价"""
        watchlist = self.config.get("watchlist", [])

        if not symbols:
            symbols = [item.get("symbol") for item in watchlist]

        if not symbols:
            return []

        # 先尝试从缓存获取
        cached = self._load_cache("watchlist_quotes", max_age_minutes=2)
        if cached and cached.get("symbols") == symbols:
            return cached.get("quotes", [])

        # 使用 QVeris 获取行情
        quotes = []

        # 分离 A股和美股
        a_share_symbols = []
        us_symbols = []

        for symbol in symbols:
            # 判断市场
            if len(symbol) == 6 and symbol.isdigit():
                # A股
                if symbol.startswith('6'):
                    a_share_symbols.append(f"{symbol}.SH")
                else:
                    a_share_symbols.append(f"{symbol}.SZ")
            else:
                # 美股
                us_symbols.append(symbol)

        # 获取 A股行情
        if a_share_symbols:
            try:
                a_share_quotes = self.qveris_fetcher.get_realtime_quote_a_share(a_share_symbols)
                for quote in a_share_quotes:
                    symbol_clean = quote.get('symbol', '').replace('.SZ', '').replace('.SH', '')

                    # 从 watchlist 获取额外信息
                    watch_item = next((w for w in watchlist if w.get('symbol') == symbol_clean), {})

                    quotes.append({
                        "symbol": symbol_clean,
                        "name": watch_item.get('name', quote.get('name', '')),
                        "market": "A",
                        "price": quote.get('price', 0),
                        "pre_close": quote.get('pre_close', 0),
                        "change": quote.get('change', 0),
                        "change_pct": quote.get('change_pct', 0),
                        "volume": quote.get('volume', 0),
                        "amount": quote.get('amount', 0),
                        "turnover": quote.get('turnover', 0),
                        "pe": quote.get('pe', 0),
                        "pb": quote.get('pb', 0),
                        "observation_levels": watch_item.get('observation_levels', {}),
                        "position": watch_item.get('position', {})
                    })
            except Exception as e:
                print(f"Error fetching A-share quotes: {e}")

        # 获取美股行情
        if us_symbols:
            try:
                us_quotes = self.qveris_fetcher.get_realtime_quote_us(us_symbols)
                for quote in us_quotes:
                    symbol = quote.get('symbol', '')

                    # 从 watchlist 获取额外信息
                    watch_item = next((w for w in watchlist if w.get('symbol') == symbol), {})

                    quotes.append({
                        "symbol": symbol,
                        "name": watch_item.get('name', quote.get('name', '')),
                        "market": "US",
                        "price": quote.get('price', 0),
                        "pre_close": quote.get('pre_close', 0),
                        "change": quote.get('change', 0),
                        "change_pct": quote.get('change_pct', 0),
                        "volume": quote.get('volume', 0),
                        "amount": quote.get('amount', 0),
                        "turnover": 0,
                        "pe": quote.get('pe', 0),
                        "pb": 0,
                        "observation_levels": watch_item.get('observation_levels', {}),
                        "position": watch_item.get('position', {})
                    })
            except Exception as e:
                print(f"Error fetching US stock quotes: {e}")

        result = {"symbols": symbols, "quotes": quotes, "fetched_at": datetime.now().isoformat()}
        self._save_cache("watchlist_quotes", result)
        return quotes

    def check_price_alerts(self, symbols: List[str] = None) -> List[Dict]:
        """检查价格提醒"""
        quotes = self.get_watchlist_quotes(symbols)

        alerts = []
        for quote in quotes:
            symbol = quote.get("symbol")
            current_price = quote.get("price", 0)
            observation_levels = quote.get("observation_levels", {})

            upper_level = observation_levels.get("upper")
            lower_level = observation_levels.get("lower")

            # 检查上破
            if upper_level and current_price >= upper_level:
                alerts.append({
                    "symbol": symbol,
                    "name": quote.get("name"),
                    "type": "break_upper",
                    "level": upper_level,
                    "current_price": current_price,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

            # 检查下破
            if lower_level and current_price <= lower_level:
                alerts.append({
                    "symbol": symbol,
                    "name": quote.get("name"),
                    "type": "break_lower",
                    "level": lower_level,
                    "current_price": current_price,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

        return alerts

    def get_morning_briefing_data(self) -> Dict:
        """获取早间推送所需的所有数据"""
        return {
            "market_indices": self.get_market_indices(),
            "hot_sectors": self.get_hot_sectors(top_n=5),
            "watchlist": self.get_watchlist_quotes(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
        }

    def get_intraday_check_data(self) -> Dict:
        """获取盘中检查所需的数据"""
        return {
            "watchlist_quotes": self.get_watchlist_quotes(),
            "price_alerts": self.check_price_alerts(),
            "time": datetime.now().strftime("%H:%M")
        }

    def get_evening_summary_data(self) -> Dict:
        """获取收盘总结所需的数据"""
        watchlist_quotes = self.get_watchlist_quotes()

        # 计算持仓收益
        positions = []
        total_value = 0
        total_cost = 0
        today_pnl = 0

        for quote in watchlist_quotes:
            position_info = quote.get('position', {})
            if not position_info or position_info.get('quantity', 0) <= 0:
                continue

            quantity = position_info.get('quantity', 0)
            cost_price = position_info.get('cost_price', 0)
            current_price = quote.get('price', 0)
            pre_close = quote.get('pre_close', cost_price)

            market_value = current_price * quantity
            cost_value = cost_price * quantity
            pnl = market_value - cost_value
            today_change = (current_price - pre_close) * quantity

            total_value += market_value
            total_cost += cost_value
            today_pnl += today_change

            positions.append({
                "symbol": quote.get('symbol'),
                "name": quote.get('name'),
                "market": quote.get('market'),
                "quantity": quantity,
                "cost_price": cost_price,
                "current_price": current_price,
                "market_value": market_value,
                "pnl": pnl,
                "pnl_pct": (current_price - cost_price) / cost_price * 100 if cost_price > 0 else 0,
                "today_change_pct": quote.get('change_pct', 0),
                "today_pnl": today_change
            })

        # 排序
        positions.sort(key=lambda x: x['today_change_pct'], reverse=True)

        return {
            "market_indices": self.get_market_indices(),
            "watchlist_quotes": watchlist_quotes,
            "positions": positions,
            "summary": {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_pnl": total_value - total_cost,
                "today_pnl": today_pnl,
                "today_pnl_pct": (today_pnl / total_cost * 100) if total_cost > 0 else 0,
                "position_count": len(positions)
            },
            "top_gainer": positions[0] if positions else None,
            "top_loser": positions[-1] if positions else None,
            "date": datetime.now().strftime("%Y-%m-%d")
        }


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Trading Assistant Data Fetcher")
    parser.add_argument("--test", action="store_true", help="Test data fetching")
    parser.add_argument("--morning-briefing", action="store_true", help="Fetch morning briefing data")
    parser.add_argument("--intraday-check", action="store_true", help="Fetch intraday check data")
    parser.add_argument("--evening-summary", action="store_true", help="Fetch evening summary data")

    args = parser.parse_args()

    fetcher = TradingDataFetcher()

    if args.test:
        print("Testing Trading Data Fetcher with QVeris...")
        print("\n1. Market Indices:")
        print(json.dumps(fetcher.get_market_indices(), indent=2, ensure_ascii=False))

        print("\n2. Hot Sectors:")
        print(json.dumps(fetcher.get_hot_sectors(), indent=2, ensure_ascii=False))

        print("\n3. Watchlist Quotes:")
        print(json.dumps(fetcher.get_watchlist_quotes(), indent=2, ensure_ascii=False))

        print("\n4. Price Alerts:")
        print(json.dumps(fetcher.check_price_alerts(), indent=2, ensure_ascii=False))

    elif args.morning_briefing:
        data = fetcher.get_morning_briefing_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.intraday_check:
        data = fetcher.get_intraday_check_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.evening_summary:
        data = fetcher.get_evening_summary_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
