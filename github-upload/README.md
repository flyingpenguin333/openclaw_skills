# 🦾 Clawdbot Tools Collection

我的 Clawdbot 工具集合，包含各种实用技能。

## 📁 项目结构

```
clawdbot_work/
├── README.md              # 项目总览
├── requirements.txt       # 全局依赖
│
├── 📊 market-panel/       # 全球行情面板
│   ├── README.md          # 模块说明
│   ├── market_panel.py    # 主程序
│   ├── market_panel.md    # 开发文档
│   └── requirements.txt   # 模块依赖
│
└── 📋 feishu-task/        # 飞书任务管理
    └── SKILL.md           # API 文档
```

## 📊 market-panel - 全球行情面板

获取全球市场行情数据，支持多数据源聚合。

**功能：**
- 📈 全球指数（S&P500 / 道琼斯 / 纳斯达克）
- 🇨🇳 中国A股（上证 / 深证）
- 🇭🇰 港股科技（腾讯 / 阿里 / 美团等）
- 🔥 美股科技（苹果 / 微软 / 英伟达等）
- 🏦 中概股（拼多多 / 京东 / 蔚来等）
- 💱 情绪指标（VIX / 美元指数）
- 🪙 大宗商品（黄金 / 白银 / 原油）

**数据源：**
- A股/港股 → iFind (同花顺) via Qveris
- 美股 → Finnhub
- 全球指数 → Financial Modeling Prep
- 黄金/白银 → GoldAPI

**快速开始：**
```bash
cd market-panel
pip install -r requirements.txt
python market_panel.py
```

## 📋 feishu-task - 飞书任务管理

使用飞书开放平台 API 管理任务。

**功能：**
- ✅ 创建任务（带截止时间和提醒）
- 👥 多成员分配
- 🔔 提前 N 分钟提醒
- ✅ 完成任务
- 📋 查询任务列表

**API 文档：** 查看 `feishu-task/SKILL.md`

## 🔧 配置

### 1. 获取飞书 Access Token

```bash
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"你的APP_ID","app_secret":"你的APP_SECRET"}'
```

### 2. 配置 API Keys

编辑各模块的 Python 文件，配置：
- `QVERIS_API_KEY` - 港股/A股数据
- `FINNHUB_API_KEY` - 美股数据
- `FMP_API_KEY` - 指数数据
- `GOLDAPI_API_KEY` - 黄金数据

## 📦 安装所有依赖

```bash
pip install -r requirements.txt
```

## 🤝 贡献

欢迎提交 Issue 或 PR！

## 📄 许可证

MIT License

---

🦾 Built with Clawdbot
