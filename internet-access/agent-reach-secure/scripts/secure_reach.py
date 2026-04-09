#!/usr/bin/env python3
"""
Agent Reach Secure - 安全封装层
基于 edison-agent-reach，添加输入验证和安全控制
"""

import re
import sys
import json
import time
import socket
import hashlib
import subprocess
import ipaddress
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

# 配置
BASE_DIR = Path.home() / ".agent-reach-secure"
AUDIT_LOG = BASE_DIR / "audit.log"
CONFIG_FILE = BASE_DIR / "config.json"
BLOCKED_IPS_FILE = BASE_DIR / "blocked_ips.txt"

# 默认配置
DEFAULT_CONFIG = {
    "rate_limit": {
        "max_requests": 20,
        "window_seconds": 60
    },
    "whitelist": {
        "enabled": False,
        "domains": []
    },
    "blacklist": {
        "domains": []
    },
    "blocked_ip_ranges": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
        "127.0.0.0/8",
        "0.0.0.0/8",
        "fc00::/7",
        "fe80::/10"
    ]
}

# 危险的 shell 字符
DANGEROUS_CHARS = re.compile(r'[;|&$`\n\r<>{}\[\]]')

# 允许的 URL 协议
ALLOWED_SCHEMES = {'http', 'https'}


class SecurityError(Exception):
    """安全验证错误"""
    pass


@dataclass
class AuditEntry:
    """审计日志条目"""
    timestamp: str
    action: str
    input_data: str
    result: str
    reason: Optional[str] = None
    blocked: bool = False
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: List[float] = []
    
    def check(self) -> Tuple[bool, int]:
        """
        检查是否允许请求
        返回: (是否允许, 剩余请求数)
        """
        now = time.time()
        # 清理过期请求
        self.requests = [r for r in self.requests if now - r < self.window]
        
        if len(self.requests) >= self.max_requests:
            return False, 0
        
        self.requests.append(now)
        remaining = self.max_requests - len(self.requests)
        return True, remaining


