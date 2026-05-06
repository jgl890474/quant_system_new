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
                 atr周期=14, 趋势阈值=0.01):
        super().__init__(名称, 品种, 初始资金)
        self.ema快 = ema快
        self.ema慢 = ema慢
        self.ema信号 = ema信号
        self.macd快 = macd快
        self.macd慢 = macd慢
        self.macd信号 = macd信号
        self.atr周期 = atr周期
        self.趋势阈值 = 趋势阈值
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
        
        # 计算信号线（MACD的9日EMA）
        macd历史 = []
        for i in range(min(self.macd信号, len(self.价格历史) - self.macd慢)):
            idx = -(self.macd信号 - i)
            if abs(idx) <= len(self.价格历史):
                prev_ema12 = self.计算EMA(self.macd快)
                prev_ema26 = self.计算EMA(self.macd慢)
                macd历史.append(prev_ema12 - prev_ema26)
        
        if macd历史:
            信号线 = sum(macd历史) / len(macd历史)
        else:
            信号线 = 0
        
        return macd线, 信号线
    
    def 计算ATR(self):
        """计算ATR（平均真实波幅）"""
        if len(self.价格历史) < self.atr周期 + 1:
            return 0
        
        true_ranges = []
        for i in range(1, len(self.价格历史)):
            high = max(self.价格历史[i], self.价格历史[i-1])
            low = min(self.价格历史[i], self.价格历史[i-1])
            true_ranges.append(high - low)
        
        return np.mean(true_ranges[-self.atr周期:])
    
    def 计算趋势强度(self):
        """计算趋势强度"""
        if len(self.价格历史) < self.ema信号:
            return 0
        
        ema快线 = self.计算EMA(self.ema快)
        ema慢线 = self.计算EMA(self.ema慢)
        
        if ema慢线 == 0:
            return 0
        
        return abs(ema快线 - ema慢线) / ema慢线
    
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
        
        # 计算趋势强度
        趋势强度 = self.计算趋势强度()
        
        # 计算ATR
        atr = self.计算ATR()
        
        当前价格 = k线['close']
        
        # ========== 买入条件 ==========
        # 条件1：无持仓
        # 条件2：EMA多头排列（价格 > 快线 > 慢线 > 信号线）
        # 条件3：MACD金叉（MACD线 > 信号线）
        # 条件4：趋势强度足够
        if self.持仓 == 0:
            if (当前价格 > ema快线 > ema慢线 > ema信号线和 
                趋势强度 > self.趋势阈值和 
                macd线 > macd信号线):
                return 'buy'
        
        # ========== 卖出条件 ==========
        # 条件1：有持仓
        # 条件2：EMA空头排列（价格 < 快线 < 慢线 < 信号线）
        # 条件3：MACD死叉（MACD线 < 信号线）
        if self.持仓 > 0:
            if (当前价格 < ema快线 < ema慢线 < ema信号线和 
                macd线 < macd信号线):
                return 'sell'
        
        return 'hold'
