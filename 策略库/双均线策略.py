"""
双均线策略
"""
from .策略基类 import 策略基类

class 双均线策略(策略基类):
    def __init__(self, 参数=None):
        super().__init__(参数)
        self.快线周期 = self.参数.get('快线周期', 5)
        self.慢线周期 = self.参数.get('慢线周期', 20)
        self.价格历史 = []
    
    async def 决策(self, 行情数据, 历史数据, 引擎):
        self.价格历史.append(行情数据['收盘'])
        
        if len(self.价格历史) < self.慢线周期:
            return {'动作': '持有'}
        
        快线 = sum(self.价格历史[-self.快线周期:]) / self.快线周期
        慢线 = sum(self.价格历史[-self.慢线周期:]) / self.慢线周期
        
        if 快线 > 慢线:
            return {'动作': '买入', '强度': 0.8}
        else:
            return {'动作': '卖出', '强度': 1.0}