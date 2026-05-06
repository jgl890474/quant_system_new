# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class HKStockBreakoutStrategy(策略基类):
    """港股突破策略"""
    
    def __init__(self, 名称, 品种, 初始资金, 观察周期=20, 突破倍数=1.02):
        super().__init__(名称, 品种, 初始资金)
        self.观察周期 = 观察周期
        self.突破倍数 = 突破倍数
        self.价格历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        if len(self.价格历史) < self.观察周期:
            return 'hold'
        
        近期高点 = max(self.价格历史[-self.观察周期:])
        当前价格 = k线['close']
        
        if self.持仓 == 0 and 当前价格 > 近期高点 * self.突破倍数:
            return 'buy'
        
        if self.持仓 > 0 and 当前价格 < 近期高点:
            return 'sell'
        
        return 'hold'
