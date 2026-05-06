# -*- coding: utf-8 -*-
import random
import yfinance as yf
from .数据模型 import 行情数据

def 获取价格(品种):
    """获取实时行情，优先yfinance，失败时降级到模拟数据"""
    try:
        # 品种映射到yfinance代码
        代码映射 = {
            "EURUSD": "EURUSD=X",
            "BTC-USD": "BTC-USD",
            "GC=F": "GC=F",
            "000001.SS": "000001.SS",
            "00700.HK": "0700.HK",
            "AAPL": "AAPL",
        }
        
        代码 = 代码映射.get(品种, 品种)
        
        # 获取实时数据
        股票 = yf.Ticker(代码)
        历史数据 = 股票.history(period="1d", interval="1m")
        
        if 历史数据 is not None and len(历史数据) > 0:
            最新 = 历史数据.iloc[-1]
            return 行情数据(
                品种=品种,
                价格=float(最新['Close']),
                最高=float(最新['High']),
                最低=float(最新['Low']),
                开盘=float(最新['Open']),
                成交量=int(最新['Volume']) if 最新['Volume'] else 0
            )
    except Exception as e:
        print(f"获取真实行情失败: {e}")
    
    # 降级到模拟数据
    基准价格 = {
        "EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950,
        "000001.SS": 3000, "00700.HK": 350, "AAPL": 175
    }.get(品种, 100)
    
    return 行情数据(
        品种=品种,
        价格=基准价格 * (1 + random.uniform(-0.005, 0.005)),
        最高=基准价格 * 1.003,
        最低=基准价格 * 0.997,
        开盘=基准价格,
        成交量=1000
    )
