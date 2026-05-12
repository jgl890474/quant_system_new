# -*- coding: utf-8 -*-
"""
行情获取模块 - 支持多数据源自动降级
主数据源: 新浪财经 (A股实时)
备用数据源: Tushare Pro (A股历史) + yfinance (美股/加密货币/外汇)
"""

import pandas as pd
import requests
import time
import numpy as np
from datetime import datetime, timedelta

# ==================== 新浪财经实时行情配置 ====================
def 获取新浪实时行情(代码):
    """
    从新浪获取A股实时行情（盘中实时）
    返回: {"当前价": xx, "涨跌幅": xx, "涨跌额": xx, "名称": xx, ...}
    """
    try:
        # 判断市场代码
        if str(代码).startswith('6'):
            symbol = f"sh{代码}"
        else:
            symbol = f"sz{代码}"
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=3)
        response.encoding = 'gbk'
        
        # 解析数据
        content = response.text
        if 'str_' not in content or '=""' in content:
            return None
        
        data = content.split(',')
        if len(data) < 10:
            return None
        
        # 提取关键数据
        名称 = data[0].split('="')[1] if '="' in data[0] else data[0]
        当前价 = float(data[3])    # 当前价
        昨日收盘 = float(data[2])   # 昨日收盘价
        涨跌额 = 当前价 - 昨日收盘
        涨跌幅 = (涨跌额 / 昨日收盘) * 100
        
        return {
            "名称": 名称,
            "当前价": 当前价,
            "昨日收盘": 昨日收盘,
            "涨跌额": round(涨跌额, 2),
            "涨跌幅": round(涨跌幅, 2),
            "最高": float(data[4]),
            "最低": float(data[5]),
            "买一价": float(data[6]) if len(data) > 6 else 0,
            "卖一价": float(data[7]) if len(data) > 7 else 0,
            "成交量": int(float(data[8])) if len(data) > 8 else 0,
            "成交额": int(float(data[9])) if len(data) > 9 else 0,
            "时间": data[-2] + ' ' + data[-1] if len(data) > 1 else ""
        }
    except Exception as e:
        print(f"新浪获取 {代码} 行情失败: {e}")
        return None


def 获取批量新浪实时行情(代码列表):
    """
    批量获取多个股票实时行情
    代码列表: ['000001', '600519', ...]
    返回: {代码: {"当前价": xx, "涨跌幅": xx, ...}}
    """
    if not 代码列表:
        return {}
    
    # 构建请求字符串（新浪支持同时查询多个）
    symbol_parts = []
    for 代码 in 代码列表:
        if str(代码).startswith('6'):
            symbol_parts.append(f"sh{代码}")
        else:
            symbol_parts.append(f"sz{代码}")
    
    url = f"https://hq.sinajs.cn/list={','.join(symbol_parts)}"
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'gbk'
        results = {}
        
        lines = response.text.strip().split('\n')
        for i, line in enumerate(lines):
            if line and 'str_' in line:
                data = line.split(',')
                if len(data) >= 10 and i < len(代码列表):
                    代码 = 代码列表[i]
                    当前价 = float(data[3])
                    昨日收盘 = float(data[2])
                    涨跌额 = 当前价 - 昨日收盘
                    涨跌幅 = (涨跌额 / 昨日收盘) * 100
                    
                    results[代码] = {
                        "当前价": 当前价,
                        "涨跌幅": round(涨跌幅, 2),
                        "涨跌额": round(涨跌额, 2),
                        "最高": float(data[4]),
                        "最低": float(data[5]),
                        "名称": data[0].split('="')[1] if '="' in data[0] else data[0]
                    }
        return results
    except Exception as e:
        print(f"批量获取失败: {e}")
        return {}


# ==================== Tushare Pro 配置（备用） ====================
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


# ==================== A股数据（优先新浪实时，降级Tushare） ====================
def 获取A股实时价格(代码):
    """
    获取A股实时价格（优先新浪实时接口）
    返回: (当前价, 涨跌幅)
    """
    # 方法1：新浪实时接口（盘中实时）
    行情 = 获取新浪实时行情(代码)
    if 行情 and 行情["当前价"] > 0:
        return 行情["当前价"], 行情["涨跌幅"]
    
    # 方法2：Tushare（昨日收盘价）
    if TUSHARE_AVAILABLE and pro:
        try:
            if len(str(代码)) == 6:
                if 代码.startswith('6'):
                    ts_code = f"{代码}.SH"
                else:
                    ts_code = f"{代码}.SZ"
            else:
                ts_code = 代码
            
            df = pro.daily(ts_code=ts_code, limit=1)
            if df is not None and not df.empty:
                return float(df['close'].iloc[0]), 0
        except Exception as e:
            print(f"Tushare获取价格失败: {e}")
    
    return None, None


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


