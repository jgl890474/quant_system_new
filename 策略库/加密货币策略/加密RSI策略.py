# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..策略基类 import BaseStrategy

class CryptoRSIStrategy(BaseStrategy):
    """加密货币RSI策略：超卖买入，超买卖出"""
    
    def __init__(self, name, symbol, initial_capital, period=14, oversold=30, overbought=70):
        super().__init__(name, symbol, initial_capital)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.prices = []
        
    def on_data(self, kline):
        self.prices.append(kline['close'])
        
        if len(self.prices) < self.period + 1:
            return 'hold'
        
        # 计算RSI
        gains = 0
        losses = 0
        for i in range(-self.period, 0):
            change = self.prices[i] - self.prices[i-1]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        avg_gain = gains / self.period
        avg_loss = losses / self.period if losses > 0 else 1
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        if rsi < self.oversold:
            return 'buy'
        elif rsi > self.overbought:
            return 'sell'
        return 'hold'