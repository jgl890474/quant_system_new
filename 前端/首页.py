# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 核心 import 行情获取

def 显示(引擎):
    # 自定义样式 - 调亮字体
    st.markdown("""
    <style>
    .stMetric label {
        color: #00d2ff !important;
        font-size: 14px !important;
    }
    .stMetric value {
        color: #ffffff !important;
        font-size: 28px !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 紧凑指标布局
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
    
    # 市场行情 - 紧凑
    st.markdown("##### 📊 市场行情")
    
    品种列表 = ["AAPL", "BTC-USD", "GC=F", "EURUSD"]
    行情列 = st.columns(4, gap="small")
    
    for i, 品种 in enumerate(品种列表):
        with 行情列[i]:
            try:
                行情数据 = 行情获取.获取价格(品种)
                价格 = 行情数据.价格
                st.metric(品种, f"${价格:.4f}")
            except:
                st.metric(品种, "—")
    
    # 持仓曲线
    if 引擎.持仓:
        st.markdown("##### 📈 持仓明细")
        
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
            st.dataframe(pd.DataFrame(持仓数据), use_container_width=True, hide_index=True)
            
            # 盈亏柱状图
            df_chart = pd.DataFrame([{
                "品种": d["品种"],
                "盈亏": float(d["盈亏"].replace("$", "").replace("+", ""))
            } for d in 持仓数据])
            
            fig = go.Figure()
            colors = ['#00ff88' if x >= 0 else '#ff4444' for x in df_chart['盈亏']]
            fig.add_trace(go.Bar(x=df_chart['品种'], y=df_chart['盈亏'], marker_color=colors))
            fig.update_layout(height=250, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("暂无持仓，请在策略中心或AI交易中买入")
