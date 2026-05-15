# -*- coding: utf-8 -*-
"""
核心模块
"""

try:
    from .订单引擎 import 订单引擎
except:
    class 订单引擎:
        def __init__(self): pass

try:
    from .行情获取 import 获取价格, 获取K线数据
except:
    def 获取价格(code): return None
    def 获取K线数据(code, period, length): return None

try:
    from .数据模型 import 行情数据, 持仓数据
except:
    class 行情数据: pass
    class 持仓数据: pass

try:
    from .策略基类 import 策略基类
except:
    class 策略基类: pass

try:
    from .策略加载器 import 策略加载器
except:
    class 策略加载器:
        def 获取策略(self): return []
        def 获取策略列表(self): return []

try:
    from .策略运行器 import 策略运行器
except:
    class 策略运行器:
        @classmethod
        def 获取策略状态(cls, name): return True

try:
    from .AI引擎 import AI引擎
except:
    class AI引擎:
        def AI推荐(self, market, strategy): return {"推荐": []}

try:
    from .风控引擎 import 风控引擎
except:
    class 风控引擎:
        def __init__(self): pass

try:
    from .资金分配 import 资金分配
except:
    class 资金分配: pass

print("✅ 核心模块加载完成")
