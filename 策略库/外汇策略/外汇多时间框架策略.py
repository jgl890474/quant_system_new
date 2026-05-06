# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class ForexMultiTimeframeStrategy(策略基类):
    """
    外汇多时间框架确认策略
    结合快慢均线 + RSI + 趋势强度过滤
    """
    
    def __init__(self, 名称, 品种, 初始资金, 
                 快周期=5, 慢周期=20, 
                 rsi周期=14, rsi超卖=30, rsi超买=70,
                 atr周期=14, atr倍数=1.5):
        super().__init__(名称, 品种, 初始资金)
        self.快周期 = 快周期
        self.慢周期 = 慢周期
        self.rsi周期 = rsi周期
        self.rsi超卖 = rsi超卖
        self.rsi超买 = rsi超买
        self.atr周期 = atr周期
        self.atr倍数 = atr倍数
        self.价格历史 = []
        self.atr历史 = []
    
    def 计算RSI(self):
        """计算RSI"""
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
    
    def 计算ATR(self):
        """计算ATR（平均真实波幅）"""
        if len(self.价格历史) < self.atr周期 + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(self.价格历史)):
            high = max(self.价格历史[i], self.价格历史[i-1])
            low = min(self.价格历史[i], self.价格历史[i-1])
            true_ranges.append(high - low)
        
        return np.mean(true_ranges[-self.atr周期:])
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.慢周期 + self.rsi周期:
            return 'hold'
        
        # 计算均线
        快均线 = sum(self.价格历史[-self.快周期:]) / self.快周期
        慢均线 = sum(self.价格历史[-self.慢周期:]) / self.慢周期
        
        # 计算RSI
        rsi = self.计算RSI()
        
        # 计算ATR（用于止损参考）
        atr = self.计算ATR()
        
        当前价格 = k线['close']
        
        # 均线多头排列 + RSI不超买 = 买入信号
        if 快均线 > 慢均线和 rsi < self.rsi超买 and self.持仓 == 0:
            return 'buy'
        
        # 均线空头排列 + RSI不超卖 = 卖出信号
        elif 快均线 < 慢均线和 rsi > self.rsi超卖 and self.持仓 > 0:
            return 'sell'
        
        return 'hold'
