# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 获取策略列表
    策略列表 = 策略加载器.获取策略()
    策略名称列表 = [s["名称"] for s in 策略列表]
    
    if not 策略名称列表:
        st.warning("没有找到策略")
        return
    
    # 选择策略
    选中策略 = st.selectbox("选择策略", 策略名称列表)
    策略信息 = 策略加载器.根据名称获取(选中策略)
    
    if 策略信息:
        # 当前行情
        行情数据 = 行情获取.获取价格(策略信息['品种'])
        当前价格 = 行情数据.价格
        st.info(f"📊 {策略信息['品种']} = ${当前价格:.4f}")
        
        # 运行信号
        if st.button("运行策略信号"):
            信号 = 策略运行器.运行(策略信息, 行情数据)
            st.session_state['策略信号'] = 信号
            st.success(f"信号: {信号.upper()}")
            st.rerun()
        
        # AI 分析
        if st.button("AI 分析"):
            with st.spinner("AI分析中..."):
                信号 = st.session_state.get('策略信号', 'hold')
                结果 = AI引擎.分析(策略信息['品种'], 当前价格, 信号)
                st.success(f"AI决策: {结果.get('最终信号', 'hold').upper()}")
                st.info(f"理由: {结果.get('理由', '无')}")
