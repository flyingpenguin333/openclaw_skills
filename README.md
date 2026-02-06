# 🦾 Clawdbot Tools Collection

我的 Clawdbot 工具集合，包含各种实用技能。

## 📁 项目结构

```
clawdbot_work/
├── README.md              # 项目总览
│
├── 📊 market-panel/       # 全球行情面板
│   ├── README.md          # 模块说明
│   ├── market_panel.py    # 主程序
│   ├── market_panel.md    # 开发文档
│   └── requirements.txt   # 模块依赖
│
├── 📋 feishu-task/        # 飞书任务管理
│   ├── README.md          # 模块说明
│   └── SKILL.md           # API 文档
│
└── 🚀 github-upload/      # GitHub 上传工具
    ├── README.md          # 说明文档
    ├── upload.py          # 上传脚本
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

**文档：** `feishu-task/SKILL.md`

## 🚀 github-upload - GitHub 上传工具

自动化上传文件到 GitHub 仓库。

**功能：**
- 🚀 上传单个文件
- 📁 上传整个目录
- 🔄 保持目录结构

**使用：**
```bash
cd github-upload
python upload.py <本地目录> <远程目录>
```

**文档：** `github-upload/SKILL.md`

## 📦 安装依赖

```bash
# market-panel
cd market-panel && pip install -r requirements.txt

# github-upload
cd github-upload && pip install requests
```

---

🦾 Built with Clawdbot
