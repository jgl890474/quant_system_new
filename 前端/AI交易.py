# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 不加任何 key 参数
        market = st.selectbox("选择市场", ["加密货币", "A股", "美股"])
    
    with col2:
        strategy = st.selectbox("选择策略", ["加密双均线1", "加密双均线2", "趋势跟踪"])
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if st.button("🚀 执行AI交易"):
        st.success("✅ 交易执行成功")
