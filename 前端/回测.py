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


def 显示(引擎=None):
    """
    显示回测页面 - 动态净值曲线 + 动态回撤曲线
    """
    st.subheader("📈 动态回测系统")
    
    # ==================== 获取可选股票列表 ====================
    可选股票 = []
    
    # 1. 从当前持仓中获取
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 代码 in 引擎.持仓.keys():
            if 代码 and not 代码.startswith(('AAPL', 'GOOG', 'MSFT')):
                可选股票.append({"代码": 代码, "名称": f"{代码} (持仓)", "来源": "持仓"})
    
    # 2. 从策略库获取（如果存在）
    try:
        from 核心.策略加载器 import 策略加载器
        策略器 = 策略加载器()
        策略股票 = 策略器.获取策略股票列表() if hasattr(策略器, '获取策略股票列表') else []
        for 股票 in 策略股票:
            if isinstance(股票, dict):
                代码 = 股票.get('代码', '')
                名称 = 股票.get('名称', 代码)
            else:
                代码 = str(股票)
                名称 = 代码
            if 代码 and 代码 not in [s["代码"] for s in 可选股票] and not 代码.startswith(('AAPL', 'GOOG', 'MSFT')):
                可选股票.append({"代码": 代码, "名称": f"{代码} ({名称})", "来源": "策略库"})
    except Exception:
        pass
    
    # 3. 常用A股备选
    常用股票 = [
        {"代码": "000001", "名称": "平安银行"},
        {"代码": "000002", "名称": "万科A"},
        {"代码": "000858", "名称": "五粮液"},
        {"代码": "002415", "名称": "海康威视"},
        {"代码": "300750", "名称": "宁德时代"},
        {"代码": "600036", "名称": "招商银行"},
        {"代码": "600519", "名称": "贵州茅台"},
        {"代码": "601318", "名称": "中国平安"},
        {"代码": "601398", "名称": "工商银行"},
        {"代码": "601857", "名称": "中国石油"},
    ]
    
    for 股票 in 常用股票:
        if 股票["代码"] not in [s["代码"] for s in 可选股票]:
            可选股票.append({"代码": 股票["代码"], "名称": f"{股票['代码']} ({股票['名称']})", "来源": "常用"})
    
    if not 可选股票:
        可选股票 = [{"代码": "000001", "名称": "000001 (平安银行)", "来源": "默认"}]
    
    # ==================== 侧边栏参数设置 ====================
    with st.sidebar:
        st.markdown("### ⚙️ 回测参数")
        
        股票选项 = {f"{s['名称']}": s["代码"] for s in 可选股票}
        股票显示名称 = list(股票选项.keys())
        选中股票显示 = st.selectbox("选择股票", 股票显示名称, help="从持仓、策略库或常用A股中选择")
        股票代码 = 股票选项.get(选中股票显示, "000001")
        股票来源 = next((s["来源"] for s in 可选股票 if s["代码"] == 股票代码), "未知")
        st.caption(f"📌 股票来源: {股票来源}")
        
        开始日期 = st.date_input("开始日期", value=datetime.date(2023, 1, 1))
        结束日期 = st.date_input("结束日期", value=datetime.date.today())
        初始资金 = st.number_input("初始资金", value=1000000, step=100000, format="%d")
        手续费率 = st.number_input("手续费率", value=0.0003, step=0.0001, format="%.4f", help="默认万分之三")
        
        st.markdown("---")
        st.markdown("### 📊 策略参数")
        
        短期均线 = st.slider("短期均线（买入信号）", 3, 30, 5, 1)
        长期均线 = st.slider("长期均线（卖出信号）", 10, 60, 20, 1)
        
        st.markdown("---")
        st.markdown("### 🎯 止盈止损")
        
        止盈百分比 = st.number_input("止盈目标 (%)", value=5.0, step=1.0, min_value=0.0, max_value=50.0)
        止损百分比 = st.number_input("止损目标 (%)", value=-3.0, step=0.5, min_value=-30.0, max_value=0.0)
        
        st.markdown("---")
        运行按钮 = st.button("🚀 开始回测", type="primary", use_container_width=True)
    
    if not 运行按钮:
        st.info("👈 请在左侧选择股票并设置参数，然后点击「开始回测」")
        
        with st.expander("📈 示例：动态净值曲线 + 动态回撤曲线（点击展开）"):
            # 生成示例数据
            dates = pd.date_range("2023-01-01", periods=100, freq='ME')
            # 使用 pandas Series 来避免 numpy 数组问题
            nav_series = pd.Series(np.random.randn(100).cumsum() + 100, index=dates)
            nav = 1000000 * (1 + nav_series / 100)
            
            # 计算回撤（使用 pandas 方法）
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
            st.caption("注：此为演示数据，实际回测请选择股票并点击「开始回测」")
        return
    
    # ==================== 执行回测 ====================
    with st.spinner(f"正在获取 {股票代码} 的历史数据并执行回测..."):
        try:
            df = 获取股票历史数据(股票代码, 开始日期, 结束日期)
            
            if df is None or df.empty:
                st.error(f"❌ 无法获取股票 {股票代码} 的历史数据")
                st.info("请尝试以下方法：\n1. 检查股票代码是否正确（A股6位数字）\n2. 选择其他股票\n3. 检查网络连接")
                return
            
            st.success(f"✅ 成功获取 {len(df)} 条历史数据")
            st.caption(f"📅 回测区间：{df['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {df['日期'].iloc[-1].strftime('%Y-%m-%d')}")
            
            df = 计算均线(df, 短期均线, 长期均线)
            
            回测结果 = 执行持仓回测(
                df, 初始资金, 手续费率, 
                止盈百分比 / 100, 止损百分比 / 100
            )
            
            回测结果 = 计算回撤(回测结果)
            
            显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比)
            
        except Exception as e:
            st.error(f"回测失败: {str(e)}")
            import traceback
            with st.expander("详细错误信息"):
                st.code(traceback.format_exc())


