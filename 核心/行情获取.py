# -*- coding: utf-8 -*-
"""
行情获取模块 v3.0 - 精简版
数据源优先级：
- 加密货币：币安API（免费）
- 美股/外汇/期货：yfinance（免费）
- A股：yfinance（尝试）+ 演示数据（降级）
- 最终降级：演示数据
"""

import yfinance as yf
import random
import requests
import time
from datetime import datetime
import pandas as pd


class 行情数据:
    """统一的行情数据类"""
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0
        self.涨跌 = 0.0


def 获取价格(品种代码):
    """
    统一入口，根据品种选择不同的数据源
    返回：行情数据 对象
    """
    # 1. A股 -> yfinance + 演示数据
    if '.SZ' in 品种代码 or '.SS' in 品种代码:
        return 获取_A股(品种代码)
    
    # 2. 加密货币 -> 币安 API
    if 'BTC' in 品种代码 or 'ETH' in 品种代码:
        return 获取_加密货币_币安(品种代码)
    
    # 3. 其他（美股、外汇、期货等）-> yfinance
    return 获取_其他_yfinance(品种代码)


def 获取_A股(品种代码):
    """
    获取 A股数据
    优先级：yfinance -> 演示数据
    """
    # 方案1：yfinance 尝试获取A股
    result = 获取_A股_yfinance(品种代码)
    if result and result.价格 > 0:
        return result
    
    # 方案2：演示数据
    return 获取_演示数据(品种代码)


def 获取_A股_yfinance(品种代码):
    """使用 yfinance 获取 A股数据"""
    try:
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            high = float(data['High'].iloc[-1]) if 'High' in data else price
            low = float(data['Low'].iloc[-1]) if 'Low' in data else price
            open_price = float(data['Open'].iloc[-1]) if 'Open' in data else price
            volume = int(data['Volume'].iloc[-1]) if 'Volume' in data else 0
            print(f"[yfinance A股] {品种代码}: {price}")
            return 行情数据(品种代码, price, high, low, open_price, volume)
    except Exception as e:
        print(f"yfinance 获取 {品种代码} 失败: {e}")
    
    return None


def 获取_加密货币_币安(品种代码):
    """币安 API 获取加密货币价格"""
    try:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = float(data['price'])
        print(f"[币安实时] {品种代码}: ${price}")
        return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取 {品种代码} 失败: {e}")
        return 获取_演示数据(品种代码)


def 获取_其他_yfinance(品种代码):
    """yfinance 获取美股、外汇、期货等数据"""
    try:
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            high = float(data['High'].iloc[-1]) if 'High' in data else price
            low = float(data['Low'].iloc[-1]) if 'Low' in data else price
            open_price = float(data['Open'].iloc[-1]) if 'Open' in data else price
            volume = int(data['Volume'].iloc[-1]) if 'Volume' in data else 0
            print(f"[yfinance] {品种代码}: {price}")
            return 行情数据(品种代码, price, high, low, open_price, volume)
    except Exception as e:
        print(f"yfinance 获取 {品种代码} 失败: {e}")
    
    return 获取_演示数据(品种代码)


def 获取_演示数据(品种代码):
    """最终降级：演示/模拟数据（用于开发测试）"""
    演示价格 = {
        # A股
        "300750.SZ": 437.00,
        "002415.SZ": 35.55,
        "000333.SZ": 80.40,
        "000001.SS": 3150,
        # 美股
        "AAPL": 175.00,
        "MSFT": 330.00,
        "GOOGL": 130.00,
        "TSLA": 240.00,
        "NVDA": 120.00,
        # 加密货币
        "BTC-USD": 45000,
        "ETH-USD": 2300,
        # 期货
        "GC=F": 1950,
        "CL=F": 95,
        # 外汇
        "EURUSD": 1.08,
        "GBPUSD=X": 1.27,
    }.get(品种代码, 100)
    
    # 添加小波动避免显示全为0
    波动 = random.uniform(-0.005, 0.005)
    价格 = 演示价格 * (1 + 波动)
    
    print(f"[演示数据] {品种代码}: {价格:.2f}")
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)


def 获取历史K线(品种代码, 开始日期, 结束日期, 频率='1d'):
    """
    获取历史K线数据（使用 yfinance）
    
    参数：
       品种代码: 如 'AAPL' 或 '300750.SZ'
       开始日期: '2024-01-01'
       结束日期: '2024-12-31'
       频率: '1d', '1wk', '1mo'
    """
    try:
        ticker = yf.Ticker(品种代码)
        df = ticker.history(start=开始日期, end=结束日期, interval=频率)
        return df
    except Exception as e:
        print(f"获取历史K线失败: {e}")
        return pd.DataFrame()


# ========== 批量获取（可选）==========
def 批量获取价格(品种列表):
    """批量获取多个品种的价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
        time.sleep(0.5)  # 避免请求过快
    return results


# 测试入口
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块 v3.0")
    print("=" * 50)
    
    # 测试A股
    print("\n--- 测试A股 ---")
    data = 获取价格("300750.SZ")
    print(f"结果: {data.品种} = {data.价格}")
    
    # 测试加密货币
    print("\n--- 测试加密货币 ---")
    data = 获取价格("ETH-USD")
    print(f"结果: {data.品种} = {data.价格}")
    
    # 测试美股
    print("\n--- 测试美股 ---")
    data = 获取价格("AAPL")
    print(f"结果: {data.品种} = {data.价格}")
