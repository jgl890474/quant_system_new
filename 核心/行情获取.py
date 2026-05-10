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


def 获取价格(品种代码):
    """统一接口"""
    
    # 加密货币 -> 币安 API
    if 品种代码 == "BTC-USD":
        return 获取_币安价格("BTCUSDT")
    if 品种代码 == "ETH-USD":
        return 获取_币安价格("ETHUSDT")
    
    # 外汇 -> ExchangeRate-API
    if 品种代码 == "EURUSD":
        return 获取_外汇价格("EUR", "USD")
    
    # 黄金期货 -> 使用 Gold-API
    if 品种代码 == "GC=F":
        return 获取_黄金价格()
    
    # 美股 -> 使用 Alpha Vantage（需注册）或 币安（如果有）
    # 临时：返回演示数据，但用成本价显示
    return 获取_演示价格(品种代码)


def 获取_币安价格(symbol):
    """币安 API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data['price'])
        print(f"[币安] {symbol}: ${price}")
        return 行情数据(symbol, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取失败 {symbol}: {e}")
        return 行情数据(symbol, 45000, 45000, 45000, 45000, 0)  # BTC 默认 45000


def 获取_外汇价格(from_currency, to_currency):
    """外汇汇率"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = data['rates'][to_currency]
        print(f"[外汇] {from_currency}/{to_currency}: {price}")
        return 行情数据(f"{from_currency}{to_currency}", price, price, price, price, 0)
    except Exception as e:
        print(f"外汇获取失败: {e}")
        return 行情数据("EURUSD", 1.08, 1.08, 1.08, 1.08, 0)


def 获取_黄金价格():
    """黄金价格"""
    try:
        url = "https://api.gold-api.com/price/XAU"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data['price'])
        print(f"[黄金] GC=F: ${price}")
        return 行情数据("GC=F", price, price, price, price, 0)
    except Exception as e:
        print(f"黄金获取失败: {e}")
        return 行情数据("GC=F", 1950, 1950, 1950, 1950, 0)


def 获取_演示价格(品种代码):
    """美股演示数据（使用接近真实的价格）"""
    价格表 = {
        "AAPL": 175.00,
        "TSLA": 170.00,
        "NVDA": 120.00,
        "MSFT": 330.00,
        "GOOGL": 130.00,
    }
    price = 价格表.get(品种代码, 100)
    print(f"[演示] {品种代码}: ${price}")
    return 行情数据(品种代码, price, price, price, price, 0)
