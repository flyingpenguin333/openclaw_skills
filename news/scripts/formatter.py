#!/usr/bin/env python3
"""输出格式化器"""
import json
import sys
from datetime import datetime


def load_json(path):
    """加载JSON文件"""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        return {}


def format_briefing(input_path, portfolio_path, preferences_path, output_path):
    """格式化简报"""
    # 加载数据
    analyzed_news = load_json(input_path)
    portfolio = load_json(portfolio_path)
    preferences = load_json(preferences_path)
    
    # 分类新闻
    holdings_news = []
    preference_news = []
    alerts = []
    macro = []
    
    for news in analyzed_news:
        score = news.get('score', 0)
        reasons = news.get('match_reasons', [])
        
        # 持仓相关 (分数>=80 或有持仓代码匹配)
        if score >= 80 or any('持仓代码' in r for r in reasons):
            holdings_news.append(news)
        # 偏好匹配 (分数60-79)
        elif score >= 60:
            preference_news.append(news)
        # 高分新闻作为宏观必读
        elif score >= 40:
            macro.append(news)
    
    lines = []
    lines.append(f"📰 财经新闻简报 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    # 持仓相关
    if holdings_news:
        lines.append("═══════════════════════════════════════════════════════")
        lines.append(f"💼 【我的持仓】{len(holdings_news)}条")
        lines.append("═══════════════════════════════════════════════════════")
        
        for news in holdings_news:
            lines.append(f"\n🔸 {news['title']}")
            
            # 匹配持仓
            matched = [r.replace('持仓代码:', '').replace('公司名称:', '') 
                      for r in news.get('match_reasons', []) 
                      if '持仓' in r or '公司' in r]
            if matched:
                lines.append(f"【持仓】{', '.join(matched[:3])}")
            
            # 摘要
            summary = news.get('summary', '')
            if summary:
                lines.append(f"【摘要】{summary[:150]}...")
            
            # 来源和时间
            source = news.get('source', '未知')
            lines.append(f"【来源】{source}")
            
            # 链接
            lines.append(f"[阅读原文]({news['link']})")
    
    # 偏好匹配
    if preference_news:
        lines.append("\n═══════════════════════════════════════════════════════")
        lines.append(f"🎯 【我的关注】{len(preference_news)}条")
        lines.append("═══════════════════════════════════════════════════════")
        
        for news in preference_news:
            lines.append(f"\n🔸 {news['title']}")
            
            # 匹配原因
            matched = [r.replace('关注关键词:', '') for r in news.get('match_reasons', []) if '关注' in r]
            if matched:
                lines.append(f"【匹配】{', '.join(matched[:3])}")
            
            summary = news.get('summary', '')
            if summary:
                lines.append(f"【摘要】{summary[:120]}...")
            
            lines.append(f"【来源】{news.get('source', '未知')}")
            lines.append(f"[阅读原文]({news['link']})")
    
    # 宏观必读
    if macro:
        lines.append("\n═══════════════════════════════════════════════════════")
        lines.append(f"🌍 【宏观必读】{len(macro)}条")
        lines.append("═══════════════════════════════════════════════════════")
        
        for news in macro[:5]:  # 最多显示5条
            lines.append(f"\n🔸 {news['title']}")
            summary = news.get('summary', '')
            if summary:
                lines.append(f"【摘要】{summary[:100]}...")
            lines.append(f"【来源】{news.get('source', '未知')}")
            lines.append(f"[阅读原文]({news['link']})")
    
    # 统计
    lines.append("\n═══════════════════════════════════════════════════════")
    lines.append("📊 简报统计")
    lines.append(f"持仓相关: {len(holdings_news)}条 | 关注匹配: {len(preference_news)}条 | 宏观必读: {len(macro)}条")
    
    if portfolio:
        lines.append(f"持仓: {', '.join(portfolio.keys())} ({len(portfolio)}只)")
    
    if preferences.get('keywords'):
        lines.append(f"关注: {', '.join(preferences['keywords'][:5])}")
    
    lines.append("═══════════════════════════════════════════════════════")
    
    # 保存输出
    output = '\n'.join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    # 同时打印到stdout (处理编码)
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print(output)
    
    print(f"\nBriefing saved to {output_path}", file=sys.stderr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='News Formatter')
    parser.add_argument('--input', required=True, help='Input analyzed news JSON')
    parser.add_argument('--portfolio', required=True, help='Path to portfolio.json')
    parser.add_argument('--preferences', required=True, help='Path to preferences.json')
    parser.add_argument('--output', required=True, help='Output markdown file path')
    args = parser.parse_args()
    
    format_briefing(args.input, args.portfolio, args.preferences, args.output)
