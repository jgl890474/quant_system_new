# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class ForexCarryStrategy(策略基类):
    """
    外汇利差策略（优化版）
    基于均线趋势 + RSI 过滤，避免盲目买入
    """
    
    def __init__(self, 名称, 品种, 初始资金, 
                 短期均线=10, 长期均线=30,
                 rsi周期=14, rsi超卖=30, rsi超买=70):
        super().__init__(名称, 品种, 初始资金)
        self.短期均线 = 短期均线
        self.长期均线 = 长期均线
        self.rsi周期 = rsi周期
        self.rsi超卖 = rsi超卖
        self.rsi超买 = rsi超买
        self.价格历史 = []
    
    def 计算RSI(self):
        """计算RSI指标"""
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
        
        # 数据不足时观望
        if len(self.价格历史) < self.长期均线:
            return 'hold'
        
        # 计算均线
        短均线 = sum(self.价格历史[-self.短期均线:]) / self.短期均线
        长均线 = sum(self.价格历史[-self.长期均线:]) / self.长期均线
        
        # 计算RSI
        rsi = self.计算RSI()
        
        当前价格 = k线['close']
        
        # ========== 买入条件 ==========
        # 条件1：无持仓
        # 条件2：短均线上穿长均线（金叉）或 价格在均线上方
        # 条件3：RSI 处于超卖区域或中性（避免追高）
        if self.持仓 == 0:
            if (短均线 > 长均线和 
                rsi < self.rsi超买和 
                当前价格 > 长均线):
                return 'buy'
        
        # ========== 卖出条件 ==========
        # 条件1：有持仓
        # 条件2：短均线下穿长均线（死叉）或 RSI 超买
        if self.持仓 > 0:
            if 短均线 < 长均线:
                return 'sell'
            if rsi > self.rsi超买:
                return 'sell'
        
        return 'hold'
