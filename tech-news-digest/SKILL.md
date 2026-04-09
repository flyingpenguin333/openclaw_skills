---
name: tech-news-digest
description: >
  Multi-source tech news aggregation and digest generation.
  Automatically collect, score, and deliver tech news from 109+ sources 
  including RSS feeds, Twitter/X, GitHub releases, Reddit, and web search.
  
  Use cases:
  (1) Daily tech news briefing at scheduled time
  (2) On-demand news digest for specific topics
  (3) Trending topics monitoring in AI/tech
  (4) Custom source aggregation (add your own RSS/Twitter/GitHub)
  
  Triggers: "tech news", "news digest", "daily briefing", "科技新闻", "新闻汇总"
---

# Tech News Digest — 多源科技新闻聚合

## 🎯 功能概述

Tech News Digest 是一个四层数据管道，自动聚合、评分和投递科技新闻：

### 数据源 (109+)

| 类型 | 数量 | 示例 |
|------|------|------|
| **RSS Feeds** | 46 | OpenAI, Hacker News, MIT Tech Review |
| **Twitter/X KOLs** | 44 | @karpathy, @sama, @VitalikButerin |
| **GitHub Releases** | 19 | vLLM, LangChain, Ollama, Dify |
| **Web Search** | 4 topics | Brave Search API |

### 质量评分算法

```
总分 = 基础分 + 优先级加分 + 多源加分 + 时效加分 + 互动加分

- 优先级来源: +3 (如 OpenAI 官方博客)
- 多源报道: +5 (被多个渠道提及)
- 时效性: +2 (24小时内发布)
- 互动数据: +1 (点赞/转发数)
```

## 📁 项目结构

```
tech-news-digest/
├── digests/                    # 生成的摘要文件
│   └── 2026/
│       └── 03/
│           └── tech-digest-2026-03-09.md
├── sources.yaml               # 数据源配置
├── news_router.py             # 核心路由逻辑
├── filters/                   # 过滤规则
│   ├── keywords.txt          # 关键词过滤
│   └── blacklist.txt         # 黑名单
├── scoring/                   # 评分算法
│   └── algorithm.py
└── delivery/                  # 投递渠道
    ├── discord.py
    ├── telegram.py
    └── email.py
```

## 🚀 使用方法

### 方式 1: 使用现有实现

#### 方案 A: 简单版本 (Ethanyoyo0917)
```bash
# 直接查看已生成的摘要
curl https://raw.githubusercontent.com/Ethanyoyo0917/tech-news-digest/main/digests/2026/03/tech-digest-2026-03-09.md

# 订阅 RSS
https://github.com/Ethanyoyo0917/tech-news-digest/commits/main.atom
```

#### 方案 B: Docker 版本 (Salman-719/TechClaw)
```bash
# 克隆仓库
git clone https://github.com/Salman-719/TechClaw.git
cd TechClaw

# 配置环境
cp .env.example .env
# 编辑 .env 填入你的 API keys

# 构建并启动
docker compose up -d
```

### 方式 2: 自定义实现

```python
# 核心流程示例
from tech_news_digest import NewsAggregator

# 初始化
aggregator = NewsAggregator(
    rss_sources=load_rss_sources(),
    twitter_accounts=load_twitter_list(),
    github_repos=load_github_repos(),
    search_queries=["LLM", "AI Agent", "Frontier Tech"]
)

# 获取新闻
articles = aggregator.fetch_all()

# 去重 (基于标题相似度)
unique_articles = deduplicate_by_similarity(articles, threshold=0.85)

# 评分排序
scored_articles = score_articles(unique_articles)

# 生成摘要
digest = generate_digest(scored_articles, top_n=20)

# 投递
deliver_to_discord(digest)
deliver_to_telegram(digest)
```

## ⚙️ 配置说明

### sources.yaml

