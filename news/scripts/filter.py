#!/usr/bin/env python3
"""本地快速筛选器"""
import json
import sys


def load_config(path):
    """加载配置文件"""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config {path}: {e}", file=sys.stderr)
        return {}


def calculate_score(news, portfolio, preferences):
    """计算新闻相关性分数"""
    text = f"{news.get('title', '')} {news.get('summary', '')}".lower()
    score = 0
    match_reason = []
    
    # 持仓代码精确匹配 (最高优先级)
    for symbol, info in portfolio.items():
        if symbol.lower() in text:
            score += 100
            match_reason.append(f"持仓代码:{symbol}")
            break
        
        # 公司名称匹配
        name = info.get('name', '').lower()
        if name and name in text:
            score += 90
            match_reason.append(f"公司名称:{name}")
            break
        
        # 业务关键词匹配
        for keyword in info.get('keywords', []):
            if keyword.lower() in text:
                score += 80
                match_reason.append(f"业务关键词:{keyword}")
                break
    
    # 用户偏好关键词匹配
    for keyword in preferences.get('keywords', []):
        if keyword.lower() in text:
            score += 70
            match_reason.append(f"关注关键词:{keyword}")
            break
    
    # 信源优先级加分
    priority_bonus = {'high': 10, 'medium': 5, 'low': 0}
    score += priority_bonus.get(news.get('source_priority', 'medium'), 0)
    
    return score, match_reason


def filter_news(input_path, portfolio_path, preferences_path, output_path, top_n=15):
    """筛选新闻"""
    # 加载数据
    with open(input_path, encoding='utf-8') as f:
        news_list = json.load(f)
    
    portfolio = load_config(portfolio_path)
    preferences = load_config(preferences_path)
    
    print(f"Filtering {len(news_list)} news items...", file=sys.stderr)
    
    # 计算分数
    scored_news = []
    for news in news_list:
        score, reasons = calculate_score(news, portfolio, preferences)
        news['score'] = score
        news['match_reasons'] = reasons
        scored_news.append(news)
    
    # 按分数排序，取top
    scored_news.sort(key=lambda x: x['score'], reverse=True)
    filtered = scored_news[:top_n]
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    
    print(f"Filtered to top {len(filtered)} news items", file=sys.stderr)
    for i, news in enumerate(filtered[:5], 1):
        print(f"  {i}. [{news['score']}] {news['title'][:50]}...", file=sys.stderr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='News Filter')
    parser.add_argument('--input', required=True, help='Input JSON from fetcher')
    parser.add_argument('--portfolio', required=True, help='Path to portfolio.json')
    parser.add_argument('--preferences', required=True, help='Path to preferences.json')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--top-n', type=int, default=15, help='Number of top news to keep')
    args = parser.parse_args()
    
    filter_news(args.input, args.portfolio, args.preferences, args.output, args.top_n)
