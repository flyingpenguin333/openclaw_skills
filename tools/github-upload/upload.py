#!/usr/bin/env python3
"""
GitHub Upload Tool
自动化上传文件到 GitHub
"""
import os
import sys
import base64
import requests
import argparse

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
            print(f"✅ {remote_path}")
            return True
        else:
            print(f"❌ {remote_path}: {resp.status_code}")
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
        count = 0
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")
                if self.upload_file(local_path, remote_path, message):
                    count += 1
        return count


def main():
    parser = argparse.ArgumentParser(description="上传文件到 GitHub")
    parser.add_argument("local", help="本地文件或目录")
    parser.add_argument("remote", help="远程路径")
    parser.add_argument("--repo", default="flyingpenguin333/clawdbot_work", help="仓库名称")
    parser.add_argument("-m", "--message", help="提交信息")
    parser.add_argument("--token", default="~/.config/github_token", help="Token 文件")
    
    args = parser.parse_args()
    
    uploader = GitHubUploader(args.repo, args.token)
    
    if os.path.isdir(args.local):
        count = uploader.upload_directory(args.local, args.remote, args.message)
        print(f"\n🚀 完成！上传 {count} 个文件")
    else:
        uploader.upload_file(args.local, args.remote, args.message)


if __name__ == "__main__":
    main()
