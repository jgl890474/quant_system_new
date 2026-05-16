# -*- coding: utf-8 -*-
"""
加密双均线策略 - 测试版（随时买入）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class 加密双均线1(策略基类):
    """加密双均线策略 - 测试版"""
    
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
        print(f"✅ 策略初始化: {名称} - {品种}")
    
    def 处理行情(self, k线):
        """测试逻辑：没有持仓就买入，有持仓就卖出"""
        当前价 = k线.get('close', 0)
        
        if 当前价 <= 0:
            return 'hold'
        
        # 没有持仓 → 买入
        if self.持仓 == 0:
            print(f"   🟢 [{self.名称}] 无持仓 → 买入信号")
            return 'buy'
        
        # 有持仓 → 卖出
        if self.持仓 > 0:
            print(f"   🔴 [{self.名称}] 有持仓 → 卖出信号")
            return 'sell'
        
        return 'hold'
    
    def 计算仓位(self, 总资金, 当前价):
        """每次买入10%资金"""
        数量 = 总资金 * 0.10 / 当前价
        print(f"   📊 买入数量: {数量:.4f}")
        return round(数量, 4)
