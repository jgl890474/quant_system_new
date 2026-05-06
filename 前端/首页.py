# -*- coding: utf-8 -*-
import streamlit as st
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
            行情列[i].markdown(f'<div style="background:#1a1d24;border-radius:8px;padding:10px;text-align:center"><b>{品种}</b><br><span style="color:#00d2ff;font-size:18px">{价格:.4f}</span></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"获取行情失败: {e}")
