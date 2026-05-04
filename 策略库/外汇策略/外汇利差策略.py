# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..策略基类 import BaseStrategy

class ForexCarryStrategy(BaseStrategy):
    """外汇利差交易策略：长期持有利息较高的货币"""
    
    def __init__(self, name, symbol, initial_capital, interest_rate=0.02):
        super().__init__(name, symbol, initial_capital)
        self.interest_rate = interest_rate
        self.days_count = 0
        
    def on_data(self, kline):
        self.days_count += 1
        # 每日计息（模拟）
        if self.days_count % 1440 == 0:  # 假设1分钟K线，1440根=1天
            daily_interest = self.capital * (self.interest_rate / 365)
            self.capital += daily_interest
        
        # 简单逻辑：持续持有
        if self.position == 0:
            return 'buy'
        return 'hold'