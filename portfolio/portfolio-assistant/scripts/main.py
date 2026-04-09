"""
Portfolio Assistant - 简报生成器
整合多源数据生成个性化投资简报
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import DataManager
from feishu_handler import MessageFormatter
from typing import Dict, List, Any, Optional
from datetime import datetime


class BriefingGenerator:
    """简报生成器"""
    
    def __init__(self):
        self.dm = DataManager()
        self.formatter = MessageFormatter()
    
    def generate_briefing(self, briefing_type: str = "general") -> str:
        """生成简报
        
        Args:
            briefing_type: "morning"(盘前), "evening"(盘后), "general"(通用)
        """
        sections = []
        
        # 1. 头部信息
        time_label = "盘前" if briefing_type == "morning" else "盘后" if briefing_type == "evening" else "简报"
        sections.append(f"📊 {time_label}简报 {datetime.now().strftime('%Y年%m月%d日')}")
        sections.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 2. 大盘概览 (占位，需接入 market-environment-analysis)
        sections.append(self._generate_market_section())
        
        # 3. 持仓动态
        sections.append(self._generate_portfolio_section())
        
        # 4. 关键词监控
        sections.append(self._generate_keywords_section())
        
        # 5. 底部
        sections.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        sections.append("💡 提示: 回复「详细」查看完整数据")
        
        return "\n\n".join(sections)
    
    def _generate_market_section(self) -> str:
        """生成大盘概览部分"""
        # TODO: 接入 market-environment-analysis skill
        # 当前使用占位符
        return """📈 市场概览
