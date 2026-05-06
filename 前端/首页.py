# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
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
    
    # ========== 持仓图表 ==========
    if 引擎.持仓:
        st.markdown("##### 📈 持仓分析")
        
        # 准备持仓数据
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                现价 = 行情获取.获取价格(品种).价格
                盈亏 = (现价 - pos.平均成本) * pos.数量
                盈亏率 = (现价 - pos.平均成本) / pos.平均成本 * 100
                持仓数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本": f"{pos.平均成本:.4f}",
                    "现价": f"{现价:.4f}",
                    "盈亏": f"${盈亏:+.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%"
                })
            except:
                pass
        
        if 持仓数据:
            # 显示表格
            st.dataframe(pd.DataFrame(持仓数据), use_container_width=True, hide_index=True)
            
            # 创建盈亏柱状图
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
                    font_color="#e6e6e6",
                    xaxis_title="品种",
                    yaxis_title="盈亏 (美元)"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 创建持仓占比饼图
                df_pie = pd.DataFrame([{
                    "品种": d["品种"],
                    "市值": float(d["现价"]) * float(d["数量"])
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
                
                # 模拟持仓走势曲线（基于持仓盈亏变化）
                st.markdown("##### 📉 持仓走势模拟")
                
                # 生成模拟的历史盈亏曲线
                日期 = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
                
                fig_line = go.Figure()
                for d in 持仓数据:
                    # 为每个持仓生成模拟走势
                    品种 = d["品种"]
                    当前盈亏 = float(d["盈亏"].replace("$", "").replace("+", ""))
                    # 生成从负到正的模拟曲线
                    历史盈亏 = [当前盈亏 * (0.3 + 0.7 * i / 30) for i in range(30)]
                    fig_line.add_trace(go.Scatter(
                        x=日期,
                        y=历史盈亏,
                        mode='lines',
                        name=品种,
                        line=dict(width=2)
                    ))
                
                fig_line.update_layout(
                    height=350,
                    title="持仓盈亏历史（模拟）",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="盈亏 (美元)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_line, use_container_width=True)
                
        else:
            st.info("暂无持仓数据")
    else:
        st.info("ℹ️ 暂无持仓，请在策略中心或AI交易中买入")
