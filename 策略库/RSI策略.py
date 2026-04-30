"""
RSI策略
"""
from .策略基类 import 策略基类

class RSI策略(策略基类):
    def __init__(self, 参数=None):
        super().__init__(参数)
        self.周期 = self.参数.get('周期', 14)
        self.价格历史 = []
    
    async def 决策(self, 行情数据, 历史数据, 引擎):
        self.价格历史.append(行情数据['收盘'])
        
        if len(self.价格历史) < self.周期 + 1:
            return {'动作': '持有'}
        
        gains = []
        losses = []
        for i in range(1, len(self.价格历史)):
            diff = self.价格历史[i] - self.价格历史[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-diff)
        
        avg_gain = sum(gains[-self.周期:]) / self.周期
        avg_loss = sum(losses[-self.周期:]) / self.周期
        
        if avg_loss == 0:
            rsi = 100
        else:
            rsi = 100 - (100 / (1 + avg_gain/avg_loss))
        
        if rsi < 30:
            return {'动作': '买入', '强度': 0.6}
        elif rsi > 70:
            return {'动作': '卖出', '强度': 1.0}
        
        return {'动作': '持有'}