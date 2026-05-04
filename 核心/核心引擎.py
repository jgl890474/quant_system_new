# -*- coding: utf-8 -*-
import multiprocessing
import time
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 数据.market_data import get_1min_kline

class CoreEngine:
    def __init__(self, strategies, capital_manager, risk_manager):
        self.strategies = strategies
        self.capital_manager = capital_manager
        self.risk_manager = risk_manager
        self.running = True
        
    def run(self):
        print("🚀 核心引擎启动（真实行情模式）")
        print(f"📊 共加载 {len(self.strategies)} 个策略\n")
        
        processes = []
        for strategy in self.strategies:
            p = multiprocessing.Process(target=self._run_strategy, args=(strategy,))
            processes.append(p)
            p.start()
            print(f"   ✅ 启动进程: {strategy.name} (PID: {p.pid})")
        
        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            print("\n🛑 停止所有策略...")
            for p in processes:
                p.terminate()
    
    def _run_strategy(self, strategy):
        print(f"[{strategy.name}] 开始运行，初始资金: ${strategy.capital:,.2f}")
        
        for step in range(1, 101):
            if not self.running:
                break
            
            # 获取真实行情
            try:
                kline = get_1min_kline(strategy.symbol)
                if not kline:
                    # 如果是外汇品种且获取失败，使用模拟数据
                    if "AUD" in strategy.symbol or "JPY" in strategy.symbol:
                        price = random.uniform(90, 110)
                        print(f"⚠️ {strategy.name} 使用模拟数据 (AUD/JPY 暂时降级): {price}")
                        kline = {
                            "close": price,
                            "high": price * 1.002,
                            "low": price * 0.998,
                            "open": price,
                            "symbol": strategy.symbol
                        }
                    else:
                        print(f"⚠️ {strategy.name} 获取行情失败，跳过")
                        time.sleep(1)
                        continue
            except Exception as e:
                print(f"❌ {strategy.name} 数据异常: {e}")
                continue
            
            if kline:
                price = kline['close']
                # 补全缺失的字段
                data = {
                    'price': price,
                    'close': price,
                    'high': kline.get('high', price * 1.002),
                    'low': kline.get('low', price * 0.998),
                    'open': kline.get('open', price)
                }
                signal = strategy.on_data(data)
                strategy.execute_signal(signal, price)
                
                if step % 20 == 0:
                    print(f"   [{strategy.name}] 第{step}周期 - 资金: ${strategy.capital:,.2f}")
                
                time.sleep(0.05)
        
        pnl = strategy.capital - strategy.initial_capital
        pnl_pct = (pnl / strategy.initial_capital) * 100
        print(f"\n📊 [{strategy.name}] 运行完成: ${pnl:+,.2f} ({pnl_pct:+.2f}%)\n")