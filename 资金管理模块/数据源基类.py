from abc import ABC, abstractmethod
import pandas as pd

class 数据源基类(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def 获取行情(self) -> pd.DataFrame:
        """获取实时行情"""
        pass
    
    @abstractmethod
    def 获取历史(self, 代码: str, 开始: str, 结束: str) -> pd.DataFrame:
        """获取历史数据"""
        pass