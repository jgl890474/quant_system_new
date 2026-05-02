import pandas as pd
import random
from .数据源基类 import 数据源基类

class 股票数据(数据源基类):
    """A股数据源"""
    
    def 获取行情(self) -> pd.DataFrame:
        return pd.DataFrame({
            "代码": ["000001", "000858", "600519", "300750"],
            "名称": ["平安银行", "五粮液", "贵州茅台", "宁德时代"],
            "最新价": [11.56, 135.20, 1450.00, 205.50],
            "涨跌幅": [random.uniform(-3, 5) for _ in range(4)],
            "量比": [random.uniform(0.5, 2.5) for _ in range(4)],
        })
    
    def 获取历史(self, 代码, 开始, 结束):
        pass