# -*- coding: utf-8 -*-
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
    """使用 yfinance 获取价格"""
    try:
        # 处理加密货币格式
        if 品种代码 == "BTC-USD":
            ticker_symbol = "BTC-USD"
        elif 品种代码 == "ETH-USD":
            ticker_symbol = "ETH-USD"
        elif 品种代码 == "GC=F":
            ticker_symbol = "GC=F"
        elif 品种代码 == "CL=F":
            ticker_symbol = "CL=F"
        elif 品种代码 == "EURUSD":
            ticker_symbol = "EURUSD=X"
        elif 品种代码 == "GBPUSD=X":
            ticker_symbol = "GBPUSD=X"
        else:
            ticker_symbol = 品种代码
        
        # 获取数据
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="1d")
        
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"[yfinance] {品种代码}: {price}")
            return 行情数据(品种代码, price, price, price, price, 0)
        else:
            print(f"[yfinance] {品种代码} 无数据")
            return 行情数据(品种代码, 0, 0, 0, 0, 0)
            
    except Exception as e:
        print(f"[yfinance] {品种代码} 错误: {e}")
        return 行情数据(品种代码, 0, 0, 0, 0, 0)
