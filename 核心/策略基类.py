# -*- coding: utf-8 -*-
"""
策略基类 - 所有策略的父类
"""

from abc import ABC, abstractmethod
from datetime import datetime


class 策略基类:
    """策略基类 - 所有策略的父类"""
    
    # ========== 策略元数据（子类可覆盖，用于自动发现） ==========
    策略名称 = "基础策略"           # 策略显示名称
    策略类别 = "通用"               # 策略类别：A股策略/加密货币策略/美股策略/外汇策略
    策略描述 = "基础策略模板"        # 策略描述
    策略版本 = "1.0.0"             # 策略版本号
    
    # 策略参数（可配置）
    策略参数 = {}
    
    def __init__(self, 名称, 品种, 初始资金):
        """
        初始化策略
        
        参数:
            名称: 策略实例名称
            品种: 交易品种代码
            初始资金: 初始资金
        """
        self.名称 = 名称
        self.品种 = 品种
        self.初始资金 = 初始资金
        self.资金 = 初始资金
        self.持仓 = 0
        self.交易记录 = []
        self.价格历史 = []
        
        # 扩展属性（用于策略发现器）
        self.入场价 = 0
        self.入场时间 = None
        self.今日交易次数 = 0
        self.今日日期 = None
        self.执行间隔 = 60      # 默认执行间隔（秒）
        self.最大持仓 = 3        # 默认最大持仓数
        self.资金分配 = 0.1      # 默认资金分配比例
        
        print(f"✅ 策略初始化: {self.策略名称} ({self.策略类别}) - {品种}")
    
    def 处理行情(self, k线):
        """
        处理行情数据，返回交易信号
        
        参数:
            k线: 行情数据字典，至少包含 'close' 键
        
        返回:
            'buy'   - 买入信号
            'sell'  - 卖出信号
            'hold'  - 持有/无信号
        """
        # 子类应重写此方法
        return 'hold'
    
    def 执行信号(self, 信号, 价格):
        """
        执行交易信号（兼容旧版）
        
        参数:
            信号: 'buy' / 'sell' / 'hold'
            价格: 当前价格
        """
        if 信号 == 'buy' and self.资金 >= 价格:
            self.持仓 += 1
            self.资金 -= 价格
            self.交易记录.append(('买入', 价格, datetime.now()))
            print(f"📈 [{self.名称}] 买入 @ {价格:.2f}")
        elif 信号 == 'sell' and self.持仓 > 0:
            self.持仓 -= 1
            self.资金 += 价格
            self.交易记录.append(('卖出', 价格, datetime.now()))
            print(f"📉 [{self.名称}] 卖出 @ {价格:.2f}")
    
    def 计算仓位(self, 总资金, 当前价):
        """
        计算开仓数量
        
        参数:
            总资金: 账户总资金
            当前价: 当前价格
        
        返回:
            建议买入数量
        """
        可用资金 = 总资金 * self.单笔仓位比例 if hasattr(self, '单笔仓位比例') else 总资金 * 0.01
        数量 = 可用资金 / 当前价 if 当前价 > 0 else 0
        return round(数量, 4)
    
    def 重置每日统计(self):
        """重置每日交易统计"""
        today = datetime.now().date()
        if self.今日日期 != today:
            self.今日日期 = today
            self.今日交易次数 = 0
    
    def 获取策略信息(self) -> dict:
        """获取策略信息"""
        return {
            "名称": self.名称,
            "策略名称": self.策略名称,
            "类别": self.策略类别,
            "品种": self.品种,
            "版本": self.策略版本,
            "持仓": self.持仓,
            "资金": round(self.资金, 2),
            "交易次数": len(self.交易记录),
            "初始资金": self.初始资金
        }


# 便捷函数
def 创建策略(策略类, 名称, 品种, 初始资金):
    """创建策略实例"""
    return 策略类(名称, 品种, 初始资金)
