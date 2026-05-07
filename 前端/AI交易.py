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
    
    if not 策略信息:
        st.warning("策略信息获取失败")
        return
    
    # 行情
    行情数据 = 行情获取.获取价格(策略信息['品种'])
    当前价格 = 行情数据.价格
    st.info(f"📊 {策略信息['品种']} = ${当前价格:.4f}")
    
    # 运行信号
    if st.button("🎯 运行策略信号", use_container_width=True):
        信号 = 策略运行器.运行(策略信息, 行情数据)
        st.session_state['my_signal'] = 信号
        st.success(f"信号: {信号}")
        st.rerun()
    
    # 显示信号（安全方式）
    当前信号 = st.session_state.get('my_signal', '')
    if 当前信号:
        st.markdown(f"### 策略信号: **{当前信号.upper()}**")
    
    # AI 分析
    st.markdown("---")
    if st.button("🧠 AI 分析", type="primary", use_container_width=True):
        with st.spinner("分析中..."):
            信号 = st.session_state.get('my_signal', 'hold')
            结果 = AI引擎.分析(策略信息['品种'], 当前价格, 信号)
            st.success(f"AI 决策: {结果.get('最终信号', 'hold')}")
            st.info(f"理由: {结果.get('理由', '无')}")
            st.session_state['ai_result'] = 结果
    
    # 显示 AI 结果
    if st.session_state.get('ai_result'):
        st.json(st.session_state['ai_result'])
    
    # 强制买入
    st.markdown("---")
    if st.button("🔴 强制买入 AAPL", use_container_width=True):
        引擎.买入("AAPL", 行情获取.获取价格("AAPL").价格, 100)
        st.rerun()
