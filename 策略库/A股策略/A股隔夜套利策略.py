# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
import pandas as pd
import numpy as np
from datetime import datetime, time


class AStockOvernightStrategy(策略基类):
    """
    A股隔夜套利策略
    尾盘买入，早盘卖出，捕捉隔夜收益
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 买入时间=time(14, 55), 
                 卖出时间=time(9, 30),
                 最小涨幅=0.01,      # 当日最低涨幅 1%
                 最大涨幅=0.05,      # 当日最大涨幅 5%
                 最小成交量倍数=1.5,  # 成交量放大倍数
                 止损比例=0.03,      # 止损 3%
                 止盈比例=0.05):     # 止盈 5%
        super().__init__(名称, 品种, 初始资金)
        self.买入时间 = 买入时间
        self.卖出时间 = 卖出时间
        self.最小涨幅 = 最小涨幅
        self.最大涨幅 = 最大涨幅
        self.最小成交量倍数 = 最小成交量倍数
        self.止损比例 = 止损比例
        self.止盈比例 = 止盈比例
        
        # 记录隔夜持仓
        self.隔夜持仓 = {}
        self.今日买入 = []
        
        # 存储历史数据
        self.价格历史 = []
        self.成交量历史 = []
        self.日期历史 = []
    
    def 判断是否买入时间(self):
        """判断当前是否在买入时间窗口"""
        当前时间 = datetime.now().time()
        # 14:55 - 15:00 之间
        return 当前时间 >= self.买入时间和 当前时间 <= time(15, 0)
    
    def 判断是否卖出时间(self):
        """判断当前是否在卖出时间窗口"""
        当前时间 = datetime.now().time()
        # 9:30 - 9:35 之间
        return 当前时间 >= self.卖出时间和 当前时间 <= time(9, 35)
    
    def 计算当日涨幅(self, 当前价格):
        """计算当日涨幅"""
        if len(self.价格历史) < 2:
            return 0
        开盘价 = self.价格历史[0] if len(self.价格历史) > 0 else 当前价格
        return (当前价格 - 开盘价) / 开盘价
    
    def 计算成交量倍数(self, 当前成交量):
        """计算成交量相对均值的倍数"""
        if len(self.成交量历史) < 20:
            return 1
        平均成交量 = np.mean(self.成交量历史[-20:])
        if 平均成交量 == 0:
            return 1
        return 当前成交量 / 平均成交量
    
    def 选股条件(self, 当前价格, 当前成交量):
        """选股过滤条件"""
        # 1. 计算当日涨幅
        当日涨幅 = self.计算当日涨幅(当前价格)
        
        # 2. 计算成交量倍数
        成交量倍数 = self.计算成交量倍数(当前成交量)
        
        # 3. 条件判断
        if (self.最小涨幅 <= 当日涨幅 <= self.最大涨幅 and 
            成交量倍数 >= self.最小成交量倍数):
            return True, {
                "涨幅": f"{当日涨幅*100:.2f}%",
                "成交量倍数": f"{成交量倍数:.1f}x"
            }
        return False, {}
    
    def 处理行情(self, k线):
        """
        策略主逻辑
        返回: 'buy' / 'sell' / 'hold'
        """
        当前时间 = datetime.now()
        当前价格 = k线['close']
        当前成交量 = k线['volume']
        
        # 记录历史
        self.价格历史.append(当前价格)
        self.成交量历史.append(当前成交量)
        self.日期历史.append(当前时间)
        
        # 限制历史长度
        if len(self.价格历史) > 100:
            self.价格历史 = self.价格历史[-100:]
            self.成交量历史 = self.成交量历史[-100:]
        
        # ========== 买入信号 ==========
        if self.判断是否买入时间和 self.持仓 == 0:
            # 选股过滤
            符合条件, 指标 = self.选股条件(当前价格, 当前成交量)
            
            if 符合条件:
                print(f"📈 买入信号触发: {指标}")
                return 'buy'
        
        # ========== 卖出信号 ==========
        if self.持仓 > 0:
            # 1. 时间触发卖出（早盘）
            if self.判断是否卖出时间():
                print(f"⏰ 时间触发卖出: 隔夜持仓")
                return 'sell'
            
            # 2. 止损检查
            当前盈亏率 = (当前价格 - self.平均成本) / self.平均成本
            if 当前盈亏率 <= -self.止损比例:
                print(f"🛑 止损触发: 亏损 {当前盈亏率*100:.2f}%")
                return 'sell'
            
            # 3. 止盈检查
            if 当前盈亏率 >= self.止盈比例:
                print(f"🎯 止盈触发: 盈利 {当前盈亏率*100:.2f}%")
                return 'sell'
        
        return 'hold'
    
    def 获取策略状态(self):
        """获取策略运行状态"""
        return {
            "买入时间窗口": f"{self.买入时间.strftime('%H:%M')} - 15:00",
            "卖出时间窗口": f"{self.卖出时间.strftime('%H:%M')} - 09:35",
            "选股条件": f"涨幅 {self.最小涨幅*100:.0f}%-{self.最大涨幅*100:.0f}%, 成交量 > {self.最小成交量倍数}x",
            "风控": f"止损 {self.止损比例*100:.0f}%, 止盈 {self.止盈比例*100:.0f}%",
            "今日买入": len(self.今日买入),
            "隔夜持仓": len(self.隔夜持仓)
        }
