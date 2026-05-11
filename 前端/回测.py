# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

# ==================== 市场配置 ====================
市场配置 = {
    "A股策略": {
        "代码前缀": ["0", "3", "6"],
        "数据源": "akshare/东方财富",
        "代码转换": lambda x: str(x).zfill(6),
        "获取数据": "获取A股历史数据"
    },
    "加密货币策略": {
        "代码前缀": ["BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "AVAX"],
        "数据源": "暂不支持",
        "代码转换": lambda x: str(x).upper(),
        "获取数据": "获取加密货币数据(开发中)"
    },
    "外汇策略": {
        "代码前缀": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"],
        "数据源": "暂不支持",
        "代码转换": lambda x: str(x).upper(),
        "获取数据": "获取外汇数据(开发中)"
    },
    "美股策略": {
        "代码前缀": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"],
        "数据源": "暂不支持",
        "代码转换": lambda x: str(x).upper(),
        "获取数据": "获取美股数据(开发中)"
    }
}


def 显示(引擎=None):
    """
    显示回测页面 - 动态净值曲线 + 动态回撤曲线
    支持多策略类别选择
    """
    st.subheader("📈 动态回测系统")

    # ==================== 获取策略类别 ====================
    策略类别列表 = ["A股策略", "加密货币策略", "外汇策略", "美股策略"]

    # ==================== 侧边栏参数设置 ====================
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")

        # 策略类别选择
        选中类别 = st.selectbox("选择策略类别", 策略类别列表, help="选择要回测的市场类别")

        st.markdown("---")

        # 根据类别显示不同的股票/品种选择
        if 选中类别 == "A股策略":
            # 从持仓中获取A股
            可选股票 = []
            if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
                for 代码 in 引擎.持仓.keys():
                    if 代码 and not 代码.upper().startswith(('AAPL', 'GOOG', 'MSFT', 'AMZN', 'TSLA')):
                        # 检查是否是A股（数字代码）
                        if str(代码).isdigit() or str(代码).startswith(('0', '3', '6')):
                            可选股票.append({"代码": 代码, "名称": f"{代码} (持仓)", "来源": "持仓"})

            if 可选股票:
                股票选项 = {f"{s['名称']}": s["代码"] for s in 可选股票}
                股票显示名称 = list(股票选项.keys())
                选中股票显示 = st.selectbox("选择持仓股票", 股票显示名称, help="从当前A股持仓中选择")
                股票代码 = 股票选项.get(选中股票显示, 可选股票[0]["代码"])
                st.caption(f"📌 当前A股持仓: {len(可选股票)} 只")
            else:
                st.warning("⚠️ 当前没有A股持仓，请在AI交易中先买入A股")
                手动输入 = st.text_input("手动输入股票代码", value="000001", help="例如：000001、600036")
                股票代码 = 手动输入
                st.caption("💡 提示：没有持仓时可以使用手动输入进行回测")

        elif 选中类别 == "加密货币策略":
            st.info("💡 加密货币数据源开发中，当前仅支持演示模式")
            加密货币列表 = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]
            选中币种 = st.selectbox("选择加密货币", 加密货币列表)
            股票代码 = 选中币种.split("/")[0]
            st.warning("⚠️ 加密货币回测功能开发中，当前为演示模式")

        elif 选中类别 == "外汇策略":
            st.info("💡 外汇数据源开发中，当前仅支持演示模式")
            外汇列表 = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
            选中外汇 = st.selectbox("选择外汇对", 外汇列表)
            股票代码 = 选中外汇.replace("/", "")
            st.warning("⚠️ 外汇回测功能开发中，当前为演示模式")

        elif 选中类别 == "美股策略":
            st.info("💡 美股数据源开发中，当前仅支持演示模式")
            美股列表 = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
            选中美股 = st.selectbox("选择美股", 美股列表)
            股票代码 = 选中美股
            st.warning("⚠️ 美股回测功能开发中，当前为演示模式")
            st.caption("💡 提示：如需回测美股，建议使用yfinance或alpha_vantage数据源")

        st.markdown("---")

        开始日期 = st.date_input("开始日期", value=datetime.date(2023, 1, 1))
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.0003, step=0.0001, format="%.4f", help="默认万分之三")

        st.markdown("---")
        st.markdown("### 📊 策略参数")

        策略类型 = st.selectbox("交易策略", ["双均线策略", "买入持有策略", "布林带策略"], index=0)

        if 策略类型 == "双均线策略":
            短期均线 = st.slider("短期均线（买入信号）", 3, 30, 5, 1)
            长期均线 = st.slider("长期均线（卖出信号）", 10, 60, 20, 1)
        else:
            短期均线, 长期均线 = 5, 20

        if 策略类型 == "布林带策略":
            布林带周期 = st.slider("布林带周期", 10, 50, 20, 5)
            布林带标准差 = st.slider("标准差倍数", 1.0, 3.0, 2.0, 0.5)

        st.markdown("---")
        st.markdown("### 🎯 止盈止损")

        止盈百分比 = st.number_input("止盈目标 (%)", value=5.0, step=1.0, min_value=0.0, max_value=50.0)
        止损百分比 = st.number_input("止损目标 (%)", value=-3.0, step=0.5, min_value=-30.0, max_value=0.0)

        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", use_container_width=True)

    # 显示当前类别信息
    st.info(f"📌 当前策略类别: **{选中类别}** | 回测品种: **{股票代码}**")

    if not 运行按钮:
        st.info("👈 请在左侧选择策略类别和参数，然后点击「开始回测」")

        with st.expander("📈 示例：动态净值曲线 + 动态回撤曲线（点击展开）"):
            dates = pd.date_range("2023-01-01", periods=100, freq='ME')
            nav_series = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
            nav = 1000000 * (1 + nav_series / 100)
            peak = nav.cummax()
            drawdown = ((nav - peak) / peak * 100).fillna(0)

            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=('动态净值 (元)', '动态回撤 (%)'),
                row_heights=[0.6, 0.4]
            )

            fig.add_trace(
                go.Scatter(x=dates, y=nav, mode='lines', name='净值',
                          line=dict(color='#FF6B6B', width=2),
                          fill='tozeroy', fillcolor='rgba(255,107,107,0.1)'),
                row=1, col=1
            )

            fig.add_trace(
                go.Scatter(x=dates, y=drawdown, mode='lines', name='回撤',
                          line=dict(color='#E74C3C', width=2),
                          fill='tozeroy', fillcolor='rgba(231,76,60,0.2)'),
                row=2, col=1
            )

            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

            fig.update_layout(title="示例：动态回测曲线", height=500, hovermode='x unified')
            fig.update_yaxes(title_text="净值 (元)", row=1, col=1, tickformat=',.0f')
            fig.update_yaxes(title_text="回撤 (%)", row=2, col=1, tickformat='.1f')

            st.plotly_chart(fig, use_container_width=True)
            st.caption("注：此为演示数据，实际回测请选择类别并点击「开始回测」")
        return

    # ==================== 执行回测 ====================
    with st.spinner(f"正在获取 {股票代码} 的历史数据并执行回测..."):
        try:
            # 根据策略类别获取历史数据
            if 选中类别 == "A股策略":
                df = 获取A股历史数据(股票代码, 开始日期, 结束日期)
            elif 选中类别 == "加密货币策略":
                df = 获取加密货币演示数据(股票代码, 开始日期, 结束日期)
            elif 选中类别 == "外汇策略":
                df = 获取外汇演示数据(股票代码, 开始日期, 结束日期)
            elif 选中类别 == "美股策略":
                df = 获取美股演示数据(股票代码, 开始日期, 结束日期)
            else:
                df = None

            if df is None or df.empty:
                st.error(f"❌ 无法获取 {股票代码} 的历史数据")
                if 选中类别 != "A股策略":
                    st.info(f"💡 {选中类别} 数据源正在开发中，当前使用演示数据。如需真实数据，请切换至「A股策略」")
                else:
                    st.info("请检查股票代码是否正确，或选择其他A股持仓")
                return

            st.success(f"✅ 成功获取 {len(df)} 条历史数据")
            st.caption(f"📅 回测区间：{df['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {df['日期'].iloc[-1].strftime('%Y-%m-%d')}")

            # 根据策略类型计算信号
            if 策略类型 == "双均线策略":
                df = 计算均线(df, 短期均线, 长期均线)
            elif 策略类型 == "布林带策略":
                df = 计算布林带(df, 布林带周期, 布林带标准差)
            else:
                df['信号'] = 0  # 买入持有策略无信号

            回测结果 = 执行持仓回测(
                df, 初始资金, 手续费率,
                止盈百分比 / 100, 止损百分比 / 100
            )

            回测结果 = 计算回撤(回测结果)

            显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比, 策略类型, 选中类别)

        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            with st.expander("详细错误信息"):
                st.code(traceback.format_exc())


