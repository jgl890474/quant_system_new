# -*- coding: utf-8 -*-
"""
行情获取模块 - Tushare + 演示数据
- A股：Tushare Pro 实时数据
- 外汇：实时API（优先）+ 演示数据（备用）
- 其他：演示数据（接近真实）
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta


class 行情数据:
    def __init__(self, 品种, 价格):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0


# ==================== Tushare 配置 ====================
TUSHARE_TOKEN = 'a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac'

def 获取Tushare实时价格(代码):
    """使用 Tushare 获取A股实时价格"""
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        if str(代码).startswith('6'):
            ts_code = f"{代码}.SH"
        else:
            ts_code = f"{代码}.SZ"
        
        df = pro.daily(ts_code=ts_code, limit=1)
        if df is not None and not df.empty:
            return float(df['close'].iloc[-1])
    except Exception as e:
        print(f"Tushare获取失败: {e}")
    return None


# ==================== 外汇实时汇率 ====================
def 获取外汇实时价格(品种):
    """获取外汇实时汇率"""
    try:
        if 品种 == "EURUSD":
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
        elif 品种 == "GBPUSD":
            url = "https://api.exchangerate-api.com/v4/latest/GBP"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
    except Exception as e:
        print(f"外汇获取失败: {e}")
    return None


# ==================== 演示数据（美股/加密货币/期货） ====================
def 获取演示价格(品种):
    """返回接近真实市场的演示价格"""
    演示价格表 = {
        # 美股
        "AAPL": 175.00,
        "TSLA": 170.00,
        "NVDA": 120.00,
        "MSFT": 330.00,
        "GOOGL": 130.00,
        "AMZN": 130.00,
        "META": 300.00,
        # 加密货币
        "BTC-USD": 45000,
        "ETH-USD": 2300,
        "SOL-USD": 95,
        "BNB-USD": 580,
        # 期货
        "GC=F": 1950,
        "CL=F": 78,
        # A股演示
        "000001": 11.24,
        "600036": 37.90,
        "300750": 180.00,
        # 外汇（备用）
        "EURUSD": 1.08,
    }
    return 演示价格表.get(品种, 100)


# ==================== 主入口 ====================
def 获取价格(品种代码):
    """统一价格获取入口"""
    print(f"🔍 获取: {品种代码}")
    
    # A股：优先使用 Tushare
    if 品种代码.isdigit() or (len(str(品种代码)) == 6 and str(品种代码).isdigit()):
        price = 获取Tushare实时价格(品种代码)
        if price and price > 0:
            print(f"✅ [Tushare] {品种代码} = {price}")
            return 行情数据(品种代码, price)
        else:
            price = 获取演示价格(品种代码)
            print(f"📊 [演示A股] {品种代码} = {price}")
            return 行情数据(品种代码, price)
    
    # 外汇：优先实时API
    if 品种代码 in ["EURUSD", "GBPUSD", "EUR/USD"]:
        price = 获取外汇实时价格(品种代码)
        if price and price > 0:
            print(f"✅ [外汇实时] {品种代码} = {price}")
            return 行情数据(品种代码, price)
        else:
            price = 获取演示价格(品种代码)
            print(f"📊 [演示外汇] {品种代码} = {price}")
            return 行情数据(品种代码, price)
    
    # 其他品种使用演示数据
    price = 获取演示价格(品种代码)
    print(f"📊 [演示] {品种代码} = {price}")
    return 行情数据(品种代码, price)


def 获取K线数据(代码, 周期="1d", 长度=60):
    """获取K线数据"""
    # A股尝试从 Tushare 获取
    if str(代码).isdigit() and len(str(代码)) == 6:
        try:
            import tushare as ts
            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()
            
            if str(代码).startswith('6'):
                ts_code = f"{代码}.SH"
            else:
                ts_code = f"{代码}.SZ"
            
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=长度*2)).strftime('%Y%m%d')
            
            df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and not df.empty:
                df = df.rename(columns={
                    'trade_date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'vol': '成交量'
                })
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
                return df.tail(长度)[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        except Exception as e:
            print(f"Tushare K线获取失败: {e}")
    
    # 生成模拟K线
    dates = pd.date_range(end=datetime.now(), periods=长度, freq='D')
    base_price = 获取演示价格(代码)
    np.random.seed(hash(代码) % 10000)
    returns = np.random.randn(长度) * 0.02
    price_series = base_price * np.cumprod(1 + returns)
    
    # 确保价格为正
    price_series = np.maximum(price_series, 0.01)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price_series * 0.99,
        '最高': price_series * 1.02,
        '最低': price_series * 0.98,
        '收盘': price_series,
        '成交量': np.random.randint(1000, 100000, 长度)
    })
    return df


def 计算技术指标(df):
    """计算技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    # RSI
    delta = df_copy['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_copy['RSI'] = 100 - (100 / (1 + rs))
    
    return df_copy


# ==================== 批量获取 ====================
def 批量获取价格(品种列表):
    """批量获取多个品种的价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
    return results


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    test_symbols = ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA", "000001"]
    for s in test_symbols:
        price = 获取价格(s)
        print(f"{s}: {price.价格}")
