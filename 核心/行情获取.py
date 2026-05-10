# -*- coding: utf-8 -*-
import yfinance as yf
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
    """获取真实价格，不降级"""
    
    # 加密货币 -> 币安API
    if 'BTC' in 品种代码 or 'ETH' in 品种代码:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        price = float(r.json()['price'])
        return 行情数据(品种代码, price, price, price, price, 0)
    
    # 其他 -> yfinance
    if 品种代码 == "GC=F" or 品种代码 == "CL=F":
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="2d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            return 行情数据(品种代码, price, price, price, price, 0)
    
    ticker = yf.Ticker(品种代码)
    data = ticker.history(period="1d")
    if not data.empty:
        price = float(data['Close'].iloc[-1])
        return 行情数据(品种代码, price, price, price, price, 0)
    
    # 如果都失败，抛出异常（不降级）
    raise Exception(f"无法获取 {品种代码} 的实时价格")
