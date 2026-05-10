# -*- coding: utf-8 -*-
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


# Alpha Vantage API Key（免费，需注册）
# 注册地址：https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_KEY = "demo"  # 替换为您的实际 Key


def 获取价格(品种代码):
    """获取真实价格"""
    
    # 加密货币 -> 币安API
    if 'BTC' in 品种代码:
        return 获取_币安价格("BTCUSDT")
    if 'ETH' in 品种代码:
        return 获取_币安价格("ETHUSDT")
    
    # 外汇 -> ExchangeRate-API（免费，无需注册）
    if 品种代码 == "EURUSD":
        return 获取_外汇价格("EUR", "USD")
    if 品种代码 == "GBPUSD=X":
        return 获取_外汇价格("GBP", "USD")
    
    # 黄金期货
    if 品种代码 == "GC=F":
        return 获取_黄金价格()
    
    # 美股 -> Alpha Vantage
    return 获取_美股价格(品种代码)


def 获取_币安价格(symbol):
    """币安 API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        price = float(r.json()['price'])
        print(f"[币安] {symbol}: ${price}")
        return 行情数据(symbol, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取失败: {e}")
        return 行情数据(symbol, 0, 0, 0, 0, 0)


def 获取_外汇价格(from_currency, to_currency):
    """外汇汇率（免费 API）"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = data['rates'][to_currency]
        print(f"[外汇] {from_currency}/{to_currency}: {price}")
        return 行情数据(f"{from_currency}{to_currency}", price, price, price, price, 0)
    except Exception as e:
        print(f"外汇获取失败: {e}")
        return 行情数据(f"{from_currency}{to_currency}", 0, 0, 0, 0, 0)


def 获取_黄金价格():
    """黄金价格（免费 API）"""
    try:
        url = "https://api.gold-api.com/price/XAU"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data['price'])
        print(f"[黄金] GC=F: ${price}")
        return 行情数据("GC=F", price, price, price, price, 0)
    except Exception as e:
        print(f"黄金价格获取失败: {e}")
        return 行情数据("GC=F", 0, 0, 0, 0, 0)


def 获取_美股价格(symbol):
    """美股价格（Alpha Vantage）"""
    try:
        # 先尝试币安（如果涉及加密货币相关）
        if symbol == "BTC-USD":
            return 获取_币安价格("BTCUSDT")
        
        # 使用 Alpha Vantage
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            price = float(data['Global Quote']['05. price'])
            print(f"[美股] {symbol}: ${price}")
            return 行情数据(symbol, price, price, price, price, 0)
        else:
            print(f"Alpha Vantage 无数据: {symbol}")
            return 行情数据(symbol, 0, 0, 0, 0, 0)
    except Exception as e:
        print(f"美股获取失败: {e}")
        return 行情数据(symbol, 0, 0, 0, 0, 0)