def 获取A股历史数据(股票代码, 开始日期, 结束日期):
    """获取A股历史日线数据"""
    代码 = str(股票代码).strip().zfill(6)

    if AKSHARE_AVAILABLE:
        try:
            df = ak.stock_zh_a_hist(
                symbol=代码,
                period="daily",
                start_date=开始日期.strftime("%Y%m%d"),
                end_date=结束日期.strftime("%Y%m%d"),
                adjust="qfq"
            )
            if df is not None and not df.empty:
                df.columns = ['日期', '开盘', '最高', '最低', '收盘', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '换手率']
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期')
                df = df.drop_duplicates(subset=['日期'])
                return df[['日期', '开盘', '最高', '最低', '收盘', '成交量']]
        except Exception as e:
            print(f"akshare 获取失败: {e}")

    try:
        市场代码 = "1" if 代码.startswith('6') else "0"
        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": f"{市场代码}.{代码}",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "beg": 开始日期.strftime("%Y%m%d"),
            "end": 结束日期.strftime("%Y%m%d"),
            "ut": "fa5fd1943c7b386a172cb689d1c0edf1"
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            rows = []
            for k in klines:
                parts = k.split(",")
                rows.append({
                    "日期": parts[0],
                    "开盘": float(parts[1]),
                    "最高": float(parts[2]),
                    "最低": float(parts[3]),
                    "收盘": float(parts[4]),
                    "成交量": float(parts[5])
                })
            df = pd.DataFrame(rows)
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.drop_duplicates(subset=['日期'])
            return df
    except Exception as e:
        print(f"东方财富接口获取失败: {e}")

    return None


