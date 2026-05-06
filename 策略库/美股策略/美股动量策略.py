# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class USStockMomentumStrategy(策略基类):
    """
    美股动量轮动策略
    捕捉强势股趋势
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 短动量周期=20, 长动量周期=60,
                 rsi周期=14, 动量阈值=0.05):
        super().__init__(名称, 品种, 初始资金)
        self.短动量周期 = 短动量周期
        self.长动量周期 = 长动量周期
        self.rsi周期 = rsi周期
        self.动量阈值 = 动量阈值
        self.价格历史 = []
    
    def 计算动量(self):
        """计算动量指标"""
        if len(self.价格历史) < self.长动量周期:
            return 0, 0
        
        当前价格 = self.价格历史[-1]
        短前价格 = self.价格历史[-self.短动量周期] if len(self.价格历史) >= self.短动量周期 else 当前价格
        长前价格 = self.价格历史[-self.长动量周期]
        
        短动量 = (当前价格 - 短前价格) / 短前价格 if 短前价格 > 0 else 0
        长动量 = (当前价格 - 长前价格) / 长前价格 if 长前价格 > 0 else 0
        
        return 短动量, 长动量
    
    def 计算RSI(self):
        """计算RSI"""
        if len(self.价格历史) < self.rsi周期 + 1:
            return 50
        
        涨跌幅 = []
        for i in range(1, len(self.价格历史)):
            涨跌幅.append(self.价格历史[i] - self.价格历史[i-1])
        
        最近涨跌幅 = 涨跌幅[-self.rsi周期:]
        平均涨幅 = sum([x for x in 最近涨跌幅 if x > 0]) / self.rsi周期
        平均跌幅 = abs(sum([x for x in 最近涨跌幅 if x < 0])) / self.rsi周期
        
        if 平均跌幅 == 0:
            return 100
        RS = 平均涨幅 / 平均跌幅
        return 100 - (100 / (1 + RS))
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.长动量周期:
            return 'hold'
        
        短动量, 长动量 = self.计算动量()
        rsi = self.计算RSI()
        
        # 买入条件：短动量和长动量都为正且持续增强 + RSI健康
        if (短动量 > self.动量阈值 and 
            长动量 > 0 and 
            短动量 > 长动量和
            rsi > 30 and rsi < 70 and 
            self.持仓 == 0):
            return 'buy'
        
        # 卖出条件：动量减弱 或 RSI超买
        elif ((短动量 < self.动量阈值 / 2 or rsi > 75) and self.持仓 > 0):
            return 'sell'
        
        return 'hold'
