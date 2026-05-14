# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类


class CryptoDualMAStrategy(策略基类):
    """加密货币双均线策略"""
    
    # ========== 策略元数据（用于自动发现） ==========
    策略名称 = "加密双均线1"
    策略类别 = "加密货币策略"
    策略描述 = "双均线交叉策略"
    策略版本 = "1.0.0"
    
    def __init__(self, 名称, 品种, 初始资金, 短周期=5, 长周期=20):
        super().__init__(名称, 品种, 初始资金)
        self.短周期 = 短周期
        self.长周期 = 长周期
        self.价格历史 = []
    
    def 处理行情(self, k线):
        self.价格历史.append(k线['close'])
        
        if len(self.价格历史) < self.长周期:
            return 'hold'
        
        短均线 = sum(self.价格历史[-self.短周期:]) / self.短周期
        长均线 = sum(self.价格历史[-self.长周期:]) / self.长周期
        
        if 短均线 > 长均线:
            return 'buy'
        elif 短均线 < 长均线:
            return 'sell'
        
        return 'hold'


# 添加中文类名别名（用于策略发现器）
class 加密双均线1(CryptoDualMAStrategy):
    """中文别名"""
    pass
