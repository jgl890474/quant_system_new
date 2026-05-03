# 文件位置: quant_system_v5/风控模块/risk_manager.py

class RiskManager:
    """风控模块 - 风险控制"""
    
    def __init__(self, max_drawdown=0.15, max_position_pct=0.05, daily_loss_limit=0.03):
        self.max_drawdown = max_drawdown
        self.max_position_pct = max_position_pct
        self.daily_loss_limit = daily_loss_limit
        self.daily_pnl = {}
        
    def can_trade(self, strategy, signal, price=None):
        """
        检查是否可以交易
        返回: (bool, reason)
        """
        # 1. 检查信号有效性
        if signal not in ['buy', 'sell', 'hold']:
            return False, "无效信号"
        
        if signal == 'hold':
            return False, "无信号"
        
        # 2. 检查资金是否足够（买入时）
        if signal == 'buy' and price and strategy.capital < price:
            return False, "资金不足"
        
        # 3. 简单风控：允许交易
        return True, "通过"
    
    def check_drawdown(self, strategy, current_value):
        """检查回撤"""
        # 简化版本，实际需要记录历史峰值
        return True