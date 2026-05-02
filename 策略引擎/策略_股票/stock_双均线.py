from ..策略基类 import 策略基类
import pandas as pd

class 双均线策略(策略基类):
    
    def __init__(self, 参数=None):
        super().__init__(参数)
        self.快线 = self.参数.get("快线", 5)
        self.慢线 = self.参数.get("慢线", 20)
        self.说明 = "双均线金叉买入，死叉卖出"
    
    def 计算信号(self, 价格):
        if len(价格) < self.慢线:
            return pd.Series(0, index=range(len(价格)))
        fast = 价格.rolling(window=self.快线).mean()
        slow = 价格.rolling(window=self.慢线).mean()
        return (fast > slow).astype(int).diff()