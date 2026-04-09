---
name: news
version: 2.0.0
description: >
  个性化财经新闻简报生成器。基于用户持仓和偏好，聚合24小时内最重要、最热门、最相关的财经新闻。
  
  核心原则：
  - 最重要：重大政策、市场异动、持仓重大事件
  - 最热门：多源报道、高关注度话题  
  - 最相关：与用户持仓、偏好高度匹配
  
  执行流程：
  1. 读取用户配置 (config/portfolio.json, preferences.json)
  2. 并发抓取RSS (scripts/fetcher.py)
  3. 本地快速筛选 (scripts/filter.py)
  4. LLM深度分析
  5. 格式化输出 (scripts/formatter.py)

triggers:
  - 财经简报
  - 今日新闻
  - 添加持仓
  - 删除持仓
  - 查看持仓
  - 关注关键词

metadata:
  clawdbot:
    emoji: "📰"
---

# 个性化财经新闻简报 Skill v2.0

## 执行流程

### 步骤1: 读取用户配置

**持仓配置** (`config/portfolio.json`):
```json
{
  "NVDA": {
    "name": "英伟达",
    "type": "holding",
    "keywords": ["GPU", "AI芯片", "数据中心", "Blackwell"]
  },
  "00700.HK": {
    "name": "腾讯",
    "type": "holding",
    "keywords": ["游戏", "微信", "云服务", "AI"]
  }
}
```

**偏好配置** (`config/preferences.json`):
```json
{
  "keywords": ["AI", "新能源", "降息", "半导体"],
  "sectors": ["科技", "医药", "新能源"]
}
```

**RSS源配置** (`config/rss_sources.json`):
```json
{
  "macro": [
    {"name": "财新宏观", "url": "https://www.caixin.com/rss/macroeconomy.xml", "priority": "high"},
    {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss/global", "priority": "high"},
    {"name": "央行官网", "url": "http://www.pbc.gov.cn/rss/Focus.xml", "priority": "high"}
  ],
  "finance": [
    {"name": "财新金融", "url": "https://www.caixin.com/rss/finance.xml", "priority": "high"},
    {"name": "财新股市", "url": "https://www.caixin.com/rss/markets.xml", "priority": "high"},
    {"name": "FT中文网", "url": "https://www.ftchinese.com/rss/feed", "priority": "medium"},
    {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "priority": "medium"}
  ],
  "tech": [
    {"name": "财新TMT", "url": "https://www.caixin.com/rss/tech.xml", "priority": "high"}
  ],
  "energy": [
    {"name": "财新能源", "url": "https://www.caixin.com/rss/energy.xml", "priority": "medium"}
  ]
}
```

### 步骤2: 并发抓取RSS

执行命令:
```bash
cd ~/.openclaw/skills/news && python3 scripts/fetcher.py --config config/rss_sources.json --output /tmp/raw_news.json
```

**功能**:
- 使用 ThreadPoolExecutor 并发抓取所有RSS源
- 每源15秒超时
- 解析XML，提取标题、链接、摘要、发布时间
- 过滤24小时内的新闻
- 输出JSON到 `/tmp/raw_news.json`

### 步骤3: 本地快速筛选

执行命令:
```bash
cd ~/.openclaw/skills/news && python3 scripts/filter.py --input /tmp/raw_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/filtered_news.json
```

**筛选逻辑** (无需LLM，本地快速处理):

| 匹配类型 | 条件 | 分数 |
|---------|------|------|
| 持仓代码精确匹配 | 股票代码出现在标题/摘要 | 100 |
| 公司名称匹配 | 公司名出现在标题/摘要 | 90 |
| 业务关键词匹配 | 持仓定义的关键词匹配 | 80 |
| 用户偏好关键词 | 关注的关键词匹配 | 70 |
| 信源优先级 | high=+10, medium=+5 | - |
| 时效性 | <6h=+10, <12h=+5, <24h=+2 | - |

保留分数最高的15条进入下一步。

### 步骤4: LLM深度分析

执行命令:
```bash
cd ~/.openclaw/skills/news && python3 scripts/analyzer.py --input /tmp/filtered_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/analyzed_news.json
```

对筛选后的新闻进行批量语义分析，生成以下维度：

```json
{
  "news_id": "hash_of_url",
  "relevance_score": 8.5,
  "match_type": "holding_direct",
  "matched_holdings": ["NVDA"],
  "core_fact": "英伟达发布Blackwell架构GPU，性能提升2.5倍",
  "impact_analysis": "利好AI算力板块，云厂商采购成本下降",
  "impact_direction": "positive",
  "key_details": "Q2出货，已获亚马逊/谷歌/微软大单",
  "why_relevant": "用户持仓NVDA，直接受益于新产品周期"
}
```

**缓存策略**: 分析结果缓存24小时，避免重复分析。

### 步骤5: 格式化输出

执行命令:
```bash
cd ~/.openclaw/skills/news && python3 scripts/formatter.py --input /tmp/analyzed_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/briefing.md
```

