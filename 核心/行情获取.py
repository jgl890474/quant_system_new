# -*- coding: utf-8 -*-
"""
行情获取模块 - 通用版
- A股：yfinance + 演示数据
- 美股/加密货币/期货：yfinance + 演示数据
- 外汇：实时API + 演示数据
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta


class 行情数据:
    def __init__(self, 品种, 价格):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0


# ==================== 通用演示价格表 ====================
演示价格 = {
    # A股
    "000001": 11.24,
    "600036": 37.90,
    "600519": 1450.00,
    "300750": 180.00,
    "002415": 35.55,
    "000333": 80.40,
    # 美股
    "AAPL": 175.00,
    "TSLA": 170.00,
    "NVDA": 120.00,
    "MSFT": 330.00,
    "GOOGL": 130.00,
    "AMZN": 130.00,
    # 加密货币
    "BTC-USD": 45000,
    "ETH-USD": 2300,
    "SOL-USD": 95,
    "BNB-USD": 580,
    # 期货
    "GC=F": 1950,
    "CL=F": 78,
    # 外汇
    "EURUSD": 1.08,
    "GBPUSD": 1.27,
}


# ==================== 获取价格（主入口） ====================
def 获取价格(品种代码):
    """获取实时价格 - 使用 yfinance + 演示数据"""
    print(f"🔍 获取行情: {品种代码}")
    
    try:
        # 处理A股代码格式（用于yfinance）
        if str(品种代码).isdigit() and len(str(品种代码)) == 6:
            if str(品种代码).startswith('6'):
                ticker = f"{品种代码}.SS"
            else:
                ticker = f"{品种代码}.SZ"
        else:
            ticker = 品种代码
        
        # 尝试从 yfinance 获取
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"✅ [yfinance] {品种代码} = {price}")
            return 行情数据(品种代码, price)
    except Exception as e:
        print(f"yfinance获取失败 {品种代码}: {e}")
    
    # 外汇专用API
    if 品种代码 in ["EURUSD", "GBPUSD"]:
        try:
            if 品种代码 == "EURUSD":
                url = "https://api.exchangerate-api.com/v4/latest/EUR"
                r = requests.get(url, timeout=3)
                price = float(r.json()['rates']['USD'])
                print(f"✅ [外汇] {品种代码} = {price}")
                return 行情数据(品种代码, price)
        except:
            pass
    
    # 使用演示价格
    price = 演示价格.get(品种代码, 100)
    print(f"📊 [演示] {品种代码} = {price}")
    return 行情数据(品种代码, price)


# ==================== K线数据 ====================
def 获取K线数据(代码, 周期="日线", 长度=60):
    """获取K线数据"""
    return 生成模拟K线数据(代码, 周期, 长度)


def 生成模拟K线数据(代码, 周期, 长度):
    """生成模拟K线数据"""
    end_date = datetime.now()
    
    # 根据周期生成日期
    if 周期 == "日线":
        dates = pd.date_range(end=end_date, periods=长度, freq='D')
    elif 周期 == "周线":
        dates = pd.date_range(end=end_date, periods=长度, freq='W')
    elif 周期 == "60分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='H')
    elif 周期 == "30分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='30min')
    elif 周期 == "10分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='10min')
    else:
        dates = pd.date_range(end=end_date, periods=长度, freq='D')
    
    # 基准价格
    base_price = 演示价格.get(str(代码), 100)
    
    np.random.seed(abs(hash(str(代码))) % 10000)
    returns = np.random.randn(长度) * 0.02
    price = base_price * np.cumprod(1 + returns)
    price = np.maximum(price, 0.01)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * (1 + np.random.randn(长度) * 0.005),
        '最高': price * (1 + abs(np.random.randn(长度) * 0.01)),
        '最低': price * (1 - abs(np.random.randn(长度) * 0.01)),
        '收盘': price,
        '成交量': np.random.randint(10000, 1000000, 长度)
    })
    
    # 确保数据正确
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    
    return df


# ==================== 技术指标 ====================
def 计算技术指标(df):
    """计算技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    # 移动平均线
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5, min_periods=1).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10, min_periods=1).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20, min_periods=1).mean()
    
    # MACD
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    # 布林带
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20, min_periods=1).mean()
    bb_std = df_copy['收盘'].rolling(window=20, min_periods=1).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + (bb_std * 2)
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - (bb_std * 2)
    
    # 填充空值
    df_copy = df_copy.fillna(method='bfill').fillna(method='ffill')
    
    return df_copy


# ==================== 批量获取 ====================
def 批量获取价格(品种列表):
    """批量获取价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
    return results


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    test_list = ["000001", "600036", "AAPL", "BTC-USD", "EURUSD", "GC=F"]
    for s in test_list:
        p = 获取价格(s)
        print(f"{s}: {p.价格}")
