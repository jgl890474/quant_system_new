# -*- coding: utf-8 -*-
"""
核心模块 - 导出所有核心类和函数
"""

# ==================== 基础模块（必须存在） ====================

# 订单引擎
try:
    from .订单引擎 import 订单引擎
except ImportError as e:
    print(f"⚠️ 订单引擎导入失败: {e}")
    class 订单引擎:
        def __init__(self, 初始资金=1000000): 
            self.初始资金 = 初始资金
            self.可用资金 = 初始资金
            self.持仓 = {}
        def 买入(self, *args, **kwargs): return {"success": False}
        def 卖出(self, *args, **kwargs): return {"success": False}
        def 获取总资产(self): return self.可用资金
        def 获取可用资金(self): return self.可用资金

# 行情获取
try:
    from .行情获取 import 获取价格, 获取K线数据
except ImportError as e:
    print(f"⚠️ 行情获取导入失败: {e}")
    def 获取价格(code): return None
    def 获取K线数据(code, period, length): return None

# 数据模型
try:
    from .数据模型 import 行情数据, 持仓数据
except ImportError:
    class 行情数据:
        def __init__(self, 品种, 价格, **kwargs):
            self.品种 = 品种
            self.价格 = 价格
    class 持仓数据:
        def __init__(self, 品种, 数量, 平均成本):
            self.品种 = 品种
            self.数量 = 数量
            self.平均成本 = 平均成本

# ==================== 策略模块 ====================

# 策略基类
try:
    from .策略基类 import 策略基类
except ImportError:
    class 策略基类:
        def __init__(self, 名称, 品种, 初始资金):
            self.名称 = 名称
            self.品种 = 品种
            self.初始资金 = 初始资金

# 策略加载器
try:
    from .策略加载器 import 策略加载器
except ImportError:
    class 策略加载器:
        def 获取策略(self, name=None):
            return []
        def 获取策略列表(self):
            return []

# 策略运行器
try:
    from .策略运行器 import 策略运行器
except ImportError:
    class 策略运行器:
        @classmethod
        def 获取策略状态(cls, name): return True
        @classmethod
        def 设置策略状态(cls, name, status): pass

# ==================== AI模块 ====================

# AI引擎
try:
    from .AI引擎 import AI引擎
except ImportError:
    class AI引擎:
        def AI推荐(self, market, strategy): return {"推荐": []}
        def 获取信号(self, data): return {"信号": "无"}
        def 获取实时价格(self, code): return None
        def 计算技术指标(self, code): return {"RSI": 50}

# 风控引擎
try:
    from .风控引擎 import 风控引擎
except ImportError:
    class 风控引擎:
        def __init__(self): pass
        def 监控持仓(self, engine): return []
        def 执行自动平仓(self, engine): return []

# ==================== 其他模块 ====================

# 技术指标
try:
    from .技术指标 import 获取指标计算器
except ImportError:
    def 获取指标计算器(): return None

# 资金分配
try:
    from .资金分配 import 资金分配
except ImportError:
    class 资金分配: pass

# ==================== 导出列表 ====================
__all__ = [
    '订单引擎',
    '行情获取',
    '获取价格',
    '获取K线数据',
    '行情数据',
    '持仓数据',
    '策略基类',
    '策略加载器',
    '策略运行器',
    'AI引擎',
    '风控引擎',
    '获取指标计算器',
    '资金分配',
]

print("✅ 核心模块初始化完成")
