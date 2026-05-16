# -*- coding: utf-8 -*-
"""
测试策略 - 随时买入
用于验证自动交易功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import random


class 测试策略随时买入(策略基类):
    """测试策略 - 只要没有持仓就买入"""
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
        self.名称 = 名称
        print(f"✅ 测试策略初始化: {名称} - {品种}")
    
    def 处理行情(self, k线):
        """简单逻辑：没有持仓就买入，有持仓就卖出"""
        当前价 = k线.get('close', 0)
        
        if 当前价 <= 0:
            return 'hold'
        
        # 策略1：如果没有持仓，立即买入
        if self.持仓 == 0:
            print(f"   🟢 [测试策略] 无持仓，发出买入信号，价格={当前价}")
            return 'buy'
        
        # 策略2：如果有持仓，立即卖出
        if self.持仓 > 0:
            print(f"   🔴 [测试策略] 有持仓，发出卖出信号，价格={当前价}")
            return 'sell'
        
        return 'hold'
    
    def 计算仓位(self, 总资金, 当前价):
        """计算买入数量：使用5%资金"""
        数量 = 总资金 * 0.05 / 当前价
        print(f"   📊 [测试策略] 计算仓位: 总资金={总资金:.0f}, 数量={数量:.4f}")
        return round(数量, 4)
