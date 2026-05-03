# 如果内容不对，补充这个基类
class BaseStrategy:
    def __init__(self, name, symbol, initial_capital):
        self.name = name
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        
    def on_data(self, data):
        return 'hold'
    
    def execute_signal(self, signal, price):
        if signal == 'buy' and self.capital >= price:
            self.position += 1
            self.capital -= price
            self.trades.append(('BUY', price))
        elif signal == 'sell' and self.position > 0:
            self.position -= 1
            self.capital += price
            self.trades.append(('SELL', price))