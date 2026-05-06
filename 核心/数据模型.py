# -*- coding: utf-8 -*-
class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = 价格
        self.最高 = 最高
        self.最低 = 最低
        self.开盘 = 开盘
        self.成交量 = 成交量
        self.涨跌 = 0

class 持仓数据:
    def __init__(self, 品种, 数量, 平均成本):
        self.品种 = 品种
        self.数量 = 数量
        self.平均成本 = 平均成本
        self.当前价格 = 平均成本
        self.已实现盈亏 = 0
