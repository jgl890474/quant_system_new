# -*- coding: utf-8 -*-

class StopLossTakeProfit:
    """止损止盈管理"""
    
    def __init__(self, stop_loss_pct=0.05, take_profit_pct=0.08):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.entry_prices = {}
        
    def check_stop_loss(self, strategy, current_price):
        """检查止损"""
        if strategy.name not in self.entry_prices:
            return False
        entry = self.entry_prices[strategy.name]
        if current_price < entry * (1 - self.stop_loss_pct):
            return True
        return False
    
    def check_take_profit(self, strategy, current_price):
        """检查止盈"""
        if strategy.name not in self.entry_prices:
            return False
        entry = self.entry_prices[strategy.name]
        if current_price > entry * (1 + self.take_profit_pct):
            return True
        return False
    
    def set_entry_price(self, strategy, price):
        """记录入场价格"""
        self.entry_prices[strategy.name] = price