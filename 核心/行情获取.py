# -*- coding: utf-8 -*-
import requests
import yfinance as yf
import time


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
    
    # 黄金期货 -> 使用 yfinance
    if 品种代码 == "GC=F":
        return 获取_黄金价格()
    
    # 美股 -> 使用 yfinance
    return 获取_美股价格(品种代码)


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
        default_price = 45000 if symbol == "BTCUSDT" else 2300
        return 行情数据(symbol, default_price, default_price, default_price, default_price, 0)


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
    """黄金价格 - 使用 yfinance"""
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"[yfinance黄金] GC=F: ${price}")
            return 行情数据("GC=F", price, price, price, price, 0)
    except Exception as e:
        print(f"黄金获取失败: {e}")
    return 行情数据("GC=F", 1950.00, 1950.00, 1950.00, 1950.00, 0)


def 获取_美股价格(symbol):
    """美股价格 - 强制使用 yfinance"""
    for i in range(3):  # 重试3次
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d")
            if not data.empty:
                price = float(data['Close'].iloc[-1])
                print(f"[yfinance美股] {symbol}: ${price}")
                return 行情数据(symbol, price, price, price, price, 0)
            time.sleep(1)
        except Exception as e:
            print(f"yfinance尝试 {i+1}/3 失败 {symbol}: {e}")
            time.sleep(1)
    
    # 最终降级：使用硬编码的真实价格（不是成本价）
    真实价格 = {
        "AAPL": 175.00,
        "TSLA": 170.00,
        "NVDA": 120.00,
        "MSFT": 330.00,
        "GOOGL": 130.00,
    }
    price = 真实价格.get(symbol, 100)
    print(f"[硬编码] {symbol}: ${price}")
    return 行情数据(symbol, price, price, price, price, 0)
