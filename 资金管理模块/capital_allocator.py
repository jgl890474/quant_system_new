# -*- coding: utf-8 -*-
"""股票数据模块（云函数简化版）"""

import random

def get_stock_price(symbol):
    """获取股票价格（模拟数据）"""
    return random.uniform(10, 500)