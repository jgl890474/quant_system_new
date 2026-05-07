# 在买入方法中，确保持仓对象有当前价格
self.持仓[品种].当前价格 = 价格

# 在计算总资产时使用
def 获取总资产(self):
    总值 = self.初始资金
    for pos in self.持仓.values():
        # 确保当前价格已更新
        if hasattr(pos, '当前价格'):
            总值 += pos.数量 * pos.当前价格 - pos.数量 * pos.平均成本
        else:
            pos.当前价格 = pos.平均成本
    return 总值
