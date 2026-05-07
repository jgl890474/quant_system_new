# -*- coding: utf-8 -*-
"""
A股隔夜套利策略 - 自动执行脚本
运行方式: python 脚本/自动交易.py
或在 Streamlit Cloud 上通过定时任务触发
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime
from 工具.定时任务 import 定时任务, 是尾盘时间, 是早盘时间, 获取交易状态
from 核心 import 订单引擎, 策略加载器, AI引擎
from 策略库.A股策略.A股隔夜套利策略 import AStockOvernightStrategy


class 自动交易机器人:
    """自动交易机器人"""
    
    def __init__(self):
        self.引擎 = 订单引擎(初始资金=100000)
        self.策略加载器 = 策略加载器()
        self.AI引擎 = AI引擎()
        self.策略 = None
        self.今日已买入 = False
        self.昨日有持仓 = False
        self.品种 = "000001.SS"  # 上证指数，可改为具体股票代码
        
    def 初始化策略(self):
        """初始化隔夜套利策略"""
        self.策略 = AStockOvernightStrategy(
            名称="A股隔夜套利",
            品种=self.品种,
            初始资金=100000,
            买入时=14,      # 14:55
            买入分=55,
            卖出时=9,       # 09:30
            卖出分=30,
            最小涨幅=0.01,
            最大涨幅=0.05,
            成交量倍数=1.5,
            止损=0.03,
            止盈=0.05
        )
        print(f"✅ 策略初始化完成")
        print(f"   品种: {self.品种}")
        print(f"   买入窗口: 14:55-15:00")
        print(f"   卖出窗口: 09:30-09:35")
        print(f"   止损/止盈: 3% / 5%")
    
    def 尾盘买入检查(self):
        """尾盘买入检查"""
        if self.今日已买入:
            return
        
        if not 是尾盘时间():
            return
        
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 尾盘买入检查")
        
        try:
            from 核心 import 行情获取
            行情 = 行情获取.获取价格(self.品种)
            k线 = {
                'close': 行情.价格,
                'volume': 行情.成交量,
                'high': 行情.最高,
                'low': 行情.最低,
                'open': 行情.开盘
            }
            
            # 运行策略
            信号 = self.策略.处理行情(k线)
            
            if 信号 == 'buy':
                print(f"   🟢 触发买入信号")
                价格 = 行情.价格
                self.引擎.买入(self.品种, 价格)
                self.今日已买入 = True
                print(f"   ✅ 已买入 {self.品种} @ {价格:.2f}")
            else:
                print(f"   ⚪ 无买入信号")
                
        except Exception as e:
            print(f"   ❌ 买入检查失败: {e}")
    
    def 早盘卖出检查(self):
        """早盘卖出检查"""
        if not 是早盘时间():
            return
        
        print(f"\n💰 [{datetime.now().strftime('%H:%M:%S')}] 早盘卖出检查")
        
        try:
            from 核心 import 行情获取
            if self.品种 in self.引擎.持仓:
                print(f"   🟡 发现隔夜持仓")
                
                行情 = 行情获取.获取价格(self.品种)
                价格 = 行情.价格
                
                self.引擎.卖出(self.品种, 价格)
                self.今日已买入 = False
                print(f"   ✅ 已卖出 {self.品种} @ {价格:.2f}")
            else:
                print(f"   ⚪ 无隔夜持仓")
                
        except Exception as e:
            print(f"   ❌ 卖出检查失败: {e}")
    
    def 实时监控(self):
        """实时监控持仓（止损止盈）"""
        if not self.策略:
            return
        
        try:
            from 核心 import 行情获取
            
            for 品种, pos in self.引擎.持仓.items():
                行情 = 行情获取.获取价格(品种)
                k线 = {'close': 行情.价格, 'volume': 行情.成交量}
                
                信号 = self.策略.处理行情(k线)
                
                if 信号 == 'sell':
                    print(f"   🛑 止损/止盈触发: {品种}")
                    self.引擎.卖出(品种, 行情.价格)
                    
        except Exception as e:
            pass
    
    def 显示状态(self):
        """显示当前状态"""
        状态 = 获取交易状态()
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 交易状态: {状态}")
        print(f"   总资产: ¥{self.引擎.获取总资产():,.0f}")
        print(f"   持仓: {len(self.引擎.持仓)} 个品种")
        if self.引擎.持仓:
            for 品种, pos in self.引擎.持仓.items():
                print(f"     - {品种}: {pos.数量}股, 成本¥{pos.平均成本:.2f}")
    
    def 运行一次(self):
        """运行一次完整流程（用于手动测试）"""
        print("🚀 手动运行一次自动交易流程")
        print("="*50)
        
        self.初始化策略()
        self.尾盘买入检查()
        self.早盘卖出检查()
        self.实时监控()
        self.显示状态()
    
    def 运行循环(self):
        """运行自动交易循环"""
        print("🚀 A股隔夜套利策略 - 自动交易机器人启动")
        print("="*50)
        
        self.初始化策略()
        
        # 创建定时任务
        调度器 = 定时任务()
        
        # 添加定时任务
        调度器.添加任务(self.尾盘买入检查, "14:55")
        调度器.添加任务(self.早盘卖出检查, "09:30")
        调度器.添加间隔任务(self.实时监控, 60)   # 每分钟监控一次
        调度器.添加间隔任务(self.显示状态, 300)  # 每5分钟显示一次状态
        
        # 立即显示一次状态
        self.显示状态()
        
        # 启动调度器
        调度器.启动()


if __name__ == "__main__":
    机器人 = 自动交易机器人()
    
    # 判断是否传入参数
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        机器人.运行循环()
    else:
        机器人.运行一次()
