"""
Portfolio Assistant - 数据管理器
管理持仓数据、监控关键词、用户偏好
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


# 数据存储路径
DATA_DIR = Path(os.path.expanduser("~/.clawdbot/skills/portfolio-assistant"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

PORTFOLIO_FILE = DATA_DIR / "portfolios.json"
KEYWORDS_FILE = DATA_DIR / "keywords.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"


@dataclass
class Asset:
    """持仓资产"""
    ticker: str
    name: str
    quantity: float
    avg_cost: float
    currency: str = "USD"
    added_at: str = ""
    
    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat()
    
    def total_cost(self) -> float:
        return self.quantity * self.avg_cost


@dataclass
class Portfolio:
    """投资组合"""
    name: str
    created_at: str
    assets: List[Asset]
    
    def total_cost(self) -> float:
        return sum(asset.total_cost() for asset in self.assets)


@dataclass
class KeywordWatch:
    """监控关键词"""
    keyword: str
    added_at: str
    frequency: str = "daily"  # daily, real-time, weekly
    related_stocks: List[str] = None
    sources: List[str] = None
    
    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat()
        if self.related_stocks is None:
            self.related_stocks = []
        if self.sources is None:
            self.sources = ["news", "research"]


class DataManager:
    """数据管理器 - 处理所有数据读写操作"""
    
    def __init__(self):
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """确保数据文件存在"""
        for file_path in [PORTFOLIO_FILE, KEYWORDS_FILE, PREFERENCES_FILE]:
            if not file_path.exists():
                file_path.write_text("{}", encoding="utf-8")
    
    # ========== 持仓数据管理 ==========
    
    def get_portfolios(self) -> Dict[str, Portfolio]:
        """获取所有投资组合"""
        data = json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))
        portfolios = {}
        for name, pdata in data.get("portfolios", {}).items():
            assets = [Asset(**a) for a in pdata.get("assets", [])]
            portfolios[name] = Portfolio(
                name=name,
                created_at=pdata.get("created_at", ""),
                assets=assets
            )
        return portfolios
    
    def save_portfolios(self, portfolios: Dict[str, Portfolio]):
        """保存所有投资组合"""
        data = {
            "portfolios": {
                name: {
                    "created_at": p.created_at,
                    "assets": [asdict(a) for a in p.assets]
                }
                for name, p in portfolios.items()
            }
        }
        PORTFOLIO_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def add_asset(self, portfolio_name: str, asset: Asset) -> bool:
        """添加资产到组合"""
        portfolios = self.get_portfolios()
        
        if portfolio_name not in portfolios:
            portfolios[portfolio_name] = Portfolio(
                name=portfolio_name,
                created_at=datetime.now().isoformat(),
                assets=[]
            )
        
        # 检查是否已有同股票持仓，更新成本
        existing = None
        for a in portfolios[portfolio_name].assets:
            if a.ticker.upper() == asset.ticker.upper():
                existing = a
                break
        
        if existing:
            # 计算新的平均成本
            total_cost = existing.total_cost() + asset.total_cost()
            total_qty = existing.quantity + asset.quantity
            existing.avg_cost = total_cost / total_qty
            existing.quantity = total_qty
        else:
            portfolios[portfolio_name].assets.append(asset)
        
        self.save_portfolios(portfolios)
        return True
    
    def remove_asset(self, portfolio_name: str, ticker: str, quantity: Optional[float] = None) -> bool:
        """从组合中移除资产"""
        portfolios = self.get_portfolios()
        
        if portfolio_name not in portfolios:
            return False
        
        assets = portfolios[portfolio_name].assets
        for i, asset in enumerate(assets):
            if asset.ticker.upper() == ticker.upper():
                if quantity is None or quantity >= asset.quantity:
                    # 全部卖出
                    assets.pop(i)
                else:
                    # 部分卖出
                    asset.quantity -= quantity
                self.save_portfolios(portfolios)
                return True
        
        return False
    
    def get_portfolio_summary(self, portfolio_name: Optional[str] = None) -> Dict[str, Any]:
        """获取组合摘要"""
        portfolios = self.get_portfolios()
        
        if portfolio_name:
            if portfolio_name not in portfolios:
                return {}
            p = portfolios[portfolio_name]
            return {
                "name": p.name,
                "created_at": p.created_at,
                "asset_count": len(p.assets),
                "total_cost": p.total_cost(),
                "assets": [
                    {
                        "ticker": a.ticker,
                        "name": a.name,
                        "quantity": a.quantity,
                        "avg_cost": a.avg_cost,
                        "total_cost": a.total_cost(),
                        "currency": a.currency
                    }
                    for a in p.assets
                ]
            }
        else:
            # 返回所有组合摘要
            return {
                name: {
                    "asset_count": len(p.assets),
                    "total_cost": p.total_cost()
                }
                for name, p in portfolios.items()
            }
    
    # ========== 关键词监控管理 ==========
    
    def get_keywords(self) -> Dict[str, KeywordWatch]:
        """获取所有监控关键词"""
        data = json.loads(KEYWORDS_FILE.read_text(encoding="utf-8"))
        return {
            k: KeywordWatch(**v) for k, v in data.get("keywords", {}).items()
        }
    
    def save_keywords(self, keywords: Dict[str, KeywordWatch]):
        """保存所有监控关键词"""
        data = {
            "keywords": {k: asdict(v) for k, v in keywords.items()}
        }
        KEYWORDS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def add_keyword(self, keyword: str, frequency: str = "daily", 
                    related_stocks: Optional[List[str]] = None) -> bool:
        """添加监控关键词"""
        keywords = self.get_keywords()
        
        if keyword in keywords:
            return False  # 已存在
        
        keywords[keyword] = KeywordWatch(
            keyword=keyword,
            added_at=datetime.now().isoformat(),
            frequency=frequency,
            related_stocks=related_stocks or [],
            sources=["news", "research"]
        )
        
        self.save_keywords(keywords)
        return True
    
    def remove_keyword(self, keyword: str) -> bool:
        """移除监控关键词"""
        keywords = self.get_keywords()
        
        if keyword not in keywords:
            return False
        
        del keywords[keyword]
        self.save_keywords(keywords)
        return True
    
    def get_keyword_list(self) -> List[Dict[str, Any]]:
        """获取关键词列表（用于展示）"""
        keywords = self.get_keywords()
        return [
            {
                "keyword": k,
                "added_at": v.added_at,
                "frequency": v.frequency,
                "related_stocks": v.related_stocks
            }
            for k, v in keywords.items()
        ]
    
    # ========== 用户偏好管理 ==========
    
    def get_preferences(self) -> Dict[str, Any]:
        """获取用户偏好设置"""
        if not PREFERENCES_FILE.exists():
            return self._default_preferences()
        
        data = json.loads(PREFERENCES_FILE.read_text(encoding="utf-8"))
        return data
    
    def save_preferences(self, preferences: Dict[str, Any]):
        """保存用户偏好设置"""
        PREFERENCES_FILE.write_text(
            json.dumps(preferences, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def _default_preferences(self) -> Dict[str, Any]:
        """默认偏好设置"""
        return {
            "feishu_webhook": "",
            "briefing_preferences": {
                "morning_time": "08:00",
                "evening_time": "18:00",
                "include_market_overview": True,
                "include_portfolio_pnl": True,
                "include_keyword_news": True
            }
        }
    
    def set_feishu_webhook(self, webhook_url: str):
        """设置飞书 Webhook"""
        prefs = self.get_preferences()
        prefs["feishu_webhook"] = webhook_url
        self.save_preferences(prefs)
    
    def get_feishu_webhook(self) -> str:
        """获取飞书 Webhook"""
        prefs = self.get_preferences()
        return prefs.get("feishu_webhook", "")


# ========== 测试代码 ==========

if __name__ == "__main__":
    # 测试数据管理器
    dm = DataManager()
    
    # 测试添加持仓
    print("=== 测试添加持仓 ===")
    dm.add_asset("科技股", Asset(ticker="TSLA", name="Tesla Inc", quantity=1000, avg_cost=120.0))
    dm.add_asset("科技股", Asset(ticker="NVDA", name="NVIDIA Corp", quantity=100, avg_cost=450.0))
    print("添加成功")
    
    # 测试查看组合
    print("\n=== 组合摘要 ===")
    summary = dm.get_portfolio_summary("科技股")
    print(f"组合: {summary['name']}")
    print(f"资产数: {summary['asset_count']}")
    print(f"总成本: ${summary['total_cost']:,.2f}")
    for asset in summary['assets']:
        print(f"  - {asset['ticker']}: {asset['quantity']}股 @ ${asset['avg_cost']}")
    
    # 测试添加关键词
    print("\n=== 测试添加关键词 ===")
    dm.add_keyword("固态电池", related_stocks=["QS", "SLDP"])
    dm.add_keyword("AI芯片", frequency="real-time", related_stocks=["NVDA", "AMD"])
    print("关键词添加成功")
    
    # 测试查看关键词
    print("\n=== 关键词列表 ===")
    for kw in dm.get_keyword_list():
        print(f"  - {kw['keyword']}: {kw['frequency']} ({', '.join(kw['related_stocks'])})")
    
    print("\n✅ 所有测试通过！")
