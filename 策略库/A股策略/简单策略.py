# -*- coding: utf-8 -*-
from 核心.策略基类 import 策略基类

class 我的新策略(策略基类):
    def __init__(self, 名称, 品种, 初始资金):
        super().__init__(名称, 品种, 初始资金)
    
    def 处理行情(self, k线):
        # 你的策略逻辑
        return 'hold'
