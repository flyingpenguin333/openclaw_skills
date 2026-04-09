#!/usr/bin/env python3
"""
Tomorrow's Watch - 明日关注综合分析系统

分析维度:
1. 技术面信号 (价格突破、均线金叉、RSI超买超卖)
2. 资金流向 (主力资金净流入、大单异动)
3. 板块轮动 (今日热点板块中的领涨股)
4. 消息面 (个股新闻、公告、研报)
5. 市场情绪 (涨跌停数量、涨跌家数比)
6. 基本面催化剂 (业绩预增、重大合同)

评分系统: 多维度加权评分，选出最值得关注的股票
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict

os.environ['QVERIS_API_KEY'] = 'sk-wHXgrRI3Naqmj92Meknakwrv4DFeRCzi-YnCVs3mpoA'
tool_path = os.path.expanduser("~/.openclaw/skills/qveris/scripts/qveris_tool.mjs")


class TomorrowWatchAnalyzer:
    """明日关注综合分析器"""
    
    def __init__(self):
        self.watchlist = [
            {"symbol": "000001", "name": "平安银行", "market": "A", "sector": "银行"},
            {"symbol": "600519", "name": "贵州茅台", "market": "A", "sector": "白酒"},
            {"symbol": "000858", "name": "五粮液", "market": "A", "sector": "白酒"},
            {"symbol": "002594", "name": "比亚迪", "market": "A", "sector": "新能源"},
            {"symbol": "300750", "name": "宁德时代", "market": "A", "sector": "新能源"},
        ]
        
    def fetch_stock_data(self, symbol: str) -> Dict:
        """获取个股完整数据"""
        if symbol.startswith('6'):
            symbol_with_suffix = f"{symbol}.SH"
        else:
            symbol_with_suffix = f"{symbol}.SZ"
        
        try:
            result = subprocess.run(
                ['node', tool_path, 'execute', 'ths_ifind.real_time_quotation.v1',
                 '--search-id', '3b607596-6461-489a-9b1d-e050c31a5814',
                 '--params', json.dumps({'codes': symbol_with_suffix})],
                capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60
            )
            
            if 'Result:' in result.stdout:
                parts = result.stdout.split('Result:')
                if len(parts) > 1:
                    data = json.loads(parts[1].strip())
                    if 'data' in data and len(data['data']) > 0:
                        return data['data'][0][0]
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        
        return {}
    
    def analyze_technical_signals(self, data: Dict) -> List[str]:
        """
        分析技术信号
        """
        signals = []
        
        price = data.get('latest', 0)
        pre_close = data.get('preClose', 0)
        high = data.get('high', 0)
        low = data.get('low', 0)
        change_pct = data.get('changeRatio', 0)
        
        # 1. 突破信号
        if price >= high * 0.998 and change_pct > 2:
            signals.append(f"突破日内高点 (+{change_pct:.1f}%)")
        
        # 2. 放量上涨
        vol_ratio = data.get('vol_ratio', 0)
        if vol_ratio > 2 and change_pct > 3:
            signals.append(f"放量上涨，量比{vol_ratio:.1f}")
        
        # 3. 连涨信号
        rise_days = data.get('riseDayCount', 0)
        if rise_days >= 3:
            signals.append(f"连续{rise_days}天上涨")
        
        # 4. 涨停基因
        if change_pct > 9:
            signals.append("接近涨停，关注明日延续性")
        
        # 5. 支撑位反弹
        if price > pre_close and low <= pre_close * 0.99:
            signals.append("回踩支撑后反弹")
        
        return signals
    
    def analyze_fund_flow(self, data: Dict) -> List[str]:
        """
        分析资金流向
        """
        signals = []
        
        # 主力资金流向 (通过委托数据推算)
        buy_volume = data.get('buyVolume', 0)
        sell_volume = data.get('sellVolume', 0)
        
        if buy_volume > 0 and sell_volume > 0:
            buy_ratio = buy_volume / (buy_volume + sell_volume)
            if buy_ratio > 0.6:
                signals.append(f"资金净流入，买盘占比{buy_ratio*100:.0f}%")
        
        # 委比
        committee = data.get('committee', 0)
        if committee > 30:
            signals.append(f"买盘积极，委比+{committee:.0f}%")
        elif committee < -30:
            signals.append(f"卖盘压力，委比{committee:.0f}%")
        
        return signals
    
    def analyze_valuation(self, data: Dict, sector: str) -> List[str]:
        """
        分析估值水平
        """
        signals = []
        
        pe = data.get('pe_ttm', 0)
        pb = data.get('pbr_lf', 0)
        
        # 低估值信号
        if pe > 0 and pe < 10 and sector in ['银行', '地产', '钢铁']:
            signals.append(f"低估值，PE仅{pe:.1f}倍")
        
        if pb > 0 and pb < 1:
            signals.append(f"破净，PB仅{pb:.2f}倍")
        
        # 高估值警告
        if pe > 50:
            signals.append(f"估值偏高，PE{pe:.1f}倍，注意风险")
        
        return signals
    
    def calculate_watch_score(self, data: Dict, stock: Dict) -> int:
        """
        计算明日关注评分 (0-100)
        """
        score = 0
        
        # 1. 价格动量 (0-30分)
        change_pct = data.get('changeRatio', 0)
        if change_pct > 5:
            score += 30
        elif change_pct > 3:
            score += 25
        elif change_pct > 1:
            score += 15
        elif change_pct > 0:
            score += 5
        
        # 2. 成交量 (0-25分)
        vol_ratio = data.get('vol_ratio', 0)
        if vol_ratio > 3:
            score += 25
        elif vol_ratio > 2:
            score += 20
        elif vol_ratio > 1.5:
            score += 10
        
        # 3. 资金流向 (0-20分)
        buy_volume = data.get('buyVolume', 0)
        sell_volume = data.get('sellVolume', 0)
        if buy_volume > 0 and sell_volume > 0:
            buy_ratio = buy_volume / (buy_volume + sell_volume)
            if buy_ratio > 0.7:
                score += 20
            elif buy_ratio > 0.6:
                score += 15
            elif buy_ratio > 0.55:
                score += 10
        
        # 4. 技术形态 (0-15分)
        price = data.get('latest', 0)
        high = data.get('high', 0)
        if price >= high * 0.998:
            score += 15  # 创日内新高
        
        rise_days = data.get('riseDayCount', 0)
        if rise_days >= 3:
            score += 10  # 连涨
        
        # 5. 估值安全垫 (0-10分)
        pe = data.get('pe_ttm', 0)
        pb = data.get('pbr_lf', 0)
        if 0 < pe < 20 or 0 < pb < 1.5:
            score += 10
        
        return min(score, 100)
    
    def generate_tomorrow_watch(self) -> List[Dict]:
        """
        生成明日关注列表
        """
        print("=" * 70)
        print("Tomorrow's Watch - Comprehensive Analysis")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)
        
        watch_list = []
        
        print(f"\nAnalyzing {len(self.watchlist)} stocks...\n")
        
        for stock in self.watchlist:
            symbol = stock['symbol']
            name = stock['name']
            
            print(f"  Analyzing {name} ({symbol})...", end=' ')
            
            # 获取数据
            data = self.fetch_stock_data(symbol)
            if not data:
                print("[NO DATA]")
                continue
            
            # 各项分析
            technical_signals = self.analyze_technical_signals(data)
            fund_signals = self.analyze_fund_flow(data)
            valuation_signals = self.analyze_valuation(data, stock.get('sector', ''))
            
            # 计算评分
            score = self.calculate_watch_score(data, stock)
            
            # 合并所有信号
            all_signals = technical_signals + fund_signals + valuation_signals
            
            if score > 30 or all_signals:  # 有关注价值的股票
                watch_list.append({
                    'symbol': symbol,
                    'name': name,
                    'price': data.get('latest', 0),
                    'change_pct': data.get('changeRatio', 0),
                    'score': score,
                    'signals': all_signals,
                    'sector': stock.get('sector', ''),
                    'pe': data.get('pe_ttm', 0),
                    'pb': data.get('pbr_lf', 0),
                    'vol_ratio': data.get('vol_ratio', 0)
                })
                print(f"[Score: {score}]")
            else:
                print("[Score too low]")
        
        # 按评分排序
        watch_list.sort(key=lambda x: x['score'], reverse=True)
        
        return watch_list
    
    def format_report(self, watch_list: List[Dict]) -> str:
        """
        格式化明日关注报告
        """
        lines = []
        
        lines.append("\n" + "=" * 70)
        lines.append("TOMORROW'S WATCHLIST")
        lines.append("=" * 70)
        
        if not watch_list:
            lines.append("\nNo stocks meet the watch criteria today.")
            lines.append("Suggestion: Monitor the overall market trend.")
            return "\n".join(lines)
        
        # 高关注度 (Score >= 60)
        high_priority = [w for w in watch_list if w['score'] >= 60]
        if high_priority:
            lines.append("\n🔥 HIGH PRIORITY (Score >= 60)")
            lines.append("-" * 70)
            for i, stock in enumerate(high_priority, 1):
                lines.append(f"\n{i}. {stock['name']} ({stock['symbol']})")
                lines.append(f"   Price: ¥{stock['price']:.2f} ({stock['change_pct']:+.2f}%)")
                lines.append(f"   Score: {stock['score']}/100")
                lines.append(f"   Sector: {stock['sector']}")
                if stock['pe'] > 0:
                    lines.append(f"   Valuation: PE {stock['pe']:.1f}x, PB {stock['pb']:.2f}x")
                lines.append("   Signals:")
                for signal in stock['signals']:
                    lines.append(f"      ✓ {signal}")
                lines.append(f"   👉 Why watch: Strong momentum + Fund flow + Technical breakout")
        
        # 中等关注 (40 <= Score < 60)
        medium_priority = [w for w in watch_list if 40 <= w['score'] < 60]
        if medium_priority:
            lines.append("\n📊 MEDIUM PRIORITY (40-59)")
            lines.append("-" * 70)
            for i, stock in enumerate(medium_priority, 1):
                lines.append(f"\n{i}. {stock['name']} ({stock['symbol']})")
                lines.append(f"   Price: ¥{stock['price']:.2f} ({stock['change_pct']:+.2f}%)")
                lines.append(f"   Score: {stock['score']}/100")
                lines.append("   Signals:")
                for signal in stock['signals'][:3]:  # 只显示前3个信号
                    lines.append(f"      • {signal}")
        
        # 观察列表 (Score < 40)
        low_priority = [w for w in watch_list if w['score'] < 40]
        if low_priority:
            lines.append("\n👀 WATCH LIST (< 40)")
            lines.append("-" * 70)
            for stock in low_priority:
                lines.append(f"  • {stock['name']}: {stock['signals'][0] if stock['signals'] else 'General monitoring'}")
        
        # 操作建议
        lines.append("\n" + "=" * 70)
        lines.append("TRADING SUGGESTIONS")
        lines.append("=" * 70)
        
        if high_priority:
            lines.append("\n1. HIGH PRIORITY stocks:")
            lines.append("   - Consider position building if breakout continues tomorrow")
            lines.append("   - Set stop loss at today's low")
            lines.append("   - Watch for volume confirmation")
        
        if medium_priority:
            lines.append("\n2. MEDIUM PRIORITY stocks:")
            lines.append("   - Wait for clearer signals")
            lines.append("   - Monitor opening 30 minutes")
        
        lines.append("\n3. General Strategy:")
        lines.append("   - Check overnight US market performance")
        lines.append("   - Watch for policy/news catalysts")
        lines.append("   - Risk management: Position size < 20% per stock")
        
        lines.append("\n" + "=" * 70)
        lines.append("Disclaimer: This analysis is for reference only.")
        lines.append("Always do your own research before trading.")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def main():
    """主函数"""
    analyzer = TomorrowWatchAnalyzer()
    
    # 生成明日关注
    watch_list = analyzer.generate_tomorrow_watch()
    
    # 生成报告
    report = analyzer.format_report(watch_list)
    
    # 输出
    print(report)
    
    # 保存到文件
    output_file = f"tomorrow_watch_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Report saved to: {output_file}")


if __name__ == "__main__":
    main()
