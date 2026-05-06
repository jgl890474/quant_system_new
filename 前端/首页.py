# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 核心 import 行情获取

def 显示(引擎):
    # 顶部指标
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        总资产 = 引擎.获取总资产()
    except:
        总资产 = 引擎.初始资金
    
    try:
        总盈亏 = 引擎.获取总盈亏()
    except:
        总盈亏 = 0
    
    col1.metric("总资产", f"${总资产:,.0f}")
    col2.metric("总盈亏", f"${总盈亏:+,.0f}")
    col3.metric("持仓数", f"{len(引擎.持仓)}")
    col4.metric("交易次数", f"{len(引擎.交易记录)}")
    
    # 市场行情
    st.markdown("### 📊 市场行情")
    
    品种列表 = ["AAPL", "BTC-USD", "GC=F", "EURUSD"]
    行情列 = st.columns(4)
    
    for i, 品种 in enumerate(品种列表):
        try:
            行情数据 = 行情获取.获取价格(品种)
            价格 = 行情数据.价格
            行情列[i].metric(品种, f"${价格:.4f}")
        except:
            行情列[i].metric(品种, "获取失败")
    
    # 持仓曲线图
    if 引擎.持仓:
        st.markdown("### 📈 持仓盈亏")
        
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                现价 = 行情获取.获取价格(品种).价格
                盈亏 = (现价 - pos.平均成本) * pos.数量
                持仓数据.append({
                    "品种": 品种,
                    "数量": pos.数量,
                    "成本": pos.平均成本,
                    "现价": 现价,
                    "盈亏": 盈亏
                })
            except:
                pass
        
        if 持仓数据:
            df = pd.DataFrame(持仓数据)
            st.dataframe(df, use_container_width=True)
            
            # 盈亏柱状图
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['品种'],
                y=df['盈亏'],
                marker_color=['green' if x > 0 else 'red' for x in df['盈亏']]
            ))
            fig.update_layout(
                height=300,
                title="持仓盈亏",
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无持仓")
