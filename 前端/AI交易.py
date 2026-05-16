# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场列表
    市场列表 = ["💰 外汇", "₿ 加密货币", "📈 A股", "🇺🇸 美股"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", 市场列表)
    
    with col2:
        策略 = st.selectbox("选择策略", ["综合推荐", "趋势跟踪", "网格交易", "均值回归"])
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if st.button("🔍 AI智能分析", type="primary"):
        st.success(f"✅ AI分析完成 - 市场: {市场}, 策略: {策略}")
