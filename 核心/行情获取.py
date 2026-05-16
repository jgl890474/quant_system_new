# -*- coding: utf-8 -*-
"""
行情获取模块 - 优化版
只保留三类市场：加密货币、A股、美股
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# ==================== 配置 ====================
TUSHARE_TOKEN = "a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac"

# 缓存配置
缓存时间 = {}
缓存数据 = {}
缓存秒数 = 5

# 本地文件缓存
本地缓存文件 = "data/price_cache.json"
本地缓存过期 = 60


def _加载本地缓存():
    """从文件加载缓存"""
    if os.path.exists(本地缓存文件):
        try:
            with open(本地缓存文件, 'r', encoding='utf-8') as f:
                data = json.load(f)
                当前时间 = time.time()
                for 品种, 缓存项 in data.items():
                    if 当前时间 - 缓存项.get('时间', 0) < 本地缓存过期:
                        缓存数据[品种] = 缓存项.get('价格')
                        缓存时间[品种] = 缓存项.get('时间', 0)
        except:
            pass


def _保存本地缓存():
    """保存缓存到文件"""
    try:
        os.makedirs('data', exist_ok=True)
        保存数据 = {}
        for 品种, 价格 in 缓存数据.items():
            if 品种 in 缓存时间:
                保存数据[品种] = {'价格': 价格, '时间': 缓存时间[品种]}
        with open(本地缓存文件, 'w', encoding='utf-8') as f:
            json.dump(保存数据, f, ensure_ascii=False)
    except:
        pass


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


# ==================== 演示价格表（只保留三类市场） ====================
演示价格 = {
    # 加密货币
    "BTC-USD": 79586.70,
    "ETH-USD": 2219.12,
    "SOL-USD": 145.30,
    "BNB-USD": 580.00,
    
    # 美股
    "AAPL": 185.50,
    "NVDA": 950.00,
    "TSLA": 175.30,
    "MSFT": 420.00,
    
    # A股
    "000001.SS": 1680.00,
    "300750.SZ": 220.50,
    "002594.SZ": 265.80,
}


# ==================== 市场识别 ====================
def 识别市场(品种代码: str) -> str:
    """识别市场类型"""
    代码 = str(品种代码).upper()
    
    # 加密货币
    if '-' in 代码 or 代码 in ['BTC', 'ETH', 'BNB', 'SOL']:
        return "加密货币"
    
    # A股（6位数字，可能带.SS或.SZ）
    if (代码.isdigit() and len(代码) == 6) or '.SS' in 代码 or '.SZ' in 代码:
        return "A股"
    
    # 美股（字母代码）
    if 代码.isalpha() and len(代码) <= 5:
        return "美股"
    
    return "美股"


# ==================== 实时价格获取 ====================
def 获取价格(品种代码: str, 强制刷新: bool = False) -> 行情数据:
    """获取实时价格（带缓存和降级）"""
    print(f"🔍 获取行情: {品种代码}")
    
    # 检查内存缓存
    if not 强制刷新:
        if 品种代码 in 缓存数据 and 品种代码 in 缓存时间:
            if time.time() - 缓存时间[品种代码] < 缓存秒数:
                print(f"📦 [内存缓存] {品种代码} = {缓存数据[品种代码]}")
                return 行情数据(品种代码, 缓存数据[品种代码], 数据源="cache")
    
    市场 = 识别市场(品种代码)
    result = None
    
    # 根据市场类型获取价格
    if 市场 == "加密货币":
        result = _获取加密货币价格(品种代码)
    elif 市场 == "A股":
        result = _获取A股价格(品种代码)
    elif 市场 == "美股":
        result = _获取美股价格(品种代码)
    
    # 使用演示价格作为降级
    if result is None:
        价格 = 演示价格.get(品种代码, 100)
        print(f"📊 [演示数据] {品种代码} = {价格}")
        result = 行情数据(品种代码, 价格, 数据源="demo")
    
    # 更新缓存
    缓存数据[品种代码] = result.价格
    缓存时间[品种代码] = time.time()
    _保存本地缓存()
    
    return result


def _获取加密货币价格(品种代码: str) -> Optional[行情数据]:
    """获取加密货币价格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"✅ [yfinance] {品种代码} = {price}")
            return 行情数据(品种代码, price, 数据源="yfinance")
    except Exception as e:
        print(f"yfinance获取失败: {e}")
    
    return None


