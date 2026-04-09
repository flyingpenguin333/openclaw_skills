#!/usr/bin/env python3
"""RSS并发抓取器"""
import json
import feedparser
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from urllib.parse import urlparse

FETCH_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; NewsSkill/2.0)"


def parse_date(date_str):
    """解析RSS日期"""
    if not date_str:
        return None
    
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S GMT',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None


def clean_html(text):
    """清理HTML标签"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:500]  # 限制长度


def fetch_feed(source):
    """抓取单个RSS源"""
    try:
        import socket
        socket.setdefaulttimeout(FETCH_TIMEOUT)
        feed = feedparser.parse(source['url'], agent=USER_AGENT)
        entries = []
        
        for entry in feed.entries:
            published = parse_date(entry.get('published', entry.get('updated')))
            
            # 过滤24小时外的新闻
            if published and (datetime.now() - published) > timedelta(hours=24):
                continue
            
            entries.append({
                'title': clean_html(entry.get('title', '')),
                'link': entry.get('link', ''),
                'summary': clean_html(entry.get('summary', '')),
                'published': published.isoformat() if published else None,
                'source': source['name'],
                'source_priority': source.get('priority', 'medium')
            })
        
        return entries
    except Exception as e:
        print(f"Error fetching {source.get('name', 'unknown')}: {e}", file=sys.stderr)
        return []


def fetch_all_feeds(config_path, output_path):
    """并发抓取所有RSS源"""
    with open(config_path, encoding='utf-8') as f:
        config = json.load(f)
    
    # 收集所有源
    all_sources = []
    for category, sources in config.items():
        all_sources.extend(sources)
    
    print(f"Fetching from {len(all_sources)} RSS sources...", file=sys.stderr)
    
    # 并发抓取
    all_entries = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_feed, s): s for s in all_sources}
        for future in as_completed(futures):
            entries = future.result()
            all_entries.extend(entries)
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    
    print(f"Fetched {len(all_entries)} news items", file=sys.stderr)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RSS News Fetcher')
    parser.add_argument('--config', required=True, help='Path to rss_sources.json')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()
    
    fetch_all_feeds(args.config, args.output)
