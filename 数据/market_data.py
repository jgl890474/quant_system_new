# -*- coding: utf-8 -*-
import yfinance as yf
import random

def get_1min_kline(symbol="EURUSD"):
    try:
        if symbol == "EURUSD":
            ticker = "EURUSD=X"
        elif symbol == "BTC-USD":
            ticker = "BTC-USD"
        elif symbol == "GC=F":
            ticker = "GC=F"
        else:
            ticker = symbol
        data = yf.Ticker(ticker).history(period="1d", interval="1m")
        if data is not None and len(data) > 0:
            latest = data.iloc[-1]
            return {
                "symbol": symbol,
                "close": float(latest['Close']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "open": float(latest['Open']),
                "timestamp": latest.name.strftime('%Y-%m-%d %H:%M:%S'),
                "volume": int(latest['Volume']) if latest['Volume'] else 0,
                "source": "yfinance"
            }
    except Exception as e:
        print(f"获取行情失败: {e}")
    price = random.uniform(1.08, 1.12)
    return {
        "symbol": symbol,
        "close": price,
        "high": price * 1.002,
        "low": price * 0.998,
        "open": price,
        "timestamp": None,
        "volume": 0,
        "source": "simulated"
    }

def get_historical_klines(symbol="EURUSD", count=50):
    try:
        if symbol == "EURUSD":
            ticker = "EURUSD=X"
        elif symbol == "BTC-USD":
            ticker = "BTC-USD"
        elif symbol == "GC=F":
            ticker = "GC=F"
        else:
            ticker = symbol
        data = yf.Ticker(ticker).history(period="5d", interval="1m")
        if data is not None and len(data) > 0:
            result = []
            for idx, row in data.tail(count).iterrows():
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
    return []
