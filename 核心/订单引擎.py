# -*- coding: utf-8 -*-

class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.可用资金 = 初始资金
        self.持仓 = {}
    
    def 买入(self, 品种, 价格, 数量, 策略名称=""):
        if 价格 <= 0 or 数量 <= 0:
            return {"success": False}
        花费 = 价格 * 数量
        if 花费 > self.可用资金:
            return {"success": False}
        self.持仓[品种] = {"数量": 数量, "成本": 价格}
        self.可用资金 -= 花费
        return {"success": True}
    
    def 卖出(self, 品种, 价格, 数量, 策略名称=""):
        if 品种 not in self.持仓:
            return {"success": False}
        if 数量 > self.持仓[品种]["数量"]:
            return {"success": False}
        self.持仓[品种]["数量"] -= 数量
        if self.持仓[品种]["数量"] <= 0:
            del self.持仓[品种]
        self.可用资金 += 价格 * 数量
        return {"success": True}
    
    def 获取可用资金(self):
        return self.可用资金
