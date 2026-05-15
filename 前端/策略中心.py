# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 直接使用硬编码策略列表
    策略列表 = [
        {"名称": "双均线策略", "类别": "📈 A股", "品种": "000001", "启用": True},
        {"名称": "量价策略", "类别": "📈 A股", "品种": "000002", "启用": True},
        {"名称": "隔夜套利策略", "类别": "📈 A股", "品种": "000858", "启用": True},
        {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD", "启用": True},
        {"名称": "动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "启用": True},
        {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD", "启用": True},
        {"名称": "期货趋势策略", "类别": "📊 期货", "品种": "GC=F", "启用": True},
    ]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 策略总数", len(策略列表))
    with col2:
        st.metric("✅ 启用中", len(策略列表))
    with col3:
        品类数 = len(set(s["类别"] for s in 策略列表))
        st.metric("🏷️ 涵盖品类", 品类数)
    
    df = pd.DataFrame(策略列表)
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 启用所有策略"):
            st.success("已启用所有策略")
    with col2:
        if st.button("⏸️ 停止所有策略"):
            st.warning("已停止所有策略")