def _获取A股价格(品种代码: str) -> Optional[行情数据]:
    """获取A股价格"""
    try:
        # 提取股票代码
        代码 = str(品种代码).replace('.SS', '').replace('.SZ', '').zfill(6)
        
        # 确定市场代码（6开头是沪市，0/3开头是深市）
        市场代码 = "1" if 代码.startswith('6') else "0"
        
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': f"{市场代码}.{代码}",
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get('data'):
            quote = data['data']
            price = quote.get('f43', 0) / 100
            if price > 0:
                print(f"✅ [东方财富] {品种代码} = {price}")
                return 行情数据(
                    品种=品种代码,
                    价格=price,
                    涨跌幅=quote.get('f170', 0) / 100,
                    数据源="eastmoney"
                )
    except Exception as e:
        print(f"东方财富获取失败: {e}")
    
    return None


def _获取美股价格(品种代码: str) -> Optional[行情数据]:
    """获取美股价格"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            print(f"✅ [yfinance] {品种代码} = {price}")
            return 行情数据(品种代码, price, 数据源="yfinance")
    except:
        pass
    return None


# ==================== K线数据获取 ====================
def 获取K线数据(品种代码: str, 周期: str = "日线", 长度: int = 60, 
                开始日期: datetime = None, 结束日期: datetime = None) -> pd.DataFrame:
    """获取K线数据"""
    return 生成模拟K线数据(品种代码, 周期, 长度)


def 生成模拟K线数据(品种代码: str, 周期: str = "日线", 长度: int = 60) -> pd.DataFrame:
    """生成模拟K线数据"""
    end_date = datetime.now()
    周期映射 = {"日线": 'D', "周线": 'W', "60分钟": 'H', "30分钟": '30min'}
    freq = 周期映射.get(周期, 'D')
    
    dates = pd.date_range(end=end_date, periods=长度, freq=freq)
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
    
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    return df


def 计算技术指标(df: pd.DataFrame) -> pd.DataFrame:
    """计算技术指标"""
    if df.empty:
        return df
    df_copy = df.copy()
    df_copy['MA5'] = df_copy['收盘'].rolling(5).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(20).mean()
    df_copy['MA60'] = df_copy['收盘'].rolling(60).mean()
    return df_copy


def 批量获取价格(品种列表: List[str]) -> Dict[str, 行情数据]:
    """批量获取价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
        time.sleep(0.1)
    return results


def 刷新所有持仓价格(引擎) -> Dict[str, 行情数据]:
    """刷新所有持仓价格"""
    if not hasattr(引擎, '持仓') or not 引擎.持仓:
        return {}
    return 批量获取价格(list(引擎.持仓.keys()))


def 清空缓存():
    """清空所有缓存"""
    global 缓存数据, 缓存时间
    缓存数据 = {}
    缓存时间 = {}
    if os.path.exists(本地缓存文件):
        try:
            os.remove(本地缓存文件)
        except:
            pass


# 加载本地缓存
_加载本地缓存()


# ==================== 市场列表 ====================
def 获取支持的市场列表() -> List[str]:
    """获取支持的市场列表"""
    return ["加密货币", "A股", "美股"]


def 获取市场品种(市场: str) -> List[str]:
    """获取指定市场的品种列表"""
    市场品种映射 = {
        "加密货币": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"],
        "A股": ["000001.SS", "300750.SZ", "002594.SZ"],
        "美股": ["AAPL", "NVDA", "TSLA", "MSFT"],
    }
    return 市场品种映射.get(市场, [])


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    print(f"\n支持的市场: {获取支持的市场列表()}")
    
    for 市场 in 获取支持的市场列表():
        print(f"\n{市场}:")
        for 品种 in 获取市场品种(市场):
            p = 获取价格(品种)
            print(f"  {品种}: ¥{p.价格:,.2f} (来源: {p.数据源})")
