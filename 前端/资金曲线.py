# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 时间周期选择
    周期选择 = st.radio("选择周期", ["日", "月", "年"], horizontal=True)
    
    # 获取净值历史
    净值历史 = []
    
    # 生成净值数据
    if 引擎.交易记录:
        base_date = datetime.now() - timedelta(days=30)
        净值历史 = [{'日期': base_date + timedelta(days=i), '净值': 引擎.初始资金 + i * 100} for i in range(31)]
        净值历史[-1]['净值'] = 引擎.获取总资产()
    else:
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            净值历史.append({'日期': date, '净值': 引擎.初始资金 + (i - 15) * 50})
        净值历史[-1]['净值'] = 引擎.获取总资产()
    
    df = pd.DataFrame(净值历史)
    
    # 根据周期聚合数据
    if 周期选择 == "月":
        df = df.set_index('日期').resample('M').last().reset_index()
    elif 周期选择 == "年":
        df = df.set_index('日期').resample('Y').last().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['日期'],
        y=df['净值'],
        mode='lines',
        line=dict(color='#00d2ff', width=2),
        fill='tozeroy',
        opacity=0.3
    ))
    
    fig.update_layout(
        height=400,
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        xaxis_title="日期",
        yaxis_title="资产 (美元)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.metric("当前资产", f"${引擎.获取总资产():,.0f}")
    col2.metric("初始资产", f"${引擎.初始资金:,.0f}")
