# -*- coding: utf-8 -*-
import requests


class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0


# Alpha Vantage API Key（免费注册获取）
ALPHA_VANTAGE_KEY = "demo"  # 替换为您的实际 Key


def 获取价格(品种代码):
    """获取真实价格"""
    try:
        # 加密货币 -> 币安API
        if 品种代码 == "BTC-USD":
            return 获取_币安价格("BTCUSDT")
        if 品种代码 == "ETH-USD":
            return 获取_币安价格("ETHUSDT")
        
        # 外汇 -> 免费汇率 API
        if 品种代码 == "EURUSD":
            return 获取_外汇价格("EUR", "USD")
        
        # 黄金期货 -> 使用 Alpha Vantage
        if 品种代码 == "GC=F":
            return 获取_期货价格("GC")
        
        # 美股 -> Alpha Vantage
        return 获取_美股价格(品种代码)
        
    except Exception as e:
        print(f"获取价格失败 {品种代码}: {e}")
        return 行情数据(品种代码, 0, 0, 0, 0, 0)


def 获取_币安价格(symbol):
    """币安 API"""
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    r = requests.get(url, timeout=10)
    price = float(r.json()['price'])
    return 行情数据(symbol, price, price, price, price, 0)


def 获取_外汇价格(from_currency, to_currency):
    """外汇汇率"""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    r = requests.get(url, timeout=10)
    data = r.json()
    price = data['rates'][to_currency]
    return 行情数据(f"{from_currency}{to_currency}", price, price, price, price, 0)


def 获取_期货价格(symbol):
    """期货价格（使用 Alpha Vantage）"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    r = requests.get(url, timeout=10)
    data = r.json()
    if 'Global Quote' in data and data['Global Quote']:
        price = float(data['Global Quote']['05. price'])
        return 行情数据(symbol, price, price, price, price, 0)
    return 行情数据(symbol, 0, 0, 0, 0, 0)


def 获取_美股价格(symbol):
    """美股价格"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    r = requests.get(url, timeout=10)
    data = r.json()
    if 'Global Quote' in data and data['Global Quote']:
        price = float(data['Global Quote']['05. price'])
        return 行情数据(symbol, price, price, price, price, 0)
    return 行情数据(symbol, 0, 0, 0, 0, 0)
