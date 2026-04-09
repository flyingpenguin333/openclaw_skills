#!/usr/bin/env python3
"""LLM深度分析器"""
import json
import sys
import os
from datetime import datetime


def load_json(path):
    """加载JSON文件"""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        return {}


def analyze_with_llm(news_batch, portfolio, preferences):
    """
    使用LLM批量分析新闻
    实际实现时通过调用外部LLM API
    这里提供分析框架
    """
    analyzed = []
    
    for news in news_batch:
        # 基础信息保留
        analyzed_news = news.copy()
        
        # 分析匹配类型
        score = news.get('score', 0)
        reasons = news.get('match_reasons', [])
        
        if score >= 80 or any('持仓代码' in r for r in reasons):
            analyzed_news['match_type'] = 'holding_direct'
            analyzed_news['matched_holdings'] = [
                r.replace('持仓代码:', '') for r in reasons if '持仓代码' in r
            ]
        elif score >= 60:
            analyzed_news['match_type'] = 'preference'
        else:
            analyzed_news['match_type'] = 'general'
        
        # 影响方向判断 (基于关键词)
        title_lower = news.get('title', '').lower()
        summary_lower = news.get('summary', '').lower()
        text = title_lower + summary_lower
        
        positive_words = ['上涨', '增长', '利好', '突破', '创新', '强劲', '超预期', '盈利']
        negative_words = ['下跌', '下滑', '利空', '亏损', '裁员', '调查', '违约', '暴雷']
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            analyzed_news['impact_direction'] = 'positive'
        elif neg_count > pos_count:
            analyzed_news['impact_direction'] = 'negative'
        else:
            analyzed_news['impact_direction'] = 'neutral'
        
        analyzed.append(analyzed_news)
    
    return analyzed


def analyze_news(input_path, portfolio_path, preferences_path, output_path):
    """分析新闻"""
    # 加载数据
    filtered_news = load_json(input_path)
    portfolio = load_json(portfolio_path)
    preferences = load_json(preferences_path)
    
    print(f"Analyzing {len(filtered_news)} news items...", file=sys.stderr)
    
    # LLM分析 (当前使用规则分析，可替换为真实LLM调用)
    analyzed = analyze_with_llm(filtered_news, portfolio, preferences)
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    
    print(f"Analysis complete. Results saved to {output_path}", file=sys.stderr)
    
    # 打印分析摘要
    holdings_count = sum(1 for n in analyzed if n.get('match_type') == 'holding_direct')
    pref_count = sum(1 for n in analyzed if n.get('match_type') == 'preference')
    print(f"  - 持仓直接相关: {holdings_count}条", file=sys.stderr)
    print(f"  - 偏好匹配: {pref_count}条", file=sys.stderr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='News Analyzer')
    parser.add_argument('--input', required=True, help='Input filtered news JSON')
    parser.add_argument('--portfolio', required=True, help='Path to portfolio.json')
    parser.add_argument('--preferences', required=True, help='Path to preferences.json')
    parser.add_argument('--output', required=True, help='Output analyzed JSON')
    args = parser.parse_args()
    
    analyze_news(args.input, args.portfolio, args.preferences, args.output)
