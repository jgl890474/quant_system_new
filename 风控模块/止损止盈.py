from .风控基类 import 风控基类

class 止损止盈(风控基类):
    
    def __init__(self, 止盈=0.05, 止损=0.03):
        self.止盈 = 止盈
        self.止损 = 止损
    
    def 检查开仓(self, 代码, 价格, 账户):
        return True, "通过"
    
    def 检查平仓(self, 持仓, 当前价):
        盈亏 = (当前价 - 持仓['买入价']) / 持仓['买入价']
        if 盈亏 >= self.止盈:
            return True, f"止盈卖出，盈利{盈亏:.2%}", 当前价
        elif 盈亏 <= -self.止损:
            return True, f"止损卖出，亏损{盈亏:.2%}", 当前价
        return False, "", 0