# 文件位置: quant_system_v5/策略引擎/strategy_base.py

class BaseStrategy:
    """策略基类 - 所有策略继承此类"""
    
    def __init__(self, name, symbol, initial_capital):
        self.name = name
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        
    def on_data(self, data):
        """接收市场数据，返回信号: 'buy', 'sell', 'hold'"""
        return 'hold'
    
    def execute_signal(self, signal, price):
        """执行交易信号"""
        if signal == 'buy' and self.capital >= price:
            self.position += 1
            self.capital -= price
            self.trades.append(('BUY', price, self.capital))
        elif signal == 'sell' and self.position > 0:
            self.position -= 1
            self.capital += price
            self.trades.append(('SELL', price, self.capital))
    
    def get_status(self):
        """获取策略状态"""
        return {
            'name': self.name,
            'symbol': self.symbol,
            'capital': self.capital,
            'position': self.position,
            'total_trades': len(self.trades)
        }