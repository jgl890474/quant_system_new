# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from 核心.核心引擎 import CoreEngine
from 资金管理模块.capital_allocator import CapitalAllocator
from 风控模块.risk_manager import RiskManager

# 直接导入策略文件（完整路径）
from 策略库.外汇策略.外汇利差策略 import ForexCarryStrategy
from 策略库.外汇策略.外汇突破策略 import ForexBreakoutStrategy
from 策略库.外汇策略.外汇双均线 import ForexDualMAStrategy

from 策略库.期货策略.期货趋势策略 import FuturesTrendStrategy
from 策略库.期货策略.期货均值回归 import FuturesMeanReversionStrategy
from 策略库.期货策略.期货ATR import FuturesATRStrategy

from 策略库.加密货币策略.加密双均线策略 import CryptoDualMAStrategy
from 策略库.加密货币策略.加密RSI策略 import CryptoRSIStrategy


def main():
    print("=" * 60)
    print("量化交易系统 v5.0 启动（真实行情 + AI决策）")
    print("=" * 60)

    total_capital = 80050
    capital_mgr = CapitalAllocator(total_capital=total_capital)
    risk_mgr = RiskManager(max_drawdown=0.15)

    strategies = [
        ForexCarryStrategy("外汇利差", "AUDJPY", 0),
        ForexBreakoutStrategy("外汇突破", "EURUSD", 0),
        ForexDualMAStrategy("外汇双均线", "GBPUSD", 0),

        FuturesTrendStrategy("期货趋势", "GC=F", 0),
        FuturesMeanReversionStrategy("期货均值回归", "CL=F", 0),
        FuturesATRStrategy("期货ATR", "SI=F", 0),

        CryptoDualMAStrategy("加密双均线", "BTC-USD", 0),
        CryptoRSIStrategy("加密RSI", "ETH-USD", 0),
    ]

    capital_mgr.allocate(strategies)

    print("\n📋 策略列表:")
    for s in strategies:
        print(f"   📈 {s.name} - {s.symbol} - 资金: ${s.capital:,.2f}")

    print(f"\n💰 总资金: ${capital_mgr.total_capital:,.2f}")
    print("🚀 核心引擎启动")
    print(f"📊 共加载 {len(strategies)} 个策略\n")

    engine = CoreEngine(
        strategies=strategies,
        capital_manager=capital_mgr,
        risk_manager=risk_mgr
    )
    engine.run()


if __name__ == "__main__":
    main()