# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class ForexMultiTimeframeStrategy(策略基类):
    """外汇多时间框架策略"""
    
    def __init__(self, 名称, 品种, 初始资金, 
                 快周期=5, 慢周期=20, 
                 rsi周期=14, rsi超卖=30, rsi超买=70):
        super().__init__(名称, 品种, 初始资金)
        self.快周期 = 快周期
        self.慢周期 = 慢周期
        self.rsi周期 = rsi周期
        self.rsi超卖 = rsi超卖
        self.rsi超买 = rsi超买
        self.价格历史 = []
    
    def 计算RSI(self):
        if len(self.价格历史) < self.rsi周期 + 1:
            return 50
        
        涨跌幅 = []
        for i in range(1, len(self.价格历史)):
            涨跌幅.append(self.价格历史[i] - self.价格历史[i-1])
        
        最近涨跌幅 = 涨跌幅[-self.rsi周期:]
        平均涨幅 = sum([x for x in 最近涨跌幅 if x > 0]) / self.rsi周期
        平均跌幅 = abs(sum([x for x in 最近涨跌幅 if x < 0])) / self.rsi周期
        
        if 平均跌幅 == 0:
            return 100
        RS = 平均涨幅 / 平均跌幅
        return 100 - (100 / (1 + RS))
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.慢周期 + self.rsi周期:
            return 'hold'
        
        快均线 = sum(self.价格历史[-self.快周期:]) / self.快周期
        慢均线 = sum(self.价格历史[-self.慢周期:]) / self.慢周期
        rsi = self.计算RSI()
        
        if self.持仓 == 0:
            if 快均线 > 慢均线和 rsi < self.rsi超买:
                return 'buy'
        
        if self.持仓 > 0:
            if 快均线 < 慢均线 or rsi > self.rsi超买:
                return 'sell'
        
        return 'hold'
