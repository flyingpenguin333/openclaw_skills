# 💾 内存条价格监控器

> 实时监控 DRAM 内存条市场价格，支持 DDR4/DDR5/LPDDR 等主流规格。

## 📊 功能特性

- 📈 实时追踪 DRAM 晶圆价格（DDR5/DDR4）
- 🏪 零售模组价格参考
- 🎨 彩色终端界面
- ⏰ 自动刷新（可配置）
- 💡 价格提醒

## 🚀 快速开始

### 1. 安装依赖

```bash
cd memory-monitor
pip install -r requirements.txt
```

### 2. 运行

```bash
python memory_monitor.py
```

### 3. 配置

编辑 `memory_monitor.py` 修改：

```python
# 刷新间隔（秒）
REFRESH_INTERVAL = 300  # 默认5分钟

# 关注的型号
WATCH_LIST = {
    'DDR5': ['DDR5 16GB 4800/5600', ...],
    'DDR4': ['DDR4 16GB 3200', ...],
}
```

## 📱 部署到服务器（后台运行）

### 方法1：使用 nohup

```bash
# 后台运行
nohup python3 memory_monitor.py > /tmp/memory.log 2>&1 &

# 查看日志
tail -f /tmp/memory.log

# 停止
pkill -f memory_monitor.py
```

### 方法2：使用 systemd（推荐）

创建服务文件 `/etc/systemd/system/memory-monitor.service`：

```ini
[Unit]
Description=Memory Price Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/workplace/memory-monitor
ExecStart=/usr/bin/python3 /root/workplace/memory-monitor/memory_monitor.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载
systemctl daemon-reload

# 启动
systemctl start memory-monitor

# 查看状态
systemctl status memory-monitor

# 开机自启
systemctl enable memory-monitor
```

### 方法3：使用 Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "memory_monitor.py"]
```

构建运行：

```bash
docker build -t memory-monitor .
docker run -d --name memory-monitor memory-monitor
```

## 📊 数据来源

- **dramx.com** - 全球半导体观察
- 更新频率：每日多次

## 📋 监控规格

### DRAM 晶圆价格
- DDR5 16Gb (2Gx8) 4800/5600
- DDR4 16Gb (2Gx8) 3200
- DDR4 8Gb (1Gx8) 3200

### 零售模组参考
- DDR5 UDIMM 16GB
- DDR5 RDIMM 32GB  
- DDR4 UDIMM 16GB

## ⚠️ 注意事项

1. 价格仅供参考，实际交易价格请以商家为准
2. 晶圆价格与零售价格有滞后性
3. 建议设置刷新间隔不低于60秒

## 📝 更新日志

- v1.0 - 初始版本，支持 dramx.com 数据源

---

🦾 Made with Clawdbot
