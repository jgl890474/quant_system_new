# -*- coding: utf-8 -*-
import requests
import os
import random

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

def ai_decision(signals, current_price, symbol="EURUSD"):
    if not DEEPSEEK_API_KEY:
        if "buy" in str(signals).lower():
            return "buy"
        elif "sell" in str(signals).lower():
            return "sell"
        return "hold"
    
    prompt = f"""You are a quant trading AI.
Symbol: {symbol}
Current price: {current_price}
Strategy signals: {signals}
Output only one word: buy, sell, or hold."""
    
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 10
            },
            timeout=10
        )
        if resp.status_code == 200:
            decision = resp.json()["choices"][0]["message"]["content"].strip().lower()
            if decision in ["buy", "sell", "hold"]:
                return decision
    except Exception as e:
        print(f"AI error: {e}")
    
    return random.choice(["buy", "sell", "hold"])
