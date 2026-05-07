# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 获取数据
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓市值 = 引擎.获取持仓市值()
    可用资金 = 引擎.获取可用资金()
    
    # 紧凑指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{总盈亏/引擎.初始资金*100:.1f}%")
    
    # 获取历史数据
    历史资金 = 数据库.获取资金曲线(90)
    
    if not 历史资金.empty:
        # 资产曲线 - 细线
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总资产'],
            mode='lines',
            name='总资产',
            line=dict(color='#3b82f6', width=1.5),
            fill='tozeroy',
            opacity=0.2
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6",
            xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#2a2e3a'),
            yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#2a2e3a')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 盈亏曲线 - 不同颜色
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总盈亏'],
            mode='lines',
            name='累计盈亏',
            line=dict(color='#10b981', width=1.5),
            fill='tozeroy',
            opacity=0.2
        ))
        fig2.update_layout(
            height=250,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.caption("暂无历史数据")
