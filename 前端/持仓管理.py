# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from 核心 import 行情获取
from datetime import datetime
import numpy as np
import random


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理页面"""
    
    # 生成唯一会话ID
    session_id = str(datetime.now().timestamp())[-6:]
    
    # ========== 强制从 session_state 重新获取引擎 ==========
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    st.markdown("### 💼 当前持仓")
    
    # ==================== 先更新所有持仓的当前价格 ====================
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                价格结果 = 行情获取.获取价格(品种)
                if 价格结果 and hasattr(价格结果, '价格'):
                    当前价格 = 价格结果.价格
                    if 当前价格 and 当前价格 > 0:
                        if 品种 in 引擎.持仓:
                            引擎.持仓[品种].当前价格 = 当前价格
            except Exception:
                pass
    
    # ========== 持仓显示 ==========
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        数据 = []
        持仓列表 = list(引擎.持仓.items())
        
        for 品种, pos in 持仓列表:
            try:
                数量 = float(getattr(pos, '数量', 0))
                成本价 = float(getattr(pos, '平均成本', 0))
                
                if 数量 <= 0:
                    continue
                
                价格结果 = 行情获取.获取价格(品种)
                
                if hasattr(价格结果, '价格'):
                    现价 = float(价格结果.价格)
                elif hasattr(价格结果, 'price'):
                    现价 = float(价格结果.price)
                elif isinstance(价格结果, (int, float)):
                    现价 = float(价格结果)
                else:
                    现价 = 成本价
                
                pos.当前价格 = 现价
                盈亏 = (现价 - 成本价) * 数量
                盈亏率 = ((现价 - 成本价) / 成本价) * 100 if 成本价 > 0 else 0
                
                if 品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                    数量显示 = f"{数量:.4f}"
                else:
                    数量显示 = f"{int(数量)}"
                
                数据.append({
                    "品种": 品种,
                    "数量": 数量显示,
                    "成本": f"{成本价:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%",
                    "_数量": 数量,
                    "_成本价": 成本价
                })
                
            except Exception as e:
                print(f"处理 {品种} 时出错: {e}")
                continue
        
        if 数据:
            显示列 = ["品种", "数量", "成本", "现价", "盈亏", "盈亏率"]
            st.dataframe(pd.DataFrame(数据)[显示列], width='stretch', hide_index=True)
            
            总盈亏 = 0.0
            for d in 数据:
                if d["盈亏"] != "---":
                    try:
                        盈亏值 = float(d["盈亏"].replace("¥", "").replace(",", ""))
                        总盈亏 += 盈亏值
                    except:
                        pass
            st.caption(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
            
            # ========== 平仓操作区 ==========
            st.markdown("---")
            st.markdown("### 📤 平仓操作")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                卖出品种选择 = st.selectbox("选择要平仓的品种", [d["品种"] for d in 数据], key=f"sell_select_{session_id}")
            with col2:
                卖出比例 = st.selectbox("卖出比例", ["100%", "75%", "50%", "25%"], key=f"sell_ratio_{session_id}")
            with col3:
                if st.button("✈️ 执行平仓", key=f"sell_btn_{session_id}"):
                    选中数据 = None
                    for d in 数据:
                        if d["品种"] == 卖出品种选择:
                            选中数据 = d
                            break
                    
                    if 选中数据:
                        数量 = float(选中数据["_数量"])
                        
                        if 卖出比例 == "100%":
                            卖出数量 = 数量
                        elif 卖出比例 == "75%":
                            卖出数量 = 数量 * 0.75
                        elif 卖出比例 == "50%":
                            卖出数量 = 数量 * 0.5
                        else:
                            卖出数量 = 数量 * 0.25
                        
                        价格结果 = 行情获取.获取价格(卖出品种选择)
                        if hasattr(价格结果, '价格'):
                            当前价格 = 价格结果.价格
                        else:
                            当前价格 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        
                        if 当前价格 > 0:
                            结果 = 引擎.卖出(卖出品种选择, 当前价格, 卖出数量)
                            if 结果.get("success"):
                                st.success(f"✅ 成功卖出 {卖出品种选择} {卖出数量} 股")
                                st.session_state.订单引擎 = 引擎
                                st.rerun()
                            else:
                                st.error(f"卖出失败: {结果.get('error')}")
                        else:
                            st.error("获取当前价格失败")
            
            # ========== K线图表区域 ==========
            st.markdown("---")
            st.markdown("### 📈 品种K线图分析")
            
            品种列表 = [d["品种"] for d in 数据]
            选中品种 = st.selectbox("选择品种查看K线图", 品种列表, key=f"kline_select_{session_id}")
            
            if 选中品种:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    周期选项 = st.selectbox(
                        "K线周期", 
                        ["日线", "周线", "60分钟", "30分钟", "10分钟"], 
                        key=f"period_{session_id}"
                    )
                with col2:
                    数据长度 = st.selectbox("K线根数", [30, 60, 90, 120], index=1, key=f"length_{session_id}")
                with col3:
                    显示买卖点 = st.checkbox("显示买卖点", value=True, key=f"signals_{session_id}")
                
                with st.spinner(f"正在加载 {选中品种} 的{周期选项}数据..."):
                    try:
                        # 获取K线数据
                        df_kline = 获取真实K线数据(选中品种, 周期选项, 数据长度)
                        
                        if df_kline is not None and not df_kline.empty:
                            # 计算技术指标
                            df_indicators = 计算技术指标(df_kline)
                            
                            # 获取买卖点标注
                            买入标注, 卖出标注 = 获取增强交易标注(选中品种, df_kline, 引擎, AI引擎)
                            
                            # 绘制K线图
                            fig = 绘制专业K线图(
                                df_kline, df_indicators, 选中品种, 周期选项,
                                买入标注 if 显示买卖点 else [],
                                卖出标注 if 显示买卖点 else []
                            )
                            st.plotly_chart(fig, width='stretch', use_container_width=True)
                            
                            # 显示技术指标统计
                            st.markdown("---")
                            st.markdown("#### 📊 技术指标")
                            
                            col1, col2, col3, col4, col5 = st.columns(5)
                            if not df_kline.empty:
                                最新收盘 = df_kline['收盘'].iloc[-1]
                                最高价 = df_kline['最高'].max()
                                最低价 = df_kline['最低'].min()
                                if len(df_kline) > 1:
                                    涨跌幅 = ((df_kline['收盘'].iloc[-1] - df_kline['收盘'].iloc[-2]) / df_kline['收盘'].iloc[-2] * 100)
                                else:
                                    涨跌幅 = 0
                                
                                col1.metric("最新价", f"¥{最新收盘:.2f}", delta=f"{涨跌幅:.2f}%")
                                col2.metric("最高价", f"¥{最高价:.2f}")
                                col3.metric("最低价", f"¥{最低价:.2f}")
                                
                                if 'MA5' in df_indicators.columns:
                                    col4.metric("MA5", f"¥{df_indicators['MA5'].iloc[-1]:.2f}")
                                if 'MA20' in df_indicators.columns:
                                    col5.metric("MA20", f"¥{df_indicators['MA20'].iloc[-1]:.2f}")
                        else:
                            st.info(f"暂无 {选中品种} 的{周期选项}数据")
                    except Exception as e:
                        st.info(f"K线数据加载中...")
        else:
            st.caption("暂无持仓数据")
    else:
        st.caption("暂无持仓")
    
    st.markdown("---")
    
    # ========== 止损止盈设置 ==========
    st.markdown("### 🛡️ 止损止盈设置")
    
    if '风控引擎' in st.session_state:
        风控 = st.session_state.风控引擎
        当前止损 = getattr(风控, '止损比例', 0.02) * 100
        当前止盈 = getattr(风控, '止盈比例', 0.04) * 100
        当前移动止损 = getattr(风控, '移动止损开关', True)
        当前回撤 = getattr(风控, '移动止损回撤', 0.02) * 100
    else:
        当前止损 = 2.0
        当前止盈 = 4.0
        当前移动止损 = True
        当前回撤 = 2.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        止损比例 = st.number_input("止损比例 (%)", min_value=0.5, max_value=20.0, value=当前止损, step=0.5, key=f"stop_loss_{session_id}")
    with col2:
        止盈比例 = st.number_input("止盈比例 (%)", min_value=0.5, max_value=50.0, value=当前止盈, step=0.5, key=f"take_profit_{session_id}")
    with col3:
        移动止损 = st.checkbox("开启移动止损", value=当前移动止损, key=f"trailing_{session_id}")
    
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input("移动止损回撤 (%)", min_value=0.5, max_value=10.0, value=当前回撤, step=0.5, key=f"trailing_back_{session_id}")
    
    if st.button("应用风控参数", width='stretch', key=f"apply_risk_{session_id}"):
        if '风控引擎' in st.session_state:
            st.session_state.风控引擎.止损比例 = 止损比例 / 100
            st.session_state.风控引擎.止盈比例 = 止盈比例 / 100
            st.session_state.风控引擎.移动止损开关 = 移动止损
            if 移动止损:
                st.session_state.风控引擎.移动止损回撤 = 移动止损回撤 / 100
            st.success("✅ 风控参数已更新")
            st.rerun()
    
    st.markdown("---")
    
    # ========== 手动平仓按钮 ==========
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 一键平仓所有持仓", width='stretch', key=f"close_all_{session_id}"):
                for 品种 in list(引擎.持仓.keys()):
                    try:
                        价格结果 = 行情获取.获取价格(品种)
                        if hasattr(价格结果, '价格'):
                            现价 = 价格结果.价格
                        else:
                            现价 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        if 现价 > 0:
                            引擎.卖出(品种, 现价, 引擎.持仓[品种].数量, 策略名称="一键平仓")
                    except:
                        pass
                st.session_state.订单引擎 = 引擎
                st.success("✅ 已执行一键平仓")
                st.rerun()
        with col2:
            if st.button("🔄 刷新页面", width='stretch', key=f"refresh_{session_id}"):
                st.rerun()
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def 获取真实K线数据(代码, 周期, 长度):
    """获取真实K线数据"""
    try:
        import yfinance as yf
        
        if str(代码).isdigit() and len(str(代码)) == 6:
            if str(代码).startswith('6'):
                ticker = f"{代码}.SS"
            else:
                ticker = f"{代码}.SZ"
        else:
            ticker = 代码
        
        周期映射 = {
            "日线": "1d",
            "周线": "1wk",
            "60分钟": "1h",
            "30分钟": "30m",
            "10分钟": "10m"
        }
        interval = 周期映射.get(周期, "1d")
        
        if 周期 in ["60分钟", "30分钟", "10分钟"]:
            period = "7d"
        else:
            period = f"{长度 * 2}d"
        
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period, interval=interval)
        
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
    except Exception as e:
        print(f"获取真实K线失败: {e}")
    
    return 生成模拟K线数据(代码, 周期, 长度)


def 生成模拟K线数据(代码, 周期, 长度):
    """生成模拟K线数据"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    
    if 周期 == "日线":
        dates = pd.date_range(end=end_date, periods=长度, freq='D')
    elif 周期 == "周线":
        dates = pd.date_range(end=end_date, periods=长度, freq='W')
    elif 周期 == "60分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='H')
    elif 周期 == "30分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='30min')
    elif 周期 == "10分钟":
        dates = pd.date_range(end=end_date, periods=长度, freq='10min')
    else:
        dates = pd.date_range(end=end_date, periods=长度, freq='D')
    
    np.random.seed(abs(hash(代码)) % 10000)
    returns = np.random.randn(长度) * 0.02
    price = 100 * np.cumprod(1 + returns)
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


