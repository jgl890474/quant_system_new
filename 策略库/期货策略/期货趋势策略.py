# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..策略基类 import BaseStrategy

class FuturesTrendStrategy(BaseStrategy):
    """期货趋势策略：双均线趋势跟踪"""
    
    def __init__(self, name, symbol, initial_capital, short=10, long=30):
        super().__init__(name, symbol, initial_capital)
        self.short = short
        self.long = long
        self.prices = []
        
    def on_data(self, kline):
        self.prices.append(kline['close'])
        
        if len(self.prices) < self.long:
            return 'hold'
        
        short_ma = sum(self.prices[-self.short:]) / self.short
        long_ma = sum(self.prices[-self.long:]) / self.long
        
        if short_ma > long_ma:
            return 'buy'
        elif short_ma < long_ma:
            return 'sell'
        return 'hold'