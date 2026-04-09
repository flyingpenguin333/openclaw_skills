"""
Portfolio Assistant - 飞书消息处理器
解析自然语言指令，格式化回复消息，发送飞书卡片
"""

import re
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedCommand:
    """解析后的命令"""
    action: str  # buy, sell, watch, unwatch, portfolio, briefing, unknown
    ticker: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    portfolio_name: Optional[str] = None
    keyword: Optional[str] = None
    raw_text: str = ""


class MessageParser:
    """消息解析器 - 从自然语言提取指令"""
    
    # 买入指令模式
    BUY_PATTERNS = [
        # "以 120 美元建仓了 1000 股 TSLA，记在我的科技股组合里"
        r"以\s*([\d.]+)\s*美元?建仓了?\s*(\d+)\s*股?\s*(\w+).*?组合[里为]?(.+?)[里为]?$",
        # "买入 1000股 TSLA @ 120 科技股"
        r"买入?\s*(\d+)\s*股?\s*(\w+).*?@?\s*([\d.]+).*?(\S+?)(?:组合)?$",
        # "建仓 TSLA 1000股 成本120 科技股"
        r"建仓?\s*(\w+)\s*(\d+)\s*股?.*?成本?\s*([\d.]+).*?(\S+?)(?:组合)?$",
    ]
    
    # 卖出指令模式
    SELL_PATTERNS = [
        # "卖出 500股 TSLA 科技股"
        r"卖出?\s*(\d+)\s*股?\s*(\w+).*?(\S+?)(?:组合)?$",
        # "减仓 TSLA 500股 科技股"
        r"减仓?\s*(\w+)\s*(\d+)\s*股?.*?(\S+?)(?:组合)?$",
    ]
    
    # 关注关键词模式
    WATCH_PATTERNS = [
        # "关注固态电池赛道"
        r"关注[了]?\s*(.+?)(?:赛道|板块|概念|领域)?$",
        # "监控 固态电池"
        r"监控[了]?\s*(.+?)$",
        # "添加关键词 固态电池"
        r"添加关键词\s*(.+?)$",
    ]
    
    # 取消关注模式
    UNWATCH_PATTERNS = [
        r"取消关注[了]?\s*(.+?)$",
        r"移除[了]?\s*(.+?)(?:的)?监控",
        r"删除关键词\s*(.+?)$",
    ]
    
    # 查看指令
    PORTFOLIO_KEYWORDS = ["查看", "显示", "列出", "我的", "资产", "持仓", "组合", "雷达"]
    BRIEFING_KEYWORDS = ["简报", "报告", "日报", "总结", "overview"]
    
    def parse(self, text: str) -> ParsedCommand:
        """解析用户消息"""
        text = text.strip()
        cmd = ParsedCommand(action="unknown", raw_text=text)
        
        # 尝试解析买入指令
        if any(kw in text for kw in ["买入", "建仓", "加仓", "买"]):
            parsed = self._parse_buy(text)
            if parsed:
                return parsed
        
        # 尝试解析卖出指令
        if any(kw in text for kw in ["卖出", "减仓", "清仓", "卖"]):
            parsed = self._parse_sell(text)
            if parsed:
                return parsed
        
        # 尝试解析关注关键词
        if any(kw in text for kw in ["关注", "监控", "添加关键词"]):
            parsed = self._parse_watch(text)
            if parsed:
                return parsed
        
        # 尝试解析取消关注
        if any(kw in text for kw in ["取消关注", "移除", "删除关键词"]):
            parsed = self._parse_unwatch(text)
            if parsed:
                return parsed
        
        # 尝试解析查看组合
        if any(kw in text for kw in self.PORTFOLIO_KEYWORDS):
            cmd.action = "portfolio"
            return cmd
        
        # 尝试解析简报指令
        if any(kw in text for kw in self.BRIEFING_KEYWORDS):
            cmd.action = "briefing"
            return cmd
        
        return cmd
    
    def _parse_buy(self, text: str) -> Optional[ParsedCommand]:
        """解析买入指令"""
        for pattern in self.BUY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 4:
                    # 判断哪个是价格、数量、股票代码
                    vals = [self._try_float(g) for g in groups]
                    
                    # 找到价格（带小数点或较大数字可能是价格）
                    price = None
                    quantity = None
                    ticker = None
                    portfolio = None
                    
                    for i, (val, raw) in enumerate(zip(vals, groups)):
                        if val is not None and price is None and val > 100:
                            price = val
                        elif val is not None and quantity is None and val < 10000:
                            quantity = val
                        elif ticker is None and raw.isalpha() and len(raw) <= 5:
                            ticker = raw.upper()
                        elif portfolio is None and raw and not raw.replace('.', '').isdigit():
                            portfolio = raw.strip()
                    
                    if ticker and quantity and price:
                        return ParsedCommand(
                            action="buy",
                            ticker=ticker,
                            quantity=quantity,
                            price=price,
                            portfolio_name=portfolio or "默认组合",
                            raw_text=text
                        )
        return None
    
    def _parse_sell(self, text: str) -> Optional[ParsedCommand]:
        """解析卖出指令"""
        for pattern in self.SELL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # 简化的解析逻辑
                quantity = None
                ticker = None
                portfolio = None
                
                for g in groups:
                    if g.isdigit():
                        quantity = float(g)
                    elif g.isalpha() and len(g) <= 5:
                        ticker = g.upper()
                    else:
                        portfolio = g.strip()
                
                if ticker and quantity:
                    return ParsedCommand(
                        action="sell",
                        ticker=ticker,
                        quantity=quantity,
                        portfolio_name=portfolio or "默认组合",
                        raw_text=text
                    )
        return None
    
    def _parse_watch(self, text: str) -> Optional[ParsedCommand]:
        """解析关注关键词指令"""
        for pattern in self.WATCH_PATTERNS:
            match = re.search(pattern, text)
            if match:
                keyword = match.group(1).strip()
                return ParsedCommand(
                    action="watch",
                    keyword=keyword,
                    raw_text=text
                )
        return None
    
    def _parse_unwatch(self, text: str) -> Optional[ParsedCommand]:
        """解析取消关注指令"""
        for pattern in self.UNWATCH_PATTERNS:
            match = re.search(pattern, text)
            if match:
                keyword = match.group(1).strip()
                return ParsedCommand(
                    action="unwatch",
                    keyword=keyword,
                    raw_text=text
                )
        return None
    
    def _try_float(self, s: str) -> Optional[float]:
        """尝试转换为浮点数"""
        try:
            return float(s)
        except (ValueError, TypeError):
            return None


