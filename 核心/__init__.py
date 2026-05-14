# -*- coding: utf-8 -*-

# ==================== 核心模块（带容错导入） ====================

# 导入订单引擎
try:
    from .订单引擎 import 订单引擎
except ImportError as e:
    print(f"订单引擎导入失败: {e}")
    # 定义一个简单的订单引擎作为备选
    class 订单引擎:
        def __init__(self, 初始资金=1000000, **kwargs):
            self.初始资金 = 初始资金
            self.可用资金 = 初始资金
            self.持仓市值 = 0
            self.总盈亏 = 0
            self.持仓 = {}
            self.交易记录 = []
        def 买入(self, *args, **kwargs):
            return {"success": False, "error": "订单引擎未正确初始化"}
        def 卖出(self, *args, **kwargs):
            return {"success": False, "error": "订单引擎未正确初始化"}
        def 获取总资产(self):
            return self.可用资金 + self.持仓市值
        def 获取可用资金(self):
            return self.可用资金
        def 获取持仓市值(self):
            return self.持仓市值
        def 获取总盈亏(self):
            return self.总盈亏
        def 获取初始资金(self):
            return self.初始资金
        def 获取持仓(self):
            return self.持仓
        def 获取持仓详情(self):
            return []

# 导入数据模型
try:
    from .数据模型 import 行情数据, 持仓数据, 持仓信息, 交易记录
except ImportError:
    # 定义简单的数据模型
    class 行情数据:
        def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
            self.品种 = 品种
            self.价格 = 价格
            self.最高 = 最高
            self.最低 = 最低
            self.开盘 = 开盘
            self.成交量 = 成交量
    
    class 持仓数据:
        def __init__(self, 品种, 数量, 平均成本):
            self.品种 = 品种
            self.数量 = 数量
            self.平均成本 = 平均成本
            self.当前价格 = 平均成本
    
    class 持仓信息:
        def __init__(self, 品种, 数量, 平均成本, 当前价格=None):
            self.品种 = 品种
            self.数量 = 数量
            self.平均成本 = 平均成本
            self.当前价格 = 当前价格 if 当前价格 else 平均成本
    
    class 交易记录:
        def __init__(self, 时间, 品种, 动作, 价格, 数量, 盈亏=0, 策略名称=""):
            self.时间 = 时间
            self.品种 = 品种
            self.动作 = 动作
            self.价格 = 价格
            self.数量 = 数量
            self.盈亏 = 盈亏
            self.策略名称 = 策略名称

# 导入行情获取模块
try:
    from .行情获取 import 获取价格, 获取实时价格, 获取历史数据, 判断市场类型, 获取新浪实时行情, 获取K线数据
except ImportError as e:
    print(f"行情获取模块导入失败: {e}")
    def 获取价格(代码):
        return None
    def 获取实时价格(代码):
        return None
    def 获取历史数据(代码, 开始, 结束):
        return None
    def 判断市场类型(代码):
        return "未知"
    def 获取新浪实时行情(代码):
        return None
    def 获取K线数据(代码, 周期, 长度):
        return None

# ==================== 可选模块（兼容处理） ====================
try:
    from .策略加载器 import 策略加载器
except ImportError:
    class 策略加载器:
        def 获取策略(self):
            return []
        def 获取策略列表(self):
            return []
        def 加载策略(self, 策略名):
            return None

try:
    from .AI引擎 import AI引擎
except ImportError:
    class AI引擎:
        def 获取信号(self, 数据):
            return {"信号": "无", "置信度": 0, "理由": "AI引擎未配置"}
        def 分析市场(self):
            return {"建议": "无法获取AI分析"}
        def AI推荐(self, 市场, 策略类型):
            return {"推荐": []}
        def 获取实时价格(self, code):
            return None
        def 计算技术指标(self, code):
            return {"RSI": 50, "趋势": "未知"}
        def 获取完整技术指标(self, code):
            return {}

try:
    from .风控引擎 import 风控引擎
except ImportError:
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
    class 策略基类:
        def __init__(self, 名称, 品种, 初始资金):
            self.名称 = 名称
            self.品种 = 品种
            self.初始资金 = 初始资金
            self.资金 = 初始资金
            self.持仓 = 0
        def 处理行情(self, k线):
            return 'hold'

try:
    from .策略运行器 import 策略运行器
except ImportError:
    class 策略运行器:
        _策略状态 = {}
        @classmethod
        def 设置策略状态(cls, 名称, 状态):
            pass
        @classmethod
        def 获取策略状态(cls, 名称):
            return True
        @classmethod
        def 获取激活策略(cls):
            return []

try:
    from .资金分配 import 资金分配
except ImportError:
    class 资金分配:
        def __init__(self):
            self.策略资金 = {}
        def 分配资金(self, 总资金, 策略列表):
            return {}

try:
    from .技术指标 import 获取指标计算器
except ImportError:
    def 获取指标计算器():
        class 空指标:
            @staticmethod
            def 计算RSI(df):
                return {'RSI': 50}
            @staticmethod
            def 计算MACD(df):
                return {'MACD': 0}
            @staticmethod
            def 计算布林带(df):
                return {'上轨': 0, '中轨': 0, '下轨': 0}
        return 空指标()

try:
    from .真实AI引擎 import 获取真实AI
except ImportError:
    def 获取真实AI():
        class 空AI:
            def 综合分析(self, code, data, sentiment=None):
                return {'综合评分': 50, '交易决策': '持有'}
        return 空AI()

try:
    from .新闻情绪 import 获取情绪分析器
except ImportError:
    def 获取情绪分析器():
        class 空情绪:
            def 获取新闻(self, code):
                return []
            def 分析情绪(self, news):
                return {'情绪': '中性', '评分': 50}
        return 空情绪()

try:
    from .策略发现器 import 获取策略发现器
except ImportError:
    def 获取策略发现器():
        class 空发现器:
            策略列表 = []
            def 获取策略(self, name=None, category=None):
                return []
        return 空发现器()

# ==================== 导出列表 ====================
__all__ = [
    '订单引擎',
    '行情数据',
    '持仓数据',
    '持仓信息',
    '交易记录',
    '获取价格',
    '获取实时价格',
    '获取历史数据',
    '判断市场类型',
    '获取新浪实时行情',
    '获取K线数据',
    '策略加载器',
    'AI引擎',
    '风控引擎',
    '策略基类',
    '策略运行器',
    '资金分配',
    '获取指标计算器',
    '获取真实AI',
    '获取情绪分析器',
    '获取策略发现器',
]

print("✅ 核心模块初始化完成")
