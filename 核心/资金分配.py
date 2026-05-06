# -*- coding: utf-8 -*-

class 资金分配器:
    def __init__(self, 总资金):
        self.总资金 = 总资金
    
    def 分配(self, 策略列表):
        if not 策略列表:
            return
        per = self.总资金 // len(策略列表)
        for s in 策略列表:
            s.初始资金 = per
            s.资金 = per
