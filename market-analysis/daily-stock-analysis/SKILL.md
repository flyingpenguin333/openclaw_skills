---
name: daily-stock-analysis
description: LLM驱动的 A/H/美股智能分析器，每日自动分析并推送决策仪表盘。支持A股、港股、美股，多数据源行情 + 实时新闻 + AI决策建议 + 多渠道推送。比 stock-analysis 更全面，专注中国市场。
version: 1.0.0
homepage: https://github.com/ZhuLinsen/daily_stock_analysis
commands:
  - /analyze - 分析单只股票 (A股/港股/美股)
  - /analyze_batch - 批量分析自选股
  - /market_review - 大盘复盘
  - /stock_watchlist - 管理自选股列表
  - /stock_report - 查看分析报告
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python"],"env":["GEMINI_API_KEY|DEEPSEEK_API_KEY"]},"install":[]}}
---

# Daily Stock Analysis

LLM驱动的 A/H/美股智能分析器，每日自动分析并推送「决策仪表盘」

## 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| 🤖 AI | 决策仪表盘 | 一句话核心结论 + 精确买卖点位 + 操作检查清单 |
| 📊 分析 | 多维度分析 | 技术面 + 筹码分布 + 舆情情报 + 实时行情 |
| 🌍 市场 | 全球市场 | 支持 A股、港股、美股 |
| 📰 舆情 | 新闻搜索 | Tavily/SerpAPI/Brave 多源搜索 |
| 🔔 推送 | 多渠道通知 | 飞书、企业微信、Telegram、邮件 |
| ⏰ 自动化 | 定时运行 | 每日自动分析并推送 |

## 数据源

| 优先级 | 数据源 | 适用市场 |
|--------|--------|----------|
| P0 | 东方财富 (efinance) | A股 |
| P1 | AkShare | A股 |
| P2 | Tushare Pro | A股 |
| P4 | Yahoo Finance | 美股/港股 |

## 配置要求

**必需**（至少配置一个 AI API）：
```bash
# 方案一：Gemini（免费额度）
export GEMINI_API_KEY=your_key

# 方案二：DeepSeek（国内）
export DEEPSEEK_API_KEY=your_key
export DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

**可选**（新闻搜索）：
```bash
export BRAVE_API_KEYS=your_key      # Brave Search
export TAVILY_API_KEYS=your_key     # Tavily
export SERPAPI_API_KEYS=your_key    # SerpAPI
```

**通知渠道**（可选）：
```bash
export FEISHU_WEBHOOK_URL=xxx       # 飞书机器人
export WECHAT_WEBHOOK_URL=xxx       # 企业微信
export EMAIL_SENDER=xxx             # 邮件推送
```

## 使用方法

### 单股分析
```bash
# A股
/analyze 600519
/analyze 贵州茅台

# 港股
/analyze hk00700
/analyze 腾讯控股

# 美股
/analyze AAPL
/analyze TSLA
```

### 批量分析
```bash
# 分析自选股列表
/analyze_batch

# 分析指定股票
/analyze_batch 600519,300750,002594
```

### 大盘复盘
```bash
# A股大盘
/market_review cn

# 美股大盘
/market_review us

# 全部
/market_review both
```

### 管理自选股
```bash
# 查看当前列表
/stock_watchlist

# 添加股票
/stock_watchlist add 600519

# 移除股票
/stock_watchlist remove 600519
```

### 查看报告
```bash
# 查看最新分析报告
/stock_report

# 指定日期
/stock_report 2026-03-06
```

## 分析输出示例

```
🎯 2026-03-06 决策仪表盘
━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 贵州茅台 (600519) | 评分: 65 | 观望

📰 重要信息速览
💭 舆情情绪: 市场关注其业绩稳定性，情绪中性偏积极
📊 业绩预期: 2025年业绩稳健增长，基本面强劲

🚨 风险警报:
• 主力资金近5日净流出
• 估值处于历史较高水平

✨ 利好催化:
• 春节动销数据良好
• 高端白酒需求稳定

🎯 作战计划
• 理想买点: 1350-1380
• 止损位: 1300
• 目标位: 1450

✅ 操作检查清单:
□ 乖离率 < 5%
□ 多头排列确认
□ 量能配合
□ 大盘环境配合
```

## 技术栈

- **Python 3.10+**
- **数据源**: efinance, akshare, tushare, yfinance
- **AI**: LiteLLM (Gemini/Anthropic/OpenAI/DeepSeek)
- **搜索**: Tavily, SerpAPI, Brave
- **Web**: FastAPI + Uvicorn
- **数据库**: SQLite

## 免责声明

⚠️ **NOT FINANCIAL ADVICE.** 本项目仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
