# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
from datetime import datetime, time

class AStockOvernightStrategy(策略基类):
    """
    A股隔夜套利策略
    尾盘买入，早盘卖出，捕捉隔夜收益
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 买入时=14, 买入分=55,
                 卖出时=9, 卖出分=30,
                 最小涨幅=0.01, 最大涨幅=0.05,
                 成交量倍数=1.5,
                 止损=0.03, 止盈=0.05):
        super().__init__(名称, 品种, 初始资金)
        self.买入时 = 买入时
        self.买入分 = 买入分
        self.卖出时 = 卖出时
        self.卖出分 = 卖出分
        self.最小涨幅 = 最小涨幅
        self.最大涨幅 = 最大涨幅
        self.成交量倍数 = 成交量倍数
        self.止损 = 止损
        self.止盈 = 止盈
        self.价格历史 = []
        self.成交量历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        self.成交量历史.append(k线['volume'])
        
        if len(self.价格历史) < 20:
            return 'hold'
        
        # 简单示例：直接返回买入信号用于测试
        # 实际使用时可以根据时间和条件判断
        if self.持仓 == 0:
            return 'buy'
        else:
            return 'hold'
