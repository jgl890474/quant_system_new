# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from 核心 import 行情获取
from datetime import datetime, timedelta
import numpy as np


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理页面"""
    
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
                卖出品种选择 = st.selectbox("选择要平仓的品种", [d["品种"] for d in 数据], key="sell_select")
            with col2:
                卖出比例 = st.selectbox("卖出比例", ["100%", "75%", "50%", "25%"], key="sell_ratio")
            with col3:
                if st.button("✈️ 执行平仓", key="sell_position_btn"):
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
            选中品种 = st.selectbox("选择品种查看K线图", 品种列表, key="kline_select")
            
            if 选中品种:
                # 周期选择
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    周期选项 = st.selectbox(
                        "K线周期",
                        ["日线", "周线", "60分钟", "30分钟", "10分钟"],
                        key="period_select"
                    )
                with col2:
                    数据长度 = st.selectbox("K线根数", [30, 60, 90, 120], index=1, key="length_select")
                with col3:
                    显示买卖点 = st.checkbox("显示买卖点", value=True, key="show_signals")
                
                with st.spinner(f"正在加载 {选中品种} 的{周期选项}数据..."):
                    try:
                        # 获取K线数据
                        df_kline = 获取K线数据模拟(选中品种, 周期选项, 数据长度)
                        
                        if df_kline is not None and not df_kline.empty:
                            # 获取买卖点标注
                            买入标注, 卖出标注 = 获取策略信号标注(选中品种, df_kline, 引擎)
                            
                            # 创建K线图
                            fig = 绘制K线图(
                                df_kline, 选中品种, 周期选项,
                                买入标注 if 显示买卖点 else [],
                                卖出标注 if 显示买卖点 else []
                            )
                            
                            st.plotly_chart(fig, width='stretch', use_container_width=True)
                        else:
                            st.info(f"暂无 {选中品种} 的{周期选项}数据")
                    except Exception as e:
                        st.info(f"K线数据暂不可用: {str(e)[:50]}")
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
        止损比例 = st.number_input("止损比例 (%)", min_value=0.5, max_value=20.0, value=当前止损, step=0.5, key="stop_loss")
    with col2:
        止盈比例 = st.number_input("止盈比例 (%)", min_value=0.5, max_value=50.0, value=当前止盈, step=0.5, key="take_profit")
    with col3:
        移动止损 = st.checkbox("开启移动止损", value=当前移动止损, key="trailing_stop")
    
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input("移动止损回撤 (%)", min_value=0.5, max_value=10.0, value=当前回撤, step=0.5, key="trailing_back")
    
    if st.button("应用风控参数", width='stretch', key="apply_risk"):
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
            if st.button("🗑️ 一键平仓所有持仓", width='stretch', key="close_all"):
                for 品种 in list(引擎.持仓.keys()):
                    try:
                        价格结果 = 行情获取.获取价格(品种)
                        if hasattr(价格结果, '价格'):
                            现价 = 价格结果.价格
                        else:
                            现价 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        if 现价 > 0:
                            引擎.卖出(品种, 现价, 引擎.持仓[品种].数量)
                    except:
                        pass
                st.session_state.订单引擎 = 引擎
                st.success("✅ 已执行一键平仓")
                st.rerun()
        with col2:
            if st.button("🔄 刷新页面", width='stretch', key="refresh_page"):
                st.rerun()
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def 获取K线数据模拟(代码, 周期, 长度):
    """生成模拟K线数据"""
    import numpy as np
    
    # 根据周期设置时间间隔
    if 周期 == "日线":
        freq = 'D'
    elif 周期 == "周线":
        freq = 'W'
    elif 周期 == "60分钟":
        freq = 'H'
        长度 = 长度 * 24  # 转换为小时
    elif 周期 == "30分钟":
        freq = '30min'
        长度 = 长度 * 48
    elif 周期 == "10分钟":
        freq = '10min'
        长度 = 长度 * 144
    else:
        freq = 'D'
    
    # 生成日期范围
    if freq == 'W':
        dates = pd.date_range(end=datetime.now(), periods=长度, freq='W')
    elif freq in ['H', '30min', '10min']:
        dates = pd.date_range(end=datetime.now(), periods=长度, freq=freq)
    else:
        dates = pd.date_range(end=datetime.now(), periods=长度, freq='D')
    
    # 随机生成价格
    np.random.seed(hash(代码) % 10000 + 12345)
    base_price = 100
    
    # 生成趋势
    trend = np.cumsum(np.random.randn(长度) * 0.5)
    price_series = base_price + trend
    price_series = np.maximum(price_series, 0.01)
    
    # 生成OHLC
    df = pd.DataFrame({
        '日期': dates,
        '开盘': price_series * (1 + np.random.randn(长度) * 0.01),
        '最高': price_series * (1 + abs(np.random.randn(长度) * 0.02)),
        '最低': price_series * (1 - abs(np.random.randn(长度) * 0.02)),
        '收盘': price_series,
        '成交量': np.random.randint(10000, 1000000, 长度)
    })
    
    # 确保最高>=最低
    df['最高'] = df[['最高', '开盘', '收盘']].max(axis=1)
    df['最低'] = df[['最低', '开盘', '收盘']].min(axis=1)
    
    return df


def 获取策略信号标注(品种, df_kline, 引擎):
    """从交易记录获取买入/卖出信号标注"""
    买入标注 = []
    卖出标注 = []
    
    if 引擎 and hasattr(引擎, '交易记录') and 引擎.交易记录:
        for 交易 in 引擎.交易记录:
            交易品种 = 交易.get("品种", "")
            
            if 交易品种 != 品种:
                continue
            
            交易时间 = 交易.get("时间")
            交易动作 = 交易.get("动作")
            交易价格 = 交易.get("价格", 0)
            
            if 交易时间 and 交易价格 > 0:
                try:
                    if isinstance(交易时间, str):
                        交易时间_dt = pd.to_datetime(交易时间)
                    else:
                        交易时间_dt = 交易时间
                    
                    for i in range(len(df_kline)):
                        日期 = df_kline['日期'].iloc[i]
                        if abs((日期 - 交易时间_dt).total_seconds()) < 86400 * 3:
                            标注 = {
                                "日期": 日期,
                                "价格": 交易价格
                            }
                            if 交易动作 == "买入":
                                买入标注.append(标注)
                            elif 交易动作 == "卖出":
                                卖出标注.append(标注)
                            break
                except Exception as e:
                    print(f"处理标注失败: {e}")
    
    return 买入标注[-10:], 卖出标注[-10:]


def 绘制K线图(df_kline, 品种名称, 周期名称, 买入标注, 卖出标注):
    """绘制K线图"""
    
    dates = df_kline['日期'].tolist()
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{品种名称} - {周期名称} K线图', '成交量')
    )
    
    # K线图
    fig.add_trace(go.Candlestick(
        x=dates,
        open=df_kline['开盘'],
        high=df_kline['最高'],
        low=df_kline['最低'],
        close=df_kline['收盘'],
        name='K线',
        showlegend=False
    ), row=1, col=1)
    
    # 添加均线
    ma5 = df_kline['收盘'].rolling(window=5).mean()
    ma10 = df_kline['收盘'].rolling(window=10).mean()
    ma20 = df_kline['收盘'].rolling(window=20).mean()
    
    fig.add_trace(go.Scatter(x=dates, y=ma5, mode='lines', name='MA5', line=dict(color='#FF6B6B', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=ma10, mode='lines', name='MA10', line=dict(color='#4ECDC4', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=ma20, mode='lines', name='MA20', line=dict(color='#FFE66D', width=1.5)), row=1, col=1)
    
    # 买入标注
    for 标注 in 买入标注:
        fig.add_annotation(
            x=标注['日期'], y=标注['价格'],
            text="🟢 买入",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#2ECC71",
            ax=0,
            ay=-35,
            font=dict(color="#2ECC71", size=10),
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=2
        )
    
    # 卖出标注
    for 标注 in 卖出标注:
        fig.add_annotation(
            x=标注['日期'], y=标注['价格'],
            text="🔴 卖出",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#E74C3C",
            ax=0,
            ay=35,
            font=dict(color="#E74C3C", size=10),
            bgcolor="rgba(0,0,0,0.6)",
            borderpad=2
        )
    
    # 成交量
    成交量颜色 = ['#2ECC71' if c >= o else '#E74C3C' 
                  for c, o in zip(df_kline['收盘'], df_kline['开盘'])]
    
    fig.add_trace(go.Bar(
        x=dates, y=df_kline['成交量'],
        name='成交量',
        marker_color=成交量颜色,
        opacity=0.5,
        showlegend=False
    ), row=2, col=1)
    
    # 布局
    fig.update_layout(
        title=dict(text=f"{品种名称} - {周期名称} 技术分析图表", x=0.5),
        height=550,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='#0a0c10',
        paper_bgcolor='#0a0c10',
        font_color='#e6e6e6'
    )
    
    fig.update_xaxes(title_text="日期", row=2, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="价格", row=1, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="成交量", row=2, col=1, gridcolor='#2a2e3a')
    
    # 设置x轴角度
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    fig.update_xaxes(tickangle=-45, row=2, col=1)
    
    return fig