def 获取加密货币演示数据(股票代码, 开始日期, 结束日期):
    """获取加密货币演示数据（模拟数据）"""
    dates = pd.date_range(开始日期, 结束日期, freq='D')
    np.random.seed(hash(股票代码) % 10000)
    returns = np.random.randn(len(dates)) * 0.03 + 0.0005
    price = 10000 * np.cumprod(1 + returns)
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * 0.99,
        '最高': price * 1.02,
        '最低': price * 0.98,
        '收盘': price,
        '成交量': np.random.randint(1000, 10000, len(dates))
    })
    return df


def 获取外汇演示数据(股票代码, 开始日期, 结束日期):
    """获取外汇演示数据（模拟数据）"""
    dates = pd.date_range(开始日期, 结束日期, freq='D')
    np.random.seed(hash(股票代码 + "FOREX") % 10000)
    returns = np.random.randn(len(dates)) * 0.005
    price = 1.1 * np.cumprod(1 + returns)
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * 0.999,
        '最高': price * 1.001,
        '最低': price * 0.999,
        '收盘': price,
        '成交量': np.random.randint(10000, 50000, len(dates))
    })
    return df


def 获取美股演示数据(股票代码, 开始日期, 结束日期):
    """获取美股演示数据（模拟数据）"""
    dates = pd.date_range(开始日期, 结束日期, freq='D')
    np.random.seed(hash(股票代码) % 10000)
    returns = np.random.randn(len(dates)) * 0.02 + 0.0003
    price = 150 * np.cumprod(1 + returns)
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price * 0.99,
        '最高': price * 1.01,
        '最低': price * 0.98,
        '收盘': price,
        '成交量': np.random.randint(1000000, 10000000, len(dates))
    })
    return df


