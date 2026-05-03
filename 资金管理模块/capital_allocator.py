# 文件位置: quant_system_v5/资金管理模块/capital_allocator.py

class CapitalAllocator:
    """资金管理模块 - 负责资金分配"""
    
    def __init__(self, total_capital):
        self.total_capital = total_capital
        self.allocated = {}
        
    def allocate(self, strategies):
        """平均分配资金给所有策略"""
        count = len(strategies)
        if count == 0:
            return
            
        per_strategy = self.total_capital // count
        remainder = self.total_capital % count
        
        for i, strategy in enumerate(strategies):
            strategy.initial_capital = per_strategy
            strategy.capital = per_strategy
            if i == 0:
                strategy.capital += remainder
                strategy.initial_capital = strategy.capital
            self.allocated[strategy.name] = strategy.capital
            
        return self.allocated
    
    def get_allocation(self, strategy_name):
        """获取策略分配的资金"""
        return self.allocated.get(strategy_name, 0)