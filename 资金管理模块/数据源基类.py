# -*- coding: utf-8 -*-
"""数据源基类"""

class DataSourceBase:
    """数据源基类"""
    
    def get_price(self, symbol):
        """获取价格"""
        raise NotImplementedError
    
    def get_kline(self, symbol, period):
        """获取K线"""
        raise NotImplementedError