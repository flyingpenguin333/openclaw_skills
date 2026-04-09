---
name: feishu-task
description: "飞书任务管理：创建任务、设置提醒、完成任务。支持截止时间和提前提醒。"
homepage: https://open.feishu.cn/document/task-v2
metadata:
  clawdbot:
    emoji: "📋"
---

# 飞书任务管理

使用飞书开放平台 API 创建和管理任务，支持截止时间和提醒功能。

## 准备工作

### 1. 获取 Access Token

```bash
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"你的APP_ID","app_secret":"你的APP_SECRET"}'
```

### 2. 需要的权限

在飞书开放平台添加以下权限：
- `task:task` - 完整任务权限
- `contact:contact.base:readonly` - 查询用户 ID

## 创建任务

### 基础任务

```bash
curl -X POST "https://open.feishu.cn/open-apis/task/v2/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-001",
    "title": "完成任务",
    "summary": "📌 摘要说明",
    "description": "详细描述"
  }'
```

### 带截止时间

```bash
curl -X POST "https://open.feishu.cn/open-apis/task/v2/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-002",
    "title": "下午四点出门",
    "summary": "🕐 准时出门",
    "description": "记得准时出门！",
    "due": {
      "date": "2026-02-06",
      "timestamp": "1770364800000",
      "timezone": "Asia/Shanghai"
    }
  }'
```

### 带提醒（推荐）

```bash
curl -X POST "https://open.feishu.cn/open-apis/task/v2/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-003",
    "title": "喝水",
    "summary": "💧 补充水分",
    "description": "记得喝水！",
    "due": {
      "date": "2026-02-06",
      "timestamp": "1770354600000",
      "timezone": "Asia/Shanghai"
    },
    "members": [
      {
        "id": "ou_c042ca2dc42425d1bef816d6dfba0a00",
        "role": "assignee"
      }
    ],
    "reminders": [
      {
        "is_whole_day": false,
        "trigger_time": "1770354120000",
        "type": "absolute",
        "relative_fire_minute": 8
      }
    ]
  }'
```

### 完整参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 任务唯一标识 |
| `title` | string | 是 | 任务标题 |
| `summary` | string | 是 | 摘要（显示在任务列表） |
| `description` | string | 否 | 详细描述 |
| `due.date` | string | 否 | 日期 "YYYY-MM-DD" |
| `due.timestamp` | string | 否 | 截止时间戳（毫秒） |
| `due.timezone` | string | 否 | 时区 "Asia/Shanghai" |
| `members[].id` | string | 否 | 用户 ID |
| `members[].role` | string | 否 | 角色 "assignee" |
| `reminders[].trigger_time` | string | 否 | 提醒时间戳 |
| `reminders[].relative_fire_minute` | int | 否 | 提前分钟数 |

## 为已有任务添加提醒

```bash
curl -X POST "https://open.feishu.cn/open-apis/task/v2/task_reminders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "t100153",
    "reminders": [
      {
        "is_whole_day": false,
        "trigger_time": "1770354120000",
        "type": "absolute",
        "relative_fire_minute": 15
      }
    ]
  }'
```

## 完成任务

```bash
curl -X PATCH "https://open.feishu.cn/open-apis/task/v2/tasks/{guid}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task": {"completed_at": "1770354600000"},
    "update_fields": ["completed_at"]
  }'
```

## 查询任务列表

```bash
curl -X GET "https://open.feishu.cn/open-apis/task/v2/tasks?page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 获取用户 ID

```bash
curl -X GET "https://open.feishu.cn/open-apis/contact/v3/users?page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 时间戳计算

```python
from datetime import datetime

# 截止时间 16:00
due = datetime(2026, 2, 6, 16, 0, 0)
timestamp_ms = int(due.timestamp() * 1000)
# 输出: 1770364800000

# 提前15分钟提醒
remind = timestamp_ms - 15 * 60 * 1000
# 输出: 1770363900000
```

## 完整示例

### 创建带提醒的任务（Python）

```python
import subprocess
import json
import time
from datetime import datetime

TOKEN = "你的TOKEN"
USER_ID = "ou_c042ca2dc42425d1bef816d6dfba0a00"

today = datetime.now()
due_time = today.replace(hour=16, minute=0, second=0, microsecond=0)
due_timestamp = int(due_time.timestamp() * 1000)
remind_time = due_timestamp - 15 * 60 * 1000  # 提前15分钟

payload = {
    "task_id": f"task-{int(today.timestamp())}",
    "title": "下午四点出门",
    "summary": "🕐 准时出门",
    "description": "记得准时出门！",
    "due": {
        "date": today.strftime('%Y-%m-%d'),
        "timestamp": str(due_timestamp),
        "timezone": "Asia/Shanghai"
    },
    "members": [{"id": USER_ID, "role": "assignee"}],
    "reminders": [{
        "is_whole_day": False,
        "trigger_time": str(remind_time),
        "type": "absolute",
        "relative_fire_minute": 15
    }]
}

cmd = [
    "curl", "-s", "-X", "POST",
    "https://open.feishu.cn/open-apis/task/v2/tasks",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload, ensure_ascii=False)
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
```

## 注意事项

1. **task_id**: 必须是唯一值，建议用时间戳
2. **summary**: 必填，用于显示在任务列表
3. **reminders**: 
   - `trigger_time` 必须是未来时间
   - 每个任务最多 5 个提醒
4. **用户权限**: 需要 `contact:contact.base:readonly` 才能查询用户
5. **Token 过期**: tenant_access_token 有效期约 2 小时

## 相关链接

- [飞书任务 API 文档](https://open.feishu.cn/document/task-v2)
- [API 错误码排查](https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting)
