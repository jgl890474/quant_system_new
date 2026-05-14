# -*- coding: utf-8 -*-
"""数据模型"""

class 行情数据:
    """行情数据类"""
    def __init__(self, 品种, 价格, 最高=0, 最低=0, 开盘=0, 成交量=0):
        self.品种 = 品种
        self.价格 = 价格
        self.最高 = 最高
        self.最低 = 最低
        self.开盘 = 开盘
        self.成交量 = 成交量


class 持仓数据:
    """持仓数据类"""
    def __init__(self, 品种, 数量, 平均成本):
        self.品种 = 品种
        self.数量 = 数量
        self.平均成本 = 平均成本
        self.当前价格 = 平均成本
