# -*- coding: utf-8 -*-
"""
消息推送模块 - 飞书机器人
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书 Webhook（从 .env 读取）
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")


def 发送飞书消息(内容):
    """发送消息到飞书群"""
    if not FEISHU_WEBHOOK:
        print("⚠️ 未配置飞书 Webhook，跳过消息推送")
        return False
    
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            "msg_type": "text",
            "content": {"text": 内容}
        }
        response = requests.post(FEISHU_WEBHOOK, headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ 飞书消息已发送")
            return True
        else:
            print(f"❌ 发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def 发送交易信号(品种, 动作, 价格, 数量, 理由=""):
    """发送交易信号"""
    内容 = f"""
📊 【交易信号】
━━━━━━━━━━━━━━━━━━
🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📈 品种: {品种}
🎯 动作: {动作}
💰 价格: {价格:.2f}
📦 数量: {数量}
📝 理由: {理由}
━━━━━━━━━━━━━━━━━━
    """
    return 发送飞书消息(内容)


def 发送测试消息():
    """发送测试消息"""
    return 发送飞书消息(f"🧪 量化交易系统测试消息\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# 测试
if __name__ == "__main__":
    发送测试消息()
    print("消息推送模块测试完成")
