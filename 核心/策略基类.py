# -*- coding: utf-8 -*-
"""
加密风控策略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from 核心.策略基类 import 策略基类


class 加密风控策略(策略基类):
    """加密货币风控策略"""
    
    # 策略元数据
    策略名称 = "加密风控策略"
    策略类别 = "加密货币策略"
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
        # 策略参数
        self.单笔仓位比例 = 0.01
        self.杠杆倍数 = 20
        
    def 处理行情(self, k线):
        # 策略逻辑
        return 'hold'