def 计算均线(df, 短期均线, 长期均线):
    """计算移动平均线"""
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
    """计算布林带"""
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
    """执行持仓回测"""
    资金 = 初始资金
    持仓数量 = 0
    交易记录 = []
    每日净值 = []
    买入价 = 0

    for i in range(len(df)):
        当前日期 = df['日期'].iloc[i]
        当前收盘 = df['收盘'].iloc[i]

        止盈触发 = False
        止损触发 = False

        if 持仓数量 > 0 and 买入价 > 0:
            当前盈亏率 = (当前收盘 - 买入价) / 买入价
            if 止盈率 > 0 and 当前盈亏率 >= 止盈率:
                止盈触发 = True
            if 止损率 < 0 and 当前盈亏率 <= 止损率:
                止损触发 = True

        if (止盈触发 or 止损触发) and 持仓数量 > 0:
            卖出金额 = 持仓数量 * 当前收盘
            手续费 = 卖出金额 * 手续费率
            实际收入 = 卖出金额 - 手续费
            资金 += 实际收入
            盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费

            交易记录.append({
                '日期': 当前日期,
                '行动': '止盈卖出' if 止盈触发 else '止损卖出',
                '价格': 当前收盘,
                '数量': 持仓数量,
                '盈亏': round(盈亏, 2)
            })
            持仓数量 = 0
            买入价 = 0

        elif df['信号'].iloc[i] == 1 and 持仓数量 == 0:
            买入数量 = int(资金 / 当前收盘 / 100) * 100
            if 买入数量 > 0:
                买入金额 = 买入数量 * 当前收盘
                手续费 = 买入金额 * 手续费率
                资金 -= (买入金额 + 手续费)
                持仓数量 = 买入数量
                买入价 = 当前收盘
                交易记录.append({
                    '日期': 当前日期,
                    '行动': '买入',
                    '价格': 当前收盘,
                    '数量': 持仓数量,
                    '盈亏': 0
                })

        elif df['信号'].iloc[i] == -1 and 持仓数量 > 0:
            卖出金额 = 持仓数量 * 当前收盘
            手续费 = 卖出金额 * 手续费率
            实际收入 = 卖出金额 - 手续费
            资金 += 实际收入
            盈亏 = (当前收盘 - 买入价) * 持仓数量 - 手续费
            交易记录.append({
                '日期': 当前日期,
                '行动': '卖出(信号)',
                '价格': 当前收盘,
                '数量': 持仓数量,
                '盈亏': round(盈亏, 2)
            })
            持仓数量 = 0
            买入价 = 0

        当前持仓市值 = 持仓数量 * 当前收盘
        当日总资产 = 资金 + 当前持仓市值
        每日净值.append(当日总资产)

    if 持仓数量 > 0:
        最后价格 = df['收盘'].iloc[-1]
        卖出金额 = 持仓数量 * 最后价格
        手续费 = 卖出金额 * 手续费率
        资金 += (卖出金额 - 手续费)
        盈亏 = (最后价格 - 买入价) * 持仓数量 - 手续费
        交易记录.append({
            '日期': df['日期'].iloc[-1],
            '行动': '强制平仓',
            '价格': 最后价格,
            '数量': 持仓数量,
            '盈亏': round(盈亏, 2)
        })
        每日净值[-1] = 资金

    return {
        '初始资金': 初始资金,
        '最终资金': 资金,
        '总盈亏': 资金 - 初始资金,
        '总收益率': (资金 - 初始资金) / 初始资金 * 100,
        '每日净值': 每日净值,
        '交易记录': 交易记录,
        '数据': df,
        '手续费率': 手续费率
    }


