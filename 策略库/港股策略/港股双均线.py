# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class HKStockDualMAStrategy(策略基类):
    """
    港股双均线策略（增强版）
    增加趋势强度过滤 + 成交量确认
    """
    
    def __init__(self, 名称, 品种, 初始资金, 
                 短周期=5, 长周期=20,
                 趋势阈值=0.005, 成交量倍率=1.3):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.趋势阈值 = 趋势阈值
        self.成交量倍率 = 成交量倍率
        self.价格历史 = []
        self.成交量历史 = []
    
    def 计算成交量均值(self):
        """计算平均成交量"""
        if len(self.成交量历史) < self.长周期:
            return 0
        return np.mean(self.成交量历史[-self.长周期:])
    
    def 判断放量(self, 当前成交量):
        """判断是否为放量"""
        if len(self.成交量历史) < self.长周期:
            return False
        
        均量 = self.计算成交量均值()
        return 当前成交量 > 均量 * self.成交量倍率
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        self.成交量历史.append(k线['volume'])
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        当前成交量 = k线['volume']
        is_放量 = self.判断放量(当前成交量)
        
        # 计算趋势强度
        if 长均线 == 0:
            return 'hold'
        趋势强度 = abs(短均线 - 长均线) / 长均线
        
        # 趋势不够强时观望
        if 趋势强度 < self.趋势阈值:
            return 'hold'
        
        # 买入：金叉 + 放量
        if 短均线 > 长均线和 is_放量 and self.持仓 == 0:
            return 'buy'
        
        # 卖出：死叉
        elif 短均线 < 长均线和 self.持仓 > 0:
            return 'sell'
        
        return 'hold'
