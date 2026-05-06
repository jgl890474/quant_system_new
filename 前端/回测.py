# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def 显示():
    st.markdown("### ⚙️ 回测参数设置")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col2:
        结束日期 = st.date_input("结束日期", datetime.now())
    with col3:
        初始资金 = st.number_input("初始资金", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测中..."):
            # 模拟结果
            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("总收益率", "+15.2%")
            col_b.metric("年化收益", "+18.5%")
            col_c.metric("最大回撤", "-8.3%")
            col_d.metric("夏普比率", "1.25")
            st.success("✅ 回测完成")
