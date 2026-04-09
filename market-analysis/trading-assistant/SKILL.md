---
name: trading-assistant
description: >
  Chinese A-share trading assistant with automated daily monitoring and notifications.
  Provides three scheduled daily updates: 9:00 morning briefing (market overview & signals),
  10:30/13:30 intraday checks (price alerts & watchlist monitoring), and 15:30 evening summary
  (position performance & tomorrow's watch). Features complete position tracking with real-time
  P&L calculation, custom rule engine for complex trading signals, and multi-source data integration.

  Triggers: "交易助手", "市场简报", "自选股", "持仓", "盘中提醒", "收盘总结"
metadata:
  clawdbot:
    requires:
      env: ["QVERIS_API_KEY"]
    primaryEnv: "QVERIS_API_KEY"
    files: ["scripts/*"]
env:
  - QVERIS_API_KEY
requirements:
  env_vars:
    - QVERIS_API_KEY
credentials:
  primary: QVERIS_API_KEY
  scope: read-only
  endpoint: https://qveris.ai/api/v1
auto_invoke: false
---

# Trading Assistant — A股交易助手

## 功能概述

交易助手是一个7×24小时运行的AI交易监控助手，自动化日常交易监控和信息推送：

### 三大核心功能

| 时间 | 功能 | 说明 |
|------|------|------|
| **9:00** | 早间推送 | 市场热点板块 + 自选股信号 |
| **10:30 / 13:30** | 盘中检查 | 价格提醒 + 异动监控 |
| **15:30** | 收盘总结 | 持仓盈亏 + 明日关注 |

### 数据架构

```
trading-assistant/
├── SKILL.md                    # 技能定义（本文件）
├── config.json                 # 用户配置（自选股、规则、持仓）
├── data_source.json            # 数据源配置
├── rules.json                  # 自定义交易规则
├── database/
│   ├── positions.db            # 持仓数据库
│   ├── transactions.db         # 交易记录
│   └── alerts.db               # 提醒历史
└── scripts/
    ├── data_fetcher.py         # 数据获取模块
    ├── rule_engine.py          # 规则引擎
    └── message_formatter.py    # 消息格式化
```

## 配置说明

### config.json - 用户配置

```json
{
  "version": "1.0.0",
  "updated_at": "2026-03-09T14:30:00",
  "watchlist": [
    {
      "id": "watch_001",
      "symbol": "000001",
      "name": "平安银行",
      "market": "A股",
      "sector": "银行",
      "exchange": "SZ",
      "added_at": "2026-03-01T10:00:00",
      "observation_levels": {
        "upper": 12.50,
        "lower": 10.50,
        "stop_loss": 9.80,
        "take_profit": 15.00
      },
      "position": {
        "quantity": 1000,
        "cost_price": 11.00,
        "total_cost": 11000.00
      },
      "notes": "长期持有，关注政策动向",
      "tags": ["银行", "价值股", "高股息"]
    }
  ],
  "notification_settings": {
    "morning_briefing": {
      "enabled": true,
      "include_sector_overview": true,
      "include_watchlist_signals": true,
      "max_items": 10
    },
    "intraday_check": {
      "enabled": true,
      "alert_on_price_break": true,
      "alert_on_volume_spike": true,
      "max_alerts_per_check": 5
    },
    "evening_summary": {
      "enabled": true,
      "include_pnl_summary": true,
      "include_tomorrow_watch": true
    }
  }
}
```

### rules.json - 交易规则配置

```json
{
  "rules": [
    {
      "id": "rule_001",
      "name": "突破前高",
      "description": "价格突破20日新高",
      "condition": "price > max_high_20days * 1.02",
      "action": "alert",
      "priority": "high",
      "enabled": true
    },
    {
      "id": "rule_002",
      "name": "放量突破",
      "description": "价格上涨且成交量超过5日均量1.5倍",
      "condition": "price_change > 0.02 AND volume > avg_volume_5days * 1.5",
      "action": "alert",
      "priority": "high",
      "enabled": true
    },
    {
      "id": "rule_003",
      "name": "跌破支撑",
      "description": "价格跌破关键支撑位",
      "condition": "price < support_level * 0.98",
      "action": "alert",
      "priority": "high",
      "enabled": true
    }
  ]
}
```

### data_source.json - 数据源配置

```json
{
  "primary": {
    "name": "CustomDataSource",
    "enabled": true,
    "api_base": "https://your-api.com",
    "api_key_env": "CUSTOM_DATA_API_KEY",
    "endpoints": {
      "quote": "/v1/quote",
      "sectors": "/v1/sectors",
      "index": "/v1/index"
    }
  },
  "fallback": {
    "name": "QVeris",
    "enabled": true
  },
  "cache": {
    "ttl_minutes": 5,
    "enabled": true
  }
}
```

## 使用方法

### 1. 首次配置

编辑 `config.json`，添加你的自选股：

```json
{
  "watchlist": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "sector": "银行",
      "observation_levels": {
        "upper": 12.50,
        "lower": 10.50
      }
    }
  ]
}
```

### 2. 配置定时任务

在 `cron/jobs.json` 中添加以下任务：

```json
{
  "id": "trading-morning-briefing",
  "name": "交易助手早间推送",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1-5",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行交易助手早间推送任务"
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "ou_410de92c81cdcad793f09f006ac4e5c3"
  }
}
```

### 3. 手动测试

```bash
# 测试数据获取
cd skills/trading-assistant/scripts
python data_fetcher.py --test

# 测试早间推送
python data_fetcher.py --morning-briefing

# 测试盘中检查
python data_fetcher.py --intraday-check

# 测试收盘总结
python data_fetcher.py --evening-summary
```

## 消息模板

### 早间推送 (9:00)

```
🌅 早间推送 | {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 【市场概览】
上证指数: {sh_index} ({sh_change}%)
深证成指: {sz_index} ({sz_change}%)
创业板指: {cyb_index} ({cyb_change}%)

隔夜美股: 道指 {dow_change}% | 纳指 {nasdaq_change}%
A50期指: {a50_change}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 【热点板块】Top 5
1. {sector1} +{change1}% - 资金净流入 {flow1}亿
   龙头: {leader1}

2. {sector2} +{change2}% - 资金净流入 {flow2}亿
   龙头: {leader2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ 【自选信号】
{watchlist_signals}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示: 本推送仅供参考，不构成投资建议
```

### 盘中检查 (10:30/13:30)

```
⏰ 盘中检查 | {time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 【价格提醒】
{price_alerts}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 【异动监控】
{unusual_movements}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  注意: 本提醒功能仅供参考，不做交易建议
```

### 收盘总结 (15:30)

```
🌙 收盘总结 | {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 【今日大盘】
上证指数: {sh_close} ({sh_change_pct}%)
深证成指: {sz_close} ({sz_change_pct}%)
成交额: {total_amount}亿

北向资金: {north_flow}亿

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 【持仓收益】
总持仓: {total_positions}只
当前市值: {total_value}元

今日盈亏: {daily_pnl}元 ({daily_pnl_pct}%)
累计盈亏: {total_pnl}元 ({total_pnl_pct}%)

【最佳表现】{best_stock}
【最差表现】{worst_stock}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 【明日关注】
{tomorrow_watch}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提醒: 明日9:00继续推送早间简报
```

## 数据获取

### QVeris API 集成

使用 QVeris 技能搜索和调用以下工具：

```bash
# 搜索A股实时行情工具
node scripts/qveris_tool.mjs search "China A-share real-time stock quote"

# 搜索板块数据工具
node scripts/qveris_tool.mjs search "China stock sector industry hot ranking"

# 搜索指数数据工具
node scripts/qveris_tool.mjs search "Shanghai Shenzhen stock market index"
```

### 数据获取流程

```python
# 1. 优先使用专业数据源 API
data = fetch_from_primary_api()

# 2. 失败则使用 QVeris
if not data:
    data = fetch_from_qveris()

# 3. 再失败则使用缓存
if not data:
    data = get_from_cache()

# 4. 更新缓存
if data:
    update_cache(data)
```

## 数据库结构

### positions.db - 持仓数据库

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT,
    quantity INTEGER DEFAULT 0,
    cost_price REAL DEFAULT 0,
    current_price REAL DEFAULT 0,
    market_value REAL DEFAULT 0,
    pnl REAL DEFAULT 0,
    pnl_pct REAL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW position_summary AS
SELECT
    COUNT(*) as total_positions,
    SUM(market_value) as total_value,
    SUM(pnl) as total_pnl
FROM positions WHERE quantity > 0;
```

### transactions.db - 交易记录

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,  -- 'buy' or 'sell'
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    amount REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
```

### alerts.db - 提醒记录

```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    rule_id TEXT,
    rule_name TEXT,
    condition TEXT,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT 0,
    acknowledged_at TIMESTAMP
);

CREATE INDEX idx_alerts_symbol ON alerts(symbol);
CREATE INDEX idx_alerts_triggered_at ON alerts(triggered_at);
```

## 交互命令

### 添加自选股

```
添加自选 000001 平安银行 银行
设置观察位 000001 上破 12.50 下破 10.50
```

### 更新持仓

```
买入 000001 500股@11.50
卖出 000001 200股@12.00
```

### 查询信息

```
查看持仓
查看自选列表
查看今日盈亏
```

## 安全考虑

1. **API Key 管理**: 使用环境变量，不要硬编码
2. **数据验证**: 验证所有外部数据
3. **错误处理**: API 失败时的降级策略
4. **市场休市检测**: 避免在休市时间发送无效通知

## 扩展思路

1. **技术指标**: 添加 MA、MACD、RSI 等技术指标分析
2. **图表生成**: 生成 K 线图、资金流向图
3. **策略回测**: 回测自定义规则的胜率
4. **多市场支持**: 扩展到港股、美股
5. **智能预警**: 基于机器学习的异常检测

---

**最后更新**: 2026-03-09
