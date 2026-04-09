# Portfolio Assistant 配置指南

## 飞书 Webhook 配置

### 获取步骤
1. 在飞书群里点击「群设置」→「群机器人」
2. 点击「添加机器人」→「自定义机器人」
3. 复制 Webhook URL
4. 将 URL 粘贴到下方

### 配置方法

#### 方法1：环境变量（推荐）
```bash
set FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx
```

#### 方法2：配置文件
编辑 `~/.clawdbot/skills/portfolio-assistant/preferences.json`：
```json
{
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx",
  "briefing_preferences": {
    "morning_time": "08:00",
    "evening_time": "18:00"
  }
}
```

#### 方法3：命令行设置
```bash
cd ~/.openclaw/workspace/skills/portfolio-assistant
python scripts/set_webhook.py "YOUR_WEBHOOK_URL"
```

## 测试消息

配置完成后，发送测试消息：
```bash
python scripts/test_feishu.py
```

## 使用示例

在飞书群里 @机器人 或直接发送：
- "买入 100股 TSLA @ 120 科技股"
- "关注 固态电池"
- "查看我的资产雷达"
