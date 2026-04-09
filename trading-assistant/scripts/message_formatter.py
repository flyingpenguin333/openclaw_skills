#!/usr/bin/env python3
"""
Trading Assistant Message Formatter
格式化交易消息用于飞书推送
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加父目录到路径
SKILL_ROOT = Path(__file__).parent.parent


class MessageFormatter:
    """消息格式化器"""

    def __init__(self):
        self.skill_root = SKILL_ROOT
        self.config_path = self.skill_root / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def format_number(self, num: float, decimals: int = 2) -> str:
        """格式化数字，保留指定小数位"""
        if num is None:
            return "N/A"
        return f"{num:.{decimals}f}"

    def format_change(self, change: float, decimals: int = 2) -> str:
        """格式化涨跌幅，带颜色符号"""
        if change is None:
            return "N/A"
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.{decimals}f}%"

    def format_morning_briefing(self, data: Dict) -> str:
        """格式化早间推送消息"""
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        weekday = data.get("weekday", "")
        market_indices = data.get("market_indices", {})
        hot_sectors = data.get("hot_sectors", [])
        watchlist = data.get("watchlist", [])

        lines = []

        # 标题
        lines.append(f"🌅 早间推送 | {date} {weekday}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        # 市场概览
        lines.append("📊 【市场概览】")

        sh = market_indices.get("shanghai", {})
        sz = market_indices.get("shenzhen", {})
        cyb = market_indices.get("cyb", {})

        lines.append(f"上证指数: {self.format_number(sh.get('price'))} ({self.format_change(sh.get('change_pct'))})")
        lines.append(f"深证成指: {self.format_number(sz.get('price'))} ({self.format_change(sz.get('change_pct'))})")
        lines.append(f"创业板指: {self.format_number(cyb.get('price'))} ({self.format_change(cyb.get('change_pct'))})")
        lines.append("")

        # 隔夜美股（如果有的话）
        # lines.append(f"隔夜美股: 道指 {dow_change}% | 纳指 {nasdaq_change}%")
        # lines.append(f"A50期指: {a50_change}%")
        # lines.append("")

        # 热点板块
        if hot_sectors:
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("🔥 【热点板块】Top 5")
            lines.append("")

            for i, sector in enumerate(hot_sectors[:5], 1):
                name = sector.get("name", "")
                change_pct = sector.get("change_pct", 0)
                fund_flow = sector.get("fund_flow", 0)
                leading = sector.get("leading_stocks", [])

                lines.append(f"{i}. {name} {self.format_change(change_pct)} - 资金净流入 {self.format_number(fund_flow)}亿")
                if leading:
                    lines.append(f"   龙头: {', '.join(leading)}")
                lines.append("")

        # 自选信号
        if watchlist:
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("⭐ 【自选信号】")
            lines.append("")

            for item in watchlist[:5]:
                symbol = item.get("symbol", "")
                name = item.get("name", "")
                obs_levels = item.get("observation_levels", {})

                signal_text = f"• {symbol} {name}"

                if obs_levels:
                    upper = obs_levels.get("upper")
                    lower = obs_levels.get("lower")
                    if upper and lower:
                        signal_text += f" | 观察位: {upper}-{lower}"

                lines.append(signal_text)

            lines.append("")

        # 关注时间
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("📅 【今日关注】")
        lines.append("• 9:30 - 开盘关注")
        lines.append("• 10:30 - 盘中检查提醒")
        lines.append("• 13:30 - 午后复盘")
        lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("💡 提示: 本推送仅供参考，不构成投资建议")

        return "\n".join(lines)

    def format_intraday_check(self, data: Dict) -> str:
        """格式化盘中检查消息"""
        time = data.get("time", datetime.now().strftime("%H:%M"))
        alerts = data.get("price_alerts", [])
        watchlist_quotes = data.get("watchlist_quotes", [])

        lines = []

        # 标题
        lines.append(f"⏰ 盘中检查 | {time}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        # 价格提醒
        if alerts:
            lines.append("🎯 【价格提醒】")
            lines.append("")

            for alert in alerts:
                symbol = alert.get("symbol", "")
                name = alert.get("name", "")
                alert_type = alert.get("type", "")
                level = alert.get("level", 0)
                current = alert.get("current_price", 0)
                alert_time = alert.get("time", "")

                lines.append(f"⚠️ {symbol} {name}")
                lines.append(f"   {alert_type}: {self.format_number(level)}")
                lines.append(f"   当前价: {self.format_number(current)}")
                lines.append(f"   时间: {alert_time}")
                lines.append("")

        else:
            lines.append("🎯 【价格提醒】")
            lines.append("")
            lines.append("暂无价格异动")
            lines.append("")

        # 持仓快照
        if watchlist_quotes:
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("💰 【持仓快照】")
            lines.append("")

            for quote in watchlist_quotes[:5]:
                symbol = quote.get("symbol", "")
                name = quote.get("name", "")
                price = quote.get("price", 0)
                change_pct = quote.get("change_pct", 0)

                lines.append(f"{symbol} {name}: {self.format_number(price)} ({self.format_change(change_pct)})")

            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("⚠️  注意: 本提醒功能仅供参考，不做交易建议")

        # 如果没有重要提醒，返回 None 表示不需要发送
        if not alerts:
            return None

        return "\n".join(lines)

    def format_evening_summary(self, data: Dict) -> str:
        """格式化收盘总结消息"""
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        market_indices = data.get("market_indices", {})
        positions = data.get("positions", [])

        lines = []

        # 标题
        lines.append(f"🌙 收盘总结 | {date}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        # 今日大盘
        lines.append("📊 【今日大盘】")

        sh = market_indices.get("shanghai", {})
        sz = market_indices.get("shenzhen", {})

        lines.append(f"上证指数: {self.format_number(sh.get('price'))} ({self.format_change(sh.get('change_pct'))})")
        lines.append(f"深证成指: {self.format_number(sz.get('price'))} ({self.format_change(sz.get('change_pct'))})")
        lines.append("")

        # 北向资金（如果有）
        # lines.append(f"北向资金: {north_flow}亿 ({north_flow_change}%)")
        # lines.append("")

        # 持仓收益
        if positions:
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("💰 【持仓收益】")
            lines.append("")

            total_positions = len(positions)
            total_value = sum(p.get("market_value", 0) for p in positions)
            total_pnl = sum(p.get("pnl", 0) for p in positions)
            total_pnl_pct = (total_pnl / (total_value - total_pnl) * 100) if (total_value - total_pnl) > 0 else 0

            lines.append(f"总持仓: {total_positions}只")
            lines.append(f"当前市值: {self.format_number(total_value)}元")
            lines.append("")
            lines.append(f"今日盈亏: {self.format_number(total_pnl)}元 ({self.format_change(total_pnl_pct)})")
            lines.append("")

            # 最佳和最差表现
            if positions:
                best = max(positions, key=lambda x: x.get("pnl_pct", 0))
                worst = min(positions, key=lambda x: x.get("pnl_pct", 0))

                lines.append(f"【最佳表现】{best.get('symbol')} {best.get('name')} +{self.format_number(best.get('pnl_pct', 0))}%")
                lines.append(f"【最差表现】{worst.get('symbol')} {worst.get('name')} {self.format_change(worst.get('pnl_pct', 0))}%")
                lines.append("")

        # 明日关注
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("🔥 【明日关注】")
        lines.append("")
        lines.append("（根据今日表现生成明日关注列表）")
        lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("💡 提醒: 明日9:00继续推送早间简报")

        return "\n".join(lines)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Trading Assistant Message Formatter")
    parser.add_argument("--data", required=True, help="JSON data file or string")
    parser.add_argument("--type", required=True, choices=["morning", "intraday", "evening"],
                        help="Message type")

    args = parser.parse_args()

    formatter = MessageFormatter()

    # 加载数据
    try:
        data_path = Path(args.data)
        if data_path.exists():
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.loads(args.data)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 格式化消息
    if args.type == "morning":
        message = formatter.format_morning_briefing(data)
    elif args.type == "intraday":
        message = formatter.format_intraday_check(data)
    elif args.type == "evening":
        message = formatter.format_evening_summary(data)
    else:
        parser.print_help()
        return

    if message:
        print(message)
    else:
        print("No message to send (e.g., no alerts for intraday check)")


if __name__ == "__main__":
    main()
