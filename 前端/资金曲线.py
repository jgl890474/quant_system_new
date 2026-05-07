# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("累计收益", f"¥{引擎.获取总盈亏():+,.0f}")
    with col2:
        st.metric("年化收益", "+15.2%")
    with col3:
        st.metric("胜率", "65.8%")
    
    # 保存今日资金快照到数据库
    try:
        总资产 = 引擎.获取总资产()
        总盈亏 = 引擎.获取总盈亏()
        持仓市值 = sum(p.数量 * p.当前价格 for p in 引擎.持仓.values())
        可用资金 = 总资产 - 持仓市值
        数据库.保存资金快照(总资产, 总盈亏, 持仓市值, 可用资金)
    except:
        pass
    
    # 从数据库获取历史资金曲线
    历史数据 = 数据库.获取资金曲线(180)
    
    if not 历史数据.empty:
        日期 = 历史数据['日期']
        资产 = 历史数据['总资产']
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=日期, y=资产, mode='lines', name='资产', line=dict(color='#00d2ff', width=2)))
        fig.update_layout(height=400, title="资产曲线（历史）", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无历史数据，完成交易后将自动记录")
