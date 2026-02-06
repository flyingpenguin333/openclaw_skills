# 🖥️ 内存条价格监控服务

实时监控京东内存条价格，支持多型号自动抓取和网页展示。

## ✨ 功能特性

- ✅ 实时抓取京东价格
- ✅ 多个内存条型号监控
- ✅ 精美网页展示
- ✅ 每5分钟自动刷新
- ✅ 手动刷新按钮
- ✅ 移动端适配

## 📦 安装依赖

```bash
cd memory-monitor
npm install
```

## 🚀 启动服务

### 方式1：前台运行（测试用）
```bash
npm start
```

### 方式2：后台运行（推荐）
```bash
nohup npm start > log.txt 2>&1 &
```

### 方式3：PM2 守护进程（生产环境推荐）
```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start server.js --name memory-monitor

# 设置开机自启
pm2 startup
pm2 save
```

## 🌐 访问地址

- **网页**: http://你的服务器IP:3000
- **API**: http://你的服务器IP:3000/api/prices

## 📱 监控的内存条型号

- 金士顿 DDR4 3200 8GB
- 金士顿 DDR4 3200 16GB
- 芝奇 DDR4 3200 16GB
- 威刚 DDR4 3200 16GB
- 海盗船 DDR4 3200 16GB

## 📁 文件结构

```
memory-monitor/
├── server.js      # 主服务程序
├── package.json   # 项目配置
├── deploy.sh      # 部署脚本
├── README.md      # 说明文档
├── data/          # 数据存储（可选）
├── logs/          # 日志文件（可选）
└── log.txt        # 运行日志
```

## ⚙️ 自定义配置

修改 `server.js` 中的 `MONITOR_ITEMS` 数组：

```javascript
const MONITOR_ITEMS = [
  { name: '你的型号', keyword: '搜索关键词', jdId: '京东ID' }
];
```

## 🔧 常用命令

```bash
# 查看 PM2 状态
pm2 status

# 查看日志
pm2 logs memory-monitor

# 重启服务
pm2 restart memory-monitor

# 停止服务
pm2 stop memory-monitor

# 删除服务
pm2 delete memory-monitor
```

## 🐳 Docker 部署（可选）

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# 构建运行
docker build -t memory-monitor .
docker run -d -p 3000:3000 --name memory-monitor memory-monitor
```

## ⚠️ 注意事项

1. 京东可能有反爬机制，频繁访问可能需要验证码
2. 建议设置 User-Agent 避免被封
3. 如需更高频次抓取，考虑使用京东开放平台 API

## 📄 License

MIT
