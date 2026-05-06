# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class HKSimpleStrategy(策略基类):
    """港股简单策略 - 永远返回买入信号"""
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
    
    def 处理行情(self, k线):
        # 永远返回买入信号，用于测试
        return 'buy'
