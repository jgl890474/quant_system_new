# -*- coding: utf-8 -*-
"""
行情获取模块 - 完整版
- A股：东方财富API + Tushare备用 + 演示数据
- 加密货币：Binance API + yfinance备用 + 演示数据
- 美股：yfinance + 演示数据
- 外汇：实时API + 演示数据
- 期货：yfinance + 演示数据

功能：
- 实时价格获取（带缓存）
- K线数据获取
- 技术指标计算
- 批量获取
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json

# ==================== 配置 ====================
# Tushare token（备用）
TUSHARE_TOKEN = "a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac"

# 缓存配置
缓存时间 = {}  # 存储缓存过期时间
缓存数据 = {}  # 存储缓存数据
缓存秒数 = 5  # 默认缓存5秒


class 行情数据:
    """行情数据对象"""
    def __init__(self, 品种: str, 价格: float, 涨跌幅: float = 0, 
                 最高价: float = 0, 最低价: float = 0, 成交量: float = 0,
                 数据源: str = "demo", 时间戳: datetime = None):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.涨跌幅 = 涨跌幅
        self.最高价 = 最高价
        self.最低价 = 最低价
        self.成交量 = 成交量
        self.数据源 = 数据源
        self.时间戳 = 时间戳 or datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            '品种': self.品种,
            '价格': self.价格,
            '涨跌幅': self.涨跌幅,
            '最高价': self.最高价,
            '最低价': self.最低价,
            '成交量': self.成交量,
            '数据源': self.数据源,
            '时间戳': self.时间戳.strftime("%Y-%m-%d %H:%M:%S")
        }


# ==================== 演示价格表（兜底数据） ====================
演示价格 = {
    # A股
    "000001": 11.24, "000002": 9.45, "000858": 128.50,
    "600036": 37.90, "600519": 1450.00, "600050": 4.56,
    "300750": 180.00, "002415": 35.55, "000333": 80.40,
    "002594": 265.00, "601318": 42.50, "600276": 45.80,
    # 美股
    "AAPL": 175.00, "TSLA": 170.00, "NVDA": 120.00,
    "MSFT": 330.00, "GOOGL": 130.00, "AMZN": 130.00,
    "META": 300.00, "NFLX": 400.00, "AMD": 110.00,
    # 加密货币
    "BTC-USD": 45000, "ETH-USD": 2300, "SOL-USD": 95,
    "BNB-USD": 580, "DOGE-USD": 0.11, "XRP-USD": 0.52,
    "ADA-USD": 0.45, "AVAX-USD": 35.00,
    # 期货
    "GC=F": 1950, "CL=F": 78, "SI=F": 23.50,
    # 外汇
    "EURUSD": 1.08, "GBPUSD": 1.27, "USDJPY": 148.50,
}

# 品种类型映射
品种类型映射 = {
    'A股': ['000001', '600036', '600519', '300750', '002415', '000333', '002594', '601318', '600276', '600050', '000002', '000858'],
    '加密货币': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'DOGE-USD', 'XRP-USD', 'ADA-USD', 'AVAX-USD'],
    '美股': ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'AMD'],
    '期货': ['GC=F', 'CL=F', 'SI=F'],
    '外汇': ['EURUSD', 'GBPUSD', 'USDJPY']
}

# CoinGecko ID 映射（备用）
COINGECKO_ID = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
    'DOGE': 'dogecoin', 'SOL': 'solana', 'XRP': 'ripple',
    'ADA': 'cardano', 'AVAX': 'avalanche-2'
}


# ==================== 市场识别 ====================
def 识别市场(品种代码: str) -> str:
    """自动识别品种市场类型"""
    代码 = str(品种代码).upper()
    
    # 检查加密货币
    if 代码 in 品种类型映射['加密货币'] or '-' in 代码:
        return "加密货币"
    
    # 检查A股（6位数字）
    if 代码.isdigit() and len(代码) == 6:
        return "A股"
    
    # 检查期货
    if 代码.endswith('=F') or 代码 in 品种类型映射['期货']:
        return "期货"
    
    # 检查外汇
    if 代码 in 品种类型映射['外汇'] or (len(代码) == 6 and 代码.isalpha()):
        return "外汇"
    
    # 默认识别为美股
    return "美股"


# ==================== 实时价格获取 ====================
def 获取价格(品种代码: str, 强制刷新: bool = False) -> 行情数据:
    """
    获取实时价格（带缓存）
    
    参数:
        品种代码: 如 "000001", "BTC-USD", "AAPL", "EURUSD"
        强制刷新: 是否强制刷新缓存
    
    返回:
        行情数据对象
    """
    print(f"🔍 获取行情: {品种代码}")
    
    # 检查缓存
    if not 强制刷新:
        if 品种代码 in 缓存数据 and 品种代码 in 缓存时间:
            if time.time() - 缓存时间[品种代码] < 缓存秒数:
                print(f"📦 [缓存] {品种代码} = {缓存数据[品种代码].价格}")
                return 缓存数据[品种代码]
    
    # 识别市场
    市场 = 识别市场(品种代码)
    
    # 根据市场获取价格
    if 市场 == "加密货币":
        result = _获取加密货币价格(品种代码)
    elif 市场 == "A股":
        result = _获取A股价格(品种代码)
    elif 市场 == "美股":
        result = _获取美股价格(品种代码)
    elif 市场 == "外汇":
        result = _获取外汇价格(品种代码)
    elif 市场 == "期货":
        result = _获取期货价格(品种代码)
    else:
        result = None
    
    # 如果获取失败，使用演示价格
    if result is None:
        价格 = 演示价格.get(品种代码, 100)
        print(f"📊 [演示] {品种代码} = {价格}")
        result = 行情数据(品种代码, 价格, 0, 0, 0, 0, "demo")
    
    # 更新缓存
    缓存数据[品种代码] = result
    缓存时间[品种代码] = time.time()
    
    return result


def _获取加密货币价格(品种代码: str) -> Optional[行情数据]:
    """获取加密货币价格 - Binance API"""
    try:
        # BTC-USD -> BTCUSDT
        symbol = 品种代码.upper().replace('-', '').replace('USD', 'USDT')
        if 'USDT' not in symbol:
            symbol = symbol + 'USDT'
        
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, params={'symbol': symbol}, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return 行情数据(
                品种=品种代码,
                价格=float(data.get('lastPrice', 0)),
                涨跌幅=float(data.get('priceChangePercent', 0)),
                最高价=float(data.get('highPrice', 0)),
                最低价=float(data.get('lowPrice', 0)),
                成交量=float(data.get('volume', 0)),
                数据源="binance"
            )
    except Exception as e:
        print(f"Binance获取失败 {品种代码}: {e}")
    
    # 备用：yfinance
    return _获取通过Yfinance(品种代码, "加密货币")


def _获取A股价格(品种代码: str) -> Optional[行情数据]:
    """获取A股价格 - 东方财富API"""
    try:
        代码 = str(品种代码).zfill(6)
        市场代码 = "1" if 代码.startswith('6') else "0"
        
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': f"{市场代码}.{代码}",
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get('data'):
            quote = data['data']
            return 行情数据(
                品种=品种代码,
                价格=quote.get('f43', 0) / 100,
                涨跌幅=quote.get('f170', 0) / 100,
                最高价=quote.get('f44', 0) / 100,
                最低价=quote.get('f45', 0) / 100,
                成交量=quote.get('f47', 0),
                数据源="eastmoney"
            )
    except Exception as e:
        print(f"东方财富获取失败 {品种代码}: {e}")
    
    # 备用：yfinance
    return _获取通过Yfinance(品种代码, "A股")


def _获取美股价格(品种代码: str) -> Optional[行情数据]:
    """获取美股价格 - yfinance"""
    return _获取通过Yfinance(品种代码, "美股")


def _获取期货价格(品种代码: str) -> Optional[行情数据]:
    """获取期货价格 - yfinance"""
    return _获取通过Yfinance(品种代码, "期货")


def _获取外汇价格(品种代码: str) -> Optional[行情数据]:
    """获取外汇价格 - 实时API"""
    try:
        if 品种代码 == "EURUSD":
            url = "https://api.exchangerate-api.com/v4/latest/EUR"
            response = requests.get(url, timeout=3)
            price = float(response.json()['rates']['USD'])
            return 行情数据(品种代码, price, 0, price, price, 0, "forex")
        elif 品种代码 == "GBPUSD":
            url = "https://api.exchangerate-api.com/v4/latest/GBP"
            response = requests.get(url, timeout=3)
            price = float(response.json()['rates']['USD'])
            return 行情数据(品种代码, price, 0, price, price, 0, "forex")
    except Exception as e:
        print(f"外汇API获取失败 {品种代码}: {e}")
    
    return None


def _获取通过Yfinance(品种代码: str, 市场类型: str) -> Optional[行情数据]:
    """通过 yfinance 获取价格（通用）"""
    try:
        import yfinance as yf
        
        # 处理A股代码格式
        if 市场类型 == "A股":
            ticker = f"{品种代码}.SS" if str(品种代码).startswith('6') else f"{品种代码}.SZ"
        else:
            ticker = 品种代码
        
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            high = float(data['High'].iloc[-1])
            low = float(data['Low'].iloc[-1])
            volume = float(data['Volume'].iloc[-1])
            return 行情数据(品种代码, price, 0, high, low, volume, "yfinance")
    except Exception as e:
        print(f"yfinance获取失败 {品种代码}: {e}")
    
    return None


# ==================== K线数据获取 ====================
def 获取K线数据(品种代码: str, 周期: str = "日线", 长度: int = 60, 
                开始日期: datetime = None, 结束日期: datetime = None) -> pd.DataFrame:
    """
    获取K线数据
    
    参数:
        品种代码: 品种代码
        周期: 日线/周线/60分钟/30分钟/10分钟
        长度: K线数量
        开始日期: 开始日期
        结束日期: 结束日期
    """
    市场 = 识别市场(品种代码)
    
    if 市场 == "加密货币":
        df = _获取加密货币K线(品种代码, 周期, 长度, 开始日期, 结束日期)
    elif 市场 == "A股":
        df = _获取A股K线(品种代码, 周期, 长度, 开始日期, 结束日期)
    else:
        df = _获取通用K线(品种代码, 周期, 长度, 开始日期, 结束日期)
    
    if df is None or df.empty:
        df = 生成模拟K线数据(品种代码, 周期, 长度)
    
    # 计算技术指标
    if not df.empty:
        df = 计算技术指标(df)
    
    return df


def _获取加密货币K线(品种代码: str, 周期: str, 长度: int, 
                      开始日期: datetime, 结束日期: datetime) -> Optional[pd.DataFrame]:
    """获取加密货币K线 - Binance API"""
    try:
        # 周期映射
        周期映射 = {
            "日线": "1d", "周线": "1w", "60分钟": "1h",
            "30分钟": "30m", "10分钟": "10m"
        }
        interval = 周期映射.get(周期, "1d")
        
        symbol = 品种代码.upper().replace('-', '').replace('USD', 'USDT')
        if 'USDT' not in symbol:
            symbol = symbol + 'USDT'
        
        url = "https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': interval, 'limit': 长度}
        
        if 开始日期:
            params['startTime'] = int(开始日期.timestamp() * 1000)
        if 结束日期:
            params['endTime'] = int(结束日期.timestamp() * 1000)
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            rows = []
            for k in data:
                rows.append({
                    '日期': pd.to_datetime(k[0], unit='ms'),
                    '开盘': float(k[1]),
                    '最高': float(k[2]),
                    '最低': float(k[3]),
                    '收盘': float(k[4]),
                    '成交量': float(k[5])
                })
            df = pd.DataFrame(rows)
            df = df.sort_values('日期')
            return df
    except Exception as e:
        print(f"加密货币K线获取失败: {e}")
    
    return None


def _获取A股K线(品种代码: str, 周期: str, 长度: int,
                 开始日期: datetime, 结束日期: datetime) -> Optional[pd.DataFrame]:
    """获取A股K线 - 东方财富API"""
    try:
        代码 = str(品种代码).zfill(6)
        市场代码 = "1" if 代码.startswith('6') else "0"
        
        # 周期映射
        周期映射 = {"日线": "101", "周线": "102", "月线": "103"}
        klt = 周期映射.get(周期, "101")
        
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            'secid': f"{市场代码}.{代码}",
            'klt': klt,
            'fqt': '1',
            'lmt': 长度,
            'ut': 'fa5fd1943c7b386a172cb689d1c0edf1'
        }
        
        if 开始日期:
            params['beg'] = 开始日期.strftime("%Y%m%d")
        if 结束日期:
            params['end'] = 结束日期.strftime("%Y%m%d")
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('data') and data['data'].get('klines'):
            rows = []
            for k in data['data']['klines']:
                parts = k.split(',')
                rows.append({
                    '日期': parts[0],
                    '开盘': float(parts[1]),
                    '最高': float(parts[2]),
                    '最低': float(parts[3]),
                    '收盘': float(parts[4]),
                    '成交量': float(parts[5])
                })
            df = pd.DataFrame(rows)
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            return df
    except Exception as e:
        print(f"A股K线获取失败: {e}")
    
    return None


def _获取通用K线(品种代码: str, 周期: str, 长度: int,
                  开始日期: datetime, 结束日期: datetime) -> Optional[pd.DataFrame]:
    """通用K线获取 - yfinance"""
    try:
        import yfinance as yf
        
        # 周期映射
        周期映射 = {"日线": "1d", "周线": "1wk", "月线": "1mo"}
        interval = 周期映射.get(周期, "1d")
        
        ticker = 品种代码
        if 识别市场(品种代码) == "A股":
            ticker = f"{品种代码}.SS" if str(品种代码).startswith('6') else f"{品种代码}.SZ"
        
        if 开始日期 and 结束日期:
            df = yf.download(ticker, start=开始日期, end=结束日期, interval=interval, progress=False)
        else:
            df = yf.download(ticker, period=f"{长度}d", interval=interval, progress=False)
        
        if not df.empty:
            df = df.reset_index()
            df.columns = ['日期', '开盘', '最高', '最低', '收盘', '成交量'] + list(df.columns[6:]) if len(df.columns) > 6 else ['日期', '开盘', '最高', '最低', '收盘', '成交量']
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
    except Exception as e:
        print(f"通用K线获取失败: {e}")
    
    return None


def 生成模拟K线数据(品种代码: str, 周期: str = "日线", 长度: int = 60) -> pd.DataFrame:
    """生成模拟K线数据（兜底）"""
    end_date = datetime.now()
    
    # 根据周期生成日期
    周期映射 = {
        "日线": 'D', "周线": 'W', "60分钟": 'H',
        "30分钟": '30min', "10分钟": '10min'
    }
    freq = 周期映射.get(周期, 'D')
    
    dates = pd.date_range(end=end_date, periods=长度, freq=freq)
    
    # 基准价格
    base_price = 演示价格.get(str(品种代码), 100)
    
    np.random.seed(abs(hash(str(品种代码))) % 10000)
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


# ==================== 技术指标计算 ====================
def 计算技术指标(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标"""
    if df.empty or len(df) < 5:
        return df
    
    df_copy = df.copy()
    
    # 移动平均线
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5, min_periods=1).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10, min_periods=1).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20, min_periods=1).mean()
    df_copy['MA60'] = df_copy['收盘'].rolling(window=60, min_periods=1).mean()
    
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
    
    # RSI
    delta = df_copy['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_copy['RSI'] = 100 - (100 / (1 + rs))
    
    # 成交量均线
    df_copy['VOL_MA5'] = df_copy['成交量'].rolling(window=5).mean()
    df_copy['VOL_MA10'] = df_copy['成交量'].rolling(window=10).mean()
    
    # 填充空值
    df_copy = df_copy.fillna(method='bfill').fillna(method='ffill')
    
    return df_copy


# ==================== 批量获取 ====================
def 批量获取价格(品种列表: List[str]) -> Dict[str, 行情数据]:
    """批量获取多个品种价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
        time.sleep(0.1)  # 避免请求过快
    return results


def 刷新所有持仓价格(引擎) -> Dict[str, 行情数据]:
    """刷新所有持仓的实时价格"""
    if not hasattr(引擎, '持仓') or not 引擎.持仓:
        return {}
    
    品种列表 = list(引擎.持仓.keys())
    return 批量获取价格(品种列表)


# ==================== 缓存管理 ====================
def 清空缓存():
    """清空所有缓存"""
    global 缓存数据, 缓存时间
    缓存数据 = {}
    缓存时间 = {}
    print("🗑️ 行情缓存已清空")


def 设置缓存时长(秒数: int):
    """设置缓存时长"""
    global 缓存秒数
    缓存秒数 = 秒数
    print(f"⏱️ 缓存时长已设置为 {秒数} 秒")


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    test_list = ["000001", "600036", "AAPL", "BTC-USD", "EURUSD", "GC=F"]
    
    for s in test_list:
        print(f"\n测试品种: {s}")
        市场 = 识别市场(s)
        print(f"  识别市场: {市场}")
        
        p = 获取价格(s)
        print(f"  价格: {p.价格}")
        print(f"  数据源: {p.数据源}")
        print(f"  涨跌幅: {p.涨跌幅}%")
    
    print("\n" + "=" * 50)
    print("K线测试")
    print("=" * 50)
    
    df = 获取K线数据("BTC-USD", "日线", 30)
    print(f"获取到 {len(df)} 条K线数据")
    print(df.head())
