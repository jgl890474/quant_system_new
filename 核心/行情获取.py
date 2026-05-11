# -*- coding: utf-8 -*-
"""
行情获取模块 - 支持多数据源自动降级
主数据源: Tushare Pro (A股)
备用数据源: yfinance (美股/加密货币/外汇)
"""

import pandas as pd
import time

# ==================== Tushare Pro 配置 ====================
try:
    import tushare as ts
    ts.set_token('a58ac285333f6f8ecc93063924c3dfd8906a1e01c1865cb624f097ac')
    pro = ts.pro_api()
    TUSHARE_AVAILABLE = True
    print("✅ Tushare Pro 已连接")
except Exception as e:
    TUSHARE_AVAILABLE = False
    print(f"⚠️ Tushare Pro 连接失败: {e}")
    pro = None

# ==================== yfinance 配置 ====================
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    print("✅ yfinance 已加载")
except Exception as e:
    YFINANCE_AVAILABLE = False
    print(f"⚠️ yfinance 加载失败: {e}")


# ==================== 判断市场类型 ====================
def 判断市场类型(代码):
    """根据代码判断属于哪个市场"""
    代码_upper = str(代码).upper()
    
    # A股判断
    if str(代码).endswith('.SZ') or str(代码).endswith('.SS'):
        return "A股"
    if str(代码).isnumeric() and len(str(代码)) == 6:
        return "A股"
    
    # 美股判断
    美股列表 = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 
               'AMD', 'INTC', 'IBM', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'PYPL', 'DIS']
    if 代码_upper in 美股列表:
        return "美股"
    if 代码_upper.isalpha() and 2 <= len(代码_upper) <= 5:
        return "美股"
    
    # 加密货币判断
    if '-' in 代码 or 代码_upper in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE', 'ADA']:
        return "加密货币"
    
    # 外汇判断
    if '/' in 代码 or 代码_upper in ['EURUSD', 'GBPUSD', 'USDJPY']:
        return "外汇"
    
    return "未知"


# ==================== A股数据（Tushare Pro） ====================
def 获取A股日线(代码, 开始日期, 结束日期):
    """获取A股日线数据（Tushare Pro）"""
    if not TUSHARE_AVAILABLE or pro is None:
        return None
    
    # 转换代码格式
    if len(str(代码)) == 6:
        if 代码.startswith('6'):
            ts_code = f"{代码}.SH"
        else:
            ts_code = f"{代码}.SZ"
    else:
        ts_code = 代码
    
    try:
        df = pro.daily(ts_code=ts_code, 
                       start_date=开始日期.replace('-', ''), 
                       end_date=结束日期.replace('-', ''))
        if df is not None and not df.empty:
            # 标准化列名
            df = df.rename(columns={
                'trade_date': '日期',
                'open': '开盘',
                'high': '最高',
                'low': '最低',
                'close': '收盘',
                'vol': '成交量',
                'amount': '成交额'
            })
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期')
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']]
    except Exception as e:
        print(f"Tushare 获取A股数据失败: {e}")
    
    return None


# ==================== 美股/加密货币/外汇（yfinance） ====================
def 获取YFinance数据(代码, 开始日期, 结束日期):
    """获取美股/加密货币/外汇数据（yfinance）"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        ticker = yf.Ticker(代码)
        df = ticker.history(start=开始日期, end=结束日期)
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df = df.rename(columns={
                'Date': '日期',
                'Open': '开盘',
                'High': '最高',
                'Low': '最低',
                'Close': '收盘',
                'Volume': '成交量'
            })
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
    except Exception as e:
        print(f"yfinance 获取数据失败: {e}")
    
    return None


# ==================== 实时价格获取 ====================
def 获取实时价格(代码):
    """获取单个品种的实时价格（自动选择数据源）"""
    市场 = 判断市场类型(代码)
    
    if 市场 == "A股":
        # 使用 Tushare 获取最新价格
        if TUSHARE_AVAILABLE and pro:
            try:
                # 转换代码格式
                if len(str(代码)) == 6:
                    if 代码.startswith('6'):
                        ts_code = f"{代码}.SH"
                    else:
                        ts_code = f"{代码}.SZ"
                else:
                    ts_code = 代码
                
                df = pro.daily(ts_code=ts_code, limit=1)
                if df is not None and not df.empty:
                    return float(df['close'].iloc[0])
            except Exception as e:
                print(f"获取A股实时价格失败: {e}")
    
    elif 市场 in ["美股", "加密货币", "外汇"]:
        # 使用 yfinance
        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(代码)
                # 获取最新交易数据
                data = ticker.history(period="1d")
                if not data.empty:
                    return float(data['Close'].iloc[-1])
            except Exception as e:
                print(f"获取{市场}实时价格失败: {e}")
    
    return None


# ==================== 统一入口（自动降级） ====================
def 获取历史数据(代码, 开始日期, 结束日期):
    """
    统一入口：自动选择数据源获取历史数据
    优先级：Tushare (A股) → yfinance (其他)
    """
    市场 = 判断市场类型(代码)
    
    if 市场 == "A股":
        # 优先 Tushare
        df = 获取A股日线(代码, 开始日期, 结束日期)
        if df is not None:
            return df
        # 降级到 yfinance（部分A股可能支持）
        df = 获取YFinance数据(代码, 开始日期, 结束日期)
        if df is not None:
            return df
    
    elif 市场 in ["美股", "加密货币", "外汇"]:
        # 使用 yfinance
        return 获取YFinance数据(代码, 开始日期, 结束日期)
    
    return None


# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("测试行情获取模块")
    print("="*50)
    
    # 测试 A股
    print("\n1. 测试 A股 (平安银行):")
    df = 获取历史数据('000001', '2024-12-01', '2024-12-31')
    if df is not None:
        print(df.head())
    else:
        print("获取失败")
    
    # 测试美股
    print("\n2. 测试 美股 (苹果):")
    price = 获取实时价格('AAPL')
    if price:
        print(f"AAPL 实时价格: ${price:.2f}")
    else:
        print("获取失败")
    
    # 测试加密货币
    print("\n3. 测试 加密货币 (比特币):")
    price = 获取实时价格('BTC-USD')
    if price:
        print(f"BTC-USD 价格: ${price:.2f}")
    else:
        print("获取失败")
    
    # 测试外汇
    print("\n4. 测试 外汇 (欧元/美元):")
    price = 获取实时价格('EURUSD=X')
    if price:
        print(f"EURUSD 汇率: {price:.4f}")
    else:
        print("获取失败")
