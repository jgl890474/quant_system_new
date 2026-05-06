# -*- coding: utf-8 -*-
import random
from .数据模型 import 行情数据

def 获取价格(品种):
    try:
        from data.market_data import get_1min_kline
        k线 = get_1min_kline(品种)
        if k线:
            return 行情数据(品种, k线.get('close', 1.085), k线.get('high', 1.085), k线.get('low', 1.085), k线.get('open', 1.085), k线.get('volume', 0))
    except:
        pass
    
    基准价格 = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950, "000001.SS": 3000, "00700.HK": 350, "AAPL": 175}.get(品种, 100)
    return 行情数据(品种, 基准价格 * (1 + random.uniform(-0.005, 0.005)), 基准价格 * 1.003, 基准价格 * 0.997, 基准价格, 1000)
