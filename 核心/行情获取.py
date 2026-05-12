# -*- coding: utf-8 -*-
"""
行情获取模块 - 实时价格数据源
数据源：
- A股：新浪财经实时行情（盘中实时）
- 加密货币：币安 API（实时）
- 美股：yfinance（实时）
- 外汇：ExchangeRate-API（实时）
- 期货：yfinance（实时）
"""

import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# ==================== 新浪财经实时行情（A股） ====================
def 获取新浪实时行情(代码):
    """
    从新浪获取A股实时行情（盘中实时）
    返回: 价格
    """
    try:
        if str(代码).startswith('6'):
            symbol = f"sh{代码}"
        else:
            symbol = f"sz{代码}"
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'gbk'
        
        content = response.text
        if 'str_' not in content or '=""' in content:
            return None
        
        data = content.split(',')
        if len(data) < 10:
            return None
        
        当前价 = float(data[3])
        return 当前价
    except Exception as e:
        print(f"新浪获取 {代码} 行情失败: {e}")
        return None


# ==================== 币安 API（加密货币） ====================
def 获取币安价格(symbol):
    """从币安获取加密货币实时价格"""
    try:
        symbol = symbol.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "price" in data:
            return float(data["price"])
    except Exception as e:
        print(f"币安获取 {symbol} 失败: {e}")
    return None


# ==================== yfinance（美股、期货、外汇备用） ====================
def 获取YFinance价格(symbol):
    """从 yfinance 获取实时价格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        
        # 方法1：获取实时价格
        info = ticker.info
        if 'regularMarketPrice' in info:
            return float(info['regularMarketPrice'])
        if 'currentPrice' in info:
            return float(info['currentPrice'])
        
        # 方法2：获取最新K线
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"yfinance获取 {symbol} 失败: {e}")
    return None


# ==================== 外汇 API（实时汇率） ====================
def 获取外汇价格(currency_pair):
    """获取外汇实时汇率"""
    try:
        # 使用 ExchangeRate-API（免费，无需注册）
        if currency_pair == "EURUSD":
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
        elif currency_pair == "GBPUSD":
            url = "https://api.exchangerate-api.com/v4/latest/GBP"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
        elif currency_pair == "USDJPY":
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['JPY'])
    except Exception as e:
        print(f"外汇获取 {currency_pair} 失败: {e}")
    return None


# ==================== 判断市场类型 ====================
def 判断市场类型(代码):
    """根据代码判断属于哪个市场"""
    代码_upper = str(代码).upper()
    
    # A股判断
    if str(代码).endswith('.SZ') or str(代码).endswith('.SS'):
        return "A股"
    if str(代码).isnumeric() and len(str(代码)) == 6:
        return "A股"
    
    # 加密货币判断
    加密货币列表 = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD']
    if 代码_upper in 加密货币列表:
        return "加密货币"
    if '-' in 代码_upper and 代码_upper.split('-')[0] in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE', 'ADA']:
        return "加密货币"
    
    # 外汇判断
    if 代码_upper in ['EURUSD', 'GBPUSD', 'USDJPY', 'EURUSD=X', 'GBPUSD=X']:
        return "外汇"
    
    # 期货判断
    if 代码_upper in ['GC=F', 'CL=F', 'SI=F', 'HG=F']:
        return "期货"
    
    # 美股判断
    美股列表 = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 
               'AMD', 'INTC', 'IBM', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'PYPL', 'DIS']
    if 代码_upper in 美股列表:
        return "美股"
    if 代码_upper.isalpha() and 2 <= len(代码_upper) <= 5:
        return "美股"
    
    return "未知"


# ==================== 实时价格获取（统一入口） ====================
class 行情数据:
    def __init__(self, 品种, 价格):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0


def 获取价格(品种代码):
    """
    获取单个品种的实时价格（统一入口）
    返回带有 .价格 属性的对象
    """
    市场 = 判断市场类型(品种代码)
    原始代码 = 品种代码
    
    # 标准化代码格式
    if 品种代码 == "EURUSD":
        品种代码 = "EURUSD"
    elif 品种代码 == "GBPUSD=X":
        品种代码 = "GBPUSD"
    
    print(f"🔍 获取价格: {原始代码} (市场: {市场})")
    
    try:
        # A股：新浪财经
        if 市场 == "A股":
            # 提取纯数字代码
            code_num = str(原始代码).replace('.SZ', '').replace('.SS', '')
            价格 = 获取新浪实时行情(code_num)
            if 价格 and 价格 > 0:
                print(f"✅ [新浪] {原始代码} = {价格}")
                return 行情数据(原始代码, 价格)
        
        # 加密货币：币安 API
        elif 市场 == "加密货币":
            价格 = 获取币安价格(原始代码)
            if 价格 and 价格 > 0:
                print(f"✅ [币安] {原始代码} = {价格}")
                return 行情数据(原始代码, 价格)
        
        # 外汇：ExchangeRate-API
        elif 市场 == "外汇":
            价格 = 获取外汇价格(原始代码)
            if 价格 and 价格 > 0:
                print(f"✅ [外汇] {原始代码} = {价格}")
                return 行情数据(原始代码, 价格)
        
        # 期货/美股：yfinance
        elif 市场 in ["期货", "美股"]:
            价格 = 获取YFinance价格(原始代码)
            if 价格 and 价格 > 0:
                print(f"✅ [yfinance] {原始代码} = {价格}")
                return 行情数据(原始代码, 价格)
        
        # 如果都失败，返回 None
        print(f"❌ 获取 {原始代码} 价格失败")
        return 行情数据(原始代码, 0)
        
    except Exception as e:
        print(f"❌ 获取 {原始代码} 价格异常: {e}")
        return 行情数据(原始代码, 0)


def 获取实时价格(代码):
    """获取实时价格，直接返回数值"""
    result = 获取价格(代码)
    if result and hasattr(result, '价格'):
        return result.价格
    return 0


# ==================== 批量获取价格 ====================
def 批量获取价格(品种列表):
    """批量获取多个品种的实时价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
        time.sleep(0.3)  # 避免请求过快
    return results