class SecureReach:
    """安全封装层主类"""
    
    def __init__(self):
        self._init_directories()
        self.config = self._load_config()
        self.rate_limiter = RateLimiter(
            self.config["rate_limit"]["max_requests"],
            self.config["rate_limit"]["window_seconds"]
        )
        self.blocked_networks = [
            ipaddress.ip_network(cidr) 
            for cidr in self.config["blocked_ip_ranges"]
        ]
    
    def _init_directories(self):
        """初始化目录"""
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        for f in [AUDIT_LOG, BLOCKED_IPS_FILE]:
            f.touch(exist_ok=True)
    
    def _load_config(self) -> dict:
        """加载配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Warning: Failed to load config: {e}", file=sys.stderr)
        
        # 创建默认配置
        self._save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    def _save_config(self, config: dict):
        """保存配置"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _audit_log(self, entry: AuditEntry):
        """记录审计日志"""
        with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')
    
    def _is_internal_ip(self, hostname: str) -> bool:
        """检查是否为内网 IP"""
        if not hostname:
            return False
        
        # 检查 localhost 变种
        if hostname.lower() in ('localhost', '127.0.0.1', '::1', '0:0:0:0:0:0:0:1'):
            return True
        
        try:
            # 解析域名
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip_str = info[4][0]
                try:
                    ip = ipaddress.ip_address(ip_str)
                    # 检查是否在禁止的网段内
                    for network in self.blocked_networks:
                        if ip in network:
                            return True
                except ValueError:
                    continue
        except socket.gaierror:
            # 域名解析失败，可能是无效的 hostname
            pass
        except Exception as e:
            print(f"Warning: IP check error: {e}", file=sys.stderr)
        
        return False
    
    def _contains_dangerous_chars(self, text: str) -> bool:
        """检查是否包含危险的 shell 字符"""
        return bool(DANGEROUS_CHARS.search(text))
    
    def _is_whitelisted(self, hostname: str) -> bool:
        """检查域名是否在白名单中"""
        if not self.config["whitelist"]["enabled"]:
            return True
        
        whitelist = self.config["whitelist"]["domains"]
        return any(hostname == domain or hostname.endswith(f'.{domain}') for domain in whitelist)
    
    def _is_blacklisted(self, hostname: str) -> bool:
        """检查域名是否在黑名单中"""
        blacklist = self.config["blacklist"]["domains"]
        return any(hostname == domain or hostname.endswith(f'.{domain}') for domain in blacklist)
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        验证 URL 安全性
        返回: (是否通过, 错误信息)
        """
        if not url:
            return False, "URL 不能为空"
        
        # 检查危险字符
        if self._contains_dangerous_chars(url):
            return False, f"URL 包含危险字符: {DANGEROUS_CHARS.pattern}"
        
        # 解析 URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"URL 解析失败: {e}"
        
        # 检查协议
        scheme = parsed.scheme.lower()
        if scheme not in ALLOWED_SCHEMES:
            return False, f"不支持的协议: {scheme} (只允许 http/https)"
        
        hostname = parsed.hostname
        if not hostname:
            return False, "URL 缺少 hostname"
        
        # 检查内网 IP
        if self._is_internal_ip(hostname):
            return False, f"禁止访问内网地址: {hostname}"
        
        # 检查黑名单
        if self._is_blacklisted(hostname):
            return False, f"域名在黑名单中: {hostname}"
        
        # 检查白名单
        if not self._is_whitelisted(hostname):
            return False, f"域名不在白名单中: {hostname}"
        
        return True, "OK"
    
    def check_rate_limit(self) -> Tuple[bool, int, int]:
        """
        检查速率限制
        返回: (是否通过, 剩余请求数, 重置时间秒)
        """
        allowed, remaining = self.rate_limiter.check()
        if allowed:
            return True, remaining, 0
        
        # 计算重置时间
        now = time.time()
        window = self.config["rate_limit"]["window_seconds"]
        oldest_request = min(self.rate_limiter.requests) if self.rate_limiter.requests else now
        reset_time = int(oldest_request + window - now)
        
        return False, 0, max(0, reset_time)
    
    def fetch_web_content(self, url: str) -> Tuple[bool, str]:
        """
        安全地获取网页内容
        返回: (是否成功, 内容/错误信息)
        """
        action = "fetch_web"
        
        # 速率限制检查
        rate_ok, remaining, reset_time = self.check_rate_limit()
        if not rate_ok:
            error_msg = f"速率限制: 请等待 {reset_time} 秒后再试"
            self._audit_log(AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                input_data=url[:100],
                result="BLOCKED",
                reason="rate_limit",
                blocked=True
            ))
            return False, error_msg
        
        # URL 验证
        valid, error = self.validate_url(url)
        if not valid:
            self._audit_log(AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                input_data=url[:100],
                result="BLOCKED",
                reason=error,
                blocked=True
            ))
            return False, f"安全验证失败: {error}"
        
        # 执行请求
        try:
            # 使用参数化调用，避免 shell 注入
            jina_url = f"https://r.jina.ai/{url}"
            result = subprocess.run(
                ['curl', '-s', '-L', '--max-time', '30', jina_url],
                capture_output=True,
                text=True,
                timeout=35
            )
            
            if result.returncode == 0:
                self._audit_log(AuditEntry(
                    timestamp=datetime.utcnow().isoformat(),
                    action=action,
                    input_data=url[:100],
                    result="SUCCESS",
                    blocked=False
                ))
                return True, result.stdout
            else:
                error_msg = f"请求失败: {result.stderr}"
                self._audit_log(AuditEntry(
                    timestamp=datetime.utcnow().isoformat(),
                    action=action,
                    input_data=url[:100],
                    result="ERROR",
                    reason=error_msg,
                    blocked=False
                ))
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "请求超时 (30s)"
            self._audit_log(AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                input_data=url[:100],
                result="TIMEOUT",
                blocked=False
            ))
            return False, error_msg
        except Exception as e:
            error_msg = f"执行错误: {e}"
            self._audit_log(AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                input_data=url[:100],
                result="ERROR",
                reason=error_msg,
                blocked=False
            ))
            return False, error_msg
    
    def web_search(self, query: str, num_results: int = 5) -> Tuple[bool, str]:
        """
        安全地执行网页搜索 (通过 Exa)
        """
        action = "web_search"
        
        # 检查危险字符
        if self._contains_dangerous_chars(query):
            self._audit_log(AuditEntry(
                timestamp=datetime.utcnow().isoformat(),
                action=action,
                input_data=query[:100],
                result="BLOCKED",
                reason="dangerous_chars",
                blocked=True
            ))
            return False, "搜索词包含危险字符"
        
        # 限制结果数量
        num_results = max(1, min(num_results, 10))
        
        try:
            # 调用 mcporter exa 搜索
            cmd = f"mcporter call 'exa.web_search_exa(query: \"{query}\", numResults: {num_results})'"
            result = subprocess.run(
                cmd,
                shell=True,  # mcporter 需要 shell
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self._audit_log(AuditEntry(
                    timestamp=datetime.utcnow().isoformat(),
                    action=action,
                    input_data=query[:100],
                    result="SUCCESS",
                    blocked=False
                ))
                return True, result.stdout
            else:
                return False, f"搜索失败: {result.stderr}"
                
        except Exception as e:
            return False, f"搜索错误: {e}"
    
    def doctor(self) -> str:
        """运行诊断检查"""
        checks = []
        
        # 检查目录
        checks.append(f"[OK] 配置目录: {BASE_DIR.exists()}")
        checks.append(f"[OK] 审计日志: {AUDIT_LOG.exists()}")
        
        # 检查配置
        checks.append(f"[OK] 配置文件: {CONFIG_FILE.exists()}")
        checks.append(f"  - 速率限制: {self.config['rate_limit']['max_requests']}/{self.config['rate_limit']['window_seconds']}s")
        checks.append(f"  - 白名单启用: {self.config['whitelist']['enabled']}")
        checks.append(f"  - 黑名单数量: {len(self.config['blacklist']['domains'])}")
        
        # 检查依赖
        try:
            subprocess.run(['curl', '--version'], capture_output=True, check=True)
            checks.append("[OK] curl 已安装")
        except:
            checks.append("[FAIL] curl 未安装")
        
        try:
            subprocess.run(['mcporter', '--version'], capture_output=True, check=True)
            checks.append("[OK] mcporter 已安装")
        except:
            checks.append("[WARN] mcporter 未安装 (部分功能受限)")
        
        # 测试安全功能
        test_url = "http://localhost/test"
        valid, error = self.validate_url(test_url)
        checks.append(f"[OK] SSRF 防护: {'内网地址被阻止' if not valid else '警告: 内网检查失效'}")
        
        test_inject = "; rm -rf /"
        has_danger = self._contains_dangerous_chars(test_inject)
        checks.append(f"[OK] 注入防护: {'危险字符检测正常' if has_danger else '警告: 检测失效'}")
        
        return "\n".join(checks)


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("Usage: secure_reach.py <command> [args...]")
        print("Commands:")
        print("  fetch <url>     - 安全获取网页内容")
        print("  search <query>  - 执行网页搜索")
        print("  doctor          - 运行诊断检查")
        print("  validate <url>  - 验证 URL 安全性")
        sys.exit(1)
    
    command = sys.argv[1]
    secure = SecureReach()
    
    if command == "fetch" and len(sys.argv) >= 3:
        url = sys.argv[2]
        success, result = secure.fetch_web_content(url)
        print(result)
        sys.exit(0 if success else 1)
    
    elif command == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        success, result = secure.web_search(query)
        print(result)
        sys.exit(0 if success else 1)
    
    elif command == "doctor":
        print(secure.doctor())
        sys.exit(0)
    
    elif command == "validate" and len(sys.argv) >= 3:
        url = sys.argv[2]
        valid, error = secure.validate_url(url)
        print(f"Valid: {valid}")
        if not valid:
            print(f"Error: {error}")
        sys.exit(0 if valid else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
