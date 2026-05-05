def get_historical_klines(symbol="EURUSD", count=50):
    """获取历史K线数据"""
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
    
    # 返回模拟数据
    result = []
    import time
    now = time.time()
    base_price = 1.09
    for i in range(count):
        result.append({
            "timestamp": int(now - (count - i) * 60),
            "open": base_price + i * 0.0001,
            "high": base_price + i * 0.0001 + 0.001,
            "low": base_price + i * 0.0001 - 0.001,
            "close": base_price + i * 0.0001
        })
    return result
