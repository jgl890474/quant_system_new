# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 方式1：使用绝对导入
from 策略库.策略基类 import BaseStrategy

class ForexCarryStrategy(BaseStrategy):
    """外汇利差策略"""
    def on_data(self, kline):
        if self.position == 0:
            return 'buy'
        return 'hold'
