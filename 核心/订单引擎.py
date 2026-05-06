# 核心/订单引擎.py
class 订单引擎:
    def __init__(self):
        self.现金 = 100000
        self.持仓列表 = []
        self.交易记录 = []

    def 买入(self, 代码, 价格, 数量=1):
        cost = 价格 * 数量
        if self.现金 < cost:
            return False, "现金不足"
        
        self.持仓列表.append({
            "代码": 代码,
            "价格": 价格,
            "数量": 数量
        })
        self.现金 -= cost
        return True, f"买入成功 {代码} @ {价格}"

    def 卖出(self, 代码, 价格):
        for i, pos in enumerate(self.持仓列表):
            if pos["代码"] == 代码:
                self.现金 += 价格 * pos["数量"]
                del self.持仓列表[i]
                return True, f"卖出成功 {代码}"
        return False, "无持仓"

    def 获取持仓(self):
        return self.持仓列表

    def 获取现金(self):
        return self.现金
