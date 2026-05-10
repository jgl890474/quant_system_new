# -*- coding: utf-8 -*-
import requests
import yfinance as yf


class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0


def 获取价格(品种代码):
    """统一接口：根据品种类型自动选择数据源"""
    
    # 1. 加密货币 -> 币安 API
    if 品种代码 == "BTC-USD":
        return 获取_币安价格("BTCUSDT")
    if 品种代码 == "ETH-USD":
        return 获取_币安价格("ETHUSDT")
    
    # 2. 外汇 -> ExchangeRate-API（免费，无需注册）
    if 品种代码 == "EURUSD":
        return 获取_外汇价格("EUR", "USD")
    if 品种代码 == "GBPUSD=X":
        return 获取_外汇价格("GBP", "USD")
    
    # 3. 黄金期货 -> 使用 yfinance
    if 品种代码 == "GC=F":
        return 获取_yfinance价格("GC=F")
    
    # 4. 美股 -> 使用 yfinance
    if 品种代码 in ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]:
        return 获取_yfinance价格(品种代码)
    
    # 5. A股 -> 使用 yfinance（需要 .SS 或 .SZ 后缀）
    return 获取_yfinance价格(品种代码)


def 获取_币安价格(symbol):
    """币安 API（加密货币）"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data['price'])
        print(f"[币安] {symbol}: ${price}")
        return 行情数据(symbol, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取失败 {symbol}: {e}")
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


def 获取_yfinance价格(symbol):
    """yfinance 获取（美股、期货、A股）"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"[yfinance] {symbol}: ${price}")
            return 行情数据(symbol, price, price, price, price, 0)
        else:
            print(f"[yfinance] {symbol} 无数据")
            return 行情数据(symbol, 0, 0, 0, 0, 0)
    except Exception as e:
        print(f"yfinance 获取失败 {symbol}: {e}")
        return 行情数据(symbol, 0, 0, 0, 0, 0)
