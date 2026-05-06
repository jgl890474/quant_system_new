# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类

class ForexCarryStrategy(策略基类):
    """外汇利差策略"""
    
    def 处理行情(self, k线):
        if self.持仓 == 0:
            return 'buy'
        return 'hold'
