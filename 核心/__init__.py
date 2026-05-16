# -*- coding: utf-8 -*-
"""
核心模块 - 最简版
"""

# 订单引擎
from .订单引擎 import 订单引擎

# 策略基类
try:
    from .策略基类 import 策略基类
except:
    class 策略基类:
        pass

# 策略加载器
try:
    from .策略加载器 import 策略加载器
except:
    class 策略加载器:
        def 获取策略列表(self):
            return []

print("✅ 核心模块加载完成")
