# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 📋 策略库")
    
    策略列表 = 策略加载器.获取策略()
    
    if not 策略列表:
        st.info("暂无策略")
        return
    
    for idx, 策略 in enumerate(策略列表):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{策略['名称']}**")
            with col2:
                st.markdown(f"`{策略['类别']}`")
            with col3:
                st.markdown(f"📈 +8.2%")
            with col4:
                st.markdown(f"📉 -12.5%")
            with col5:
                if st.button("运行", key=f"run_{idx}"):
                    行情数据 = 行情获取.获取价格(策略['品种'])
                    信号 = 策略运行器.运行(策略, 行情数据)
                    策略信号[策略['名称']] = 信号
                    st.success(f"信号: {信号.upper()}")
                    st.rerun()
            
            if 策略['名称'] in 策略信号:
                信号 = 策略信号[策略['名称']]
                if 信号 == "buy":
                    if st.button("执行买入", key=f"buy_{idx}"):
                        引擎.买入(策略['品种'], 行情获取.获取价格(策略['品种']).价格)
                        st.rerun()
                elif 信号 == "sell":
                    if st.button("执行卖出", key=f"sell_{idx}"):
                        引擎.卖出(策略['品种'], 行情获取.获取价格(策略['品种']).价格)
                        st.rerun()
                else:
                    st.caption(f"信号: {信号.upper()}")
            st.divider()
