
# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI智能交易")
    策略列表 = 策略加载器.获取策略()
    策略名称列表 = [s["名称"] for s in 策略列表]
    if 策略名称列表:
        选中策略 = st.selectbox("选择策略", 策略名称列表)
        if st.button("🚀 AI分析并执行", type="primary", use_container_width=True):
            策略信息 = 策略加载器.根据名称获取(选中策略)
            if 策略信息:
                行情数据 = 行情获取.获取价格(策略信息['品种'])
                策略信号 = 策略运行器.运行(策略信息, 行情数据)
                st.info(f"📊 策略信号: {策略信号.upper()}")
                结果 = AI引擎.分析(策略信息['品种'], 行情数据.价格, 策略信号)
                st.success(f"🤖 AI决策: {结果['最终信号'].upper()}")
                if 结果['最终信号'] == 'buy':
                    if st.button("确认执行买入"):
                        引擎.买入(策略信息['品种'], 行情数据.价格)
                        st.rerun()
                elif 结果['最终信号'] == 'sell':
                    if st.button("确认执行卖出"):
                        引擎.卖出(策略信息['品种'], 行情数据.价格)
                        st.rerun()
