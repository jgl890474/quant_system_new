# -*- coding: utf-8 -*-
"""
行情获取模块 - 稳定版
数据源：
- A股：Tushare Pro（优先）+ 演示数据（备用）
- 外汇：实时API（优先）+ 演示数据（备用）
- 美股/加密货币/期货：演示数据（接近真实价格）
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
    """
    使用 Tushare 获取A股最新价格
    返回: 价格(float) 或 None
    """
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        # 转换代码格式
        if str(代码).startswith('6'):
            ts_code = f"{代码}.SH"
        else:
            ts_code = f"{代码}.SZ"
        
        # 获取最新一条日线数据
        df = pro.daily(ts_code=ts_code, limit=1)
        if df is not None and not df.empty:
            price = float(df['close'].iloc[-1])
            print(f"✅ [Tushare] {代码} = {price}")
            return price
    except Exception as e:
        print(f"Tushare获取失败 {代码}: {e}")
    
    return None


def 获取Tushare历史K线(代码, 开始日期, 结束日期, 长度=60):
    """
    使用 Tushare 获取A股历史K线数据
    返回: DataFrame 或 None
    """
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


# ==================== 外汇实时汇率 ====================
def 获取外汇实时价格(品种):
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
            print(f"✅ [外汇] {品种} = {price}")
            return price
    except Exception as e:
        print(f"外汇获取失败 {品种}: {e}")
    
    return None


# ==================== 演示数据（美股/加密货币/期货） ====================
def 获取演示价格(品种):
    """
    返回接近真实市场的演示价格
    用于美股、加密货币、期货等无法获取实时数据的品种
    """
    # 外汇演示数据
    if 品种 in ["EURUSD", "EUR/USD", "EUR-USD"]:
        return 1.08
    if 品种 in ["GBPUSD", "GBP/USD"]:
        return 1.27
    if 品种 in ["USDJPY", "USD/JPY"]:
        return 148.50
    
    # 演示价格表
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
        # A股演示（Tushare失败时备用）
        "000001": 11.24,
        "600036": 37.90,
        "300750": 180.00,
    }
    
    return 演示价格表.get(品种, 1.08)


# ==================== 判断品种类型 ====================
def 是A股(代码):
    """判断是否为A股代码"""
    代码_str = str(代码)
    # 6位数字
    if 代码_str.isdigit() and len(代码_str) == 6:
        return True
    # 带后缀
    if 代码_str.endswith('.SS') or 代码_str.endswith('.SZ'):
        return True
    return False


def 是外汇(代码):
    """判断是否为外汇"""
    return 代码 in ["EURUSD", "EUR/USD", "EUR-USD", "GBPUSD", "GBP/USD", "USDJPY", "USD/JPY"]


# ==================== 主入口 ====================
def 获取价格(品种代码):
    """
    统一价格获取入口
    优先级：
    1. A股 -> Tushare 实时数据
    2. 外汇 -> 实时API
    3. 其他 -> 演示数据
    """
    # 处理显示名称
    原始代码 = 品种代码
    if 品种代码 == "EUR/USD":
        品种代码 = "EURUSD"
    
    print(f"🔍 获取: {原始代码}")
    
    # ========== A股：优先使用 Tushare ==========
    if 是A股(品种代码):
        # 提取纯数字代码
        code_num = str(品种代码).replace('.SS', '').replace('.SZ', '')
        price = 获取Tushare实时价格(code_num)
        if price and price > 0:
            return 行情数据(原始代码, price)
        
        # Tushare 失败，使用演示数据
        price = 获取演示价格(code_num)
        print(f"📊 [演示A股] {原始代码} = {price}")
        return 行情数据(原始代码, price)
    
    # ========== 外汇：优先实时API ==========
    if 是外汇(品种代码):
        price = 获取外汇实时价格(品种代码)
        if price and price > 0:
            return 行情数据(原始代码, price)
        
        # API失败，使用演示数据
        price = 获取演示价格(品种代码)
        print(f"📊 [演示外汇] {原始代码} = {price}")
        return 行情数据(原始代码, price)
    
    # ========== 其他品种（美股/加密货币/期货）：使用演示数据 ==========
    price = 获取演示价格(品种代码)
    print(f"📊 [演示] {原始代码} = {price}")
    return 行情数据(原始代码, price)


def 获取K线数据(代码, 周期="1d", 长度=60):
    """
    获取K线数据
    优先使用 Tushare，失败时生成模拟K线
    """
    # A股：优先使用 Tushare 历史数据
    if 是A股(代码):
        code_num = str(代码).replace('.SS', '').replace('.SZ', '')
        
        # 计算日期范围
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=长度*2)).strftime('%Y%m%d')
        
        df = 获取Tushare历史K线(code_num, start_date, end_date, 长度)
        if df is not None and not df.empty:
            return df
    
    # 生成模拟K线（美观且稳定）
    dates = pd.date_range(end=datetime.now(), periods=长度, freq='D')
    base_price = 获取演示价格(代码)
    
    # 确保基础价格有效
    if base_price <= 0:
        base_price = 100
    
    np.random.seed(hash(str(代码)) % 10000)
    returns = np.random.randn(长度) * 0.02
    price_series = base_price * np.cumprod(1 + returns)
    price_series = np.maximum(price_series, 0.01)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price_series * (1 + np.random.randn(长度) * 0.005),
        '最高': price_series * (1 + abs(np.random.randn(长度) * 0.01)),
        '最低': price_series * (1 - abs(np.random.randn(长度) * 0.01)),
        '收盘': price_series,
        '成交量': np.random.randint(10000, 1000000, 长度)
    })
    
    # 确保最高>=最低
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    
    return df


def 计算技术指标(df):
    """
    计算技术指标（MA、MACD、RSI）
    """
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    if '收盘' not in df_copy.columns:
        return df_copy
    
    # 移动平均线
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    df_copy['MA60'] = df_copy['收盘'].rolling(window=60).mean()
    
    # 指数移动平均
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    # RSI
    delta = df_copy['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_copy['RSI'] = 100 - (100 / (1 + rs))
    
    # 布林带
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20).mean()
    bb_std = df_copy['收盘'].rolling(window=20).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + (bb_std * 2)
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - (bb_std * 2)
    
    return df_copy


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
    
    # 测试A股
    print("\n1. 测试A股 (000001):")
    price = 获取价格("000001")
    print(f"结果: {price.品种} = {price.价格}")
    
    # 测试美股（演示数据）
    print("\n2. 测试美股 (AAPL):")
    price = 获取价格("AAPL")
    print(f"结果: {price.品种} = {price.价格}")
    
    # 测试加密货币（演示数据）
    print("\n3. 测试加密货币 (BTC-USD):")
    price = 获取价格("BTC-USD")
    print(f"结果: {price.品种} = {price.价格}")
    
    # 测试外汇
    print("\n4. 测试外汇 (EURUSD):")
    price = 获取价格("EURUSD")
    print(f"结果: {price.品种} = {price.价格}")
    
    # 测试期货
    print("\n5. 测试期货 (GC=F):")
    price = 获取价格("GC=F")
    print(f"结果: {price.品种} = {price.价格}")
