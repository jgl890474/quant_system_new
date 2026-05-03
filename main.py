#!/usr/bin/env python3
# 文件位置: quant_system_v5/main.py

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入您的模块（使用您实际的文件名）
from 核心 import 核心引擎
from 资金管理模块 import capital_allocator
from 风控模块 import risk_manager
from 策略库 import 期货策略1, 期货策略2, 外汇策略1, 外汇策略2
from 策略引擎 import strategy_base, 策略加载器

def main():
    print("=" * 60)
    print("量化交易系统 v5.0")
    print("多类目 · 多策略 · AI自动交易")
    print("=" * 60)
    
    # 初始化资金管理
    capital_mgr = capital_allocator.CapitalAllocator(total_capital=80050)
    
    # 初始化风控
    risk_mgr = risk_manager.RiskManager(max_drawdown=0.15)
    
    # 加载策略（使用您现有的策略类）
    strategies = [
        期货策略1.FuturesTrendStrategy("期货趋势策略", "GC=F", 0),
        期货策略2.FuturesMeanReversionStrategy("期货均值回归", "CL=F", 0),
        外汇策略1.ForexCarryStrategy("外汇利差交易", "AUDJPY", 0),
        外汇策略2.ForexBreakoutStrategy("外汇突破策略", "EURUSD", 0),
    ]
    
    # 分配资金
    capital_mgr.allocate(strategies)
    
    # 显示策略
    print("\n📋 策略列表:")
    for s in strategies:
        print(f"   📈 {s.name} - {s.symbol} - 资金: ${s.capital:,.2f}")
    
    print(f"\n💰 总资金: ${capital_mgr.total_capital:,.2f}")
    
    # 启动核心引擎
    engine = 核心引擎.CoreEngine(
        strategies=strategies,
        capital_manager=capital_mgr,
        risk_manager=risk_mgr
    )
    
    engine.run()

if __name__ == "__main__":
    main()