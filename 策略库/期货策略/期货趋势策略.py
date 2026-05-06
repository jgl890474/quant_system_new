# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class FuturesTrendStrategy(策略基类):
    """
    期货趋势策略（简洁稳健版）
    增加趋势强度过滤
    """
    
    def __init__(self, 名称, 品种, 初始资金, 
                 短周期=10, 长周期=30,
                 趋势阈值=0.008):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.趋势阈值 = 趋势阈值
        self.价格历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        
        # 计算趋势强度
        趋势强度 = abs(短均线 - 长均线) / 长均线
        
        # 趋势不够强时观望
        if 趋势强度 < self.趋势阈值:
            return 'hold'
        
        if 短均线 > 长均线:
            return 'buy'
        elif 短均线 < 长均线:
            return 'sell'
        
        return 'hold'
