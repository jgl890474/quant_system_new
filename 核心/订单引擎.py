def 获取总资产(self):
    总值 = self.初始资金
    for pos in self.持仓.values():
        总值 += pos.数量 * pos.当前价格 - pos.数量 * pos.平均成本
    return 总值

def 获取总盈亏(self):
    return self.获取总资产() - self.初始资金
