# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from 核心 import 行情获取

def 显示(引擎):
    # 自定义样式
    st.markdown("""
    <style>
    .stMetric label { color: #00d2ff !important; font-size: 14px !important; }
    .stMetric value { color: #ffffff !important; font-size: 28px !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
    try:
        总资产 = 引擎.获取总资产()
    except:
        总资产 = 引擎.初始资金
    
    try:
        总盈亏 = 引擎.获取总盈亏()
    except:
        总盈亏 = 0
    
    col1.metric("总资产", f"${总资产:,.0f}")
    col2.metric("总盈亏", f"${总盈亏:+,.0f}", delta_color="normal")
    col3.metric("持仓数", f"{len(引擎.持仓)}")
    col4.metric("交易次数", f"{len(引擎.交易记录)}")
    
    # 市场行情
    st.markdown("##### 📊 市场行情")
    
    品种列表 = ["AAPL", "BTC-USD", "GC=F", "EURUSD=X"]
    行情列 = st.columns(4, gap="small")
    
    for i, 品种 in enumerate(品种列表):
        with 行情列[i]:
            try:
                行情数据 = 行情获取.获取价格(品种)
                价格 = 行情数据.价格
                st.metric(品种, f"${价格:.4f}")
            except Exception as e:
                st.metric(品种, "—")
    
    # ========== 持仓分析 ==========
    if 引擎.持仓:
        st.markdown("##### 📈 持仓分析")
        
        # 准备持仓数据
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                现价 = 行情获取.获取价格(品种).价格
                盈亏 = (现价 - pos.平均成本) * pos.数量
                盈亏率 = (现价 - pos.平均成本) / pos.平均成本 * 100
                市值 = 现价 * pos.数量
                持仓数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本价": f"{pos.平均成本:.4f}",
                    "现价": f"{现价:.4f}",
                    "市值": f"${市值:,.0f}",
                    "盈亏": f"${盈亏:+.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%"
                })
            except:
                pass
        
        if 持仓数据:
            # 显示表格
            st.dataframe(pd.DataFrame(持仓数据), use_container_width=True, hide_index=True)
            
            # 盈亏柱状图
            df_chart = pd.DataFrame([{
                "品种": d["品种"],
                "盈亏": float(d["盈亏"].replace("$", "").replace("+", ""))
            } for d in 持仓数据])
            
            if not df_chart.empty:
                colors = ['#00ff88' if x >= 0 else '#ff4444' for x in df_chart['盈亏']]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=df_chart['品种'], 
                    y=df_chart['盈亏'],
                    marker_color=colors,
                    text=df_chart['盈亏'].apply(lambda x: f"${x:+.2f}"),
                    textposition='outside'
                ))
                fig_bar.update_layout(
                    height=300,
                    title="持仓盈亏分布",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 市值占比饼图
                df_pie = pd.DataFrame([{
                    "品种": d["品种"],
                    "市值": float(d["市值"].replace("$", "").replace(",", ""))
                } for d in 持仓数据])
                
                if not df_pie.empty:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=df_pie['品种'],
                        values=df_pie['市值'],
                        hole=0.4,
                        marker=dict(colors=['#00d2ff', '#ffaa00', '#00ff88', '#ff6600'])
                    )])
                    fig_pie.update_layout(
                        height=300,
                        title="持仓市值占比",
                        paper_bgcolor="#0a0c10",
                        plot_bgcolor="#15171a",
                        font_color="#e6e6e6"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
    
    # ========== 新增：K线图区域 ==========
    st.markdown("##### 📉 实时K线图")
    
    # 选择查看的品种
    if 引擎.持仓:
        可选品种 = list(引擎.持仓.keys()) + ["AAPL", "BTC-USD", "GC=F", "EURUSD=X"]
    else:
        可选品种 = ["AAPL", "BTC-USD", "GC=F", "EURUSD=X"]
    
    k线品种 = st.selectbox("选择品种查看K线", 可选品种, key="kline_select")
    
    # K线周期选择
    k线周期 = st.selectbox("K线周期", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
    
    with st.spinner("加载K线数据..."):
        try:
            # 获取K线数据
            代码映射 = {
                "EURUSD=X": "EURUSD=X",
                "BTC-USD": "BTC-USD",
                "GC=F": "GC=F",
                "AAPL": "AAPL"
            }
            股票代码 = 代码映射.get(k线品种, k线品种)
            
            # 计算日期范围
            if k线周期 == "1d":
                获取周期 = "1d"
            elif k线周期 == "5d":
                获取周期 = "5d"
            elif k线周期 == "1mo":
                获取周期 = "1mo"
            elif k线周期 == "3mo":
                获取周期 = "3mo"
            elif k线周期 == "6mo":
                获取周期 = "6mo"
            else:
                获取周期 = "1y"
            
            # 获取真实K线数据
            股票 = yf.Ticker(股票代码)
            历史数据 = 股票.history(period=获取周期)
            
            if not 历史数据.empty:
                # 创建K线图
                fig_k线 = go.Figure(data=[go.Candlestick(
                    x=历史数据.index,
                    open=历史数据['Open'],
                    high=历史数据['High'],
                    low=历史数据['Low'],
                    close=历史数据['Close'],
                    name='K线'
                )])
                
                # 添加成交量
                fig_k线.add_trace(go.Bar(
                    x=历史数据.index,
                    y=历史数据['Volume'],
                    name='成交量',
                    marker_color='rgba(0,210,255,0.3)',
                    yaxis='y2'
                ))
                
                # 添加均线
                历史数据['MA5'] = 历史数据['Close'].rolling(window=5).mean()
                历史数据['MA20'] = 历史数据['Close'].rolling(window=20).mean()
                历史数据['MA60'] = 历史数据['Close'].rolling(window=60).mean()
                
                fig_k线.add_trace(go.Scatter(
                    x=历史数据.index,
                    y=历史数据['MA5'],
                    mode='lines',
                    name='MA5',
                    line=dict(color='#ffaa00', width=1)
                ))
                fig_k线.add_trace(go.Scatter(
                    x=历史数据.index,
                    y=历史数据['MA20'],
                    mode='lines',
                    name='MA20',
                    line=dict(color='#00ff88', width=1)
                ))
                fig_k线.add_trace(go.Scatter(
                    x=历史数据.index,
                    y=历史数据['MA60'],
                    mode='lines',
                    name='MA60',
                    line=dict(color='#ff4444', width=1)
                ))
                
                # 布局设置
                fig_k线.update_layout(
                    title=f"{k线品种} K线图 ({获取周期})",
                    height=500,
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="价格 (美元)",
                    yaxis2=dict(
                        title="成交量",
                        overlaying='y',
                        side='right',
                        showgrid=False
                    ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_k线, use_container_width=True)
                
                # 显示当前价格和涨跌幅
                最新收盘 = 历史数据['Close'].iloc[-1]
                前日收盘 = 历史数据['Close'].iloc[-2] if len(历史数据) > 1 else 最新收盘
                涨跌额 = 最新收盘 - 前日收盘
                涨跌幅 = (涨跌额 / 前日收盘) * 100 if 前日收盘 != 0 else 0
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("最新价", f"${最新收盘:.4f}", delta=f"{涨跌额:+.4f}")
                col_b.metric("涨跌幅", f"{涨跌幅:+.2f}%", delta_color="normal")
                col_c.metric("数据范围", f"{历史数据.index[0].strftime('%Y-%m-%d')} - {历史数据.index[-1].strftime('%Y-%m-%d')}")
                
                # 技术指标摘要
                with st.expander("📊 技术指标"):
                    最新MA5 = 历史数据['MA5'].iloc[-1] if not pd.isna(历史数据['MA5'].iloc[-1]) else 0
                    最新MA20 = 历史数据['MA20'].iloc[-1] if not pd.isna(历史数据['MA20'].iloc[-1]) else 0
                    最新MA60 = 历史数据['MA60'].iloc[-1] if not pd.isna(历史数据['MA60'].iloc[-1]) else 0
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("MA5", f"${最新MA5:.4f}")
                    col_m2.metric("MA20", f"${最新MA20:.4f}")
                    col_m3.metric("MA60", f"${最新MA60:.4f}")
                    
                    趋势 = "📈 上涨趋势" if 最新MA5 > 最新MA20 > 最新MA60 else "📉 下跌趋势" if 最新MA5 < 最新MA20 < 最新MA60 else "🔄 震荡整理"
                    st.info(f"趋势判断: {趋势}")
                    
            else:
                st.warning(f"无法获取 {k线品种} 的K线数据")
                
        except Exception as e:
            st.warning(f"获取K线数据失败: {str(e)}")
            st.info("提示：请选择其他品种或稍后重试")
    
    # 持仓走势（基于真实数据）
    if 引擎.持仓:
        st.markdown("##### 📉 持仓走势分析")
        
        # 为每个持仓生成基于真实数据的走势图
        fig_持仓 = go.Figure()
        
        for 品种, pos in 引擎.持仓.items():
            try:
                # 获取该品种的历史数据
                股票代码 = 代码映射.get(品种, 品种)
                股票 = yf.Ticker(股票代码)
                历史数据 = 股票.history(period="1mo")
                
                if not 历史数据.empty:
                    历史价格 = 历史数据['Close'].values
                    成本价 = pos.平均成本
                    # 计算持仓盈亏走势
                    盈亏走势 = (历史价格 - 成本价) * pos.数量
                    
                    fig_持仓.add_trace(go.Scatter(
                        x=历史数据.index,
                        y=盈亏走势,
                        mode='lines',
                        name=品种,
                        line=dict(width=2)
                    ))
            except:
                pass
        
        if fig_持仓.data:
            fig_持仓.update_layout(
                height=350,
                title="持仓盈亏走势 (基于真实历史数据)",
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="日期",
                yaxis_title="盈亏 (美元)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            st.plotly_chart(fig_持仓, use_container_width=True)