**输出分类**:
1. **【我的持仓】** - 持仓直接相关 (relevance_score >= 8)
2. **【我的关注】** - 偏好匹配 (relevance_score 6-7)
3. **【市场警报】** - 重大异动、突发事件
4. **【宏观必读】** - 其他高分重要新闻

## 用户命令

### 生成简报
```
财经简报
今日新闻
```
执行完整流程生成个性化简报。

### 持仓管理
```
添加持仓 NVDA
添加持仓 00700.HK 腾讯
删除持仓 TSLA
查看持仓
```
修改 `config/portfolio.json`。

### 偏好设置
```
关注关键词 AI,新能源,降息
关注板块 科技,医药
```
修改 `config/preferences.json`。

## 输出格式

```
📰 财经新闻简报 | 2026-04-02 09:00

═══════════════════════════════════════════════════════
💼 【我的持仓】2条
═══════════════════════════════════════════════════════

🔸 英伟达发布新一代AI芯片 | NVDA +3.2%
【核心】Blackwell架构GPU性能提升2.5倍，已获亚马逊/谷歌/微软大单
【影响】利好 | 直接受益AI算力需求增长，竞争对手压力增大
【关联】你的持仓NVDA今日领涨，建议关注Q2出货量指引
[阅读原文](https://...)

🔸 腾讯Q1游戏收入超预期 | 00700.HK +1.8%
【核心】王者荣耀/和平精英流水创新高，海外游戏增长35%
【影响】利好 | 游戏业务复苏确认，AI应用加速
【关联】你的持仓腾讯今日跟随板块上涨
[阅读原文](https://...)

═══════════════════════════════════════════════════════
🎯 【我的关注】AI/新能源 2条
═══════════════════════════════════════════════════════

🔸 OpenAI发布GPT-5预览版
【核心】推理能力提升40%，API价格下降50%
【影响】AI应用层受益，算力需求持续增长
【关联】匹配你关注的AI关键词，利好你的NVDA持仓
[阅读原文](https://...)

🔸 国家发改委发布储能产业规划
【核心】2025年装机目标翻倍至30GW，补贴延续至2027年
【影响】储能产业链受益，光伏配储需求增加
【关联】匹配你关注的新能源关键词
[阅读原文](https://...)

═══════════════════════════════════════════════════════
⚠️ 【市场警报】1条
═══════════════════════════════════════════════════════

🔸 美股期货盘前大跌 | 纳指期货 -1.2%
【触发】美联储官员放鹰，暗示加息可能未结束
【影响】科技股承压，关注开盘表现
【建议】你的持仓NVDA/TSLA可能波动，关注止损位
[阅读原文](https://...)

═══════════════════════════════════════════════════════
🌍 【宏观必读】2条
═══════════════════════════════════════════════════════

🔸 央行开展1000亿MLF操作，利率维持2.5%不变
【解读】流动性合理充裕，降准降息预期降温
[阅读原文](https://...)

🔸 美联储3月FOMC会议纪要：多数支持年内降息3次
【解读】6月或首次降息，美元走弱利于新兴市场
[阅读原文](https://...)

═══════════════════════════════════════════════════════
📊 简报统计
持仓相关: 2条 | 关注匹配: 2条 | 市场警报: 1条 | 宏观必读: 2条
时间范围: 过去24小时 | 信源: 财新/FT/Bloomberg等8个
持仓: NVDA, 00700.HK (2只) | 关注: AI, 新能源, 降息
═══════════════════════════════════════════════════════
```

## 技术实现

### scripts/fetcher.py
```python
#!/usr/bin/env python3
"""RSS并发抓取器"""
import json
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

FETCH_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; NewsSkill/2.0)"

def fetch_feed(source):
    """抓取单个RSS源"""
    try:
        feed = feedparser.parse(source['url'], agent=USER_AGENT, timeout=FETCH_TIMEOUT)
        entries = []
        for entry in feed.entries:
            published = parse_date(entry.get('published', entry.get('updated')))
            if published and (datetime.now() - published) > timedelta(hours=24):
                continue
            entries.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'summary': clean_html(entry.get('summary', '')),
                'published': published.isoformat() if published else None,
                'source': source['name'],
                'source_priority': source.get('priority', 'medium')
            })
        return entries
    except Exception as e:
        print(f"Error fetching {source['name']}: {e}")
        return []

def fetch_all_feeds(config_path, output_path):
    with open(config_path) as f:
        config = json.load(f)
    
    all_sources = []
    for category, sources in config.items():
        all_sources.extend(sources)
    
    all_entries = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_feed, s): s for s in all_sources}
        for future in as_completed(futures):
            entries = future.result()
            all_entries.extend(entries)
    
    with open(output_path, 'w') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    
    print(f"Fetched {len(all_entries)} news items from {len(all_sources)} sources")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    fetch_all_feeds(args.config, args.output)
```

