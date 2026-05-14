# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


def 显示(引擎=None):
    """
    显示回测页面 - 动态净值曲线 + 动态回撤曲线
    支持：技术指标策略 / 策略库策略
    """
    st.subheader("📈 动态回测系统")

    # ==================== 从持仓获取所有品种（过滤数量为0的持仓） ====================
    持仓品种列表 = []
    
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 代码, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            
            try:
                数量_float = float(数量)
                if 数量_float <= 0.0001:
                    continue
            except:
                continue
                
            if 代码:
                if str(代码).isdigit() or str(代码).startswith(('0', '3', '6')):
                    类型 = "A股"
                elif '-' in 代码 or 代码.upper() in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX']:
                    类型 = "加密货币"
                elif 代码.isalpha() and len(代码) <= 5:
                    类型 = "美股"
                else:
                    类型 = "其他"
                
                持仓品种列表.append({
                    "代码": 代码,
                    "名称": f"{代码} ({类型})",
                    "类型": 类型,
                    "数量": 数量_float
                })

    if not 持仓品种列表:
        st.warning("⚠️ 当前没有有效持仓，请先在AI交易中买入品种后再进行回测")
        st.info("💡 提示：您可以在「AI交易」页面选择市场并进行买入交易")
        return

    # ==================== 侧边栏参数设置 ====================
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")

        # 品种选择器
        st.markdown("#### 📊 选择回测品种")
        
        品种选项 = {}
        for i, s in enumerate(持仓品种列表, 1):
            if s["类型"] in ["A股", "美股"]:
                显示文本 = f"{i}. {s['代码']} ({s['类型']}) | 持仓: {int(s['数量'])}股"
            else:
                显示文本 = f"{i}. {s['代码']} ({s['类型']}) | 持仓: {s['数量']:.4f}个"
            品种选项[显示文本] = s["代码"]
        
        品种显示名称 = list(品种选项.keys())
        选中品种显示 = st.selectbox("选择持仓品种", 品种显示名称, help="从当前持仓中选择要回测的品种")
        品种代码 = 品种选项.get(选中品种显示, 持仓品种列表[0]["代码"])
        
        选中品种信息 = next((s for s in 持仓品种列表 if s["代码"] == 品种代码), None)
        if 选中品种信息:
            if 选中品种信息["类型"] in ["A股", "美股"]:
                st.caption(f"📌 品种类型: {选中品种信息['类型']} | 持仓数量: {int(选中品种信息['数量'])}股")
            else:
                st.caption(f"📌 品种类型: {选中品种信息['类型']} | 持仓数量: {选中品种信息['数量']:.4f}个")
        
        st.caption(f"📊 当前有效持仓数量: {len(持仓品种列表)}")
        st.markdown("---")

        # 日期范围
        if 选中品种信息 and 选中品种信息["类型"] == "加密货币":
            st.info("💡 加密货币7x24小时交易，建议选择近期日期")
            开始日期默认 = datetime.date.today() - datetime.timedelta(days=90)
        else:
            开始日期默认 = datetime.date(2024, 1, 1)
        
        开始日期 = st.date_input("开始日期", value=开始日期默认)
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.001, step=0.0005, format="%.4f")

        st.markdown("---")
        st.markdown("### 📊 策略来源")

        # ========== 策略来源选择 ==========
        策略来源 = st.radio(
            "选择策略来源",
            ["技术指标策略", "策略库策略"],
            horizontal=True,
            help="技术指标策略：双均线/布林带；策略库策略：使用策略中心中的策略"
        )

        st.markdown("### 📊 策略参数")

        # 初始化变量
        策略名称 = ""
        使用策略库策略 = False
        策略类型 = "双均线策略"
        短期均线 = 5
        长期均线 = 20
        布林带周期 = 20
        布林带标准差 = 2.0
        策略库参数 = {}

        if 策略来源 == "技术指标策略":
            # 原有的技术指标选择
            策略类型 = st.selectbox("交易策略", ["双均线策略", "买入持有策略", "布林带策略"], index=0)

            if 策略类型 == "双均线策略":
                短期均线 = st.slider("短期均线（买入信号）", 3, 30, 5, 1)
                长期均线 = st.slider("长期均线（卖出信号）", 10, 60, 20, 1)

            if 策略类型 == "布林带策略":
                布林带周期 = st.slider("布林带周期", 10, 50, 20, 5)
                布林带标准差 = st.slider("标准差倍数", 1.0, 3.0, 2.0, 0.5)
            
            策略名称 = 策略类型

        else:
            # ========== 从策略库获取策略 ==========
            try:
                from 核心 import 策略加载器
                加载器 = 策略加载器()
                所有策略 = 加载器.获取策略()
                
                # 过滤出与当前品种类型匹配的策略
                匹配策略 = []
                for s in 所有策略:
                    策略类别 = s.get("类别", "")
                    if 选中品种信息:
                        if 选中品种信息["类型"] == "加密货币" and "加密" in 策略类别:
                            匹配策略.append(s)
                        elif 选中品种信息["类型"] == "A股" and "A股" in 策略类别:
                            匹配策略.append(s)
                        elif 选中品种信息["类型"] == "美股" and "美股" in 策略类别:
                            匹配策略.append(s)
                        elif 选中品种信息["类型"] == "外汇" and "外汇" in 策略类别:
                            匹配策略.append(s)
                
                if not 匹配策略:
                    st.warning(f"没有找到适合 {选中品种信息['类型']} 的策略，请使用技术指标策略")
                    策略来源 = "技术指标策略"
                    策略类型 = st.selectbox("交易策略", ["双均线策略", "买入持有策略", "布林带策略"], index=0)
                else:
                    策略选项 = [s.get("名称", "") for s in 匹配策略]
                    策略名称 = st.selectbox("选择策略", 策略选项)
                    使用策略库策略 = True
                    
                    # 找到选中的策略详情
                    当前策略详情 = None
                    for s in 匹配策略:
                        if s.get("名称") == 策略名称:
                            当前策略详情 = s
                            break
                    
                    if 当前策略详情:
                        st.caption(f"📋 策略类型: {当前策略详情.get('类别', '未知')}")
                        st.caption(f"📝 策略描述: {当前策略详情.get('描述', '无描述')}")
                        
                        # ========== 显示策略参数（可调整） ==========
                        策略参数配置 = 当前策略详情.get('参数', {})
                        
                        if 策略参数配置:
                            st.markdown("---")
                            st.markdown("#### 🔧 策略参数调整")
                            
                            for 参数名, 参数配置 in 策略参数配置.items():
                                if isinstance(参数配置, dict):
                                    参数类型 = 参数配置.get('类型', 'float')
                                    参数默认值 = 参数配置.get('默认值', 0)
                                    参数最小值 = 参数配置.get('最小值', 0)
                                    参数最大值 = 参数配置.get('最大值', 100)
                                    参数步长 = 参数配置.get('步长', 1)
                                    参数描述 = 参数配置.get('描述', 参数名)
                                    
                                    if 参数类型 == 'int':
                                        策略库参数[参数名] = st.number_input(
                                            f"{参数描述}",
                                            value=int(参数默认值),
                                            min_value=int(参数最小值),
                                            max_value=int(参数最大值),
                                            step=int(参数步长),
                                            key=f"param_{参数名}"
                                        )
                                    elif 参数类型 == 'float':
                                        策略库参数[参数名] = st.number_input(
                                            f"{参数描述}",
                                            value=float(参数默认值),
                                            min_value=float(参数最小值),
                                            max_value=float(参数最大值),
                                            step=float(参数步长),
                                            format="%.2f",
                                            key=f"param_{参数名}"
                                        )
                                    elif 参数类型 == 'bool':
                                        策略库参数[参数名] = st.checkbox(
                                            f"{参数描述}",
                                            value=bool(参数默认值),
                                            key=f"param_{参数名}"
                                        )
                                    elif 参数类型 == 'select':
                                        参数选项 = 参数配置.get('选项', [])
                                        if 参数默认值 in 参数选项:
                                            默认索引 = 参数选项.index(参数默认值)
                                        else:
                                            默认索引 = 0
                                        策略库参数[参数名] = st.selectbox(
                                            f"{参数描述}",
                                            参数选项,
                                            index=默认索引,
                                            key=f"param_{参数名}"
                                        )
                            
                            st.session_state['策略库参数'] = 策略库参数
                        else:
                            st.info("该策略使用内置默认参数，无可调整参数")
                    
            except Exception as e:
                st.error(f"加载策略库失败: {e}")
                策略类型 = st.selectbox("交易策略", ["双均线策略", "买入持有策略", "布林带策略"], index=0)

        st.markdown("---")
        st.markdown("### 🎯 止盈止损")

        止盈百分比 = st.number_input("止盈目标 (%)", value=5.0, step=1.0, min_value=0.0, max_value=50.0)
        止损百分比 = st.number_input("止损目标 (%)", value=-3.0, step=0.5, min_value=-30.0, max_value=0.0)

        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", width="stretch")

    # ==================== 显示当前有效持仓列表 ====================
    with st.expander("📋 当前有效持仓列表", expanded=False):
        持仓显示数据 = []
        for item in 持仓品种列表:
            if item["类型"] in ["A股", "美股"]:
                数量显示 = f"{int(item['数量'])}"
            else:
                数量显示 = f"{item['数量']:.4f}"
            持仓显示数据.append({
                "品种": item["代码"],
                "类型": item["类型"],
                "数量": 数量显示
            })
        
        if 持仓显示数据:
            df_持仓 = pd.DataFrame(持仓显示数据)
            st.dataframe(df_持仓, width="stretch", hide_index=True)
            st.caption(f"💡 共 {len(持仓显示数据)} 个有效持仓（数量 > 0）")

    if not 运行按钮:
        st.info("👈 请在左侧选择持仓品种并设置参数，然后点击「开始回测」")
        return

    # ==================== 执行回测 ====================
    with st.spinner(f"正在获取 {品种代码} 的历史数据并执行回测..."):
        try:
            # 获取历史数据
            if 选中品种信息 and 选中品种信息["类型"] == "A股":
                df = 获取A股历史数据(品种代码, 开始日期, 结束日期)
            elif 选中品种信息 and 选中品种信息["类型"] == "加密货币":
                df = 获取加密货币历史数据(品种代码, 开始日期, 结束日期)
            elif 选中品种信息 and 选中品种信息["类型"] == "美股":
                df = 获取美股历史数据(品种代码, 开始日期, 结束日期)
            else:
                df = 获取通用演示数据(品种代码, 开始日期, 结束日期)

            if df is None or df.empty:
                st.error(f"❌ 无法获取 {品种代码} 的历史数据")
                return

            st.success(f"✅ 成功获取 {len(df)} 条历史数据")

            # ========== 计算信号 ==========
            if 使用策略库策略:
                try:
                    from 核心 import 策略加载器 as 加载器类
                    加载器 = 加载器类()
                    所有策略 = 加载器.获取策略()
                    目标策略 = next((s for s in 所有策略 if s.get("名称") == 策略名称), None)
                    
                    if 目标策略 and 目标策略.get("类"):
                        用户参数 = st.session_state.get('策略库参数', {})
                        策略实例 = 目标策略["类"](策略名称, 品种代码, 初始资金, **用户参数)
                        
                        信号列表 = []
                        for i in range(len(df)):
                            当前行情 = {'close': df['收盘'].iloc[i], 'date': df['日期'].iloc[i]}
                            信号 = 策略实例.处理行情(当前行情)
                            if 信号 == 'buy' or 信号 == 1:
                                信号列表.append(1)
                            elif 信号 == 'sell' or 信号 == -1:
                                信号列表.append(-1)
                            else:
                                信号列表.append(0)
                        df['信号'] = 信号列表
                    else:
                        df = 计算均线(df, 5, 20)
                except Exception as e:
                    st.warning(f"策略运行失败: {e}")
                    df = 计算均线(df, 5, 20)
            else:
                if 策略类型 == "双均线策略":
                    df = 计算均线(df, 短期均线, 长期均线)
                elif 策略类型 == "布林带策略":
                    df = 计算布林带(df, 布林带周期, 布林带标准差)
                else:
                    df['信号'] = 0

            回测结果 = 执行持仓回测(df, 初始资金, 手续费率, 止盈百分比 / 100, 止损百分比 / 100)
            回测结果 = 计算回撤(回测结果)
            显示回测结果(回测结果, 品种代码, 短期均线, 长期均线, 止盈百分比, 止损百分比, 策略名称, 选中品种信息["类型"] if 选中品种信息 else "未知")

        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            with st.expander("详细错误信息"):
                st.code(traceback.format_exc())