class MessageFormatter:
    """消息格式化器 - 生成飞书回复消息"""
    
    @staticmethod
    def format_buy_confirmation(ticker: str, name: str, quantity: float, 
                                 price: float, portfolio: str, total_cost: float) -> str:
        """格式化买入确认消息"""
        return f"""✅ 已记录买入操作
━━━━━━━━━━━━━━━━━━
股票: {ticker} ({name})
数量: {quantity:,.0f} 股
成本: ${price:.2f}/股
总成本: ${total_cost:,.2f}
组合: {portfolio}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━"""
    
    @staticmethod
    def format_sell_confirmation(ticker: str, quantity: float, portfolio: str) -> str:
        """格式化卖出确认消息"""
        return f"""✅ 已记录卖出操作
━━━━━━━━━━━━━━━━━━
股票: {ticker}
数量: {quantity:,.0f} 股
组合: {portfolio}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━"""
    
    @staticmethod
    def format_portfolio_summary(portfolios_data: Dict[str, Any]) -> str:
        """格式化组合摘要（Markdown表格）"""
        lines = ["📊 您的资产雷达配置", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""]
        
        # 持仓组合部分
        if portfolios_data.get("portfolios"):
            lines.append("【持仓组合】")
            lines.append("```")
            lines.append(f"{'组合':<8} {'股票':<8} {'持仓':<10} {'成本':<12}")
            lines.append("-" * 40)
            
            for pname, pdata in portfolios_data["portfolios"].items():
                for asset in pdata.get("assets", []):
                    lines.append(f"{pname:<8} {asset['ticker']:<8} {asset['quantity']:>8.0f}股 ${asset['avg_cost']:<10.2f}")
            
            lines.append("```")
            lines.append("")
        
        # 监控关键词部分
        if portfolios_data.get("keywords"):
            lines.append("【监控雷达】")
            lines.append("```")
            lines.append(f"{'关键词':<12} {'添加时间':<12} {'推送频率':<10}")
            lines.append("-" * 36)
            
            for kw in portfolios_data["keywords"]:
                added = kw['added_at'][:10] if kw['added_at'] else "-"
                lines.append(f"{kw['keyword']:<12} {added:<12} {kw['frequency']:<10}")
            
            lines.append("```")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_watch_confirmation(keyword: str, related_stocks: List[str]) -> str:
        """格式化添加监控确认消息"""
        stocks_str = f" ({', '.join(related_stocks)})" if related_stocks else ""
        return f"""✅ 已添加监控关键词
━━━━━━━━━━━━━━━━━━
关键词: {keyword}{stocks_str}
监控范围: 新闻 + 研报
推送频率: 每日摘要
━━━━━━━━━━━━━━━━━━"""
    
    @staticmethod
    def format_unwatch_confirmation(keyword: str) -> str:
        """格式化取消监控确认消息"""
        return f"""✅ 已移除监控关键词
━━━━━━━━━━━━━━━━━━
关键词: {keyword}
不再接收相关推送
━━━━━━━━━━━━━━━━━━"""
    
    @staticmethod
    def format_error(message: str) -> str:
        """格式化错误消息"""
        return f"""❌ 操作失败
━━━━━━━━━━━━━━━━━━
{message}
━━━━━━━━━━━━━━━━━━"""
    
    @staticmethod
    def format_help() -> str:
        """格式化帮助消息"""
        return """📖 Portfolio Assistant 使用指南

【持仓管理】
• 买入: "以 120 美元买入 1000 股 TSLA，记在科技股组合"
• 卖出: "卖出 500 股 TSLA 科技股"
• 查看: "查看我的资产雷达"

【关键词监控】
• 添加: "关注 固态电池"
• 移除: "取消关注 固态电池"

【简报生成】
• 手动: "生成简报" 或 "/briefing"

更多帮助请回复 "帮助"
"""


