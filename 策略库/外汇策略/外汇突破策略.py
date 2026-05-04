# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..策略基类 import BaseStrategy

class ForexBreakoutStrategy(BaseStrategy):
    """外汇突破策略：20周期高低点突破"""
    
    def __init__(self, name, symbol, initial_capital, lookback=20):
        super().__init__(name, symbol, initial_capital)
        self.lookback = lookback
        self.highs = []
        self.lows = []
        
    def on_data(self, kline):
        self.highs.append(kline['high'])
        self.lows.append(kline['low'])
        
        if len(self.highs) < self.lookback:
            return 'hold'
        
        highest = max(self.highs[-self.lookback:])
        lowest = min(self.lows[-self.lookback:])
        price = kline['close']
        
        if price > highest:
            return 'buy'
        elif price < lowest:
            return 'sell'
        return 'hold'