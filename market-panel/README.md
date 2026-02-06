# 🦾 Clawdbot Global Market Dashboard

全球实时行情面板 - 飞书/终端多端发布

## ✨ 特性

- 📊 **全球指数**: S&P500 / 道琼斯 / 纳斯达克 / 上证 / 深证
- 🇭🇰 **港股科技**: 腾讯 / 阿里 / 美团 / 快手 / 小米
- 🔥 **美股科技**: 苹果 / 微软 / 谷歌 / 英伟达 / 特斯拉 / Meta / 亚马逊
- 🏦 **中概股**: 拼多多 / 京东 / 蔚来 / 小鹏 / 理想
- 💱 **情绪指标**: VIX 恐慌指数 / 美元指数
- 🪙 **大宗商品**: 黄金 / 白银 / 原油

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API Keys

编辑 `market_panel.py`，设置：

```python
# Qveris API Key (用于获取港股/A股数据)
QVERIS_API_KEY = "your-api-key"

# Finnhub API Key (用于获取美股数据)
FINNHUB_API_KEY = "your-api-key"

# Financial Modeling Prep API Key (用于获取指数数据)
FMP_API_KEY = "your-api-key"
```

### 3. 运行

```bash
python market_panel.py
```

## 📦 数据源

| 数据类型 | 数据源 |
|---------|--------|
| A股/港股 | iFind (同花顺) via Qveris |
| 美股 | Finnhub |
| 全球指数 | Financial Modeling Prep |
| 黄金/白银 | GoldAPI |
| 汇率 | 备用数据源 |

## 📱 发布支持

- ✅ 飞书 (Feishu)
- ✅ 终端输出
- 🔜 Telegram
- 🔜 Slack

## 📋 示例输出

```
**📊 全球行情面板**
更新时间: 2026-02-06 12:00

**🌏 全球指数**
- 标普500: 5,832.66 🔴 -0.48%
- 道琼斯: 43,910.24 🔴 -0.49%

**🇨🇳 中国A股**
- 上证指数: 3,262.56 🔴 -0.49%
- 深证成指: 10,438.45 🔴 -0.54%

**💱 情绪指标**
- VIX恐慌指数: 18.52 🟢 +3.25%

**🪙 大宗商品**
- 黄金: $2,658.50 🟢 +0.25%
```

## 🤝 贡献

欢迎提交 PR 或 Issue！

## 📄 许可证

MIT License

---

🦾 Built with Clawdbot
