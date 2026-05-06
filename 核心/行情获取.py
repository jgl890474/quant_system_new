# -*- coding: utf-8 -*-
import yfinance as yf
import random

def 获取价格(品种代码):
    """获取实时价格，失败时返回模拟数据"""
    try:
        映射表 = {
            "EURUSD": "EURUSD=X",
            "BTC-USD": "BTC-USD", 
            "GC=F": "GC=F",
            "AAPL": "AAPL",
            "MSFT": "MSFT",
            "00700.HK": "0700.HK",
        }
        代码 = 映射表.get(品种代码, 品种代码)
        
        # 尝试获取实时数据
        股票 = yf.Ticker(代码)
        数据 = 股票.history(period="2d")
        
        if not 数据.empty and len(数据) >= 1:
            价格 = float(数据['Close'].iloc[-1])
            return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
    except Exception as e:
        print(f"yfinance获取失败: {e}")
    
    # 返回模拟数据
    基准价格 = {"EURUSD": 1.08, "BTC-USD": 45000, "GC=F": 1950, "AAPL": 175, "MSFT": 330}.get(品种代码, 100)
    价格 = 基准价格 * (1 + random.uniform(-0.01, 0.01))
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)


class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = 价格
        self.最高 = 最高
        self.最低 = 最低
        self.开盘 = 开盘
        self.成交量 = 成交量
        self.涨跌 = 0
