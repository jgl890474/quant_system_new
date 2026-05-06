# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class HKStockBreakoutStrategy(策略基类):
    """
    港股突破交易策略（简洁实用版）
    关键价位突破 + RSI过滤
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 观察周期=20, 突破倍数=1.02,
                 rsi周期=14, rsi超买=70):
        super().__init__(名称, 品种, 初始资金)
        self.观察周期 = 观察周期
        self.突破倍数 = 突破倍数
        self.rsi周期 = rsi周期
        self.rsi超买 = rsi超买
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
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.观察周期:
            return 'hold'
        
        # 计算近期高点和低点
        近期高点 = max(self.价格历史[-self.观察周期:])
        近期低点 = min(self.价格历史[-self.观察周期:])
        
        当前价格 = k线['close']
        rsi = self.计算RSI()
        
        # 买入：向上突破近期高点 + RSI不超买
        if self.持仓 == 0:
            if 当前价格 > 近期高点 * self.突破倍数 and rsi < self.rsi超买:
                return 'buy'
        
        # 卖出：跌破近期低点 或 RSI超买
        if self.持仓 > 0:
            if 当前价格 < 近期低点 or rsi > self.rsi超买:
                return 'sell'
        
        return 'hold'
