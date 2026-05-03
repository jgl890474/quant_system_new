# 文件位置: quant_system_v5/策略库/期货策略2.py
# 布林带均值回归策略

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 策略引擎.strategy_base import BaseStrategy

class FuturesMeanReversionStrategy(BaseStrategy):
    """期货均值回归策略 - 布林带上下轨"""
    
    def __init__(self, name, symbol, initial_capital, window=20, num_std=2):
        super().__init__(name, symbol, initial_capital)
        self.window = window
        self.num_std = num_std
        self.price_history = []
        
    def on_data(self, data):
        price = data.get('close', data.get('price'))
        self.price_history.append(price)
        
        if len(self.price_history) < self.window:
            return 'hold'
        
        # 取最近window个价格
        prices = self.price_history[-self.window:]
        mean = sum(prices) / self.window
        
        # 计算标准差
        variance = sum((p - mean) ** 2 for p in prices) / self.window
        std = math.sqrt(variance)
        
        upper = mean + self.num_std * std
        lower = mean - self.num_std * std
        
        # 布林带逻辑：触及下轨买入，上轨卖出
        if price <= lower:
            return 'buy'
        elif price >= upper:
            return 'sell'
        return 'hold'