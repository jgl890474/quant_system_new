# -*- coding: utf-8 -*-
import akshare as ak
import yfinance as yf
import jqdatasdk as jq
import random
import requests

# ---------- JQData 配置（请务必替换为你的账号密码）----------
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
    """使用 JQData 获取 A 股实时价格（取最新一条数据）"""
    try:
        # 确保 JQData 已认证
        if not jq.is_auth():
            jq.auth(JQ_ACCOUNT, JQ_PWD)
        # 获取最新1条1分钟K线作为实时价格
        df = jq.get_price(品种代码, count=1, frequency="1m", fields=['open', 'high', 'low', 'close', 'volume'])
        if not df.empty:
            latest = df.iloc[-1]
            price = latest['close']
            return 行情数据(品种代码, price, latest['high'], latest['low'], latest['open'], latest['volume'])
    except Exception as e:
        print(f"JQData 获取 {品种代码} 失败: {e}")
    # 降级到 AKShare
    return 获取_A股_AKShare(品种代码)


def 获取_A股_AKShare(品种代码):
    """AKShare 备用获取 A 股实时行情"""
    try:
        纯代码 = 品种代码.replace('.SZ', '').replace('.SS', '')
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == 纯代码]
        if not row.empty:
            价格 = float(row['最新价'].iloc[0])
            return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
    except Exception as e:
        print(f"AKShare 获取 {品种代码} 失败: {e}")
    return 行情数据(品种代码, 0, 0, 0, 0, 0)


def 获取_加密货币_币安(品种代码):
    """币安 API 获取加密货币价格"""
    try:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        price = float(r.json()['price'])
        return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"币安获取 {品种代码} 失败: {e}")
        return 行情数据(品种代码, 0, 0, 0, 0, 0)


def 获取_其他_yfinance(品种代码):
    """yfinance 获取美股、外汇、期货等数据"""
    try:
        ticker = yf.Ticker(品种代码)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"yfinance 获取 {品种代码} 失败: {e}")
    
    # 最终降级：演示数据
    演示价格 = {
        "AAPL": 175, "TSLA": 240, "NVDA": 120, "BTC-USD": 45000,
        "GC=F": 1950, "EURUSD": 1.08, "CL=F": 95, "ETH-USD": 2300,
        "300750.SZ": 437, "002415.SZ": 35.55, "000333.SZ": 80.4
    }.get(品种代码, 100)
    price = 演示价格 * (1 + random.uniform(-0.005, 0.005))
    return 行情数据(品种代码, price, price, price, price, 0)
