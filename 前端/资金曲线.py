
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    日期列表 = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    资产列表 = [引擎.初始资金 + i * (引擎.获取总资产() - 引擎.初始资金) / 30 for i in range(30)]
    fig = go.Figure(data=go.Scatter(x=日期列表, y=资产列表, mode='lines', line=dict(color='#00d2ff', width=2)))
    fig.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
    st.plotly_chart(fig, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric("当前资产", f"${引擎.获取总资产():,.0f}")
    col2.metric("初始资产", f"${引擎.初始资金:,.0f}")
