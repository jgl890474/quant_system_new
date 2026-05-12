# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime

# 飞书机器人 Webhook 地址
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/oc_5961acd60f94fd4e9df9f8cae3259945"

def 发送飞书消息(内容):
    """发送消息到飞书"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            "msg_type": "text",
            "content": {"text": 内容}
        }
        response = requests.post(FEISHU_WEBHOOK, headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            print("✅ 飞书消息已发送")
        else:
            print(f"❌ 发送失败: {response.text}")
    except Exception as e:
        print(f"❌ 异常: {e}")

# 测试发送
if __name__ == "__main__":
    发送飞书消息("🔔 量化交易系统测试消息\n时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
