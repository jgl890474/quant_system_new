# -*- coding: utf-8 -*-
import json
import urllib.parse
import requests
import os
from datetime import datetime

ALLTICK_TOKEN = os.environ.get("ALLTICK_TOKEN")

def get_1min_kline(symbol="EURUSD"):
    if not ALLTICK_TOKEN:
        return None
    query_data = {
        "trace": "quant_trade",
        "data": {
            "code": symbol,
            "kline_type": 1,
            "query_kline_num": 1,
            "kline_timestamp_end": 0
        }
    }
    query_str = urllib.parse.quote(json.dumps(query_data))
    url = f"https://quote.alltick.co/quote-b-api/kline?token={ALLTICK_TOKEN}&query={query_str}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("ret") == 200 and data.get("data"):
            k = data["data"][0]
            return {
                "close": k["close"],
                "high": k["high"],
                "low": k["low"],
                "open": k["open"],
                "timestamp": k["timestamp"]
            }
    except Exception as e:
        print(f"获取K线失败: {e}")
    return None

class BaseStrategy:
    def __init__(self, name):
        self.name = name
        self.position = 0
    def on_data(self, kline):
        return "hold"

class FuturesTrendStrategy(BaseStrategy):
    def __init__(self, name):
        super().__init__(name)
        self.prices = []
    def on_data(self, kline):
        self.prices.append(kline["close"])
        if len(self.prices) < 20:
            return "hold"
        short_ma = sum(self.prices[-5:]) / 5
        long_ma = sum(self.prices[-20:]) / 20
        if short_ma > long_ma:
            return "buy"
        elif short_ma < long_ma:
            return "sell"
        return "hold"

class ForexBreakoutStrategy(BaseStrategy):
    def __init__(self, name):
        super().__init__(name)
        self.highs = []
        self.lows = []
    def on_data(self, kline):
        self.highs.append(kline["high"])
        self.lows.append(kline["low"])
        if len(self.highs) < 20:
            return "hold"
        highest = max(self.highs[-20:])
        lowest = min(self.lows[-20:])
        if kline["close"] > highest:
            return "buy"
        if kline["close"] < lowest:
            return "sell"
        return "hold"

def call_deepseek_arbitrage(signals, current_price):
    if not DEEPSEEK_API_KEY:
        return "hold"
    signals_text = "\n".join([f"- {name}: {signal}" for name, signal in signals.items()])
    prompt = f"""你是一个量化交易AI仲裁者。
当前价格: {current_price}
各策略信号:
{signals_text}
请综合判断后只输出一个词：buy 或 sell 或 hold。"""
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 10
            },
            timeout=15
        )
        if resp.status_code == 200:
            decision = resp.json()["choices"][0]["message"]["content"].strip().lower()
            if decision in ["buy", "sell", "hold"]:
                return decision
    except Exception as e:
        print(f"DeepSeek调用失败: {e}")
    return "hold"

def handler(event, context):
    print(f"[{datetime.now()}] 函数执行")
    kline = get_1min_kline("EURUSD")
    if not kline:
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "error", "message": "获取行情失败"})
        }
    strategies = [
        FuturesTrendStrategy("期货趋势策略"),
        ForexBreakoutStrategy("外汇突破策略"),
    ]
    signals = {}
    for s in strategies:
        signals[s.name] = s.on_data(kline)
    final_signal = call_deepseek_arbitrage(signals, kline["close"])
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "ok",
            "price": kline["close"],
            "signals": signals,
            "ai_decision": final_signal,
            "timestamp": str(datetime.now())
        })
    }