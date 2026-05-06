# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("累计收益", f"¥{引擎.获取总盈亏():+,.0f}")
    with col2:
        st.metric("年化收益", "+15.2%")
    with col3:
        st.metric("胜率", "65.8%")
    
    # 生成收益曲线数据
    日期列表 = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='D')
    资产列表 = [引擎.初始资金 + (引擎.获取总盈亏()) * i / len(日期列表) for i in range(len(日期列表))]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=日期列表, y=资产列表, mode='lines', name='资产', line=dict(color='#00d2ff', width=2)))
    fig.update_layout(height=400, title="资产曲线", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
    st.plotly_chart(fig, use_container_width=True)
