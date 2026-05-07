# -*- coding: utf-8 -*-
import streamlit as st

def 显示():
    st.markdown("### 📈 策略回测系统")
    st.info("回测功能正在开发中，敬请期待...")
    
    # 简单的参数设置
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F"])
    with col2:
        周期 = st.selectbox("周期", ["1d", "1w", "1m"])
    
    初始资金 = st.number_input("初始资金", value=100000, step=10000)
    
    if st.button("开始回测", type="primary"):
        st.success(f"回测完成！\n品种: {品种}, 周期: {周期}, 初始资金: {初始资金}")
