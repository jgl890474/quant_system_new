# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class HKStockBreakoutStrategy(策略基类):
    """
    港股突破交易策略
    识别关键价位突破
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 观察周期=20, 突破倍数=1.02,
                 rsi周期=14, rsi阈值=70):
        super().__init__(名称, 品种, 初始资金)
        self.观察周期 = 观察周期
        self.突破倍数 = 突破倍数
        self.rsi周期 = rsi周期
        self.rsi阈值 = rsi阈值
        self.价格历史 = []
    
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
    
    def 计算关键价位(self):
        """计算关键支撑/阻力位"""
        if len(self.价格历史) < self.观察周期:
            return 0, 1000000
        
        最近价格 = self.价格历史[-self.观察周期:]
        阻力位 = max(最近价格)
        支撑位 = min(最近价格)
        
        return 支撑位, 阻力位
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.观察周期:
            return 'hold'
        
        支撑位, 阻力位 = self.计算关键价位()
        当前价格 = k线['close']
        rsi = self.计算RSI()
        
        # 向上突破阻力位 + RSI不超买 = 买入
        if 当前价格 > 阻力位 * self.突破倍数 and rsi < self.rsi阈值 and self.持仓 == 0:
            return 'buy'
        
        # 跌破支撑位 = 卖出
        elif 当前价格 < 支撑位 and self.持仓 > 0:
            return 'sell'
        
        # 高位RSI超买止盈
        elif rsi > self.rsi阈值 + 10 and self.持仓 > 0:
            return 'sell'
        
        return 'hold'
