"""
策略基类
"""
from abc import ABC, abstractmethod

class 策略基类(ABC):
    def __init__(self, 参数=None):
        self.参数 = 参数 or {}
        self.名称 = self.__class__.__name__
    
    @abstractmethod
    async def 决策(self, 行情数据, 历史数据, 引擎):
        pass