# -*- coding: utf-8 -*-
import akshare as ak
import yfinance as yf
import jqdatasdk as jq
import random
import requests
import time
from datetime import datetime, timedelta


# ---------- JQData 配置（请替换为你的账号密码）----------
JQ_ACCOUNT = "13908808670"   # 替换为你的聚宽手机号
JQ_PWD = "jgl240736CC"       # 替换为你的聚宽密码
# -------------------------------------------------------

# 尝试初始化 JQData 连接
try:
    jq.auth(JQ_ACCOUNT, JQ_PWD)
    JQ_AVAILABLE = True
    print("✅ JQData 认证成功")
except Exception as e:
    JQ_AVAILABLE = False
    print(f"❌ JQData 认证失败: {e}，将使用备用数据源")


class 行情数据:
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = 价格
        self.最高 = 最高
        self.最低 = 最低
        self.开盘 = 开盘
        self.成交量 = 成交量
        self.涨跌 = 0


def 获取价格(品种代码):
    """统一入口，根据品种选择不同的数据源"""
    
    # 1. A股 -> 首选 JQData，失败后降级到 AKShare
    if '.SZ' in 品种代码 or '.SS' in 品种代码:
        return 获取_A股_JQData(品种代码) if JQ_AVAILABLE else 获取_A股_AKShare(品种代码)
    
    # 2. 加密货币 -> 币安 API
    if 'BTC' in 品种代码 or 'ETH' in 品种代码:
        return 获取_加密货币_币安(品种代码)
    
    # 3. 其他（美股、外汇、期货等）-> yfinance
    return 获取_其他_yfinance(品种代码)


def 获取_A股_JQData(品种代码):
    """
    使用 JQData 获取 A 股最新价格
    关键：限定只请求最近1条数据，避免试用账号历史数据权限限制
    """
    try:
        # 确保 JQData 已认证
        if not jq.is_auth():
            jq.auth(JQ_ACCOUNT, JQ_PWD)
        
        # 关键修改：只取最新1条数据，不指定 start_date，避免触发历史数据限制
        df = jq.get_price(
            品种代码,
            count=1,                    # 只取1条最新数据
            frequency="1m",            # 1分钟K线作为实时价格
            fields=['open', 'high', 'low', 'close', 'volume'],
            skip_paused=True,
            fq='pre'
        )
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            price = float(latest['close'])
            return 行情数据(
                品种代码, 
                price, 
                float(latest['high']), 
                float(latest['low']), 
                float(latest['open']), 
                int(latest['volume'])
            )
        else:
            print(f"JQData 未返回 {品种代码} 的数据")
            
    except Exception as e:
        print(f"JQData 获取 {品种代码} 失败: {e}")
    
    # 降级到 AKShare
    return 获取_A股_AKShare(品种代码)


def 获取_A股_AKShare(品种代码):
    """AKShare 备用获取 A 股实时行情"""
    try:
        # 提取纯数字代码
        纯代码 = 品种代码.replace('.SZ', '').replace('.SS', '')
        
        # 获取全部A股实时行情（东方财富源）
        df = ak.stock_zh_a_spot_em()
        
        # 筛选目标股票
        row = df[df['代码'] == 纯代码]
        
        if not row.empty:
            价格 = float(row['最新价'].iloc[0])
            最高 = float(row['最高'].iloc[0]) if '最高' in row.columns else 价格
            最低 = float(row['最低'].iloc[0]) if '最低' in row.columns else 价格
            开盘 = float(row['今开'].iloc[0]) if '今开' in row.columns else 价格
            成交量 = int(row['成交量'].iloc[0]) if '成交量' in row.columns else 0
            
            return 行情数据(品种代码, 价格, 最高, 最低, 开盘, 成交量)
        else:
            print(f"AKShare 未找到 {品种代码}")
            
    except Exception as e:
        print(f"AKShare 获取 {品种代码} 失败: {e}")
    
    # 最终降级：演示数据
    return 获取_演示数据(品种代码)


def 获取_加密货币_币安(品种代码):
    """币安 API 获取加密货币价格"""
    try:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = float(data['price'])
        return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取 {品种代码} 失败: {e}")
        return 获取_演示数据(品种代码)


def 获取_其他_yfinance(品种代码):
    """yfinance 获取美股、外汇、期货等数据"""
    try:
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            high = float(data['High'].iloc[-1]) if 'High' in data else price
            low = float(data['Low'].iloc[-1]) if 'Low' in data else price
            open_price = float(data['Open'].iloc[-1]) if 'Open' in data else price
            volume = int(data['Volume'].iloc[-1]) if 'Volume' in data else 0
            return 行情数据(品种代码, price, high, low, open_price, volume)
    except Exception as e:
        print(f"yfinance 获取 {品种代码} 失败: {e}")
    
    return 获取_演示数据(品种代码)


def 获取_演示数据(品种代码):
    """最终降级：演示/模拟数据"""
    演示价格 = {
        # A股
        "300750.SZ": 437.00,
        "002415.SZ": 35.55,
        "000333.SZ": 80.40,
        "000001.SS": 3150,
        # 美股
        "AAPL": 175.00,
        "MSFT": 330.00,
        "GOOGL": 130.00,
        "TSLA": 240.00,
        "NVDA": 120.00,
        # 加密货币
        "BTC-USD": 45000,
        "ETH-USD": 2300,
        # 期货
        "GC=F": 1950,
        "CL=F": 95,
        # 外汇
        "EURUSD": 1.08,
        "GBPUSD=X": 1.27,
    }.get(品种代码, 100)
    
    # 添加小波动避免显示全为0
    波动 = random.uniform(-0.005, 0.005)
    价格 = 演示价格 * (1 + 波动)
    
    print(f"[演示模式] {品种代码}: {价格:.2f}")
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
