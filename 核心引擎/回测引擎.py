"""
事件驱动回测引擎
"""
import asyncio
import heapq
from datetime import datetime
import pandas as pd
import numpy as np

class 回测引擎:
    def __init__(self, 初始资金=1000000, 手续费率=0.0003, 滑点=0.001):
        self.初始资金 = 初始资金
        self.当前资金 = 初始资金
        self.手续费率 = 手续费率
        self.滑点 = 滑点
        self.事件队列 = []
        self.持仓 = {}
        self.成交记录 = []
        self.权益曲线 = []