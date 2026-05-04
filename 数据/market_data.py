# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import random
import time

# ================== 使用 yfinance 获取外汇数据 ==================
def get_forex_rate_yf(symbol="EURUSD=X"):
    """
    使用 yfinance 获取外汇汇率
    symbol: EURUSD=X, GBPUSD=X, AUDJPY=X, USDJPY=X 等
    """
    try:
        ticker = yf.Ticker(symbol)
        # 获取最近1分钟数据
        data = ticker.history(period="1d", interval="1m")
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            return {
                "symbol": symbol.replace("=X", ""),
                "close": float(latest['Close']),
                "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": int(latest['Volume']) if latest['Volume'] else 0,
                "source": "yfinance"
            }
    except Exception as e:
        print(f"yfinance 外汇获取失败 ({symbol}): {e}")
    
    # 模拟数据兜底
    price = random.uniform(1.08, 1.12) if "USD" in symbol else random.uniform(90, 110)
    return {
        "symbol": symbol.replace("=X", ""),
        "close": price,
        "timestamp": datetime.now().isoformat(),
        "open": price,
        "high": price * 1.002,
        "low": price * 0.998,
        "volume": 0,
        "source": "simulated"
    }

# ================== 使用 yfinance 获取期货数据 ==================
def get_futures_quote_yf(symbol="GC=F"):
    """
    使用 yfinance 获取期货行情
    symbol: GC=F(黄金), CL=F(原油), SI=F(白银) 等
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            return {
                "symbol": symbol,
                "close": float(latest['Close']),
                "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": int(latest['Volume']) if latest['Volume'] else 0,
                "source": "yfinance"
            }
    except Exception as e:
        print(f"yfinance 期货获取失败 ({symbol}): {e}")
    
    # 模拟数据兜底
    price = random.uniform(1900, 2100) if symbol == "GC=F" else random.uniform(70, 90)
    return {
        "symbol": symbol,
        "close": price,
        "timestamp": datetime.now().isoformat(),
        "open": price,
        "high": price * 1.005,
        "low": price * 0.995,
        "volume": 0,
        "source": "simulated"
    }

# ================== 加密货币数据 ==================
def get_crypto_price(symbol="BTC-USD"):
    """
    使用 yfinance 获取加密货币价格
    symbol: BTC-USD, ETH-USD 等
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            return {
                "symbol": symbol,
                "close": float(latest['Close']),
                "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": int(latest['Volume']) if latest['Volume'] else 0,
                "source": "yfinance"
            }
    except Exception as e:
        print(f"yfinance 加密货币获取失败 ({symbol}): {e}")
    
    price = random.uniform(50000, 60000)
    return {
        "symbol": symbol,
        "close": price,
        "timestamp": datetime.now().isoformat(),
        "open": price,
        "high": price * 1.005,
        "low": price * 0.995,
        "volume": 0,
        "source": "simulated"
    }

# ================== 统一获取1分钟K线接口 ==================
def get_1min_kline(symbol="BTC-USD"):
    """
    统一获取1分钟K线接口
    支持格式:
      - 加密货币: BTC-USD, ETH-USD
      - 外汇: EURUSD=X, GBPUSD=X, AUDJPY=X
      - 期货: GC=F, CL=F
    """
    # 加密货币
    if symbol in ["BTC-USD", "ETH-USD", "BTCUSDT"]:
        if symbol == "BTCUSDT":
            symbol = "BTC-USD"
        return get_crypto_price(symbol)
    
    # 外汇
    elif symbol in ["EURUSD", "GBPUSD", "AUDJPY", "USDJPY", "EURUSD=X", "GBPUSD=X", "AUDJPY=X"]:
        if "=X" not in symbol:
            symbol = f"{symbol}=X"
        return get_forex_rate_yf(symbol)
    
    # 期货
    elif symbol in ["GC=F", "CL=F"]:
        return get_futures_quote_yf(symbol)
    
    # 模拟数据兜底
    price = random.uniform(90, 110)
    return {
        "symbol": symbol,
        "close": price,
        "high": price * 1.005,
        "low": price * 0.995,
        "open": price,
        "timestamp": datetime.now().isoformat(),
        "volume": 0,
        "source": "simulated"
    }

# ================== 获取历史K线数据 ==================
def get_historical_klines(symbol="BTC-USD", count=50):
    try:
        # 格式化 symbol
        if symbol == "BTCUSDT":
            symbol = "BTC-USD"
        elif symbol in ["EURUSD", "GBPUSD", "AUDJPY"]:
            symbol = f"{symbol}=X"
        
        df = yf.Ticker(symbol).history(period="5d", interval="1m")
        if df is not None and len(df) > 0:
            result = []
            for idx, row in df.tail(count).iterrows():
                result.append({
                    "timestamp": int(idx.timestamp()),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close'])
                })
            return result
    except Exception as e:
        print(f"获取历史K线失败: {e}")
    
    # 生成模拟历史数据
    result = []
    now = datetime.now()
    base_price = 1.085
    for i in range(count):
        ts = now - timedelta(minutes=count - i)
        timestamp = int(ts.timestamp())
        price = base_price + (i * 0.0001)
        result.append({
            "timestamp": timestamp,
            "open": price,
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price
        })
    return result