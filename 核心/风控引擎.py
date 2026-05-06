# -*- coding: utf-8 -*-

class 风控引擎:
    def __init__(self, 最大仓位比例=0.3, 止损比例=0.02, 止盈比例=0.04):
        self.最大仓位比例 = 最大仓位比例
        self.止损比例 = 止损比例
        self.止盈比例 = 止盈比例
        self.当日盈亏 = 0
    
    def 允许交易(self, 品种, 方向, 数量, 价格, 总资金):
        持仓价值 = 数量 * 价格
        if 总资金 > 0 and 持仓价值 / 总资金 > self.最大仓位比例:
            return False, "仓位超限"
        return True, "通过"
