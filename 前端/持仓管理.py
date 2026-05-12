# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from 核心 import 行情获取
from datetime import datetime


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理页面"""
    
    st.markdown("### 💼 当前持仓")
    
    # ========== 持仓显示 ==========
    if 引擎.持仓:
        数据 = []
        持仓列表 = list(引擎.持仓.items())
        
        for 品种, pos in 持仓列表:
            try:
                # 获取实时价格（带容错）
                价格结果 = 行情获取.获取价格(品种)
                
                # 兼容不同的返回格式
                if hasattr(价格结果, '价格'):
                    现价 = float(价格结果.价格)
                elif hasattr(价格结果, 'price'):
                    现价 = float(价格结果.price)
                elif isinstance(价格结果, (int, float)):
                    现价 = float(价格结果)
                else:
                    现价 = float(pos.平均成本)
                
                # 更新持仓当前价格
                pos.当前价格 = 现价
                
                # 计算盈亏
                成本价 = float(pos.平均成本)
                数量 = float(pos.数量)
                盈亏 = 数量 * (现价 - 成本价)
                盈亏率 = (现价 / 成本价 - 1) * 100 if 成本价 > 0 else 0
                
                数据.append({
                    "品种": 品种,
                    "数量": f"{数量:.0f}",
                    "成本": f"{成本价:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%"
                })
            except Exception as e:
                数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本": f"{pos.平均成本:.2f}",
                    "现价": "获取失败",
                    "盈亏": "---",
                    "盈亏率": "---"
                })
        
        if 数据:
            df = pd.DataFrame(数据)
            st.dataframe(df, width='stretch', hide_index=True)
            
            # 显示总盈亏
            总盈亏 = 0.0
            for d in 数据:
                if d["盈亏"] != "---":
                    try:
                        总盈亏 += float(d["盈亏"].replace("¥", "").replace(",", ""))
                    except:
                        pass
            st.caption(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
            
            # ========== K线图表区域 ==========
            st.markdown("---")
            st.markdown("### 📈 品种K线图分析")
            
            # 选择要查看的品种
            品种列表 = [d["品种"] for d in 数据]
            选中品种 = st.selectbox("选择品种查看K线图", 品种列表, key="kline_select")
            
            if 选中品种:
                with st.spinner(f"正在加载 {选中品种} 的K线数据..."):
                    # 周期选择
                    周期选项 = st.selectbox(
                        "选择周期", 
                        ["日线", "周线", "60分钟", "30分钟", "10分钟"], 
                        key="period_select"
                    )
                    
                    if 周期选项 == "日线":
                        周期 = "1d"
                        长度 = 60
                    elif 周期选项 == "周线":
                        周期 = "1wk"
                        长度 = 50
                    elif 周期选项 == "60分钟":
                        周期 = "1h"
                        长度 = 100
                    elif 周期选项 == "30分钟":
                        周期 = "30m"
                        长度 = 120
                    else:  # 10分钟
                        周期 = "10m"
                        长度 = 150
                    
                    # 获取K线数据
                    df_kline = 行情获取.获取K线数据(选中品种, 周期, 长度)
                    
                    if not df_kline.empty:
                        # 计算技术指标
                        df_indicators = 行情获取.计算技术指标(df_kline)
                        
                        # ===== 获取策略信号标注 =====
                        买入标注, 卖出标注 = 获取策略信号标注(
                            选中品种, df_kline, 策略加载器, 引擎
                        )
                        
                        # 创建子图
                        fig = make_subplots(
                            rows=3, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_heights=[0.55, 0.2, 0.25],
                            subplot_titles=(f'{选中品种} - K线图（含策略买卖点）', '成交量', 'MACD')
                        )
                        
                        # K线图
                        fig.add_trace(go.Candlestick(
                            x=df_indicators['日期'],
                            open=df_indicators['开盘'],
                            high=df_indicators['最高'],
                            low=df_indicators['最低'],
                            close=df_indicators['收盘'],
                            name='K线',
                            showlegend=False
                        ), row=1, col=1)
                        
                        # 添加均线
                        if 'MA5' in df_indicators.columns:
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['MA5'],
                                mode='lines',
                                name='MA5',
                                line=dict(color='#FF6B6B', width=1.5)
                            ), row=1, col=1)
                        
                        if 'MA10' in df_indicators.columns:
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['MA10'],
                                mode='lines',
                                name='MA10',
                                line=dict(color='#4ECDC4', width=1.5)
                            ), row=1, col=1)
                        
                        if 'MA20' in df_indicators.columns:
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['MA20'],
                                mode='lines',
                                name='MA20',
                                line=dict(color='#FFE66D', width=1.5)
                            ), row=1, col=1)
                        
                        # 布林带
                        if 'BB_Upper' in df_indicators.columns:
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['BB_Upper'],
                                mode='lines',
                                name='布林上轨',
                                line=dict(color='#95A5A6', width=1, dash='dash'),
                                showlegend=True
                            ), row=1, col=1)
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['BB_Lower'],
                                mode='lines',
                                name='布林下轨',
                                line=dict(color='#95A5A6', width=1, dash='dash'),
                                fill='tonexty',
                                fillcolor='rgba(149,165,166,0.1)',
                                showlegend=True
                            ), row=1, col=1)
                        
                        # ===== 添加策略买入/卖出标注 =====
                        # 买入标注（绿色向上箭头）
                        for 标注 in 买入标注:
                            fig.add_annotation(
                                x=标注['日期'],
                                y=标注['价格'],
                                text="买入",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1.5,
                                arrowwidth=2,
                                arrowcolor="#2ECC71",
                                ax=0,
                                ay=-35,
                                font=dict(color="#2ECC71", size=11, family="Microsoft YaHei"),
                                bgcolor="rgba(0,0,0,0.8)",
                                borderpad=4,
                                borderwidth=1,
                                bordercolor="#2ECC71"
                            )
                            
                            # 添加标记点
                            fig.add_trace(go.Scatter(
                                x=[标注['日期']],
                                y=[标注['价格']],
                                mode='markers',
                                name='买入信号',
                                marker=dict(symbol='triangle-up', size=14, color='#2ECC71', line=dict(width=1, color='white')),
                                showlegend=False,
                                hovertemplate=f"<b>买入信号</b><br>日期: {标注['日期']}<br>价格: {标注['价格']:.2f}<br>策略: {标注.get('策略', '未知')}<extra></extra>"
                            ), row=1, col=1)
                        
                        # 卖出标注（红色向下箭头）
                        for 标注 in 卖出标注:
                            fig.add_annotation(
                                x=标注['日期'],
                                y=标注['价格'],
                                text="卖出",
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1.5,
                                arrowwidth=2,
                                arrowcolor="#E74C3C",
                                ax=0,
                                ay=35,
                                font=dict(color="#E74C3C", size=11, family="Microsoft YaHei"),
                                bgcolor="rgba(0,0,0,0.8)",
                                borderpad=4,
                                borderwidth=1,
                                bordercolor="#E74C3C"
                            )
                            
                            # 添加标记点
                            fig.add_trace(go.Scatter(
                                x=[标注['日期']],
                                y=[标注['价格']],
                                mode='markers',
                                name='卖出信号',
                                marker=dict(symbol='triangle-down', size=14, color='#E74C3C', line=dict(width=1, color='white')),
                                showlegend=False,
                                hovertemplate=f"<b>卖出信号</b><br>日期: {标注['日期']}<br>价格: {标注['价格']:.2f}<br>策略: {标注.get('策略', '未知')}<extra></extra>"
                            ), row=1, col=1)
                        
                        # 成交量图
                        if len(df_indicators) > 0:
                            颜色 = []
                            for i in range(len(df_indicators)):
                                c = df_indicators['收盘'].iloc[i]
                                o = df_indicators['开盘'].iloc[i]
                                if c >= o:
                                    颜色.append('#2ECC71')
                                else:
                                    颜色.append('#E74C3C')
                        else:
                            颜色 = []
                        
                        fig.add_trace(go.Bar(
                            x=df_indicators['日期'],
                            y=df_indicators['成交量'] if '成交量' in df_indicators.columns else [0]*len(df_indicators),
                            name='成交量',
                            marker_color=颜色,
                            opacity=0.5,
                            showlegend=False
                        ), row=2, col=1)
                        
                        # MACD图
                        if 'MACD' in df_indicators.columns:
                            macd_colors = []
                            for x in df_indicators['MACD_Histogram']:
                                if x >= 0:
                                    macd_colors.append('#2ECC71')
                                else:
                                    macd_colors.append('#E74C3C')
                            
                            fig.add_trace(go.Bar(
                                x=df_indicators['日期'],
                                y=df_indicators['MACD_Histogram'],
                                name='MACD柱',
                                marker_color=macd_colors,
                                opacity=0.5,
                                showlegend=False
                            ), row=3, col=1)
                            
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['MACD'],
                                mode='lines',
                                name='MACD',
                                line=dict(color='#3498DB', width=1.5)
                            ), row=3, col=1)
                            
                            fig.add_trace(go.Scatter(
                                x=df_indicators['日期'],
                                y=df_indicators['MACD_Signal'],
                                mode='lines',
                                name='信号线',
                                line=dict(color='#E74C3C', width=1.5)
                            ), row=3, col=1)
                        
                        # 更新布局
                        fig.update_layout(
                            title=f"{选中品种} 技术分析图表",
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
                        
                        st.plotly_chart(fig, width='stretch')
                        
                        # 技术指标摘要
                        with st.expander("📊 技术指标摘要", expanded=False):
                            最新数据 = df_indicators.iloc[-1]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("当前价格", f"¥{最新数据['收盘']:.2f}")
                                if 'MA5' in 最新数据.index:
                                    st.metric("5日均线", f"¥{最新数据['MA5']:.2f}")
                            
                            with col2:
                                if 'MA10' in 最新数据.index:
                                    st.metric("10日均线", f"¥{最新数据['MA10']:.2f}")
                                if 'MA20' in 最新数据.index:
                                    st.metric("20日均线", f"¥{最新数据['MA20']:.2f}")
                            
                            with col3:
                                if 'RSI' in 最新数据.index:
                                    rsi = 最新数据['RSI']
                                    st.metric("RSI", f"{rsi:.1f}")
                                    if rsi > 70:
                                        st.caption("🔴 超买区域")
                                    elif rsi < 30:
                                        st.caption("🟢 超卖区域")
                                    else:
                                        st.caption("🟡 中性区域")
                            
                            with col4:
                                if 'MACD' in 最新数据.index and 'MACD_Signal' in 最新数据.index:
                                    st.metric("MACD", f"{最新数据['MACD']:.4f}")
                                    if 最新数据['MACD'] > 最新数据['MACD_Signal']:
                                        st.caption("🟢 MACD金叉信号")
                                    else:
                                        st.caption("🔴 MACD死叉信号")
                            
                            # 显示策略信号摘要
                            if 买入标注 or 卖出标注:
                                st.markdown("---")
                                st.markdown("**📊 策略信号统计**")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("买入信号", len(买入标注))
                                    if 买入标注:
                                        st.caption(f"最新: {买入标注[-1]['日期'].strftime('%m-%d %H:%M')}")
                                with col_b:
                                    st.metric("卖出信号", len(卖出标注))
                                    if 卖出标注:
                                        st.caption(f"最新: {卖出标注[-1]['日期'].strftime('%m-%d %H:%M')}")
                            else:
                                st.info("当前暂无策略信号，请在策略中心运行策略")
                    else:
                        st.warning(f"无法获取 {选中品种} 的K线数据")
    else:
        st.caption("暂无持仓")
    
    st.markdown("---")
    
    # ========== 止损止盈设置 ==========
    st.markdown("### 🛡️ 止损止盈设置")
    
    # 获取当前风控参数
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
    
    # 参数设置界面
    col1, col2, col3 = st.columns(3)
    with col1:
        止损比例 = st.number_input(
            "止损比例 (%)", 
            min_value=0.5, 
            max_value=20.0, 
            value=当前止损, 
            step=0.5,
            key="stop_loss_input"
        )
    with col2:
        止盈比例 = st.number_input(
            "止盈比例 (%)", 
            min_value=0.5, 
            max_value=50.0, 
            value=当前止盈, 
            step=0.5,
            key="take_profit_input"
        )
    with col3:
        移动止损 = st.checkbox(
            "开启移动止损", 
            value=当前移动止损,
            key="trailing_stop"
        )
    
    # 移动止损回撤设置
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input(
                "移动止损回撤 (%)", 
                min_value=0.5, 
                max_value=10.0, 
                value=当前回撤, 
                step=0.5,
                key="trailing_stop_back"
            )
    
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
    if 引擎.持仓:
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
            st.success("✅ 已执行一键平仓")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ==================== 辅助函数 ====================
def 获取策略信号标注(品种, df_kline, 策略加载器, 引擎):
    """
    根据策略实时计算买入/卖出信号，返回标注列表
    参数:
        品种: 品种代码
        df_kline: K线数据
        策略加载器: 策略加载器实例
        引擎: 订单引擎实例
    返回:
        买入标注: [{"日期": xxx, "价格": xxx, "策略": xxx}, ...]
        卖出标注: [{"日期": xxx, "价格": xxx, "策略": xxx}, ...]
    """
    买入标注 = []
    卖出标注 = []
    
    if 策略加载器 is None:
        print("策略加载器为空，无法获取策略信号")
        return 买入标注, 卖出标注
    
    try:
        # 获取所有策略
        策略列表 = 策略加载器.获取策略()
        
        if not 策略列表:
            print("策略列表为空")
            return 买入标注, 卖出标注
        
        print(f"找到 {len(策略列表)} 个策略")
        
        # 简化品种代码用于匹配
        简化品种 = 品种
        if 品种.endswith('.SS') or 品种.endswith('.SZ'):
            简化品种 = 品种[:-3]
        
        # 导入策略运行器
        try:
            from 核心.策略运行器 import 策略运行器
        except ImportError:
            print("策略运行器导入失败")
            return 买入标注, 卖出标注
        
        for 策略 in 策略列表:
            策略品种 = 策略.get("品种", "")
            # 只处理匹配当前品种的策略
            if 策略品种 != 品种 and 策略品种 != 简化品种:
                continue
            
            策略名称 = 策略.get("名称", "未知")
            print(f"匹配到策略: {策略名称} -> 品种: {品种}")
            
            # 为每个K线点计算策略信号
            for i in range(len(df_kline)):
                当前日期 = df_kline['日期'].iloc[i]
                当前价格 = df_kline['收盘'].iloc[i]
                
                # 构建行情数据对象
                class 行情对象:
                    pass
                行情对象.价格 = 当前价格
                
                try:
                    信号 = 策略运行器.运行(策略, 行情对象)
                    
                    if 信号 == "buy":
                        买入标注.append({
                            "日期": 当前日期,
                            "价格": 当前价格,
                            "策略": 策略名称
                        })
                        print(f"买入信号: {当前日期} {当前价格}")
                    elif 信号 == "sell":
                        卖出标注.append({
                            "日期": 当前日期,
                            "价格": 当前价格,
                            "策略": 策略名称
                        })
                        print(f"卖出信号: {当前日期} {当前价格}")
                except Exception as e:
                    print(f"策略运行失败: {e}")
    
    except Exception as e:
        print(f"获取策略信号失败: {e}")
    
    # 去重
    买入标注_去重 = []
    卖出标注_去重 = []
    买入日期集合 = set()
    卖出日期集合 = set()
    
    for 标注 in 买入标注:
        日期_str = 标注["日期"].strftime("%Y-%m-%d %H:%M")
        if 日期_str not in 买入日期集合:
            买入日期集合.add(日期_str)
            买入标注_去重.append(标注)
    
    for 标注 in 卖出标注:
        日期_str = 标注["日期"].strftime("%Y-%m-%d %H:%M")
        if 日期_str not in 卖出日期集合:
            卖出日期集合.add(日期_str)
            卖出标注_去重.append(标注)
    
    print(f"最终信号: 买入{len(买入标注_去重)}个, 卖出{len(卖出标注_去重)}个")
    
    # 只保留最近的15个信号
    return 买入标注_去重[-15:], 卖出标注_去重[-15:]
