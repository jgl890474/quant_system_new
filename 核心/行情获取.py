# -*- coding: utf-8 -*-
"""
行情获取模块 v2.0
数据源优先级：
- A股历史数据：JQData（试用账号，范围2024-02 ~ 2026-02）
- A股实时数据：AKShare（备用，可能不稳定）
- 加密货币：币安API（免费）
- 美股/外汇/期货：yfinance（免费）
- 最终降级：演示数据
"""

import akshare as ak
import yfinance as yf
import jqdatasdk as jq
import random
import requests
import time
from datetime import datetime, timedelta
import pandas as pd


# ========== JQData 配置 ==========
JQ_ACCOUNT = "13908808670"   # 你的聚宽手机号
JQ_PWD = "jgl240736CC"       # 你的聚宽密码
# ================================

# 尝试初始化 JQData 连接
try:
    jq.auth(JQ_ACCOUNT, JQ_PWD)
    JQ_AVAILABLE = True
    print("✅ JQData 认证成功（试用账号，仅限历史数据）")
except Exception as e:
    JQ_AVAILABLE = False
    print(f"❌ JQData 认证失败: {e}")


class 行情数据:
    """统一的行情数据类"""
    def __init__(self, 品种, 价格, 最高, 最低, 开盘, 成交量):
        self.品种 = 品种
        self.价格 = float(价格) if 价格 else 0.0
        self.最高 = float(最高) if 最高 else 0.0
        self.最低 = float(最低) if 最低 else 0.0
        self.开盘 = float(开盘) if 开盘 else 0.0
        self.成交量 = int(成交量) if 成交量 else 0
        self.涨跌 = 0.0


def 获取价格(品种代码):
    """
    统一入口，根据品种选择不同的数据源
    返回：行情数据 对象
    """
    # 1. A股 -> JQData历史数据（或AKShare备用）
    if '.SZ' in 品种代码 or '.SS' in 品种代码:
        return 获取_A股(品种代码)
    
    # 2. 加密货币 -> 币安 API
    if 'BTC' in 品种代码 or 'ETH' in 品种代码:
        return 获取_加密货币_币安(品种代码)
    
    # 3. 其他（美股、外汇、期货等）-> yfinance
    return 获取_其他_yfinance(品种代码)


def 获取_A股(品种代码):
    """
    获取 A股数据
    优先级：1. 实时行情(AKShare) -> 2. 历史数据(JQData) -> 3. 演示数据
    """
    # 方案1：AKShare 实时行情（最接近实时，但可能不稳定）
    result = 获取_A股_AKShare(品种代码)
    if result and result.价格 > 0:
        return result
    
    # 方案2：JQData 历史数据（稳定，但只能拿2024-02到2026-02的数据）
    if JQ_AVAILABLE:
        result = 获取_A股_JQData(品种代码)
        if result and result.价格 > 0:
            return result
    
    # 方案3：演示数据
    return 获取_演示数据(品种代码)


def 获取_A股_JQData(品种代码):
    """
    使用 JQData 获取 A股历史数据（试用账号范围：前15个月~前3个月）
    注意：无法获取今日实时数据
    """
    try:
        if not jq.is_auth():
            jq.auth(JQ_ACCOUNT, JQ_PWD)
        
        # 试用账号只能获取历史数据，指定一个在权限范围内的日期
        # 使用最近的可用日期（比如3天前）
        end_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=95)).strftime('%Y-%m-%d')
        
        df = jq.get_price(
            品种代码,
            start_date=start_date,
            end_date=end_date,
            frequency='daily',
            fields=['open', 'high', 'low', 'close', 'volume']
        )
        
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            price = float(latest['close'])
            print(f"[JQData历史] {品种代码}: {price} (日期: {latest.name})")
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
    
    return None


