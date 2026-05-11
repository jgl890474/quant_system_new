# -*- coding: utf-8 -*-

# ==================== 核心模块 ====================
from .订单引擎 import 订单引擎
from .数据模型 import 行情数据, 持仓数据, 持仓信息, 交易记录

# ==================== 行情获取模块 ====================
from .行情获取 import (
    获取价格,           # 原有接口，返回对象
    获取实时价格,       # 新增，返回数值
    获取历史数据,       # 新增，获取K线数据
    判断市场类型        # 新增，判断市场
)

# ==================== 可选模块（兼容处理） ====================
try:
    from .策略加载器 import 策略加载器
except ImportError:
    # 如果策略加载器不存在，定义一个简单的替代
    class 策略加载器:
        def 获取策略列表(self):
            return []
        def 加载策略(self, 策略名):
            return None

try:
    from .AI引擎 import AI引擎
except ImportError:
    # 如果AI引擎不存在，定义一个简单的替代
    class AI引擎:
        def 获取信号(self, 数据):
            return {"信号": "无", "置信度": 0, "理由": "AI引擎未配置"}
        def 分析市场(self):
            return {"建议": "无法获取AI分析"}
        def AI推荐(self, 市场, 策略类型):
            return {"推荐": []}

try:
    from .风控引擎 import 风控引擎
except ImportError:
    # 如果风控引擎不存在，定义一个简单的替代
    class 风控引擎:
        def __init__(self):
            self.止损比例 = 0.05
            self.止盈比例 = 0.03
            self.移动止损开关 = False
            self.移动止损回撤 = 0.02
        def 监控持仓(self, 引擎):
            return []
        def 执行自动平仓(self, 引擎):
            return []

try:
    from .策略基类 import 策略基类
except ImportError:
    # 如果策略基类不存在，定义一个简单的替代
    class 策略基类:
        pass

# ==================== 导出列表 ====================
__all__ = [
    # 订单引擎
    '订单引擎',
    
    # 数据模型
    '行情数据',
    '持仓数据',
    '持仓信息',
    '交易记录',
    
    # 行情获取
    '获取价格',
    '获取实时价格',
    '获取历史数据',
    '判断市场类型',
    
    # 可选模块
    '策略加载器',
    'AI引擎',
    '风控引擎',
    '策略基类',
]
