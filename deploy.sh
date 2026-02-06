#!/bin/bash

echo "🚀 开始部署内存条价格监控服务..."

# 检查是否安装 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未安装 Node.js，请先安装:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

# 显示 Node.js 版本
echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"

# 安装依赖
echo "📦 安装依赖..."
npm install

# 创建数据目录
mkdir -p data

# 测试运行
echo "🧪 测试运行..."
timeout 10 node server.js || true

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║           部署完成！请继续以下步骤：                ║"
echo "╠═══════════════════════════════════════════════════╣"
echo "║  1. 前台运行: npm start                            ║"
echo "║  2. 后台运行: nohup npm start > log.txt 2>&1 &    ║"
echo "║  3. 访问地址: http://你的服务器IP:3000            ║"
echo "║  4. PM2 守护进程 (推荐):                          ║"
echo "║     npm install -g pm2                            ║"
echo "║     pm2 start server.js --name memory-monitor    ║"
echo "║     pm2 startup                                   ║"
echo "║     pm2 save                                      ║"
echo "╚═══════════════════════════════════════════════════╝"