def 获取_A股_AKShare(品种代码):
    """AKShare 获取 A 股实时行情（东方财富源）"""
    try:
        纯代码 = 品种代码.replace('.SZ', '').replace('.SS', '')
        
        # 方法1：获取单只股票实时行情（更快）
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == 纯代码]
            if not row.empty:
                价格 = float(row['最新价'].iloc[0])
                最高 = float(row['最高'].iloc[0]) if '最高' in row.columns else 价格
                最低 = float(row['最低'].iloc[0]) if '最低' in row.columns else 价格
                开盘 = float(row['今开'].iloc[0]) if '今开' in row.columns else 价格
                成交量 = int(row['成交量'].iloc[0]) if '成交量' in row.columns else 0
                
                if 价格 > 0:
                    print(f"[AKShare实时] {品种代码}: {价格}")
                    return 行情数据(品种代码, 价格, 最高, 最低, 开盘, 成交量)
        except Exception as e:
            print(f"AKShare 方法1失败: {e}")
        
        # 方法2：使用个股实时行情接口（备用）
        try:
            df = ak.stock_zh_a_spot()
            row = df[df['代码'] == 纯代码]
            if not row.empty:
                价格 = float(row['最新价'].iloc[0])
                print(f"[AKShare备用] {品种代码}: {价格}")
                return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)
        except Exception as e:
            print(f"AKShare 方法2失败: {e}")
            
    except Exception as e:
        print(f"AKShare 获取 {品种代码} 失败: {e}")
    
    return None


def 获取_加密货币_币安(品种代码):
    """币安 API 获取加密货币价格"""
    try:
        symbol = 品种代码.replace('-', '').upper()
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = float(data['price'])
        print(f"[币安实时] {品种代码}: ${price}")
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
            print(f"[yfinance] {品种代码}: {price}")
            return 行情数据(品种代码, price, price, price, price, 0)
    except Exception as e:
        print(f"yfinance 获取 {品种代码} 失败: {e}")
    
    return 获取_演示数据(品种代码)


def 获取_演示数据(品种代码):
    """最终降级：演示/模拟数据（用于开发测试）"""
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
    
    print(f"[演示数据] {品种代码}: {价格:.2f}")
    return 行情数据(品种代码, 价格, 价格, 价格, 价格, 0)


def 获取历史K线(品种代码, 开始日期, 结束日期, 频率='daily'):
    """
    获取历史K线数据（专门用于回测）
    
    参数：
       品种代码: 如 '300750.SZ'
       开始日期: '2024-01-01'
       结束日期: '2024-12-31'
       频率: 'daily', '60m', '30m', '15m', '5m', '1m'
    """
    if not JQ_AVAILABLE:
        print("JQData 不可用，无法获取历史K线")
        return pd.DataFrame()
    
    try:
        if not jq.is_auth():
            jq.auth(JQ_ACCOUNT, JQ_PWD)
        
        df = jq.get_price(
            品种代码,
            start_date=开始日期,
            end_date=结束日期,
            frequency=频率,
            fields=['open', 'high', 'low', 'close', 'volume']
        )
        return df
    except Exception as e:
        print(f"获取历史K线失败: {e}")
        return pd.DataFrame()


# ========== 批量获取（可选）==========
def 批量获取价格(品种列表):
    """批量获取多个品种的价格"""
    results = {}
    for 品种 in 品种列表:
        results[品种] = 获取价格(品种)
        time.sleep(0.5)  # 避免请求过快
    return results


# 测试入口
if __name__ == "__main__":
    print("=" * 50)
    print("测试行情获取模块")
    print("=" * 50)
    
    # 测试A股
    print("\n--- 测试A股 ---")
    data = 获取价格("300750.SZ")
    print(f"结果: {data.品种} = {data.价格}")
    
    # 测试加密货币
    print("\n--- 测试加密货币 ---")
    data = 获取价格("ETH-USD")
    print(f"结果: {data.品种} = {data.价格}")
    
    # 测试美股
    print("\n--- 测试美股 ---")
    data = 获取价格("AAPL")
    print(f"结果: {data.品种} = {data.价格}")
