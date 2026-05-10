# -*- coding: utf-8 -*-
import random

class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0

def 获取价格(品种代码):
    演示价格 = {
        "300750.SZ": 437.00, "002415.SZ": 35.55, "000333.SZ": 80.40,
        "AAPL": 175.00, "TSLA": 240.00, "NVDA": 120.00,
        "BTC-USD": 45000, "ETH-USD": 2300,
        "GC=F": 1950, "CL=F": 95, "EURUSD": 1.08, "GBPUSD=X": 1.27,
    }
    价格 = 演示价格.get(品种代码, 100)
    价格 = 价格 * (1 + random.uniform(-0.005, 0.005))
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
