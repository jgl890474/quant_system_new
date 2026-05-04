# -*- coding: utf-8 -*-

class BaseStrategy:
    """策略基类"""
    
    def __init__(self, name, symbol, initial_capital):
        self.name = name
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        
    def on_data(self, kline):
        """接收K线数据，返回信号"""
        return 'hold'
    
    def execute_signal(self, signal, price):
        """执行交易信号"""
        if signal == 'buy' and self.capital >= price:
            self.position += 1
            self.capital -= price
            self.trades.append(('BUY', price))
        elif signal == 'sell' and self.position > 0:
            self.position -= 1
            self.capital += price
            self.trades.append(('SELL', price))
    
    def get_status(self):
        return {
            'name': self.name,
            'symbol': self.symbol,
            'capital': round(self.capital, 2),
            'position': self.position,
            'total_trades': len(self.trades)
        }