# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from 核心 import 行情获取

def 显示(引擎):
    col1, col2, col3, col4 = st.columns(4)
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    col1.metric("总资产", f"${总资产:,.0f}")
    col2.metric("总盈亏", f"${总盈亏:+,.0f}")
    col3.metric("持仓数", f"{len(引擎.持仓)}")
    col4.metric("交易次数", f"{len(引擎.交易记录)}")
    
    st.markdown("### 市场行情")
    
    try:
        品种列表 = ["AAPL", "BTC-USD", "GC=F", "EURUSD"]
        行情列 = st.columns(4)
        for i, 品种 in enumerate(品种列表):
            行情数据 = 行情获取.获取价格(品种)
            价格 = 行情数据.价格
            涨跌 = 行情数据.涨跌 if hasattr(行情数据, '涨跌') else 0
            delta = f"{涨跌:+.2f}%" if 涨跌 != 0 else None
            行情列[i].metric(品种, f"${价格:.4f}", delta=delta)
    except Exception as e:
        st.error(f"获取行情失败: {e}")
    
    # ========== 新增：持仓实时图表 ==========
    if 引擎.持仓:
        st.markdown("### 📊 持仓实时盈亏")
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            现价 = 行情获取.获取价格(品种).价格
            盈亏 = (现价 - pos.平均成本) * pos.数量
            持仓数据.append({
                "品种": 品种,
                "数量": pos.数量,
                "成本": pos.平均成本,
                "现价": 现价,
                "盈亏": 盈亏,
                "盈亏率": (现价 - pos.平均成本) / pos.平均成本 * 100
            })
        
        df = pd.DataFrame(持仓数据)
        fig = go.Figure(data=[
            go.Bar(name='盈亏', x=df['品种'], y=df['盈亏'], 
                   marker_color=['green' if x > 0 else 'red' for x in df['盈亏']])
        ])
        fig.update_layout(title="持仓盈亏分布", height=400, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
        st.plotly_chart(fig, use_container_width=True)
