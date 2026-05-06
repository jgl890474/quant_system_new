# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import numpy as np


class FuturesTrendFollowStrategy(策略基类):
    """
    期货趋势跟踪策略
    使用EMA + MACD确认 + ATR动态止损
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 ema快=9, ema慢=21, ema信号=50,
                 macd快=12, macd慢=26, macd信号=9,
                 atr周期=14):
        super().__init__(名称, 品种, 初始资金)
        self.ema快 = ema快
        self.ema慢 = ema慢
        self.ema信号 = ema信号
        self.macd快 = macd快
        self.macd慢 = macd慢
        self.macd信号 = macd信号
        self.atr周期 = atr周期
        self.价格历史 = []
    
    def 计算EMA(self, period):
        """计算指数移动平均"""
        if len(self.价格历史) < period:
            return 0
        
        prices = self.价格历史[-period:]
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def 计算MACD(self):
        """计算MACD指标"""
        if len(self.价格历史) < self.macd慢:
            return 0, 0
        
        ema12 = self.计算EMA(self.macd快)
        ema26 = self.计算EMA(self.macd慢)
        macd线 = ema12 - ema26
        
        # 简化信号线
        if len(self.价格历史) >= self.macd信号 + 1:
            macd历史 = []
            for i in range(self.macd信号):
                prev_ema12 = self.计算EMA(self.macd快)
                prev_ema26 = self.计算EMA(self.macd慢)
                macd历史.append(prev_ema12 - prev_ema26)
            信号线 = sum(macd历史) / len(macd历史) if macd历史 else 0
        else:
            信号线 = 0
        
        return macd线, 信号线
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.ema信号:
            return 'hold'
        
        # 计算EMA
        ema快线 = self.计算EMA(self.ema快)
        ema慢线 = self.计算EMA(self.ema慢)
        ema信号线 = self.计算EMA(self.ema信号)
        
        # 计算MACD
        macd线, macd信号线 = self.计算MACD()
        
        当前价格 = k线['close']
        
        # 买入条件：EMA多头排列 + MACD金叉
        if (当前价格 > ema快线 > ema慢线 > ema信号线和 
            macd线 > macd信号线和 self.持仓 == 0):
            return 'buy'
        
        # 卖出条件：EMA空头排列 + MACD死叉
        elif (当前价格 < ema快线 < ema慢线 < ema信号线和 
              macd线 < macd信号线和 self.持仓 > 0):
            return 'sell'
        
        return 'hold'
