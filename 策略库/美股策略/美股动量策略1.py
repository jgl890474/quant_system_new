# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class USStockMomentumStrategy(策略基类):
    """美股动量策略"""
    
    def __init__(self, 名称, 品种, 初始资金, 短周期=10, 长周期=30):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.价格历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        
        if 短均线 > 长均线:
            return 'buy'
        elif 短均线 < 长均线:
            return 'sell'
        
        return 'hold'
