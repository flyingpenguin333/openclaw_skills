"""
设置飞书 Webhook 配置
"""
import sys
import json
from pathlib import Path

# 数据目录
DATA_DIR = Path("~/.clawdbot/skills/portfolio-assistant").expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)
PREFERENCES_FILE = DATA_DIR / "preferences.json"

def set_webhook(url: str):
    """设置飞书 Webhook URL"""
    # 读取现有配置
    if PREFERENCES_FILE.exists():
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
    else:
        prefs = {}
    
    # 更新 webhook
    prefs['feishu_webhook'] = url
    
    # 添加默认简报设置
    if 'briefing_preferences' not in prefs:
        prefs['briefing_preferences'] = {
            'morning_time': '08:00',
            'evening_time': '18:00',
            'include_market_overview': True,
            'include_portfolio_pnl': True,
            'include_keyword_news': True
        }
    
    # 保存
    with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)
    
    print(f'[OK] Webhook 已配置')
    print(f'[INFO] 配置文件: {PREFERENCES_FILE}')
    
    # 测试发送
    print('\n[INFO] 正在发送测试消息...')
    test_send(url)

def test_send(webhook_url: str):
    """发送测试消息"""
    import requests
    
    payload = {
        'msg_type': 'text',
        'content': {
            'text': '[Portfolio Assistant] 配置成功！\n\n现在可以开始使用：\n• 买入/卖出记录持仓\n• 添加关注关键词\n• 查看资产雷达\n• 生成投资简报'
        }
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            print('[OK] 测试消息发送成功！')
            print('[INFO] 请检查飞书群是否收到消息')
        else:
            print(f'[ERROR] 发送失败: {response.status_code}')
            print(f'[INFO] 响应: {response.text}')
    except Exception as e:
        print(f'[ERROR] 发送异常: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python set_webhook.py <webhook_url>')
        print('')
        print('Example:')
        print('  python set_webhook.py "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"')
        sys.exit(1)
    
    url = sys.argv[1]
    set_webhook(url)
