# -*- coding: utf-8 -*-
import random

def get_1min_kline(symbol="BTC-USD"):
    """获取1分钟K线数据（模拟数据）"""
    price_ranges = {
        "BTC-USD": (50000, 60000),
        "ETH-USD": (3000, 3500),
        "EURUSD": (1.08, 1.12),
        "GBPUSD": (1.25, 1.30),
        "AUDJPY": (90, 110),
        "GC=F": (1900, 2100),
        "CL=F": (70, 90),
    }
    low, high = price_ranges.get(symbol, (90, 110))
    close = random.uniform(low, high)
    return {
        "symbol": symbol,
        "close": close,
        "high": close * (1 + random.uniform(0.001, 0.005)),
        "low": close * (1 - random.uniform(0.001, 0.005)),
        "open": close,
        "timestamp": None,
        "volume": 0,
        "source": "simulated"
    }

def get_historical_klines(symbol="BTC-USD", count=50):
    """获取历史K线数据（用于前端画图）"""
    result = []
    base_price = 50000 if "BTC" in symbol else 1.08
    for i in range(count):
        price = base_price + (i * 0.01)
        result.append({
            "timestamp": i,
            "open": price,
            "high": price * 1.002,
            "low": price * 0.998,
            "close": price
        })
    return result