# -*- coding: utf-8 -*-
class 策略基类:
    def __init__(self, 名称, 品种, 初始资金):
        self.名称 = 名称
        self.品种 = 品种
        self.初始资金 = 初始资金
        self.资金 = 初始资金
        self.持仓 = 0

    def 处理行情(self, k线):
        return 'hold'
