# -*- coding: utf-8 -*-
"""
行情获取模块 - 稳定版
- A股：Tushare Pro（优先）+ 演示数据（备用）
- 美股/加密货币/期货：yfinance + 演示数据
- 外汇：实时API
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
    """使用 Tushare 获取A股最新价格"""
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
            price = float(df['close'].iloc[-1])
            print(f"✅ [Tushare] {代码} = {price}")
            return price
    except Exception as e:
        print(f"Tushare获取失败 {代码}: {e}")
    
    return None


def 获取Tushare历史K线(代码, 开始日期, 结束日期, 长度=60):
    """使用 Tushare 获取A股历史K线"""
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        if str(代码).startswith('6'):
            ts_code = f"{代码}.SH"
        else:
            ts_code = f"{代码}.SZ"
        
        df = pro.daily(ts_code=ts_code, start_date=开始日期, end_date=结束日期)
        
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
        print(f"Tushare历史K线获取失败 {代码}: {e}")
    
    return None


# ==================== yfinance 获取美股/加密货币/期货 ====================
def 获取YFinance价格(代码):
    """使用 yfinance 获取价格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"✅ [yfinance] {代码} = {price}")
            return price
    except Exception as e:
        print(f"yfinance获取失败 {代码}: {e}")
    return None


# ==================== 外汇实时汇率 ====================
def 获取外汇价格(品种):
    """获取外汇实时汇率"""
    try:
        if 品种 in ["EURUSD", "EUR/USD", "EUR-USD"]:
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            r = requests.get(url, timeout=5)
            data = r.json()
            price = float(data['rates']['USD'])
            print(f"✅ [外汇] {品种} = {price}")
            return price
        elif 品种 in ["GBPUSD", "GBP/USD"]:
            url = "https://api.exchangerate-api.com/v4/latest/GBP"
            r = requests.get(url, timeout=5)
            data = r.json()
            price = float(data['rates']['USD'])
            return price
    except Exception as e:
        print(f"外汇获取失败 {品种}: {e}")
    return None


# ==================== A股演示价格表 ====================
A股演示价格 = {
    "000001": 11.24,
    "600036": 37.90,
    "300750": 180.00,
    "002415": 35.55,
    "000333": 80.40,
}


# ==================== 通用演示价格表 ====================
通用演示价格 = {
    "AAPL": 175.00,
    "TSLA": 170.00,
    "NVDA": 120.00,
    "MSFT": 330.00,
    "GOOGL": 130.00,
    "BTC-USD": 45000,
    "ETH-USD": 2300,
    "SOL-USD": 95,
    "BNB-USD": 580,
    "GC=F": 1950,
    "CL=F": 78,
    "EURUSD": 1.08,
}


# ==================== 判断品种类型 ====================
def 是A股(代码):
    code_str = str(代码)
    if code_str.isdigit() and len(code_str) == 6:
        return True
    if code_str.endswith('.SS') or code_str.endswith('.SZ'):
        return True
    return False


def 是外汇(代码):
    return 代码 in ["EURUSD", "EUR/USD", "EUR-USD", "GBPUSD", "GBP/USD"]


# ==================== 主入口 ====================
def 获取价格(品种代码):
    """统一价格获取入口"""
    原始代码 = 品种代码
    print(f"🔍 获取: {原始代码}")
    
    # ========== A股：优先 Tushare ==========
    if 是A股(品种代码):
        code_num = str(品种代码).replace('.SS', '').replace('.SZ', '')
        
        # 优先 Tushare 实时数据
        price = 获取Tushare实时价格(code_num)
        if price is not None and price > 0:
            return 行情数据(原始代码, price)
        
        # Tushare 失败，使用 A股演示价格
        demo_price = A股演示价格.get(code_num, 37.90)
        print(f"📊 [演示A股] {原始代码} = {demo_price}")
        return 行情数据(原始代码, demo_price)
    
    # ========== 外汇：优先实时API ==========
    if 是外汇(品种代码):
        price = 获取外汇价格(品种代码)
        if price is not None and price > 0:
            return 行情数据(原始代码, price)
        
        demo_price = 通用演示价格.get(品种代码, 1.08)
        print(f"📊 [演示外汇] {原始代码} = {demo_price}")
        return 行情数据(原始代码, demo_price)
    
    # ========== 其他：yfinance + 演示 ==========
    price = 获取YFinance价格(品种代码)
    if price is not None and price > 0:
        return 行情数据(原始代码, price)
    
    demo_price = 通用演示价格.get(品种代码, 100)
    print(f"📊 [演示] {原始代码} = {demo_price}")
    return 行情数据(原始代码, demo_price)


def 获取K线数据(代码, 周期="1d", 长度=60):
    """获取K线数据"""
    if 是A股(代码):
        code_num = str(代码).replace('.SS', '').replace('.SZ', '')
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=长度*2)).strftime('%Y%m%d')
        df = 获取Tushare历史K线(code_num, start_date, end_date, 长度)
        if df is not None and not df.empty:
            return df
    
    return 生成模拟K线数据(代码, 周期, 长度)


def 生成模拟K线数据(代码, 周期, 长度):
    """生成模拟K线数据"""
    end_date = datetime.now()
    
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
    
    # 获取基准价格
    if 是A股(代码):
        code_num = str(代码).replace('.SS', '').replace('.SZ', '')
        base_price = A股演示价格.get(code_num, 37.90)
    else:
        base_price = 通用演示价格.get(str(代码), 100)
    
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
    
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    
    return df


def 计算技术指标(df):
    """计算技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5, min_periods=1).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10, min_periods=1).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20, min_periods=1).mean()
    
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20, min_periods=1).mean()
    bb_std = df_copy['收盘'].rolling(window=20, min_periods=1).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + (bb_std * 2)
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - (bb_std * 2)
    
    df_copy = df_copy.fillna(method='bfill').fillna(method='ffill')
    
    return df_copy


def 批量获取价格(品种列表):
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
    return results


# 测试
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    test_symbols = ["000001", "600036", "AAPL", "BTC-USD", "EURUSD", "GC=F"]
    for s in test_symbols:
        price = 获取价格(s)
        print(f"{s}: {price.价格}")
