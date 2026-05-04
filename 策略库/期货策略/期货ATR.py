# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..策略基类 import BaseStrategy

class FuturesATRStrategy(BaseStrategy):
    """期货ATR突破策略：基于波动率的突破交易"""
    
    def __init__(self, name, symbol, initial_capital, period=14, multiplier=2):
        super().__init__(name, symbol, initial_capital)
        self.period = period
        self.multiplier = multiplier
        self.highs = []
        self.lows = []
        self.closes = []
        
    def on_data(self, kline):
        self.highs.append(kline['high'])
        self.lows.append(kline['low'])
        self.closes.append(kline['close'])
        
        if len(self.closes) < self.period + 1:
            return 'hold'
        
        # 计算 ATR
        tr_values = []
        for i in range(1, len(self.closes)):
            hl = self.highs[i] - self.lows[i]
            hc = abs(self.highs[i] - self.closes[i-1])
            lc = abs(self.lows[i] - self.closes[i-1])
            tr_values.append(max(hl, hc, lc))
        
        atr = sum(tr_values[-self.period:]) / self.period
        entry = self.closes[-1] + self.multiplier * atr
        
        if self.position == 0 and kline['close'] > entry:
            return 'buy'
        return 'hold'