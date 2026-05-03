# 文件位置: quant_system_v5/策略库/期货策略1.py
# 双均线趋势策略

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 策略引擎.strategy_base import BaseStrategy

class FuturesTrendStrategy(BaseStrategy):
    """期货趋势策略 - 双均线金叉/死叉"""
    
    def __init__(self, name, symbol, initial_capital, short_window=20, long_window=50):
        super().__init__(name, symbol, initial_capital)
        self.short_window = short_window
        self.long_window = long_window
        self.price_history = []
        
    def on_data(self, data):
        """
        策略逻辑：短期均线上穿长期均线买入，下穿卖出
        """
        price = data.get('close', data.get('price'))
        self.price_history.append(price)
        
        if len(self.price_history) < self.long_window:
            return 'hold'
        
        # 计算均线
        short_ma = sum(self.price_history[-self.short_window:]) / self.short_window
        long_ma = sum(self.price_history[-self.long_window:]) / self.long_window
        
        # 判断信号
        if short_ma > long_ma:
            return 'buy'
        elif short_ma < long_ma:
            return 'sell'
        return 'hold'