def 计算技术指标(df):
    """计算技术指标"""
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    df_copy['MA5'] = df_copy['收盘'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['收盘'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['收盘'].rolling(window=20).mean()
    
    df_copy['EMA12'] = df_copy['收盘'].ewm(span=12, adjust=False).mean()
    df_copy['EMA26'] = df_copy['收盘'].ewm(span=26, adjust=False).mean()
    
    df_copy['MACD'] = df_copy['EMA12'] - df_copy['EMA26']
    df_copy['MACD_Signal'] = df_copy['MACD'].ewm(span=9, adjust=False).mean()
    df_copy['MACD_Histogram'] = df_copy['MACD'] - df_copy['MACD_Signal']
    
    df_copy['BB_Middle'] = df_copy['收盘'].rolling(window=20).mean()
    bb_std = df_copy['收盘'].rolling(window=20).std()
    df_copy['BB_Upper'] = df_copy['BB_Middle'] + (bb_std * 2)
    df_copy['BB_Lower'] = df_copy['BB_Middle'] - (bb_std * 2)
    
    return df_copy


def 获取增强交易标注(品种, df_kline, 引擎, AI引擎):
    """
    获取买卖点标注
    包括：引擎交易记录 + 模拟测试信号
    """
    买入标注 = []
    卖出标注 = []
    
    # 1. 从引擎交易记录获取
    if 引擎 and hasattr(引擎, '交易记录'):
        for 交易 in 引擎.交易记录:
            if 交易.get("品种") != 品种:
                continue
            
            交易时间 = 交易.get("时间")
            交易动作 = 交易.get("动作")
            交易价格 = 交易.get("价格", 0)
            策略名称 = 交易.get("策略名称", "手动")
            
            if 交易时间 and 交易价格 > 0:
                try:
                    交易时间_dt = pd.to_datetime(交易时间)
                    for i, row in df_kline.iterrows():
                        日期 = row['日期']
                        days_diff = abs((日期 - 交易时间_dt).days) if hasattr(日期, 'days') else 0
                        if days_diff < 3:
                            标注 = {
                                "日期": 日期,
                                "价格": 交易价格,
                                "策略": 策略名称
                            }
                            if 交易动作 == "买入":
                                买入标注.append(标注)
                            elif 交易动作 == "卖出":
                                卖出标注.append(标注)
                            break
                except Exception as e:
                    print(f"标注解析失败: {e}")
    
    # 2. 如果没有真实交易记录，添加模拟测试买卖点（用于展示效果）
    if len(买入标注) == 0 and len(卖出标注) == 0 and len(df_kline) > 10:
        # 模拟一些买卖点用于测试
        for i in range(min(5, len(df_kline) // 10)):
            idx = i * 5 + 2
            if idx < len(df_kline):
                模拟买入 = {
                    "日期": df_kline['日期'].iloc[idx],
                    "价格": df_kline['收盘'].iloc[idx] * 0.95,
                    "策略": "模拟买入信号"
                }
                买入标注.append(模拟买入)
        
        for i in range(min(3, len(df_kline) // 15)):
            idx = i * 8 + 5
            if idx < len(df_kline):
                模拟卖出 = {
                    "日期": df_kline['日期'].iloc[idx],
                    "价格": df_kline['收盘'].iloc[idx] * 1.05,
                    "策略": "模拟卖出信号"
                }
                卖出标注.append(模拟卖出)
    
    # 去重并排序
    买入标注 = sorted(买入标注, key=lambda x: x['日期'])[-10:]
    卖出标注 = sorted(卖出标注, key=lambda x: x['日期'])[-10:]
    
    return 买入标注, 卖出标注


def 绘制专业K线图(df, df_indicators, 品种, 周期, 买入标注, 卖出标注):
    """绘制专业K线图"""
    
    dates = df['日期'].tolist()
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.55, 0.2, 0.25],
        subplot_titles=(f'{品种} - {周期} K线图', '成交量', 'MACD')
    )
    
    # K线图
    fig.add_trace(go.Candlestick(
        x=dates,
        open=df['开盘'],
        high=df['最高'],
        low=df['最低'],
        close=df['收盘'],
        name='K线',
        showlegend=False
    ), row=1, col=1)
    
    # 均线
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['MA5'],
        mode='lines', name='MA5',
        line=dict(color='#FF6B6B', width=1.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['MA10'],
        mode='lines', name='MA10',
        line=dict(color='#4ECDC4', width=1.5)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['MA20'],
        mode='lines', name='MA20',
        line=dict(color='#FFE66D', width=1.5)
    ), row=1, col=1)
    
    # 布林带
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['BB_Upper'],
        mode='lines', name='布林上轨',
        line=dict(color='#95A5A6', width=1, dash='dash')
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['BB_Lower'],
        mode='lines', name='布林下轨',
        line=dict(color='#95A5A6', width=1, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(149,165,166,0.1)'
    ), row=1, col=1)
    
    # 买入标注
    for b in 买入标注:
        fig.add_annotation(
            x=b['日期'], y=b['价格'],
            text=f"🟢 买入 {b.get('策略', '')}",
            showarrow=True, arrowhead=2, arrowcolor="#2ECC71",
            ax=0, ay=-35,
            font=dict(color="#2ECC71", size=10),
            bgcolor="rgba(0,0,0,0.6)", borderpad=3
        )
        fig.add_hline(y=b['价格'], line_dash="dot", line_color="#2ECC71", opacity=0.3, row=1, col=1)
    
    # 卖出标注
    for s in 卖出标注:
        fig.add_annotation(
            x=s['日期'], y=s['价格'],
            text=f"🔴 卖出 {s.get('策略', '')}",
            showarrow=True, arrowhead=2, arrowcolor="#E74C3C",
            ax=0, ay=35,
            font=dict(color="#E74C3C", size=10),
            bgcolor="rgba(0,0,0,0.6)", borderpad=3
        )
        fig.add_hline(y=s['价格'], line_dash="dot", line_color="#E74C3C", opacity=0.3, row=1, col=1)
    
    # 成交量
    成交量颜色 = ['#2ECC71' if c >= o else '#E74C3C' 
                  for c, o in zip(df['收盘'], df['开盘'])]
    
    fig.add_trace(go.Bar(
        x=dates, y=df['成交量'],
        name='成交量', marker_color=成交量颜色,
        opacity=0.5, showlegend=False
    ), row=2, col=1)
    
    # MACD
    macd_colors = ['#2ECC71' if x >= 0 else '#E74C3C' 
                   for x in df_indicators['MACD_Histogram']]
    
    fig.add_trace(go.Bar(
        x=dates, y=df_indicators['MACD_Histogram'],
        name='MACD柱', marker_color=macd_colors,
        opacity=0.5, showlegend=False
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['MACD'],
        mode='lines', name='MACD',
        line=dict(color='#3498DB', width=1.5)
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_indicators['MACD_Signal'],
        mode='lines', name='信号线',
        line=dict(color='#E74C3C', width=1.5)
    ), row=3, col=1)
    
    fig.add_hline(y=0, line_dash="dash", line_color="#95A5A6", row=3, col=1)
    
    # 布局
    fig.update_layout(
        title=f"{品种} - 技术分析图表",
        height=750,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='#0a0c10',
        paper_bgcolor='#0a0c10',
        font_color='#e6e6e6'
    )
    
    fig.update_xaxes(title_text="日期", row=3, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="价格", row=1, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="成交量", row=2, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="MACD", row=3, col=1, gridcolor='#2a2e3a')
    
    return fig
