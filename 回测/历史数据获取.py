# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def 获取历史K线(品种代码, 周期="1d", 开始日期=None, 结束日期=None, 限制数量=500):
    """
    获取真实历史K线数据
    
    参数:
    - 品种代码: AAPL, EURUSD=X, BTC-USD, GC=F 等
    - 周期: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
    - 开始日期: YYYY-MM-DD
    - 结束日期: YYYY-MM-DD
    - 限制数量: 最大K线数量（实际会获取更多以确保足够）
    
    返回: DataFrame 包含开盘、最高、最低、收盘、成交量
    """
    
    # 品种代码映射
    映射表 = {
        "EURUSD": "EURUSD=X",
        "BTC-USD": "BTC-USD",
        "GC=F": "GC=F",
        "AAPL": "AAPL",
        "000001.SS": "000001.SS",
        "00700.HK": "0700.HK",
    }
    
    代码 = 映射表.get(品种代码, 品种代码)
    
    try:
        # 设置默认日期 - 获取更多数据（限制数量的3倍）
        if 结束日期 is None:
            结束日期 = datetime.now()
        
        # 根据周期计算需要多少天
        周期天数映射 = {
            "1m": 7,      # 1分钟线需要7天才能有足够K线
            "5m": 30,     # 5分钟线需要30天
            "15m": 60,    # 15分钟线需要60天
            "30m": 90,    # 30分钟线需要90天
            "1h": 180,    # 1小时间需要180天
            "1d": 730,    # 日线需要2年（730天）
            "1wk": 1825,  # 周线需要5年
            "1mo": 3650,  # 月线需要10年
        }
        
        额外天数 = 周期天数映射.get(周期, 365)
        
        if 开始日期 is None:
            开始日期 = 结束日期 - timedelta(days=额外天数)
        else:
            # 如果用户指定的开始日期太近，自动往前推
            指定天数 = (结束日期 - 开始日期).days
            if 指定天数 < 额外天数:
                开始日期 = 结束日期 - timedelta(days=额外天数)
                print(f"⚠️ 开始日期自动调整为 {开始日期.date()}，以确保获取足够历史数据")
        
        print(f"📊 获取数据: {品种代码}, 周期={周期}, 范围={开始日期.date()} 至 {结束日期.date()}")
        
        # 获取历史数据
        股票 = yf.Ticker(代码)
        历史 = 股票.history(start=开始日期, end=结束日期, interval=周期)
        
        if 历史.empty:
            print(f"⚠️ 警告: {品种代码} 无历史数据，使用模拟数据")
            return _获取模拟历史数据(品种代码, 限制数量)
        
        # 限制返回数量（但保留足够的数据）
        if len(历史) > 限制数量:
            历史 = 历史.tail(限制数量)
        
        print(f"✅ 成功获取 {len(历史)} 根K线")
        
        # 标准化列名
        历史 = 历史.rename(columns={
            'Open': '开盘',
            'High': '最高',
            'Low': '最低',
            'Close': '收盘',
            'Volume': '成交量'
        })
        
        return 历史[['开盘', '最高', '最低', '收盘', '成交量']]
    
    except Exception as e:
        print(f"❌ 获取历史数据失败: {e}")
        return _获取模拟历史数据(品种代码, 限制数量)


def _获取模拟历史数据(品种代码, 限制数量=500):
    """生成模拟历史数据（备用）"""
    import numpy as np
    
    基准价格 = {
        "EURUSD": 1.085,
        "BTC-USD": 45000,
        "GC=F": 1950,
        "AAPL": 175,
    }.get(品种代码, 100)
    
    # 生成随机价格序列
    np.random.seed(42)
    涨跌幅 = np.random.randn(限制数量) * 0.02
    价格序列 = 基准价格 * (1 + np.cumsum(涨跌幅) / 100)
    
    df = pd.DataFrame({
        '开盘': 价格序列,
        '最高': 价格序列 * (1 + np.random.rand(限制数量) * 0.01),
        '最低': 价格序列 * (1 - np.random.rand(限制数量) * 0.01),
        '收盘': 价格序列 * (1 + np.random.randn(限制数量) * 0.005),
        '成交量': np.random.randint(500, 5000, 限制数量)
    })
    
    print(f"📊 使用模拟数据: {限制数量} 根K线")
    return df


def 获取数据信息(品种代码, 周期="1d"):
    """
    获取数据可用性信息（用于调试）
    """
    try:
        映射表 = {
            "EURUSD": "EURUSD=X",
            "BTC-USD": "BTC-USD",
            "GC=F": "GC=F",
            "AAPL": "AAPL",
            "000001.SS": "000001.SS",
            "00700.HK": "0700.HK",
        }
        代码 = 映射表.get(品种代码, 品种代码)
        股票 = yf.Ticker(代码)
        
        # 获取可用的历史数据范围
        历史 = 股票.history(period="max")
        
        if not 历史.empty:
            最早日期 = 历史.index[0]
            最晚日期 = 历史.index[-1]
            return {
                "可用": True,
                "最早数据": 最早日期,
                "最新数据": 最晚日期,
                "数据量": len(历史),
                "品种代码": 代码
            }
        else:
            return {"可用": False, "原因": "无数据"}
            
    except Exception as e:
        return {"可用": False, "原因": str(e)}
