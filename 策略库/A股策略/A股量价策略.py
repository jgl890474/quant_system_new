# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类

class AStockVolumePriceStrategy(策略基类):
    """
    A股量价策略 - 真正考虑成交量的策略
    买入条件: 价格上涨 + 成交量放大
    卖出条件: 价格下跌 + 成交量萎缩
    """
    
    def __init__(self, 名称, 品种, 初始资金, 量比周期=5, 价格周期=5):
        super().__init__(名称, 品种, 初始资金)
        self.量比周期 = 量比周期
        self.价格周期 = 价格周期
        self.价格历史 = []
        self.成交量历史 = []
    
    def 处理行情(self, k线):
        # 记录历史数据
        self.价格历史.append(k线['close'])
        self.成交量历史.append(k线['volume'])
        
        if len(self.价格历史) < max(self.价格周期, self.量比周期):
            return 'hold'
        
        # 计算价格变化
        当前价格 = self.价格历史[-1]
        之前价格 = self.价格历史[-self.价格周期]
        价格变化率 = (当前价格 - 之前价格) / 之前价格 if 之前价格 > 0 else 0
        
        # 计算量比（当前成交量 / 平均成交量）
        平均成交量 = sum(self.成交量历史[-self.量比周期:]) / self.量比周期
        当前成交量 = self.成交量历史[-1]
        量比 = 当前成交量 / 平均成交量 if 平均成交量 > 0 else 1
        
        # 量价判断
        if 价格变化率 > 0.02 and 量比 > 1.5:
            return 'buy'      # 价涨量增 → 买入
        elif 价格变化率 < -0.02 and 量比 < 0.7:
            return 'sell'     # 价跌量缩 → 卖出
        elif 价格变化率 > 0.05 and 量比 > 2.0:
            return 'buy'      # 强势突破 → 买入
        
        return 'hold'