━━━━━━━━━━━━━━━━━━
(需要配置 market-environment-analysis skill)
• 纳指: --
• 道指: --
• 标普: --
• VIX: --"""
    
    def _generate_portfolio_section(self) -> str:
        """生成持仓动态部分"""
        portfolios = self.dm.get_portfolios()
        
        if not portfolios:
            return "💼 持仓动态\n━━━━━━━━━━━━━━━━━━\n暂无持仓记录"
        
        lines = ["💼 持仓动态", "━━━━━━━━━━━━━━━━━━"]
        
        for pname, portfolio in portfolios.items():
            total_cost = portfolio.total_cost()
            lines.append(f"\n【{pname}】")
            lines.append(f"总成本: ${total_cost:,.2f}")
            
            for asset in portfolio.assets:
                # TODO: 接入实时行情API获取当前价格
                lines.append(f"• {asset.ticker}: {asset.quantity:,.0f}股 @ 成本${asset.avg_cost:.2f}")
        
        return "\n".join(lines)
    
    def _generate_keywords_section(self) -> str:
        """生成关键词监控部分"""
        keywords = self.dm.get_keywords()
        
        if not keywords:
            return "📡 监控雷达\n━━━━━━━━━━━━━━━━━━\n暂无监控关键词"
        
        lines = ["📡 监控雷达", "━━━━━━━━━━━━━━━━━━"]
        
        for kw_name, kw_data in keywords.items():
            lines.append(f"\n【{kw_name}】")
            lines.append(f"监控频率: {kw_data.frequency}")
            if kw_data.related_stocks:
                lines.append(f"关联股票: {', '.join(kw_data.related_stocks)}")
            # TODO: 接入新闻搜索API获取最新动态
            lines.append("(新闻搜索功能需配置API Key)")
        
        return "\n".join(lines)
    
    def generate_detailed_report(self) -> str:
        """生成详细报告"""
        # TODO: 详细版本，包含更多数据
        return self.generate_briefing("general")


class PortfolioAssistant:
    """Portfolio Assistant 主入口"""
    
    def __init__(self):
        self.dm = DataManager()
        self.parser = __import__('feishu_handler').MessageParser()
        self.formatter = MessageFormatter()
        self.briefing_gen = BriefingGenerator()
    
    def handle_message(self, message: str, webhook_url: str = "") -> str:
        """处理用户消息
        
        Args:
            message: 用户输入消息
            webhook_url: 飞书Webhook URL（可选）
        
        Returns:
            回复消息内容
        """
        # 解析指令
        cmd = self.parser.parse(message)
        
        # 执行对应操作
        if cmd.action == "buy":
            return self._handle_buy(cmd)
        elif cmd.action == "sell":
            return self._handle_sell(cmd)
        elif cmd.action == "watch":
            return self._handle_watch(cmd)
        elif cmd.action == "unwatch":
            return self._handle_unwatch(cmd)
        elif cmd.action == "portfolio":
            return self._handle_portfolio()
        elif cmd.action == "briefing":
            return self._handle_briefing()
        else:
            return self.formatter.format_help()
    
    def _handle_buy(self, cmd) -> str:
        """处理买入指令"""
        from data_manager import Asset
        
        asset = Asset(
            ticker=cmd.ticker,
            name=cmd.ticker,  # TODO: 查询股票名称
            quantity=cmd.quantity,
            avg_cost=cmd.price,
            currency="USD"
        )
        
        success = self.dm.add_asset(cmd.portfolio_name, asset)
        
        if success:
            return self.formatter.format_buy_confirmation(
                ticker=cmd.ticker,
                name=cmd.ticker,
                quantity=cmd.quantity,
                price=cmd.price,
                portfolio=cmd.portfolio_name,
                total_cost=cmd.quantity * cmd.price
            )
        else:
            return self.formatter.format_error("添加持仓失败")
    
    def _handle_sell(self, cmd) -> str:
        """处理卖出指令"""
        success = self.dm.remove_asset(cmd.portfolio_name, cmd.ticker, cmd.quantity)
        
        if success:
            return self.formatter.format_sell_confirmation(
                ticker=cmd.ticker,
                quantity=cmd.quantity,
                portfolio=cmd.portfolio_name
            )
        else:
            return self.formatter.format_error("未找到该持仓或卖出数量超过持仓")
    
    def _handle_watch(self, cmd) -> str:
        """处理添加监控关键词"""
        success = self.dm.add_keyword(cmd.keyword)
        
        if success:
            return self.formatter.format_watch_confirmation(
                keyword=cmd.keyword,
                related_stocks=[]
            )
        else:
            return self.formatter.format_error(f"关键词 '{cmd.keyword}' 已存在")
    
    def _handle_unwatch(self, cmd) -> str:
        """处理移除监控关键词"""
        success = self.dm.remove_keyword(cmd.keyword)
        
        if success:
            return self.formatter.format_unwatch_confirmation(cmd.keyword)
        else:
            return self.formatter.format_error(f"未找到关键词 '{cmd.keyword}'")
    
    def _handle_portfolio(self) -> str:
        """处理查看组合"""
        # 构建组合数据
        portfolios = self.dm.get_portfolios()
        keywords = self.dm.get_keyword_list()
        
        data = {
            "portfolios": {
                name: {
                    "assets": [
                        {
                            "ticker": a.ticker,
                            "quantity": a.quantity,
                            "avg_cost": a.avg_cost
                        }
                        for a in p.assets
                    ]
                }
                for name, p in portfolios.items()
            },
            "keywords": keywords
        }
        
        return self.formatter.format_portfolio_summary(data)
    
    def _handle_briefing(self) -> str:
        """处理生成简报"""
        return self.briefing_gen.generate_briefing()


# ========== 测试入口 ==========

if __name__ == "__main__":
    print("=== Portfolio Assistant 测试 ===\n")
    
    assistant = PortfolioAssistant()
    
    # 测试买入
    print("1. 测试买入:")
    response = assistant.handle_message("以 120 美元买入 1000 股 TSLA，记在科技股组合")
    print(response)
    print()
    
    # 测试添加关键词
    print("2. 测试添加关键词:")
    response = assistant.handle_message("关注 固态电池")
    print(response)
    print()
    
    # 测试查看组合
    print("3. 测试查看组合:")
    response = assistant.handle_message("查看我的资产雷达")
    print(response)
    print()
    
    # 测试生成简报
    print("4. 测试生成简报:")
    response = assistant.handle_message("生成简报")
    print(response)
    print()
    
    print("✅ 所有测试通过！")
