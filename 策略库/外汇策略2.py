# 文件位置: quant_system_v5/策略库/外汇策略2.py
# 突破策略

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 策略引擎.strategy_base import BaseStrategy

class ForexBreakoutStrategy(BaseStrategy):
    """外汇突破策略 - 20周期高低点突破"""
    
    def __init__(self, name, symbol, initial_capital, lookback=20):
        super().__init__(name, symbol, initial_capital)
        self.lookback = lookback
        self.highs = []
        self.lows = []
        
    def on_data(self, data):
        high = data.get('high', data.get('close'))
        low = data.get('low', data.get('close'))
        close = data.get('close', data.get('price'))
        
        self.highs.append(high)
        self.lows.append(low)
        
        if len(self.highs) < self.lookback:
            return 'hold'
        
        highest = max(self.highs[-self.lookback:])
        lowest = min(self.lows[-self.lookback:])
        
        if close > highest:
            return 'buy'
        elif close < lowest:
            return 'sell'
        return 'hold'