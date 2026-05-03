# 文件位置: quant_system_v5/核心/核心引擎.py

import multiprocessing
import time
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CoreEngine:
    """核心引擎 - 调度所有策略"""
    
    def __init__(self, strategies, capital_manager, risk_manager):
        self.strategies = strategies
        self.capital_manager = capital_manager
        self.risk_manager = risk_manager
        self.running = True
        
    def run(self):
        """启动所有策略（多进程）"""
        print("🚀 核心引擎启动")
        print(f"📊 共加载 {len(self.strategies)} 个策略\n")
        
        processes = []
        for strategy in self.strategies:
            p = multiprocessing.Process(
                target=self._run_strategy,
                args=(strategy,)
            )
            processes.append(p)
            p.start()
            print(f"   ✅ 启动进程: {strategy.name} (PID: {p.pid})")
        
        print(f"\n🔄 所有策略运行中... (按 Ctrl+C 停止)\n")
        
        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，正在关闭所有策略...")
            for p in processes:
                p.terminate()
                p.join()
            print("✅ 系统已安全停止")
    
    def _run_strategy(self, strategy):
        """运行单个策略"""
        import random
        
        print(f"[{strategy.name}] 开始运行，初始资金: ${strategy.capital:,.2f}")
        
        # 模拟交易循环（100个周期）
        for step in range(1, 101):
            if not self.running:
                break
            
            # 模拟行情数据
            if "期货" in strategy.name:
                # 期货价格范围 90-110
                price = random.uniform(90, 110)
            else:
                # 外汇价格范围 1.08-1.12
                price = random.uniform(1.08, 1.12)
            
            # 策略产生信号
            signal = strategy.on_data({'price': price, 'close': price})
            
            # 执行交易
            strategy.execute_signal(signal, price)
            
            # 每20个周期输出一次状态
            if step % 20 == 0:
                print(f"   [{strategy.name}] 第{step}周期 - 资金: ${strategy.capital:,.2f}")
            
            time.sleep(0.05)  # 模拟实时节奏
        
        # 输出最终结果
        pnl = strategy.capital - strategy.initial_capital
        pnl_pct = (pnl / strategy.initial_capital) * 100
        print(f"\n📊 [{strategy.name}] 运行完成")
        print(f"   初始资金: ${strategy.initial_capital:,.2f}")
        print(f"   最终资金: ${strategy.capital:,.2f}")
        print(f"   盈亏: ${pnl:+,.2f} ({pnl_pct:+.2f}%)\n")