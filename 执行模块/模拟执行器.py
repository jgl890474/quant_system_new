from .执行器基类 import 执行器基类

class 模拟执行器(执行器基类):
    
    def __init__(self):
        self.持仓 = {}
        self.现金 = 100000
    
    def 买入(self, 代码, 价格, 数量):
        if self.现金 < 价格 * 数量:
            return {"success": False, "error": "资金不足"}
        self.现金 -= 价格 * 数量
        self.持仓[代码] = {"数量": 数量, "成本": 价格}
        return {"success": True, "order_id": "sim_001"}
    
    def 卖出(self, 代码, 价格, 数量):
        if 代码 not in self.持仓:
            return {"success": False, "error": "无持仓"}
        self.现金 += 价格 * 数量
        del self.持仓[代码]
        return {"success": True}
    
    def 查询持仓(self):
        return self.持仓