# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", ["加密货币", "A股", "美股"])
    
    with col2:
        策略 = st.selectbox("选择策略", ["趋势跟踪", "网格交易", "均值回归"])
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if st.button("🚀 执行AI交易"):
        st.success("✅ AI交易执行成功")
        st.balloons()