def 计算回撤(回测结果):
    """计算动态回撤"""
    净值列表 = 回测结果['每日净值']
    净值序列 = pd.Series(净值列表)

    历史高点 = 净值序列.cummax()
    回撤序列 = ((净值序列 - 历史高点) / 历史高点 * 100).fillna(0)

    回测结果['回撤'] = 回撤序列.tolist()
    回测结果['最大回撤'] = 回撤序列.min()
    回测结果['历史高点'] = 历史高点.tolist()

    return 回测结果


def 绘制动态净值曲线(df, 回测结果, 股票代码):
    """绘制动态净值曲线 + 动态回撤曲线"""
    dates = df['日期'].tolist()
    净值 = 回测结果['每日净值']
    回撤 = 回测结果['回撤']
    历史高点 = 回测结果['历史高点']

    基准净值 = 回测结果['初始资金'] * df['收盘'] / df['收盘'].iloc[0]
    基准净值 = 基准净值.tolist()

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=('动态净值 (元)', '动态回撤 (%)'),
        row_heights=[0.6, 0.4]
    )

    fig.add_trace(
        go.Scatter(x=dates, y=净值, mode='lines', name='策略净值',
                  line=dict(color='#FF6B6B', width=2),
                  fill='tozeroy', fillcolor='rgba(255,107,107,0.1)'),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=dates, y=基准净值, mode='lines', name='基准净值',
                  line=dict(color='#95A5A6', width=1.5, dash='dash')),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=dates, y=历史高点, mode='lines', name='历史高点',
                  line=dict(color='#2ECC71', width=1.5, dash='dot')),
        row=1, col=1
    )

    # 买卖点标记
    买入记录 = [t for t in 回测结果['交易记录'] if t['行动'] == '买入']
    卖出记录 = [t for t in 回测结果['交易记录'] if t['行动'] in ['卖出(信号)', '止盈卖出', '止损卖出', '强制平仓']]

    if 买入记录:
        买入日期 = [t['日期'] for t in 买入记录]
        买入净值 = []
        for d in 买入日期:
            try:
                idx = dates.index(d)
                买入净值.append(净值[idx])
            except ValueError:
                pass
        if 买入净值:
            fig.add_trace(
                go.Scatter(x=买入日期, y=买入净值, mode='markers', name='买入信号',
                          marker=dict(symbol='triangle-up', size=10, color='#2ECC71')),
                row=1, col=1
            )

    if 卖出记录:
        卖出日期 = [t['日期'] for t in 卖出记录]
        卖出净值 = []
        for d in 卖出日期:
            try:
                idx = dates.index(d)
                卖出净值.append(净值[idx])
            except ValueError:
                pass
        if 卖出净值:
            fig.add_trace(
                go.Scatter(x=卖出日期, y=卖出净值, mode='markers', name='卖出信号',
                          marker=dict(symbol='triangle-down', size=10, color='#E74C3C')),
                row=1, col=1
            )

    fig.add_trace(
        go.Scatter(x=dates, y=回撤, mode='lines', name='回撤',
                  line=dict(color='#E74C3C', width=2),
                  fill='tozeroy', fillcolor='rgba(231,76,60,0.2)'),
        row=2, col=1
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)

    # 最大回撤标记
    最大回撤值 = 回测结果['最大回撤']
    回撤列表 = 回测结果['回撤']
    最大回撤索引 = 回撤列表.index(min(回撤列表)) if 回撤列表 else 0
    if 最大回撤索引 < len(dates):
        fig.add_annotation(
            x=dates[最大回撤索引], y=最大回撤值,
            text=f"最大回撤: {最大回撤值:.2f}%",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor="#E74C3C", ax=0, ay=-30,
            row=2, col=1
        )

    fig.update_layout(
        title=dict(text=f"{股票代码} - 动态回测曲线", x=0.5, font=dict(size=18)),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        height=600, plot_bgcolor='white'
    )

    fig.update_xaxes(title_text="日期", row=2, col=1, gridcolor='#E8E8E8')
    fig.update_yaxes(title_text="净值 (元)", row=1, col=1, gridcolor='#E8E8E8', tickformat=',.0f')
    fig.update_yaxes(title_text="回撤 (%)", row=2, col=1, gridcolor='#E8E8E8', tickformat='.1f')

    return fig


