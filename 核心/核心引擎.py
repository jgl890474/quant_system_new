# -*- coding: utf-8 -*-
import time
import random

class CoreEngine:
    def __init__(self, strategies, capital_manager, risk_manager):
        self.strategies = strategies

    def run(self):
        print(f"共加载 {len(self.strategies)} 个策略")
        for s in self.strategies:
            print(f"运行策略: {s.name}")
            for i in range(10):
                price = random.uniform(90, 110)
                signal = s.on_data({'price': price, 'close': price})
                s.execute_signal(signal, price)
            print(f"{s.name} 完成")