from abc import ABC, abstractmethod

class 风控基类(ABC):
    
    @abstractmethod
    def 检查开仓(self, 代码, 价格, 账户) -> tuple:
        """返回 (是否允许, 原因)"""
        pass
    
    @abstractmethod
    def 检查平仓(self, 持仓, 当前价) -> tuple:
        """返回 (是否平仓, 原因, 价格)"""
        pass