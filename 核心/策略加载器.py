# -*- coding: utf-8 -*-
"""
策略加载器
"""

class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self._加载策略()
    
    def _加载策略(self):
        print("策略加载器初始化...")
        self.策略列表 = [
            {
                "名称": "加密双均线1",
                "类别": "加密货币策略",
                "品种": "BTC-USD",
                "描述": "双均线交叉策略"
            },
            {
                "名称": "加密风控策略2",
                "类别": "加密货币策略",
                "品种": "BTC-USD", 
                "描述": "风控策略"
            }
        ]
        print(f"加载 {len(self.策略列表)} 个策略")
    
    def 获取策略(self, 名称=None):
        if 名称:
            for s in self.策略列表:
                if s.get("名称") == 名称:
                    return s
            return None
        return self.策略列表
    
    def 获取策略列表(self):
        return self.策略列表


def 获取策略加载器():
    return 策略加载器()
