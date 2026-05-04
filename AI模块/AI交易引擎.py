# -*- coding: utf-8 -*-

def ai_decision(signals, current_price, symbol="EURUSD"):
    """
    AI决策函数（云函数简化版）
    返回 buy / sell / hold
    """
    print(f"AI决策: 当前价格={current_price}, 信号={signals}")
    
    if "buy" in str(signals).lower():
        return "buy"
    elif "sell" in str(signals).lower():
        return "sell"
    return "hold"