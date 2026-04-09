# 🦾 Clawdbot Skills Collection

我的 Clawdbot 工具集合，包含各种实用技能。本仓库用于共同维护和同步所有已安装的 skills。

---

## 📊 市场分析类

### market-panel
全球行情面板 - 获取全球市场行情数据，支持多数据源聚合。
- 📈 全球指数（S&P500 / 道琼斯 / 纳斯达克）
- 🇨🇳 中国A股（上证 / 深证）
- 🇭🇰 港股科技（腾讯 / 阿里 / 美团等）
- 🔥 美股科技（苹果 / 微软 / 英伟达等）
- 💱 情绪指标（VIX / 美元指数）
- 🪙 大宗商品（黄金 / 白银 / 原油）

### stock-analysis
股票分析工具 - 使用 Yahoo Finance 数据，支持投资组合管理、观察列表、股息分析等。

### us-stock-analysis
美股分析工具 - 全面的美股分析，包括基本面分析、技术分析、股票对比和投资报告生成。

### daily-stock-analysis
A/H/美股每日智能分析器 - LLM 驱动的每日自动分析和推送决策仪表盘。

### trading-assistant
A股交易助手 - 提供盘中提醒、持仓跟踪、收盘总结等功能。

### yahoo-finance
Yahoo Finance 数据获取 - 获取股票价格、基本面、财报、期权、股息和分析师评级。

---

## 🔮 加密货币与宏观分析

### btc-bottom-model
比特币抄底时机判断模型 - 通过6大核心指标（RSI、成交量、MVRV、恐慌指数、矿机关机价、长期持有者行为）综合评估比特币底部区间。

### macro-liquidity
宏观流动性监控系统 - 追踪美联储净流动性、SOFR利率、MOVE美债波动率、日元套利交易信号等4大核心指标。

---

## 📰 新闻与信息

### news
个性化财经新闻简报生成器 - 基于用户持仓和偏好，聚合24小时内最重要、最热门、最相关的财经新闻。

### news-summary
新闻摘要生成器 - 从可信的国际 RSS 源获取新闻并生成语音摘要。

### tech-news-digest
科技新闻聚合 - 从 109+ 个来源自动收集、评分和推送科技新闻。

---

## 🌐 互联网访问与搜索

### edison-agent-reach
互联网访问工具 - 支持 Twitter/X、Reddit、YouTube、GitHub、Bilibili、小红书、抖音、微信公众号、LinkedIn、Boss直聘、RSS 等平台。

### agent-reach-secure
安全的互联网访问封装层 - 基于 edison-agent-reach，自动阻止命令注入、SSRF内网扫描、恶意URL。

### browser
浏览器自动化 - 使用 Puppeteer 渲染 JavaScript 密集型网页并提取动态内容。

### qveris
QVeris 搜索与行动引擎 - 为 AI Agent 构建的搜索和行动引擎，聚合数千种工具和服务。

---

## 📈 财务分析

### financial-analysis
财务分析工具包 - 支持可比公司分析（comps）、DCF估值、LBO建模、三表财务建模等。

### tech-earnings-deepdive
科技股财报深度分析 - 覆盖16大分析模块、6大投资哲学视角、机构级证据标准。

### market-environment-analysis
市场环境综合分析 - 分析全球市场、外汇、大宗商品和经济指标，提供风险/避险评估。

---

## 📅 日历与任务

### icloud-calendar
iCloud 日历管理 - 通过 CalDAV 协议添加、查看和管理日历事件。

### feishu-task
飞书任务管理 - 使用飞书开放平台 API 管理任务。

### feishu-doc
飞书文档相关工具。

### feishu-wiki
飞书知识库相关工具。

---

## 💼 投资组合

### portfolio-assistant
投资组合助手 - 投资组合跟踪和管理工具。

---

## 🚀 工具类

### github-upload
GitHub 上传工具 - 自动化上传文件到 GitHub 仓库。

### memory-monitor
内存监控工具。

---

## 📦 安装说明

每个 skill 目录下都有 `SKILL.md` 文件，包含详细的使用说明和安装步骤。

通用安装方式：
```bash
# 将 skill 复制到 OpenClaw skills 目录
cp -r <skill-name> ~/.openclaw/skills/

# 或者使用符号链接
ln -s $(pwd)/<skill-name> ~/.openclaw/skills/<skill-name>
```

---

## 🤝 协作流程

1. **安装新 skill** → 复制到本仓库并更新 README
2. **更新 skill** → 同步修改到本仓库
3. **从外部获取 skill** → 上传到这个仓库共享

---

🦾 Built with Clawdbot
