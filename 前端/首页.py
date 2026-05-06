# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
from 核心 import 行情获取

def 显示(引擎):
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        总资产 = 引擎.获取总资产()
        总盈亏 = 引擎.获取总盈亏()
    except:
        总资产 = 100000
        总盈亏 = 0
    
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}", delta=f"{总盈亏/总资产*100:.1f}%")
    with col2:
        st.metric("可用资金", f"¥{总资产 - sum(p.数量 * 行情获取.获取价格(s).价格 for s,p in 引擎.持仓.items()):,.0f}")
    with col3:
        持仓市值 = sum(p.数量 * 行情获取.获取价格(s).价格 for s,p in 引擎.持仓.items())
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("今日盈亏", f"¥{总盈亏:+,.0f}")
    
    # 实时行情滚动条
    st.markdown("### 📈 实时行情")
    行情品种 = ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA"]
    行情列 = st.columns(len(行情品种))
    for i, 品种 in enumerate(行情品种):
        with 行情列[i]:
            try:
                价格 = 行情获取.获取价格(品种).价格
                st.metric(品种, f"${价格:.2f}")
            except:
                st.metric(品种, "—")
    
    # 快捷买卖
    st.markdown("### 🚀 快捷交易")
    col1, col2 = st.columns(2)
    with col1:
        买入品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD"], key="buy")
        if st.button("买入", type="primary", use_container_width=True):
            价格 = 行情获取.获取价格(买入品种).价格
            引擎.买入(买入品种, 价格)
            st.rerun()
    with col2:
        卖品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD"], key="sell")
        if st.button("卖出", use_container_width=True):
            价格 = 行情获取.获取价格(卖品种).价格
            引擎.卖出(卖品种, 价格)
            st.rerun()