# ==================== K线数据获取（用于回测和图表） ====================
def 获取K线数据(代码, 周期="1d", 长度=60):
    """获取K线数据用于图表显示"""
    try:
        import yfinance as yf
        
        市场 = 判断市场类型(代码)
        
        # A股代码转换
        if 市场 == "A股":
            if str(代码).startswith('6'):
                ticker_symbol = f"{代码}.SS"
            else:
                ticker_symbol = f"{代码}.SZ"
        else:
            ticker_symbol = 代码
        
        # 周期映射
        周期映射 = {
            "1d": "1d",
            "1wk": "1wk", 
            "1h": "1h",
            "30m": "30m",
            "10m": "10m"
        }
        interval = 周期映射.get(周期, "1d")
        
        # 计算获取天数
        if 周期 in ["30m", "10m", "1h"]:
            get_days = 7
        else:
            get_days = 长度 + 30
        
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=f"{get_days}d", interval=interval)
        
        if not df.empty:
            df = df.reset_index()
            date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            df = df.rename(columns={
                date_col: '日期',
                'Open': '开盘',
                'High': '最高',
                'Low': '最低',
                'Close': '收盘',
                'Volume': '成交量'
            })
            df = df.sort_values('日期')
            df = df.tail(长度)
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        
    except Exception as e:
        print(f"获取K线数据失败: {e}")
    
    return pd.DataFrame()


def 计算技术指标(df):
    """计算常用技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    if '收盘' not in df_copy.columns:
        return df_copy
    
    # 移动平均线
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    
    # MACD
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
    
    # 布林带
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20).mean()
    bb_std = df_copy['收盘'].rolling(window=20).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + 2 * bb_std
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - 2 * bb_std
    
    return df_copy


# ==================== 测试 ====================
if __name__ == "__main__":
    print("="*50)
    print("测试行情获取模块")
    print("="*50)
    
    # 测试 A股
    print("\n1. 测试 A股 (000001):")
    price = 获取价格("000001")
    print(f"价格: {price.价格}")
    
    # 测试 加密货币
    print("\n2. 测试 加密货币 (ETH-USD):")
    price = 获取价格("ETH-USD")
    print(f"价格: {price.价格}")
    
    # 测试 美股
    print("\n3. 测试 美股 (AAPL):")
    price = 获取价格("AAPL")
    print(f"价格: {price.价格}")
    
    # 测试 外汇
    print("\n4. 测试 外汇 (EURUSD):")
    price = 获取价格("EURUSD")
    print(f"价格: {price.价格}")
