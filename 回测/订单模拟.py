# -*- coding: utf-8 -*-
from datetime import datetime


class 订单:
    """订单类"""
    def __init__(self, 订单ID, 品种, 方向, 价格, 数量, 订单类型="限价单"):
        self.id = 订单ID
        self.品种 = 品种
        self.方向 = 方向  # buy / sell
        self.价格 = 价格
        self.数量 = 数量
        self.类型 = 订单类型  # 限价单 / 市价单
        self.状态 = "挂单"  # 挂单 / 成交 / 取消
        self.成交价格 = None
        self.成交时间 = None
        self.创建时间 = datetime.now()


class 订单簿:
    """订单簿模拟器"""
    
    def __init__(self, 滑点基点=0.0001, 手续费率=0.0005):
        self.挂买单 = []  # 买单列表
        self.挂卖单 = []  # 卖单列表
        self.历史订单 = []
        self.订单计数器 = 0
        self.滑点基点 = 滑点基点
        self.手续费率 = 手续费率
    
    def 创建订单(self, 品种, 方向, 价格, 数量, 订单类型="限价单"):
        """创建新订单"""
        self.订单计数器 += 1
        订单对象 = 订单(self.订单计数器, 品种, 方向, 价格, 数量, 订单类型)
        return 订单对象
    
    def 提交订单(self, 订单对象, 当前价格, 当前时间):
        """提交订单到订单簿"""
        if 订单对象.类型 == "市价单":
            return self._执行市价单(订单对象, 当前价格, 当前时间)
        else:
            return self._挂单(订单对象, 当前价格, 当前时间)
    
    def _执行市价单(self, 订单对象, 当前价格, 当前时间):
        """执行市价单（加滑点）"""
        滑点 = 当前价格 * self.滑点基点
        
        if 订单对象.方向 == "buy":
            成交价 = 当前价格 + 滑点
        else:
            成交价 = 当前价格 - 滑点
        
        手续费 = 成交价 * 订单对象.数量 * self.手续费率
        
        订单对象.状态 = "成交"
        订单对象.成交价格 = 成交价
        订单对象.成交时间 = 当前时间
        
        return {
            "成交": True,
            "成交价": 成交价,
            "数量": 订单对象.数量,
            "手续费": 手续费,
            "订单": 订单对象
        }
    
    def _挂单(self, 订单对象, 当前价格, 当前时间):
        """挂限价单"""
        if 订单对象.方向 == "buy":
            self.挂买单.append(订单对象)
            self.挂买单.sort(key=lambda x: -x.价格)
        else:
            self.挂卖单.append(订单对象)
            self.挂卖单.sort(key=lambda x: x.价格)
        
        return {
            "成交": False,
            "成交价": None,
            "数量": 0,
            "手续费": 0,
            "订单": 订单对象
        }
    
    def 撮合(self, 品种, 当前价格, 当前时间):
        """撮合限价单"""
        成交记录 = []
        
        # 撮合买单
        while self.挂买单 and self.挂买单[0].价格 >= 当前价格:
            买单 = self.挂买单.pop(0)
            手续费 = 当前价格 * 买单.数量 * self.手续费率
            成交记录.append({
                "订单": 买单,
                "成交价": 当前价格,
                "数量": 买单.数量,
                "手续费": 手续费
            })
        
        # 撮合卖单
        while self.挂卖单 and self.挂卖单[0].价格 <= 当前价格:
            卖单 = self.挂卖单.pop(0)
            手续费 = 当前价格 * 卖单.数量 * self.手续费率
            成交记录.append({
                "订单": 卖单,
                "成交价": 当前价格,
                "数量": 卖单.数量,
                "手续费": 手续费
            })
        
        return 成交记录
    
    def 取消订单(self, 订单ID):
        """取消订单"""
        for i, 订单 in enumerate(self.挂买单):
            if 订单.id == 订单ID:
                self.挂买单.pop(i)
                return True
        for i, 订单 in enumerate(self.挂卖单):
            if 订单.id == 订单ID:
                self.挂卖单.pop(i)
                return True
        return False
