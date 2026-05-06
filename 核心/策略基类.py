# -*- coding: utf-8 -*-

class 策略基类:
    def __init__(self, 名称, 品种, 初始资金):
        self.名称 = 名称
        self.品种 = 品种
        self.初始资金 = 初始资金
        self.资金 = 初始资金
        self.持仓 = 0
        self.交易记录 = []
        self.价格历史 = []
        
    def 处理行情(self, k线):
        return 'hold'
    
    def 执行信号(self, 信号, 价格):
        if 信号 == 'buy' and self.资金 >= 价格:
            self.持仓 += 1
            self.资金 -= 价格
            self.交易记录.append(('买入', 价格))
        elif 信号 == 'sell' and self.持仓 > 0:
            self.持仓 -= 1
            self.资金 += 价格
            self.交易记录.append(('卖出', 价格))
