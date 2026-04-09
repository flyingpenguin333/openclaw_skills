---
name: agent-reach-secure
description: >
  安全的互联网访问封装层，基于 edison-agent-reach。
  自动阻止命令注入、SSRF内网扫描、恶意URL。
  支持审计日志、速率限制、URL白名单。
  
  使用场景：
  (1) 用户要求安全地搜索网页或视频
  (2) 用户要求访问互联网资源
  (3) 需要访问 Twitter/X, YouTube, Bilibili, Reddit, GitHub 等平台
  
  触发词："安全搜索", "安全上网", "搜一下", "search", "查一下", "找资料", "看视频"
---

# Agent Reach Secure — 安全封装层

这是 edison-agent-reach 的安全封装版本，在调用底层工具前进行输入验证和过滤。

## 🛡️ 安全特性

- ✅ **命令注入防护**: 过滤所有 shell 元字符
- ✅ **SSRF 防护**: 禁止访问内网 IP (10.x, 192.168.x, 127.x, 169.254.x)
- ✅ **协议限制**: 只允许 http/https
- ✅ **审计日志**: 记录所有操作到 `~/.agent-reach-secure/audit.log`
- ✅ **速率限制**: 每分钟最多 20 次请求
- ✅ **URL 白名单**: 可配置允许的域名

## 📁 目录结构

```
~/.agent-reach-secure/
├── audit.log          # 审计日志
├── config.json        # 配置文件
└── blocked_ips.txt    # 被阻止的IP记录
```

## 🔧 使用方法

### 直接使用 (推荐)

```
安全搜索 OpenClaw 最新动态
搜一下 YouTube 上关于 AI 的视频
安全访问 https://github.com/openclaw/openclaw
```

### 调用底层工具

当安全验证通过后，会自动调用 edison-agent-reach 的底层工具：

- Web 内容: `curl -s "https://r.jina.ai/URL"`
- Web 搜索: `mcporter call 'exa.web_search_exa(...)'`
- Twitter: `xreach search ...`
- YouTube: `yt-dlp --dump-json ...`
- GitHub: `gh search repos ...`

## ⚠️ 限制

以下操作会被阻止：
- 访问内网地址 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16)
- 访问 localhost/127.0.0.1
- URL 中包含 shell 元字符 (`;`, `|`, `&&`, `$`, `` ` `` 等)
- 非 http/https 协议 (file://, ftp://, etc.)
- 超过速率限制 (20 req/min)

## 🔍 安全检查流程

```
用户输入
    ↓
1. 提取 URL/搜索词
    ↓
2. URL 格式验证
    ↓
3. 内网 IP 检查 ← 阻止
    ↓
4. 协议检查 ← 阻止非 http/https
    ↓
5. 命令注入检查 ← 阻止危险字符
    ↓
6. 速率限制检查 ← 阻止超限
    ↓
7. 记录审计日志
    ↓
8. 调用底层工具执行
```

## 📝 配置

编辑 `~/.agent-reach-secure/config.json`:

```json
{
  "rate_limit": {
    "max_requests": 20,
    "window_seconds": 60
  },
  "whitelist": {
    "enabled": false,
    "domains": ["github.com", "youtube.com"]
  },
  "blacklist": {
    "domains": ["malicious-site.com"]
  }
}
```

## 📊 查看审计日志

```bash
# 查看最近 10 条记录
tail -n 10 ~/.agent-reach-secure/audit.log

# 查看被阻止的请求
grep "BLOCKED" ~/.agent-reach-secure/audit.log
```

## 🐛 故障排除

### 请求被误杀
如果合法 URL 被阻止，检查：
1. 是否包含特殊字符（尝试 URL encode）
2. 是否在黑名单中
3. 查看审计日志了解原因

### 速率限制触发
- 默认每分钟 20 次请求
- 等待 60 秒后自动恢复
- 或修改 config.json 提高限制

### 依赖检查
运行诊断：
```bash
python ~/.openclaw/skills/agent-reach-secure/scripts/secure_reach.py --doctor
```

## 📄 安全说明

**本封装层能解决的安全问题**:
- ✅ 命令注入
- ✅ SSRF 内网扫描
- ✅ 恶意 URL 过滤
- ✅ 审计追溯

**仍存在的限制** (底层工具相关):
- ⚠️ MCP 服务端仍可能记录数据（小红书/抖音等）
- ⚠️ Cookie 存储仍由下游工具管理
- ⚠️ 依赖的第三方工具（xreach, yt-dlp）需自行信任

**建议**:
- 使用专用小号登录社交平台
- 不要在隔离环境外处理敏感数据
- 定期审查审计日志

---

**版本**: 1.0.0  
**基于**: edison-agent-reach 1.0.0  
**作者**: 安全封装层 (派生版本)
