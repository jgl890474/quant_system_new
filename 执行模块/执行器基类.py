from abc import ABC, abstractmethod

class 执行器基类(ABC):
    """执行器抽象基类"""
    
    @abstractmethod
    def 买入(self, 代码: str, 价格: float, 数量: int) -> dict:
        pass
    
    @abstractmethod
    def 卖出(self, 代码: str, 价格: float, 数量: int) -> dict:
        pass
    
    @abstractmethod
    def 查询持仓(self) -> dict:
        pass