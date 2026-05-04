# -*- coding: utf-8 -*-

class RiskManager:
    """风控模块 - 风险控制"""
    
    def __init__(self, max_drawdown=0.15, max_position_pct=0.05, daily_loss_limit=0.03):
        self.max_drawdown = max_drawdown
        self.max_position_pct = max_position_pct
        self.daily_loss_limit = daily_loss_limit
        self.daily_pnl = {}
        self.peak_value = {}
        
    def can_trade(self, strategy, signal, price=None):
        """检查是否可以交易"""
        if signal not in ['buy', 'sell', 'hold']:
            return False, "无效信号"
        if signal == 'hold':
            return False, "无信号"
        if signal == 'buy' and price and strategy.capital < price:
            return False, "资金不足"
        return True, "通过"
    
    def check_drawdown(self, strategy, current_value):
        """检查回撤"""
        name = strategy.name
        if name not in self.peak_value:
            self.peak_value[name] = current_value
        elif current_value > self.peak_value[name]:
            self.peak_value[name] = current_value
        if self.peak_value[name] > 0:
            drawdown = (self.peak_value[name] - current_value) / self.peak_value[name]
            if drawdown > self.max_drawdown:
                return False
        return True
    
    def reset_daily_pnl(self):
        """重置每日盈亏"""
        self.daily_pnl = {}