### scripts/filter.py
```python
#!/usr/bin/env python3
"""本地快速筛选器"""
import json
import re
from difflib import SequenceMatcher

def load_config(path):
    with open(path) as f:
        return json.load(f)

def calculate_score(news, portfolio, preferences):
    """计算新闻相关性分数"""
    text = f"{news['title']} {news['summary']}".lower()
    score = 0
    
    # 持仓代码匹配
    for symbol, info in portfolio.items():
        if symbol.lower() in text:
            score += 100
            break
        
        name = info.get('name', '').lower()
        if name and name in text:
            score += 90
            break
        
        for keyword in info.get('keywords', []):
            if keyword.lower() in text:
                score += 80
                break
    
    # 偏好关键词匹配
    for keyword in preferences.get('keywords', []):
        if keyword.lower() in text:
            score += 70
            break
    
    # 信源优先级
    priority_bonus = {'high': 10, 'medium': 5, 'low': 0}
    score += priority_bonus.get(news.get('source_priority', 'medium'), 0)
    
    return score

def filter_news(input_path, portfolio_path, preferences_path, output_path, top_n=15):
    with open(input_path) as f:
        news_list = json.load(f)
    
    portfolio = load_config(portfolio_path)
    preferences = load_config(preferences_path)
    
    # 计算分数
    for news in news_list:
        news['score'] = calculate_score(news, portfolio, preferences)
    
    # 排序并取top
    filtered = sorted(news_list, key=lambda x: x['score'], reverse=True)[:top_n]
    
    with open(output_path, 'w') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    
    print(f"Filtered to top {len(filtered)} news items")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--portfolio', required=True)
    parser.add_argument('--preferences', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    filter_news(args.input, args.portfolio, args.preferences, args.output)
```

### scripts/formatter.py
```python
#!/usr/bin/env python3
"""输出格式化器"""
import json
from datetime import datetime

def format_briefing(input_path, portfolio_path, output_path):
    with open(input_path) as f:
        analyzed_news = json.load(f)
    
    with open(portfolio_path) as f:
        portfolio = json.load(f)
    
    # 分类
    holdings_news = [n for n in analyzed_news if n.get('match_type') == 'holding_direct']
    preference_news = [n for n in analyzed_news if n.get('match_type') == 'preference']
    alerts = [n for n in analyzed_news if n.get('is_alert')]
    macro = [n for n in analyzed_news if n not in holdings_news + preference_news + alerts]
    
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
            if news.get('matched_holdings'):
                holdings_str = ', '.join(news['matched_holdings'])
                lines.append(f"【持仓】{holdings_str}")
            if news.get('core_fact'):
                lines.append(f"【核心】{news['core_fact']}")
            if news.get('impact_analysis'):
                direction = "利好" if news.get('impact_direction') == 'positive' else "利空" if news.get('impact_direction') == 'negative' else "中性"
                lines.append(f"【影响】{direction} | {news['impact_analysis']}")
            if news.get('why_relevant'):
                lines.append(f"【关联】{news['why_relevant']}")
            lines.append(f"[阅读原文]({news['link']})")
    
    # 其他分类类似...
    
    # 统计
    lines.append("\n═══════════════════════════════════════════════════════")
    lines.append(f"📊 简报统计")
    lines.append(f"持仓相关: {len(holdings_news)}条 | 关注匹配: {len(preference_news)}条 | 市场警报: {len(alerts)}条 | 宏观必读: {len(macro)}条")
    lines.append(f"持仓: {', '.join(portfolio.keys())} ({len(portfolio)}只)")
    lines.append("═══════════════════════════════════════════════════════")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Briefing saved to {output_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--portfolio', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    format_briefing(args.input, args.portfolio, args.output)
```

## 完整执行命令

当用户触发 "财经简报" 时，按顺序执行：

```bash
# 安装依赖
pip install feedparser -q

# Step 1: 抓取RSS
cd ~/.openclaw/skills/news && python3 scripts/fetcher.py --config config/rss_sources.json --output /tmp/raw_news.json

# Step 2: 本地筛选
cd ~/.openclaw/skills/news && python3 scripts/filter.py --input /tmp/raw_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/filtered_news.json

# Step 3: LLM分析
cd ~/.openclaw/skills/news && python3 scripts/analyzer.py --input /tmp/filtered_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/analyzed_news.json

# Step 4: 格式化输出
cd ~/.openclaw/skills/news && python3 scripts/formatter.py --input /tmp/analyzed_news.json --portfolio config/portfolio.json --preferences config/preferences.json --output /tmp/briefing.md

# Step 5: 显示结果
cat /tmp/briefing.md
```

## 首次使用配置

当用户首次使用 "财经简报" 时：

```
Agent: 📰 欢迎使用个性化财经新闻简报！

让我为你配置个性化设置：

💼 你有持仓的股票吗？（如：NVDA, 00700.HK）
     直接输入代码，或回复"跳过"

User: NVDA, TSLA, 00700.HK

Agent: 好的！已记录你的持仓。

🎯 你关注哪些领域？（如：AI, 新能源, 降息）
     输入关键词，用逗号分隔

User: AI, 新能源, 半导体

Agent: 配置完成！正在为你生成首份个性化简报...
```

配置文件自动创建在 `config/` 目录下。
