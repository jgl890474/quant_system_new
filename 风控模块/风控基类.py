# -*- coding: utf-8 -*-

class RiskBase:
    """风控基类"""
    
    def __init__(self):
        pass
    
    def check(self, strategy, signal, price):
        """检查风控"""
        return True, "通过"