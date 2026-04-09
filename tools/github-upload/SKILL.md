---
name: github-upload
description: "自动化上传文件到 GitHub 仓库，保持模块化目录结构。"
homepage: https://docs.github.com
metadata:
  clawdbot:
    emoji: "🚀"
---

# GitHub Upload Skill

自动化上传文件到 GitHub 仓库，保持模块化目录结构。

## 准备工作

### 生成 Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens
2. Tokens (classic) → 生成新 token
3. 勾选 `repo` 权限
4. 复制 token（格式：`ghp_xxxxx`）

### 配置 Credential

```bash
echo "ghp_your_token_here" > ~/.config/github_token
chmod 600 ~/.config/github_token
```

## Python 上传工具

创建 `github_upload.py`：

```python
#!/usr/bin/env python3
"""
GitHub 文件上传工具
保持模块化目录结构
"""
import os
import base64
import requests

class GitHubUploader:
    def __init__(self, repo, token_file="~/.config/github_token"):
        self.repo = repo
        with open(os.path.expanduser(token_file)) as f:
            self.token = f.read().strip()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def upload_file(self, local_path, remote_path, message=None):
        """上传单个文件"""
        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
        
        sha = self.get_file_sha(remote_path)
        
        data = {
            "message": message or f"Upload {remote_path}",
            "content": content
        }
        if sha:
            data["sha"] = sha
        
        url = f"https://api.github.com/repos/{self.repo}/contents/{remote_path}"
        resp = requests.put(url, headers=self.headers, json=data)
        
        if resp.status_code in [200, 201]:
            print(f"✅ 已上传: {remote_path}")
            return True
        else:
            print(f"❌ 失败: {resp.status_code}")
            return False
    
    def get_file_sha(self, path):
        """获取文件 SHA"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{path}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get("sha")
        return None
    
    def upload_directory(self, local_dir, remote_dir="", message=None):
        """上传整个目录"""
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                remote_path = os.path.join(
                    remote_dir,
                    os.path.relpath(local_path, local_dir)
                ).replace("\\", "/")
                self.upload_file(local_path, remote_path, message)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python github_upload.py <本地目录> <远程目录>")
        sys.exit(1)
    
    uploader = GitHubUploader("flyingpenguin333/clawdbot_work")
    uploader.upload_directory(sys.argv[1], sys.argv[2])
```

## 使用方法

```bash
# 1. 配置 token
echo "ghp_your_token" > ~/.config/github_token

# 2. 上传单个文件
python github_upload.py market_panel.py market-panel/

# 3. 上传整个目录
python github_upload.py market-panel/ market-panel/
```

## Shell 上传脚本

创建 `upload.sh`：

```bash
#!/bin/bash

REPO="flyingpenguin333/clawdbot_work"
TOKEN=$(cat ~/.config/github_token)

upload_file() {
    local file=$1
    local remote=$2
    local content=$(base64 -w 0 "$file")
    local sha=$(curl -s -H "Authorization: Bearer $TOKEN" \
        "https://api.github.com/repos/$REPO/contents/$remote" | \
        python3 -c "import sys,json; print(json.load(sys.stdin).get('sha',''))")
    
    local data='{"message":"Upload","content":"'$content}'"
    [ -n "$sha" ] && data="${data%,\"sha\"},\"sha\":\"$sha\"}"
    
    curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
        -d "$data" \
        "https://api.github.com/repos/$REPO/contents/$remote" > /dev/null
    
    echo "✅ $remote"
}

upload_dir() {
    local dir=$1
    local remote=$2
    for file in $(find "$dir" -type f); do
        rel=$(realpath --relative-to="$dir" "$file")
        upload_file "$file" "$remote/$rel"
    done
}

upload_dir $1 $2
echo "完成！"
```

## 使用

```bash
chmod +x upload.sh
./upload.sh market-panel/ market-panel/
./upload.sh feishu-task/ feishu-task/
```

## 约定结构

```
仓库/
├── README.md
├── 📊 模块1/
│   ├── README.md
│   └── 主程序.py
└── 📋 模块2/
    └── SKILL.md
```

## 注意事项

1. Token 不要提交到代码仓库
2. 单文件最大 100MB
3. Rate limit: 认证后 5000次/小时