def 显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比, 策略类型, 策略类别):
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
    st.subheader("📈 动态净值曲线 & 动态回撤曲线")

    fig = 绘制动态净值曲线(回测结果['数据'], 回测结果, 股票代码)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📖 策略参数", expanded=False):
        col1, col2 = st.columns(2)
        col1.markdown(f"""
        - **策略类别**: {策略类别}
        - **品种代码**: {股票代码}
        - **回测区间**: {回测结果['数据']['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {回测结果['数据']['日期'].iloc[-1].strftime('%Y-%m-%d')}
        - **策略类型**: {策略类型}
        """)
        if 策略类型 == "双均线策略":
            col1.markdown(f"- **短期均线**: {短期均线}日\n- **长期均线**: {长期均线}日")
        col2.markdown(f"""
        - **手续费率**: {回测结果['手续费率']*100:.2f}%
        - **止盈目标**: {止盈百分比}%
        - **止损目标**: {止损百分比}%
        - **初始资金**: ¥{回测结果['初始资金']:,.0f}
        """)

    st.subheader("📊 收益分析")

    盈利交易 = [t for t in 回测结果['交易记录'] if t['盈亏'] > 0]
    亏损交易 = [t for t in 回测结果['交易记录'] if t['盈亏'] < 0]

    col1, col2 = st.columns(2)

    with col1:
        if len(盈利交易) + len(亏损交易) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['盈利交易', '亏损交易'],
                values=[len(盈利交易), len(亏损交易)],
                marker_colors=['#2ECC71', '#E74C3C'],
                hole=0.4
            )])
            fig_pie.update_layout(title="盈亏交易比例", height=350)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("暂无盈亏数据")

    with col2:
        if 盈利交易 or 亏损交易:
            盈利总额 = sum(t['盈亏'] for t in 盈利交易) if 盈利交易 else 0
            亏损总额 = abs(sum(t['盈亏'] for t in 亏损交易)) if 亏损交易 else 0
            st.metric("总盈利", f"¥{盈利总额:,.2f}")
            st.metric("总亏损", f"¥{亏损总额:,.2f}")
            if len(盈利交易) + len(亏损交易) > 0:
                胜率 = len(盈利交易) / (len(盈利交易) + len(亏损交易)) * 100
                st.metric("胜率", f"{胜率:.1f}%")

    if 回测结果['交易记录']:
        st.subheader("📋 交易记录")
        交易_df = pd.DataFrame(回测结果['交易记录'])
        st.dataframe(交易_df, use_container_width=True, hide_index=True)
    else:
        st.info("本次回测没有产生任何交易记录")

    st.markdown("---")
    st.subheader("💡 回测总结")

    if 回测结果['总收益率'] > 0:
        st.success(f"✅ 策略在回测区间内取得了 {回测结果['总收益率']:+.2f}% 的正收益")
    else:
        st.warning(f"⚠️ 策略在回测区间内取得了 {回测结果['总收益率']:+.2f}% 的负收益")

    st.markdown("""
    **⚠️ 风险提示**：
    - 历史回测结果不代表未来收益
    - 实际交易中可能存在滑点和流动性风险
    - 建议在实盘前进行充分的参数优化和压力测试
    """)