def 获取加密货币历史数据(品种代码, 开始日期, 结束日期):
    """获取加密货币历史数据"""
    try:
        symbol = 品种代码.upper()
        binance_symbol = symbol.replace('-', '').replace('USD', 'USDT')
        if 'USDT' not in binance_symbol:
            binance_symbol = binance_symbol + 'USDT'
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': binance_symbol,
            'interval': '1d',
            'startTime': int(开始日期.timestamp() * 1000),
            'endTime': int(结束日期.timestamp() * 1000),
            'limit': 1000
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
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
        print(f"加密货币数据获取失败: {e}")
    
    return 获取通用演示数据(品种代码, 开始日期, 结束日期)


def 获取美股历史数据(股票代码, 开始日期, 结束日期):
    """获取美股历史数据"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(股票代码.upper())
        df = ticker.history(start=开始日期.strftime("%Y-%m-%d"), end=结束日期.strftime("%Y-%m-%d"))
        if not df.empty:
            df = df.reset_index()
            df.columns = ['日期', '开盘', '最高', '最低', '收盘', '成交量', '拆股', '分红']
            return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
    except Exception as e:
        print(f"美股数据获取失败: {e}")
    return 获取通用演示数据(股票代码, 开始日期, 结束日期)


def 获取A股历史数据(股票代码, 开始日期, 结束日期):
    """获取A股历史数据"""
    代码 = str(股票代码).strip().zfill(6)
    
    if AKSHARE_AVAILABLE:
        try:
            df = ak.stock_zh_a_hist(symbol=代码, period="daily", 
                start_date=开始日期.strftime("%Y%m%d"), end_date=结束日期.strftime("%Y%m%d"), adjust="qfq")
            if df is not None and not df.empty:
                df.columns = ['日期', '开盘', '最高', '最低', '收盘', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
                df['日期'] = pd.to_datetime(df['日期'])
                return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        except Exception as e:
            print(f"akshare失败: {e}")
    
    # 东方财富备用接口
    try:
        市场代码 = "1" if 代码.startswith('6') else "0"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {"secid": f"{市场代码}.{代码}", "klt": "101", "fqt": "1",
                  "beg": 开始日期.strftime("%Y%m%d"), "end": 结束日期.strftime("%Y%m%d")}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data.get("data") and data["data"].get("klines"):
            rows = []
            for k in data["data"]["klines"]:
                parts = k.split(",")
                rows.append({'日期': parts[0], '开盘': float(parts[1]), '最高': float(parts[2]),
                            '最低': float(parts[3]), '收盘': float(parts[4]), '成交量': float(parts[5])})
            df = pd.DataFrame(rows)
            df['日期'] = pd.to_datetime(df['日期'])
            return df
    except Exception as e:
        print(f"东方财富失败: {e}")
    
    return 获取通用演示数据(股票代码, 开始日期, 结束日期)


def 获取通用演示数据(品种代码, 开始日期, 结束日期):
    """获取演示数据"""
    dates = pd.date_range(开始日期, 结束日期, freq='D')
    np.random.seed(hash(品种代码) % 10000)
    returns = np.random.randn(len(dates)) * 0.02 + 0.0003
    price = 100 * np.cumprod(1 + returns)
    df = pd.DataFrame({
        '日期': dates, '开盘': price * 0.99, '最高': price * 1.01,
        '最低': price * 0.98, '收盘': price, '成交量': np.random.randint(1000, 10000, len(dates))
    })
    st.info(f"📊 使用演示数据模拟 {品种代码}")
    return df


def 计算均线(df, 短期均线, 长期均线):
    """计算均线策略信号"""
    df_copy = df.copy()
    df_copy['MA_短期'] = df_copy['收盘'].rolling(window=短期均线).mean()
    df_copy['MA_长期'] = df_copy['收盘'].rolling(window=长期均线).mean()
    df_copy['信号'] = 0
    for i in range(1, len(df_copy)):
        if df_copy['MA_短期'].iloc[i] > df_copy['MA_长期'].iloc[i]:
            if df_copy['MA_短期'].iloc[i-1] <= df_copy['MA_长期'].iloc[i-1]:
                df_copy.loc[df_copy.index[i], '信号'] = 1
        elif df_copy['MA_短期'].iloc[i] < df_copy['MA_长期'].iloc[i]:
            if df_copy['MA_短期'].iloc[i-1] >= df_copy['MA_长期'].iloc[i-1]:
                df_copy.loc[df_copy.index[i], '信号'] = -1
    return df_copy


def 计算布林带(df, 周期, 标准差倍数):
    """计算布林带策略信号"""
    df_copy = df.copy()
    df_copy['中轨'] = df_copy['收盘'].rolling(window=周期).mean()
    df_copy['标准差'] = df_copy['收盘'].rolling(window=周期).std()
    df_copy['上轨'] = df_copy['中轨'] + 标准差倍数 * df_copy['标准差']
    df_copy['下轨'] = df_copy['中轨'] - 标准差倍数 * df_copy['标准差']
    df_copy['信号'] = 0
    for i in range(1, len(df_copy)):
        if df_copy['收盘'].iloc[i] <= df_copy['下轨'].iloc[i]:
            df_copy.loc[df_copy.index[i], '信号'] = 1
        elif df_copy['收盘'].iloc[i] >= df_copy['上轨'].iloc[i]:
            df_copy.loc[df_copy.index[i], '信号'] = -1
    return df_copy


def 执行持仓回测(df, 初始资金, 手续费率, 止盈率, 止损率):
    """执行回测"""
    资金 = 初始资金
    持仓数量 = 0.0
    交易记录 = []
    每日净值 = []
    买入价 = 0.0

    for i in range(len(df)):
        当前日期 = df['日期'].iloc[i]
        当前收盘 = df['收盘'].iloc[i]

        if 持仓数量 > 0 and 买入价 > 0:
            当前盈亏率 = (当前收盘 - 买入价) / 买入价
            if 止盈率 > 0 and 当前盈亏率 >= 止盈率:
                卖出金额 = 持仓数量 * 当前收盘
                手续费 = 卖出金额 * 手续费率
                资金 += 卖出金额 - 手续费
                盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
                交易记录.append({'日期': 当前日期, '行动': '止盈卖出', '价格': 当前收盘, '数量': round(持仓数量, 4), '盈亏': round(盈亏, 2)})
                持仓数量 = 0.0
                买入价 = 0.0
                continue
            elif 止损率 < 0 and 当前盈亏率 <= 止损率:
                卖出金额 = 持仓数量 * 当前收盘
                手续费 = 卖出金额 * 手续费率
                资金 += 卖出金额 - 手续费
                盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
                交易记录.append({'日期': 当前日期, '行动': '止损卖出', '价格': 当前收盘, '数量': round(持仓数量, 4), '盈亏': round(盈亏, 2)})
                持仓数量 = 0.0
                买入价 = 0.0
                continue

        if df['信号'].iloc[i] == 1 and 持仓数量 == 0:
            买入数量 = (资金 * 0.95) / 当前收盘
            if 买入数量 > 0:
                买入金额 = 买入数量 * 当前收盘
                手续费 = 买入金额 * 手续费率
                资金 -= (买入金额 + 手续费)
                持仓数量 = 买入数量
                买入价 = 当前收盘
                交易记录.append({'日期': 当前日期, '行动': '买入', '价格': 当前收盘, '数量': round(持仓数量, 4), '盈亏': 0})

        elif df['信号'].iloc[i] == -1 and 持仓数量 > 0:
            卖出金额 = 持仓数量 * 当前收盘
            手续费 = 卖出金额 * 手续费率
            资金 += 卖出金额 - 手续费
            盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
            交易记录.append({'日期': 当前日期, '行动': '卖出(信号)', '价格': 当前收盘, '数量': round(持仓数量, 4), '盈亏': round(盈亏, 2)})
            持仓数量 = 0.0
            买入价 = 0.0

        每日净值.append(资金 + 持仓数量 * 当前收盘)

    if 持仓数量 > 0:
        最后价格 = df['收盘'].iloc[-1]
        卖出金额 = 持仓数量 * 最后价格
        手续费 = 卖出金额 * 手续费率
        资金 += 卖出金额 - 手续费
        盈亏 = (最后价格 - 买入价) * 持仓数量 - 手续费
        交易记录.append({'日期': df['日期'].iloc[-1], '行动': '强制平仓', '价格': 最后价格, '数量': round(持仓数量, 4), '盈亏': round(盈亏, 2)})
        每日净值[-1] = 资金

    return {
        '初始资金': 初始资金, '最终资金': 资金, '总盈亏': 资金 - 初始资金,
        '总收益率': (资金 - 初始资金) / 初始资金 * 100, '每日净值': 每日净值,
        '交易记录': 交易记录, '数据': df, '手续费率': 手续费率
    }


def 计算回撤(回测结果):
    """计算回撤"""
    净值序列 = pd.Series(回测结果['每日净值'])
    历史高点 = 净值序列.cummax()
    回撤序列 = ((净值序列 - 历史高点) / 历史高点 * 100).fillna(0)
    回测结果['回撤'] = 回撤序列.tolist()
    回测结果['最大回撤'] = 回撤序列.min()
    回测结果['历史高点'] = 历史高点.tolist()
    return 回测结果


def 显示回测结果(回测结果, 品种代码, 短期均线, 长期均线, 止盈百分比, 止损百分比, 策略名称, 品种类型):
    """显示回测结果"""
    st.markdown("---")
    st.subheader("📊 回测指标")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("初始资金", f"¥{回测结果['初始资金']:,.0f}")
    col2.metric("最终资金", f"¥{回测结果['最终资金']:,.0f}", delta=f"¥{回测结果['总盈亏']:+,.0f}")
    col3.metric("总收益率", f"{回测结果['总收益率']:+.2f}%")
    col4.metric("最大回撤", f"{回测结果['最大回撤']:.2f}%")
    col5.metric("交易次数", len([t for t in 回测结果['交易记录'] if t['行动'] != '买入']))

    st.markdown("---")
    st.subheader("📈 净值曲线")

    # 绘制净值曲线
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=回测结果['数据']['日期'], y=回测结果['每日净值'], mode='lines', name='策略净值', line=dict(color='#FF6B6B', width=2)))
    fig.update_layout(title=f"{品种代码} - 回测净值曲线", xaxis_title="日期", yaxis_title="净值(元)", height=400)
    st.plotly_chart(fig, width="stretch")

    with st.expander("📖 策略参数", expanded=False):
        st.markdown(f"- **品种类型**: {品种类型}\n- **品种代码**: {品种代码}\n- **策略名称**: {策略名称}")
        st.markdown(f"- **手续费率**: {回测结果['手续费率']*100:.2f}%\n- **止盈目标**: {止盈百分比}%\n- **止损目标**: {止损百分比}%")

    if 回测结果['交易记录']:
        st.subheader("📋 交易记录")
        st.dataframe(pd.DataFrame(回测结果['交易记录']), width="stretch", hide_index=True)

    if 回测结果['总收益率'] > 0:
        st.success(f"✅ 策略取得了 {回测结果['总收益率']:+.2f}% 的正收益")
    else:
        st.warning(f"⚠️ 策略取得了 {回测结果['总收益率']:+.2f}% 的负收益")
