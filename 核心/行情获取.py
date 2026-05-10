# -*- coding: utf-8 -*-
"""
行情获取模块 v3.0 - 稳定版
数据源：
- 加密货币：币安API
- 美股/外汇/期货：yfinance
- A股及其他：演示数据
"""

import yfinance as yf
import random
import requests
import time


class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0
        self.涨跌 = 0.0


def 获取价格(品种代码):
    """统一入口"""
    # 加密货币 -> 币安API
    if 'BTC' in 品种代码 or 'ETH' in 品种代码:
        return 获取_加密货币_币安(品种代码)
    
    # 其他 -> yfinance
    return 获取_其他_yfinance(品种代码)


def 获取_加密货币_币安(品种代码):
    """币安API获取加密货币价格"""
    try:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = float(data['price'])
        print(f"[币安] {品种代码}: ${price}")
        return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取失败: {e}")
        return 获取_演示数据(品种代码)


def 获取_其他_yfinance(品种代码):
    """yfinance获取数据"""
    try:
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"[yfinance] {品种代码}: {price}")
            return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"yfinance获取失败: {e}")
    
    return 获取_演示数据(品种代码)


def 获取_演示数据(品种代码):
    """演示数据"""
    价格表 = {
        "300750.SZ": 437.00, "002415.SZ": 35.55, "000333.SZ": 80.40,
        "AAPL": 175.00, "TSLA": 240.00, "NVDA": 120.00,
        "BTC-USD": 45000, "ETH-USD": 2300,
        "GC=F": 1950, "CL=F": 95, "EURUSD": 1.08
    }
    价格 = 价格表.get(品种代码, 100)
    # 添加小波动
    价格 = 价格 * (1 + random.uniform(-0.005, 0.005))
    print(f"[演示] {品种代码}: {价格:.2f}")
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
