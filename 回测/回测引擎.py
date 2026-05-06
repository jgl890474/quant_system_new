# -*- coding: utf-8 -*-

class 回测引擎:
    def __init__(self, 初始资金=100000):
        self.初始资金 = 初始资金
        self.结果 = []
    
    def 运行(self, 策略, 历史数据):
        return {"总收益率": 0, "夏普比率": 0, "最大回撤": 0}
