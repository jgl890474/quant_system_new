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


class 持仓信息:
    def __init__(self, 品种, 数量, 平均成本, 当前价格=None):
        self.品种 = 品种
        self.数量 = 数量
        self.平均成本 = 平均成本
        self.当前价格 = 当前价格 if 当前价格 else 平均成本


class 交易记录:
    def __init__(self, 时间, 品种, 动作, 价格, 数量, 盈亏=0, 策略名称=""):
        self.时间 = 时间
        self.品种 = 品种
        self.动作 = 动作
        self.价格 = 价格
        self.数量 = 数量
        self.盈亏 = 盈亏
        self.策略名称 = 策略名称
