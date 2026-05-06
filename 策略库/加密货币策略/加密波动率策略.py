# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class CryptoVolatilityStrategy(策略基类):
    """
    加密货币波动率自适应策略
    根据市场波动自动调整参数
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 基础周期=20, 波动率周期=14,
                 rsi周期=14, 波动率阈值=0.03):
        super().__init__(名称, 品种, 初始资金)
        self.基础周期 = 基础周期
        self.波动率周期 = 波动率周期
        self.rsi周期 = rsi周期
        self.波动率阈值 = 波动率阈值
        self.价格历史 = []
        self.成交量历史 = []
    
    def 计算波动率(self):
        """计算历史波动率"""
        if len(self.价格历史) < self.波动率周期 + 1:
            return 0
        
        收益率 = []
        for i in range(1, len(self.价格历史)):
            ret = (self.价格历史[i] - self.价格历史[i-1]) / self.价格历史[i-1]
            收益率.append(ret)
        
        return np.std(收益率[-self.波动率周期:]) * np.sqrt(365)
    
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
    
    def 计算动态周期(self):
        """根据波动率动态调整周期"""
        波动率 = self.计算波动率()
        if 波动率 > self.波动率阈值:
            return int(self.基础周期 * 0.5)  # 高波动 → 更短周期
        else:
            return int(self.基础周期 * 1.5)  # 低波动 → 更长周期
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        self.成交量历史.append(k线['volume'])
        
        if len(self.价格历史) < self.基础周期 * 2:
            return 'hold'
        
        # 动态调整周期
        动态周期 = self.计算动态周期()
        
        # 计算动态均线
        短周期 = max(3, int(动态周期 * 0.3))
        长周期 = 动态周期
        
        短均线 = sum(self.价格历史[-短周期:]) / 短周期
        长均线 = sum(self.价格历史[-长周期:]) / 长周期
        
        rsi = self.计算RSI()
        波动率 = self.计算波动率()
        
        # 高波动时更谨慎
        if 波动率 > self.波动率阈值:
            # 只在极值位置交易
            if 短均线 > 长均线和 rsi < 35 and self.持仓 == 0:
                return 'buy'
            elif 短均线 < 长均线和 rsi > 65 and self.持仓 > 0:
                return 'sell'
        else:
            # 正常波动
            if 短均线 > 长均线和 rsi < 50 and self.持仓 == 0:
                return 'buy'
            elif 短均线 < 长均线和 rsi > 50 and self.持仓 > 0:
                return 'sell'
        
        return 'hold'