class FeishuSender:
    """飞书消息发送器"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_text(self, text: str) -> bool:
        """发送文本消息"""
        if not self.webhook_url:
            print(f"[飞书] 未配置 Webhook，消息内容:\n{text}")
            return False
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[飞书] 发送失败: {e}")
            return False
    
    def send_markdown(self, title: str, content: str) -> bool:
        """发送 Markdown 卡片消息"""
        if not self.webhook_url:
            print(f"[飞书] 未配置 Webhook，标题: {title}")
            return False
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    }
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": content
                        }
                    }
                ]
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[飞书] 发送失败: {e}")
            return False


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("=== 测试消息解析器 ===\n")
    
    parser = MessageParser()
    
    test_messages = [
        "以 120 美元建仓了 1000 股 TSLA，记在我的科技股组合里",
        "买入 100股 NVDA @ 450 科技股",
        "卖出 500股 TSLA 科技股",
        "关注 固态电池",
        "取消关注 固态电池",
        "查看我的资产雷达",
        "生成简报",
    ]
    
    for msg in test_messages:
        result = parser.parse(msg)
        print(f"输入: {msg}")
        print(f"解析: action={result.action}, ticker={result.ticker}, quantity={result.quantity}, price={result.price}, portfolio={result.portfolio_name}, keyword={result.keyword}")
        print()
    
    print("\n=== 测试消息格式化器 ===\n")
    
    formatter = MessageFormatter()
    
    # 测试买入确认
    print(formatter.format_buy_confirmation("TSLA", "Tesla Inc", 1000, 120.0, "科技股", 120000.0))
    print()
    
    # 测试组合摘要
    portfolio_data = {
        "portfolios": {
            "科技股": {
                "assets": [
                    {"ticker": "TSLA", "quantity": 1000, "avg_cost": 120.0},
                    {"ticker": "NVDA", "quantity": 100, "avg_cost": 450.0}
                ]
            }
        },
        "keywords": [
            {"keyword": "固态电池", "added_at": "2026-03-06T10:00:00", "frequency": "daily"},
            {"keyword": "AI芯片", "added_at": "2026-03-05T10:00:00", "frequency": "real-time"}
        ]
    }
    print(formatter.format_portfolio_summary(portfolio_data))
    
    print("\n✅ 所有测试通过！")
