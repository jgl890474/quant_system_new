# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略基类 import 策略基类
from datetime import datetime, time

class AStockOvernightStrategy(策略基类):
    """
    A股隔夜套利策略
    尾盘买入（14:55），早盘卖出（09:30）
    """
    
    def __init__(self, 名称, 品种, 初始资金,
                 买入时=14, 买入分=55,
                 卖出时=9, 卖出分=30,
                 最小涨幅=0.01, 最大涨幅=0.05,
                 成交量倍数=1.5,
                 止损=0.03, 止盈=0.05):
        super().__init__(名称, 品种, 初始资金)
        self.买入时 = 买入时
        self.买入分 = 买入分
        self.卖出时 = 卖出时
        self.卖出分 = 卖出分
        self.最小涨幅 = 最小涨幅
        self.最大涨幅 = 最大涨幅
        self.成交量倍数 = 成交量倍数
        self.止损 = 止损
        self.止盈 = 止盈
        self.价格历史 = []
        self.成交量历史 = []
        self.今日已买入 = False  # 添加今日买入标记
    
    def 获取当前时间(self):
        """获取当前时间"""
        return datetime.now()
    
    def 处理行情(self, k线):
        """处理行情数据，返回交易信号"""
        self.价格历史.append(k线['close'])
        self.成交量历史.append(k线['volume'])
        
        if len(self.价格历史) < 20:
            return 'hold'
        
        # ========== 测试模式：强制返回买入信号 ==========
        # 用于测试AI交易功能
        # 如果还没有买入，返回买入信号
        if not self.今日已买入:
            return 'buy'   # 强制买入
        else:
            return 'hold'
    
    def 重置每日状态(self):
        """重置每日状态（每天开盘前调用）"""
        self.今日已买入 = False
