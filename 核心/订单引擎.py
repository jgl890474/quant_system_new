# -*- coding: utf-8 -*-
"""
订单引擎 - 最简版
"""

class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.可用资金 = 初始资金
        self.持仓 = {}
    
    def 买入(self, 品种, 价格, 数量, 策略名称="手动"):
        if 价格 <= 0 or 数量 <= 0:
            return {"success": False, "error": "价格或数量无效"}
        
        花费 = 价格 * 数量
        if 花费 > self.可用资金:
            return {"success": False, "error": f"资金不足"}
        
        if 品种 in self.持仓:
            self.持仓[品种]["数量"] += 数量
        else:
            self.持仓[品种] = {"数量": 数量, "成本": 价格}
        
        self.可用资金 -= 花费
        return {"success": True, "message": f"买入成功 {品种} {数量} @ {价格}"}
    
    def 卖出(self, 品种, 价格, 数量, 策略名称="手动"):
        if 品种 not in self.持仓:
            return {"success": False, "error": "无此持仓"}
        
        if 数量 > self.持仓[品种]["数量"]:
            return {"success": False, "error": "数量不足"}
        
        收入 = 价格 * 数量
        self.持仓[品种]["数量"] -= 数量
        
        if self.持仓[品种]["数量"] <= 0:
            del self.持仓[品种]
        
        self.可用资金 += 收入
        return {"success": True, "message": f"卖出成功 {品种} {数量} @ {价格}"}
    
    def 获取可用资金(self):
        return self.可用资金
    
    def 获取总资产(self):
        return self.可用资金


def 创建订单引擎(初始资金=1000000):
    return 订单引擎(初始资金)
