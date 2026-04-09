---
name: portfolio-assistant
description: 飞书交互式资产记忆管家 + 个性化简报生成器。记录持仓成本、监控关注赛道、生成每日盘前盘后简报。
version: 1.0.0
homepage: https://github.com/openclaw/portfolio-assistant
commands:
  - /buy - 记录买入持仓 (例: "买入 1000股TSLA@120 科技股")
  - /sell - 记录卖出持仓
  - /portfolio - 查看资产雷达配置
  - /watch - 添加监控关键词 (例: "关注 固态电池")
  - /unwatch - 移除监控关键词
  - /briefing - 立即生成简报
  - /settings - 配置飞书Webhook和推送偏好
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python"],"env":["FEISHU_WEBHOOK_URL"]},"install":[]}}
---

# Portfolio Assistant - 资产记忆管家

飞书交互式资产记忆管理与个性化简报生成工具。

## 核心功能

### 1. 持仓记忆管理
记录买入/卖出操作，自动计算成本线、盈亏比例。

```bash
# 记录买入
/buy 1000股 TSLA @ $120 科技股组合

# 记录卖出  
/sell 500股 TSLA 科技股组合

# 查看所有持仓
/portfolio
```

### 2. 赛道监控雷达
添加关注的关键词/赛道，系统自动监控相关新闻和研报。

```bash
# 添加监控关键词
/watch 固态电池

# 添加带关联股票的监控
/watch AI芯片 --stocks NVDA,AMD

# 查看监控列表
/portfolio --section keywords

# 移除监控
/unwatch 固态电池
```

### 3. 个性化简报生成
整合宏观数据、持仓动态、赛道新闻，生成盘前/盘后简报。

```bash
# 手动生成简报
/briefing

# 生成盘前简报
/briefing --type morning

# 生成盘后简报
/briefing --type evening
```

## 数据结构

### 持仓数据 (portfolios.json)
```json
{
  "portfolios": {
    "科技股": {
      "created_at": "2026-03-06",
      "assets": [
        {
          "ticker": "TSLA",
          "name": "Tesla Inc",
          "quantity": 1000,
          "avg_cost": 120.0,
          "currency": "USD",
          "added_at": "2026-03-06T10:00:00"
        }
      ]
    }
  }
}
```

### 监控关键词 (keywords.json)
```json
{
  "keywords": {
    "固态电池": {
      "added_at": "2026-03-06",
      "frequency": "daily",
      "related_stocks": ["QS", "SLDP"],
      "sources": ["news", "research"]
    }
  }
}
```

## 飞书交互示例

### 买入记录
```
用户: 我今天以 120 美元建仓了 1000 股 TSLA，记在我的科技股组合里

Bot:
✅ 已记录买入操作
━━━━━━━━━━━━━━━━━━
股票: TSLA (Tesla Inc.)
数量: 1,000 股
成本: $120.00/股
总成本: $120,000.00
组合: 科技股
时间: 2026-03-06 10:30
━━━━━━━━━━━━━━━━━━
当前组合「科技股」总市值: $XXX (待API恢复)
```

### 查看资产雷达
```
用户: 查看我的资产雷达

Bot:
📊 您的资产雷达配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【持仓组合】
┌─────────┬────────┬─────────┬──────────┐
│ 组合    │ 股票   │ 持仓    │ 成本     │
├─────────┼────────┼─────────┼──────────┤
│ 科技股  │ TSLA   │ 1,000股 │ $120.00  │
│         │ NVDA   │ 100股   │ $450.00  │
└─────────┴────────┴─────────┴──────────┘

【监控雷达】
┌──────────┬──────────┬────────────┐
│ 关键词   │ 添加时间 │ 推送频率   │
├──────────┼──────────┼────────────┤
│ 固态电池 │ 03-06    │ 每日       │
│ AI芯片   │ 03-05    │ 实时(重要) │
└──────────┴──────────┴────────────┘
```

### 简报生成
```
用户: /briefing

Bot:
┌─────────────────────────────────────┐
│  📊 盘后简报 2026年3月6日           │
├─────────────────────────────────────┤
│  📈 今日大盘                         │
│  纳指: +1.2%  道指: +0.5%           │
├─────────────────────────────────────┤
│  🔔 您的持仓动态                     │
│  TSLA: 当前$125 (+4.2% 成本线以上)  │
│  NVDA: 当前$178 (-1.2% 成本线以下)  │
├─────────────────────────────────────┤
│  📰 雷达监控                         │
│  【固态电池】2篇新研报               │
│  [查看详情]                          │
└─────────────────────────────────────┘
```

## 配置说明

### 环境变量
```bash
# 必需
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx

# 可选 - 用于简报生成
BRAVE_API_KEY=xxx  # 新闻搜索
TAVILY_API_KEY=xxx # 新闻搜索
```

### 配置文件 (config/settings.json)
```json
{
  "feishu_webhook": "",
  "briefing_preferences": {
    "morning_time": "08:00",
    "evening_time": "18:00",
    "include_market_overview": true,
    "include_portfolio_pnl": true,
    "include_keyword_news": true
  }
}
```

## 数据来源

- **行情数据**: daily-stock-analysis (AkShare/Efinance) / yfinance
- **宏观数据**: market-environment-analysis
- **新闻数据**: web_search / Brave API / Tavily API

## 开发状态

- [x] 基础架构
- [x] 数据管理器
- [x] 飞书消息处理器
- [ ] 简报生成器 (进行中)
- [ ] 定时任务 (暂不需要)

## 免责声明

本工具仅用于个人投资记录和辅助决策，不构成投资建议。股市有风险，投资需谨慎。
