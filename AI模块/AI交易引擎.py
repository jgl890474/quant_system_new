# -*- coding: utf-8 -*-
import requests
import os

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

def ai_decision(signals, current_price, symbol="EURUSD"):
    if not DEEPSEEK_API_KEY:
        return "hold"
    
    prompt = f"""你是一个量化交易AI仲裁者。
当前标的: {symbol}
当前价格: {current_price}
各策略信号:
{signals}
请综合判断后只输出一个词：buy 或 sell 或 hold。"""
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 10
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            decision = resp.json()["choices"][0]["message"]["content"].strip().lower()
            if decision in ["buy", "sell", "hold"]:
                return decision
    except Exception as e:
        print(f"DeepSeek调用失败: {e}")
    return "hold"