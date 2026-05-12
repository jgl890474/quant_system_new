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
    """从新浪获取A股实时行情"""
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
        
        return float(data[3])  # 当前价
    except Exception as e:
        print(f"新浪获取 {代码} 失败: {e}")
        return None


# ==================== 币安 API（加密货币） ====================
def 获取币安价格(symbol):
    """从币安获取加密货币实时价格"""
    try:
        # 处理不同格式
        if symbol == "BTC-USD":
            api_symbol = "BTCUSDT"
        elif symbol == "ETH-USD":
            api_symbol = "ETHUSDT"
        elif symbol == "SOL-USD":
            api_symbol = "SOLUSDT"
        elif symbol == "BNB-USD":
            api_symbol = "BNBUSDT"
        else:
            api_symbol = symbol.replace('-', '').upper()
        
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={api_symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "price" in data:
            return float(data["price"])
    except Exception as e:
        print(f"币安获取 {symbol} 失败: {e}")
    return None


# ==================== yfinance（美股、期货） ====================
def 获取YFinance价格(symbol):
    """从 yfinance 获取实时价格"""
    try:
        import yfinance as yf
        
        # 特殊处理
        if symbol == "GC=F":
            ticker_symbol = "GC=F"
        elif symbol == "CL=F":
            ticker_symbol = "CL=F"
        else:
            ticker_symbol = symbol
        
        ticker = yf.Ticker(ticker_symbol)
        
        # 获取实时价格
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"yfinance获取 {symbol} 失败: {e}")
    return None


# ==================== 外汇 API ====================
def 获取外汇价格(currency_pair):
    """获取外汇实时汇率"""
    try:
        if currency_pair == "EURUSD" or currency_pair == "EUR/USD":
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
        elif currency_pair == "GBPUSD":
            url = "https://api.exchangerate-api.com/v4/latest/GBP"
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data['rates']['USD'])
    except Exception as e:
        print(f"外汇获取 {currency_pair} 失败: {e}")
    return None


# ==================== 判断市场类型 ====================
def 判断市场类型(代码):
    """根据代码判断属于哪个市场"""
    代码_upper = str(代码).upper()
    
    # A股
    if str(代码).endswith('.SZ') or str(代码).endswith('.SS'):
        return "A股"
    if str(代码).isnumeric() and len(str(代码)) == 6:
        return "A股"
    
    # 加密货币
    if 'BTC' in 代码_upper or 'ETH' in 代码_upper or 'SOL' in 代码_upper or 'BNB' in 代码_upper:
        return "加密货币"
    
    # 外汇
    if 代码_upper in ['EURUSD', 'EUR/USD', 'GBPUSD']:
        return "外汇"
    
    # 期货
    if 代码_upper in ['GC=F', 'CL=F']:
        return "期货"
    
    # 美股
    return "美股"


# ==================== 实时价格获取（统一入口） ====================
class 行情数据:
    def __init__(self, 品种, 价格):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0


def 获取价格(品种代码):
    """获取单个品种的实时价格"""
    # 处理显示名称
    if 品种代码 == "EUR/USD":
        市场 = "外汇"
    else:
        市场 = 判断市场类型(品种代码)
    
    print(f"🔍 获取: {品种代码} (市场: {市场})")
    
    try:
        # A股：新浪财经
        if 市场 == "A股":
            code_num = str(品种代码).replace('.SZ', '').replace('.SS', '')
            价格 = 获取新浪实时行情(code_num)
            if 价格 and 价格 > 0:
                print(f"✅ [新浪] {品种代码} = {价格}")
                return 行情数据(品种代码, 价格)
        
        # 加密货币：币安
        elif 市场 == "加密货币":
            价格 = 获取币安价格(品种代码)
            if 价格 and 价格 > 0:
                print(f"✅ [币安] {品种代码} = {价格}")
                return 行情数据(品种代码, 价格)
        
        # 外汇
        elif 市场 == "外汇":
            价格 = 获取外汇价格(品种代码)
            if 价格 and 价格 > 0:
                print(f"✅ [外汇] {品种代码} = {价格}")
                return 行情数据(品种代码, 价格)
        
        # 期货/美股：yfinance
        elif 市场 in ["期货", "美股"]:
            价格 = 获取YFinance价格(品种代码)
            if 价格 and 价格 > 0:
                print(f"✅ [yfinance] {品种代码} = {价格}")
                return 行情数据(品种代码, 价格)
        
        print(f"❌ 获取 {品种代码} 失败")
        return 行情数据(品种代码, 0)
        
    except Exception as e:
        print(f"❌ {品种代码} 异常: {e}")
        return 行情数据(品种代码, 0)


def 获取实时价格(代码):
    """获取实时价格，直接返回数值"""
    result = 获取价格(代码)
    return result.价格 if result else 0


# ==================== K线数据获取 ====================
def 获取K线数据(代码, 周期="1d", 长度=60):
    """获取K线数据用于图表显示"""
    try:
        import yfinance as yf
        
        # A股代码转换
        if 判断市场类型(代码) == "A股":
            if str(代码).startswith('6'):
                ticker_symbol = f"{代码}.SS"
            else:
                ticker_symbol = f"{代码}.SZ"
        else:
            ticker_symbol = 代码
        
        # 周期映射
        周期映射 = {
            "1d": "1d", "1wk": "1wk", "1h": "1h", "30m": "30m", "10m": "10m"
        }
        interval = 周期映射.get(周期, "1d")
        
        get_days = 长度 + 30 if 周期 == "1d" else 7
        
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
            df = df.tail(长度)
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        
    except Exception as e:
        print(f"获取K线失败: {e}")
    
    return pd.DataFrame()


def 计算技术指标(df):
    """计算技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    if '收盘' not in df_copy.columns:
        return df_copy
    
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    delta = df_copy['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_copy['RSI'] = 100 - (100 / (1 + rs))
    
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20).mean()
    bb_std = df_copy['收盘'].rolling(window=20).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + 2 * bb_std
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - 2 * bb_std
    
    return df_copy


# ==================== Tushare 数据（可选，用于历史数据） ====================
TUSHARE_TOKEN = 'a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac'

def 获取Tushare日线(代码, 开始日期, 结束日期):
    """获取A股历史日线（用于回测）"""
    try:
        import tushare as ts
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        if str(代码).startswith('6'):
            ts_code = f"{代码}.SH"
        else:
            ts_code = f"{代码}.SZ"
        
        df = pro.daily(ts_code=ts_code, 
                       start_date=开始日期.replace('-', ''), 
                       end_date=结束日期.replace('-', ''))
        
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
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
    except Exception as e:
        print(f"Tushare获取失败: {e}")
    
    return None


# ==================== 测试 ====================
if __name__ == "__main__":
    print("="*50)
    print("测试行情获取模块")
    print("="*50)
    
    test_symbols = ["000001", "AAPL", "BTC-USD", "EURUSD", "GC=F", "TSLA", "NVDA"]
    
    for symbol in test_symbols:
        price = 获取价格(symbol)
        print(f"{symbol}: {price.价格}")
        time.sleep(0.5)
