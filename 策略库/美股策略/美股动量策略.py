# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class USStockMomentumStrategy(策略基类):
    """
    美股动量轮动策略（简洁实用版）
    双均线 + 动量过滤
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 短周期=10, 长周期=30,
                 动量阈值=0.03):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.动量阈值 = 动量阈值
        self.价格历史 = []
    
    def 计算动量(self):
        """计算动量（N日收益率）"""
        if len(self.价格历史) < self.长周期:
            return 0
        
        当前价格 = self.价格历史[-1]
        前期价格 = self.价格历史[-self.长周期]
        
        return (当前价格 - 前期价格) / 前期价格 if 前期价格 > 0 else 0
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        动量 = self.计算动量()
        
        # 买入：金叉 + 正动量
        if self.持仓 == 0:
            if 短均线 > 长均线和 动量 > self.动量阈值:
                return 'buy'
        
        # 卖出：死叉 或 动量转负
        if self.持仓 > 0:
            if 短均线 < 长均线 or 动量 < 0:
                return 'sell'
        
        return 'hold'
