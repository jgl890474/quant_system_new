# -*- coding: utf-8 -*-
import sys
import os
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 策略库.策略基类 import BaseStrategy

class USStockBBStrategy(BaseStrategy):
    """美股布林带策略"""
    
    def __init__(self, name, symbol, initial_capital, window=20, num_std=2):
        super().__init__(name, symbol, initial_capital)
        self.window = window
        self.num_std = num_std
        self.prices = []
        
    def on_data(self, kline):
        self.prices.append(kline['close'])
        
        if len(self.prices) < self.window:
            return 'hold'
        
        recent = self.prices[-self.window:]
        mean = sum(recent) / self.window
        variance = sum((p - mean) ** 2 for p in recent) / self.window
        std = math.sqrt(variance)
        
        lower = mean - self.num_std * std
        
        if kline['close'] <= lower:
            return 'buy'
        return 'hold'