def 获取股票历史数据(股票代码, 开始日期, 结束日期):
    """获取A股历史日线数据"""
    
    代码 = str(股票代码).strip().zfill(6)
    
    if 代码.startswith(('AAPL', 'GOOG', 'MSFT', 'TSLA', 'AMZN')):
        return None
    
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
        每日净值[-1] =资金
    
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
    # 转换为 pandas Series 以便使用 expanding 和 cummax
   净值列表 = 回测结果['每日净值']
   净值序列 = pd.Series(净值列表)
    
    # 计算历史高点
    历史高点 = 净值序列.cummax()
    # 计算回撤
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
    
    # 基准净值
    基准净值 = 回测结果['初始资金'] * df['收盘'] / df['收盘'].iloc[0]
    基准净值 = 基准净值.tolist()
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=('动态净值 (元)', '动态回撤 (%)'),
        row_heights=[0.6, 0.4]
    )
    
    # 第一行：净值曲线
    fig.add_trace(
        go.Scatter(
            x=dates, y=净值,
            mode='lines', name='策略净值',
            line=dict(color='#FF6B6B', width=2),
            fill='tozeroy', fillcolor='rgba(255,107,107,0.1)',
            hovertemplate='%{x|%Y-%m-%d}<br>净值: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates, y=基准净值,
            mode='lines', name='基准净值',
            line=dict(color='#95A5A6', width=1.5, dash='dash'),
            hovertemplate='%{x|%Y-%m-%d}<br>基准: ¥%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates, y=历史高点,
            mode='lines', name='历史高点',
            line=dict(color='#2ECC71', width=1.5, dash='dot'),
            hovertemplate='%{x|%Y-%m-%d}<br>高点: ¥%{y:,.0f}<extra></extra>'
        ),
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
                go.Scatter(
                    x=买入日期, y=买入净值,
                    mode='markers', name='买入信号',
                    marker=dict(symbol='triangle-up', size=10, color='#2ECC71'),
                    hovertemplate='买入<br>%{x|%Y-%m-%d}<extra></extra>'
                ),
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
                go.Scatter(
                    x=卖出日期, y=卖出净值,
                    mode='markers', name='卖出信号',
                    marker=dict(symbol='triangle-down', size=10, color='#E74C3C'),
                    hovertemplate='卖出<br>%{x|%Y-%m-%d}<extra></extra>'
                ),
                row=1, col=1
            )
    
    # 第二行：回撤曲线
    fig.add_trace(
        go.Scatter(
            x=dates, y=回撤,
            mode='lines', name='回撤',
            line=dict(color='#E74C3C', width=2),
            fill='tozeroy', fillcolor='rgba(231,76,60,0.2)',
            hovertemplate='%{x|%Y-%m-%d}<br>回撤: %{y:.2f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    # 最大回撤标记
    最大回撤值 = 回测结果['最大回撤']
    最大回撤索引 = 回撤.index(min(回撤)) if 回撤 else 0
    if 最大回撤索引 < len(dates):
        fig.add_annotation(
            x=dates[最大回撤索引],
            y=最大回撤值,
            text=f"最大回撤: {最大回撤值:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#E74C3C",
            ax=0,
            ay=-30,
            row=2, col=1
        )
    
    fig.update_layout(
        title=dict(text=f"{股票代码} - 动态回测曲线", x=0.5, font=dict(size=18)),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        height=600,
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(title_text="日期", row=2, col=1, gridcolor='#E8E8E8')
    fig.update_yaxes(title_text="净值 (元)", row=1, col=1, gridcolor='#E8E8E8', tickformat=',.0f')
    fig.update_yaxes(title_text="回撤 (%)", row=2, col=1, gridcolor='#E8E8E8', tickformat='.1f')
    
    return fig


def 显示回测结果(回测结果, 股票代码, 短期均线, 长期均线, 止盈百分比, 止损百分比):
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
        - **股票代码**: {股票代码}
        - **回测区间**: {回测结果['数据']['日期'].iloc[0].strftime('%Y-%m-%d')} 至 {回测结果['数据']['日期'].iloc[-1].strftime('%Y-%m-%d')}
        - **短期均线**: {短期均线}日
        - **长期均线**: {长期均线}日
        """)
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
        fig_pie = go.Figure(data=[go.Pie(
            labels=['盈利交易', '亏损交易'],
            values=[len(盈利交易), len(亏损交易)],
            marker_colors=['#2ECC71', '#E74C3C'],
            hole=0.4
        )])
        fig_pie.update_layout(title="盈亏交易比例", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    
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
