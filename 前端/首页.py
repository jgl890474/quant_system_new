# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取

def 显示(引擎):
    # 计算资金指标
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓市值 = 引擎.获取持仓市值()
    可用资金 = 引擎.获取可用资金()
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{(总盈亏/引擎.初始资金)*100:.1f}%")
    
    # 实时行情
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
    
    # 快捷交易
    st.markdown("### 🚀 快捷交易")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 买入")
        买入品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA"], key="buy")
        买入数量 = st.number_input("数量", min_value=1, value=30, step=10, key="buy_qty")
        if st.button("买入", type="primary", use_container_width=True):
            try:
                价格 = 行情获取.获取价格(买入品种).价格
                引擎.买入(买入品种, 价格, 买入数量)
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    with col2:
        st.markdown("#### 卖出")
        卖品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA"], key="sell")
        卖出数量 = st.number_input("数量", min_value=1, value=30, step=10, key="sell_qty")
        if st.button("卖出", use_container_width=True):
            try:
                价格 = 行情获取.获取价格(卖品种).价格
                引擎.卖出(卖品种, 价格, 卖出数量)
            except Exception as e:
                st.error(f"卖出失败: {e}")