# ==================== 获取美股/加密货币实时价格 ====================
def 获取YFinance实时价格(代码):
    """获取美股/加密货币实时价格"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        ticker = yf.Ticker(代码)
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"获取{代码}实时价格失败: {e}")
    
    return None


# ==================== 生成模拟K线数据（备用） ====================
def 生成模拟K线数据(品种代码, 长度=60, 周期="1d"):
    """当无法获取真实K线数据时，生成模拟数据用于演示"""
    if 周期 == "30m" or 周期 == "10m":
        # 分钟数据使用更密集的时间点
        dates = pd.date_range(end=datetime.now(), periods=长度, freq='30min' if 周期 == "30m" else '10min')
    else:
        dates = pd.date_range(end=datetime.now(), periods=长度, freq='D')
    
    np.random.seed(abs(hash(品种代码)) % 10000)
    
    # 生成随机价格走势
    returns = np.random.randn(长度) * 0.02
    price = 100 * np.cumprod(1 + returns)
    price = np.maximum(price, 0.01)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * (1 + np.random.randn(长度) * 0.005),
        '最高': price * (1 + abs(np.random.randn(长度) * 0.01)),
        '最低': price * (1 - abs(np.random.randn(长度) * 0.01)),
        '收盘': price,
        '成交量': np.random.randint(1000, 100000, 长度)
    })
    # 确保最高>=最低>=开盘/收盘
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    return df


# ==================== K线数据获取 ====================
def 获取K线数据(代码, 周期="1d", 长度=60):
    """
    获取K线数据用于图表显示
    参数:
        代码: 品种代码 (如 AAPL, BTC-USD, 000001)
        周期: 时间周期 (1d=日线, 1wk=周线, 1h=小时线, 30m=30分钟, 10m=10分钟)
        长度: 获取多少根K线
    返回:
        DataFrame 包含 日期, 开盘, 最高, 最低, 收盘, 成交量
    """
    try:
        市场 = 判断市场类型(代码)
        
        if 市场 == "A股":
            # A股不支持分钟线，降级为日线
            if 周期 in ["30m", "10m", "1h"]:
                print(f"A股不支持{周期}周期，使用日线")
                周期 = "1d"
            
            if TUSHARE_AVAILABLE and pro:
                # 转换代码格式
                if len(str(代码)) == 6:
                    if 代码.startswith('6'):
                        ts_code = f"{代码}.SH"
                    else:
                        ts_code = f"{代码}.SZ"
                else:
                    ts_code = 代码
                
                # 计算开始日期
                天数 = 长度 * 2
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=天数)).strftime('%Y%m%d')
                
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                if df is not None and not df.empty:
                    df = df.sort_values('trade_date')
                    df = df.tail(长度)
                    df['日期'] = pd.to_datetime(df['trade_date'])
                    return df[['日期', 'open', 'high', 'low', 'close', 'vol']].rename(columns={
                        'open': '开盘', 'high': '最高', 'low': '最低', 'close': '收盘', 'vol': '成交量'
                    })
        
        elif 市场 in ["美股", "加密货币", "外汇"]:
            if YFINANCE_AVAILABLE:
                # 周期映射
                周期映射 = {
                    "1d": "1d",
                    "1wk": "1wk", 
                    "1h": "1h",
                    "30m": "30m",
                    "10m": "10m"
                }
                yf_interval = 周期映射.get(周期, "1d")
                
                # 对于分钟数据，需要不同的period参数
                if 周期 in ["30m", "10m", "1h"]:
                    # 分钟数据获取最近几天的数据
                    get_days = 7  # 获取7天数据
                    try:
                        ticker = yf.Ticker(代码)
                        df = ticker.history(period=f"{get_days}d", interval=yf_interval)
                        
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
                            # 按时间排序
                            df = df.sort_values('日期')
                            df = df.tail(长度)
                            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
                        else:
                            print(f"yfinance 未获取到 {周期} 数据，尝试使用模拟数据")
                    except Exception as e:
                        print(f"yfinance 获取分钟数据失败: {e}")
                else:
                    # 日线/周线数据
                    if 周期 == "1d":
                        get_days = 长度 + 20
                    elif 周期 == "1wk":
                        get_days = 长度 * 7 + 30
                    else:
                        get_days = 长度 + 20
                    
                    ticker = yf.Ticker(代码)
                    df = ticker.history(period=f"{get_days}d", interval=yf_interval)
                    
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
        
        # 如果获取失败，返回模拟数据
        print(f"获取 {代码} 真实K线数据失败，使用模拟数据 (周期: {周期})")
        return 生成模拟K线数据(代码, 长度, 周期)
        
    except Exception as e:
        print(f"获取K线数据失败: {e}")
        return 生成模拟K线数据(代码, 长度, 周期)


def 计算技术指标(df):
    """
    计算常用技术指标
    返回: 包含均线等指标的DataFrame
    """
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    # 确保有收盘价
    if '收盘' not in df_copy.columns:
        return df_copy
    
    # 简单移动平均线
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    df_copy['MA60'] = df_copy['收盘'].rolling(window=60).mean()
    
    # 指数移动平均线
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    # RSI (相对强弱指数)
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
    
    # 成交量均线
    if '成交量' in df_copy.columns:
        df_copy['VOL_MA5'] = df_copy['成交量'].rolling(window=5).mean()
        df_copy['VOL_MA10'] = df_copy['成交量'].rolling(window=10).mean()
    
    return df_copy


# ==================== 实时价格获取（统一入口） ====================
def 获取价格(代码):
    """
    获取单个品种的实时价格
    这是兼容原有接口的函数名
    返回一个带有 .价格 属性的对象
    """
    市场 = 判断市场类型(代码)
    
    if 市场 == "A股":
        # 优先使用新浪实时接口
        价格, 涨跌幅 = 获取A股实时价格(代码)
        if 价格:
            class PriceObj:
                pass
            result = PriceObj()
            result.价格 = 价格
            result.涨跌幅 = 涨跌幅
            return result
    
    elif 市场 in ["美股", "加密货币", "外汇"]:
        if YFINANCE_AVAILABLE:
            价格 = 获取YFinance实时价格(代码)
            if 价格:
                class PriceObj:
                    pass
                result = PriceObj()
                result.价格 = 价格
                return result
    
    return None


# ==================== 获取实时价格（返回数值） ====================
def 获取实时价格(代码):
    """获取实时价格，直接返回数值"""
    result = 获取价格(代码)
    if result and hasattr(result, '价格'):
        return result.价格
    return None


# ==================== 获取A股实时行情（返回完整信息） ====================
def 获取A股实时行情完整(代码):
    """获取A股完整实时行情，用于AI推荐"""
    return 获取新浪实时行情(代码)


# ==================== 获取股票列表 ====================
def 获取股票列表():
    """获取A股股票列表"""
    if not TUSHARE_AVAILABLE or pro is None:
        return pd.DataFrame()
    
    try:
        df = pro.stock_basic(exchange='', list_status='L', 
                            fields='ts_code,symbol,name,industry')
        return df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return pd.DataFrame()


# ==================== 统一入口（自动降级） ====================
def 获取历史数据(代码, 开始日期, 结束日期):
    """
    统一入口：自动选择数据源获取历史数据
    优先级：Tushare (A股) → yfinance (其他)
    """
    市场 = 判断市场类型(代码)
    
    if 市场 == "A股":
        df = 获取A股日线(代码, 开始日期, 结束日期)
        if df is not None:
            return df
        df = 获取YFinance数据(代码, 开始日期, 结束日期)
        if df is not None:
            return df
    
    elif 市场 in ["美股", "加密货币", "外汇"]:
        return 获取YFinance数据(代码, 开始日期, 结束日期)
    
    return None


# ==================== 测试代码 ====================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("测试行情获取模块")
    print("="*50)
    
    # 测试新浪实时行情
    print("\n1. 测试新浪实时行情 (平安银行):")
    result = 获取新浪实时行情('000001')
    if result:
        print(f"名称: {result['名称']}")
        print(f"当前价: {result['当前价']}")
        print(f"涨跌幅: {result['涨跌幅']:.2f}%")
    else:
        print("获取失败")
    
    # 测试K线数据 - 日线
    print("\n2. 测试K线数据 (ETH-USD, 日线):")
    df = 获取K线数据('ETH-USD', '1d', 20)
    if not df.empty:
        print(f"获取 {len(df)} 根K线")
        print(df[['日期', '收盘']].tail(3))
    else:
        print("获取失败")
    
    # 测试K线数据 - 30分钟
    print("\n3. 测试K线数据 (ETH-USD, 30分钟):")
    df = 获取K线数据('ETH-USD', '30m', 30)
    if not df.empty:
        print(f"获取 {len(df)} 根30分钟K线")
        print(df[['日期', '收盘']].head(3))
    else:
        print("获取失败（将使用模拟数据）")
    
    # 测试技术指标
    print("\n4. 测试技术指标计算:")
    df = 获取K线数据('BTC-USD', '1d', 30)
    if not df.empty:
        df_tech = 计算技术指标(df)
        print(f"技术指标列: {list(df_tech.columns)}")
