# 文件位置: quant_system_v5/策略库/外汇策略1.py
# 利差交易策略

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 策略引擎.strategy_base import BaseStrategy

class ForexCarryStrategy(BaseStrategy):
    """外汇利差交易策略 - 持有高息货币"""
    
    def __init__(self, name, symbol, initial_capital, interest_diff=0.02):
        super().__init__(name, symbol, initial_capital)
        self.interest_diff = interest_diff  # 年化利差2%
        self.days_held = 0
        
    def on_data(self, data):
        # 检查是否新的一天（用于计算利息）
        if data.get('is_new_day', False):
            self.days_held += 1
            # 每日计息
            daily_interest = self.capital * (self.interest_diff / 365)
            self.capital += daily_interest
        
        # 简单逻辑：持续持有
        if self.position == 0:
            return 'buy'
        return 'hold'