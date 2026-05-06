# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class USStockDualMAStrategy(策略基类):
    """
    美股双均线策略（增强版）
    双均线 + RSI过滤，避免追涨杀跌
    """
    
    def __init__(self, 名称, 品种, 初始资金, 
                 短周期=5, 长周期=20,
                 rsi周期=14, rsi超卖=30, rsi超买=70,
                 趋势阈值=0.005):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.rsi周期 = rsi周期
        self.rsi超卖 = rsi超卖
        self.rsi超买 = rsi超买
        self.趋势阈值 = 趋势阈值
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
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        
        # 计算趋势强度
        if 长均线 == 0:
            return 'hold'
        趋势强度 = abs(短均线 - 长均线) / 长均线
        
        # 计算RSI
        rsi = self.计算RSI()
        
        # 趋势不够强时观望
        if 趋势强度 < self.趋势阈值:
            return 'hold'
        
        # 买入：金叉 + RSI不超买（避免追高）
        if self.持仓 == 0:
            if 短均线 > 长均线和 rsi < self.rsi超买:
                return 'buy'
        
        # 卖出：死叉 或 RSI超买止盈
        if self.持仓 > 0:
            if 短均线 < 长均线 or rsi > self.rsi超买:
                return 'sell'
        
        return 'hold'
