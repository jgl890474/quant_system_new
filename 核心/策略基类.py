# -*- coding: utf-8 -*-
"""策略基类 - 所有策略的父类"""

class 策略基类:
    """策略基类"""
    
    def __init__(self, 名称, 品种, 初始资金):
        self.名称 = 名称
        self.品种 = 品种
        self.初始资金 = 初始资金
        self.资金 = 初始资金
        self.持仓 = 0
        self.交易记录 = []
        self.价格历史 = []
        self.入场价 = 0
        self.入场时间 = None

    def 处理行情(self, k线):
        """处理行情数据，子类需要重写"""
        return 'hold'

    def 计算仓位(self, 总资金, 当前价):
        """计算开仓数量，子类可以重写"""
        数量 = 总资金 * 0.01 / 当前价
        return round(数量, 4)
