from abc import ABC, abstractmethod
import pandas as pd

class 策略基类(ABC):
    """策略抽象基类"""
    
    def __init__(self, 参数=None):
        self.参数 = 参数 or {}
        self.名称 = self.__class__.__name__
    
    @abstractmethod
    def 计算信号(self, 价格: pd.Series) -> pd.Series:
        """计算交易信号：1=买入, -1=卖出, 0=持有"""
        pass
    
    def 获取参数说明(self):
        return {}