```yaml
rss:
  - name: "OpenAI Blog"
    url: https://openai.com/blog/rss.xml
    priority: high
    
  - name: "Hacker News"
    url: https://news.ycombinator.com/rss
    priority: high
    
  - name: "MIT Tech Review"
    url: https://www.technologyreview.com/feed/
    priority: medium

twitter:
  - handle: "@karpathy"
    category: "AI Research"
    
  - handle: "@sama"
    category: "Tech Industry"
    
  - handle: "@VitalikButerin"
    category: "Crypto"

github:
  - repo: "vllm-project/vllm"
    watch_releases: true
    
  - repo: "langchain-ai/langchain"
    watch_releases: true

search:
  queries:
    - "LLM breakthrough 2026"
    - "AI agent framework"
    - "frontier technology"
```

### 环境变量

```bash
# Twitter/X API
X_BEARER_TOKEN=your_twitter_api_token

# Brave Search
BRAVE_API_KEY=your_brave_api_key

# GitHub (提高 rate limit)
GITHUB_TOKEN=your_github_token

# 投递渠道
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🎓 学习要点

### 1. 多源数据聚合模式

```python
# 并行获取多个数据源
import asyncio

async def fetch_all_sources():
    tasks = [
        fetch_rss_feeds(),
        fetch_twitter_posts(),
        fetch_github_releases(),
        fetch_web_search()
    ]
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

### 2. 去重算法 (文本相似度)

```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate(articles, threshold=0.85):
    unique = []
    for article in articles:
        is_duplicate = any(
            similarity(article.title, existing.title) > threshold
            for existing in unique
        )
        if not is_duplicate:
            unique.append(article)
    return unique
```

### 3. 评分算法

```python
def score_article(article, sources_config):
    score = 0
    
    # 来源优先级
    source_priority = sources_config.get(article.source, {}).get('priority', 'low')
    score += {'high': 3, 'medium': 2, 'low': 1}.get(source_priority, 0)
    
    # 多源报道加分
    if article.mention_count > 1:
        score += min(article.mention_count * 2, 5)
    
    # 时效性
    hours_old = (now - article.published_at).total_seconds() / 3600
    if hours_old < 24:
        score += 2
    elif hours_old < 72:
        score += 1
    
    # 互动数据
    score += min(article.engagement_score, 3)
    
    return score
```

### 4. 定时调度 (Cron)

```yaml
# .openclaw/cron.yaml
cron:
  - name: "morning-tech-digest"
    schedule: "0 9 * * *"  # 每天上午9点
    message: "Generate and deliver tech news digest"
    skill: "tech-news-digest"
    
  - name: "evening-tech-digest"
    schedule: "0 21 * * *"  # 每天晚上9点
    message: "Generate evening tech digest"
    skill: "tech-news-digest"
```

## 🛡️ 安全考虑

1. **API Key 管理**: 使用环境变量，不要硬编码
2. **Rate Limiting**: 遵守各平台的 API 限制
3. **内容过滤**: 配置关键词黑名单，过滤不当内容
4. **数据来源验证**: 优先可信来源，标记未验证来源

## 📚 参考资源

| 资源 | 链接 | 说明 |
|------|------|------|
| 官方 Use Case | [multi-source-tech-news-digest](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/multi-source-tech-news-digest.md) | 完整实现指南 |
| 简单版本 | [Ethanyoyo0917/tech-news-digest](https://github.com/Ethanyoyo0917/tech-news-digest) | 每日自动生成 |
| Docker 版本 | [Salman-719/TechClaw](https://github.com/Salman-719/TechClaw) | Telegram 投递 |
| ClawHub | [tech-news-digest](https://clawhub.ai/skills/tech-news-digest) | 官方 skill |

## 🔧 扩展思路

1. **金融领域版本**: 替换科技源为金融源 (Bloomberg, WSJ, 财新)
2. **多语言支持**: 添加翻译层，支持中英双语
3. **AI 摘要**: 使用 LLM 生成更智能的摘要
4. **个性化推荐**: 基于用户阅读历史推荐
5. **情感分析**: 分析新闻情绪倾向

---

**学习建议**: 
1. 先运行简单版本，理解基本流程
2. 研究评分算法和去重逻辑
3. 尝试添加自定义数据源
4. 最后构建自己的版本
