# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class ForexCarryStrategy(策略基类):
    """外汇利差策略"""
    
    def __init__(self, 名称, 品种, 初始资金, 均线周期=20):
        super().__init__(名称, 品种, 初始资金)
        self.均线周期 = 均线周期
        self.价格历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.均线周期:
            return 'hold'
        
        均线 = sum(self.价格历史[-self.均线周期:]) / self.均线周期
        当前价格 = k线['close']
        
        if self.持仓 == 0 and 当前价格 > 均线:
            return 'buy'
        
        if self.持仓 > 0 and 当前价格 < 均线:
            return 'sell'
        
        return 'hold'
