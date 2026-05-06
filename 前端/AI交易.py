# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    st.markdown("AI 会综合分析行情和策略信号，给出交易建议")
    
    # ========== 添加强制买入测试按钮 ==========
    st.markdown("---")
    st.markdown("### 🧪 强制买入测试区")
    
    col_test1, col_test2 = st.columns(2)
    with col_test1:
        if st.button("🔴 强制买入 AAPL", type="primary", use_container_width=True):
            价格 = 行情获取.获取价格("AAPL").价格
            st.success(f"当前价格: {价格}")
            引擎.买入("AAPL", 价格)
            st.rerun()
    
    with col_test2:
        if st.button("🟢 查看持仓", use_container_width=True):
            if 引擎.持仓:
                for 品种, 持仓 in 引擎.持仓.items():
                    st.write(f"{品种}: {持仓.数量} 股, 成本: {持仓.平均成本}")
            else:
                st.info("暂无持仓")
    
    st.markdown("---")
    # ========== 测试区结束 ==========
    
    st.markdown("### 📊 正常AI交易区")
    
    策略列表 = 策略加载器.获取策略()
    策略名称列表 = [s["名称"] for s in 策略列表]
    
    if not 策略名称列表:
        st.warning("没有找到策略，请检查策略库")
        return
    
    选中策略 = st.selectbox("选择策略", 策略名称列表)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 AI 分析并执行", type="primary", use_container_width=True):
            with st.spinner("AI 正在分析中..."):
                策略信息 = 策略加载器.根据名称获取(选中策略)
                if 策略信息:
                    行情数据 = 行情获取.获取价格(策略信息['品种'])
                    策略信号 = 策略运行器.运行(策略信息, 行情数据)
                    
                    st.info(f"📊 策略信号: {策略信号.upper()}")
                    
                    结果 = AI引擎.分析(策略信息['品种'], 行情数据.价格, 策略信号)
                    
                    st.success(f"🤖 AI 决策: **{结果['最终信号'].upper()}**")
                    st.info(f"📝 置信度: {结果['置信度']}%")
                    st.write(f"💡 理由: {结果['理由']}")
                    
                    if 结果['最终信号'] == 'buy':
                        if st.button("✅ 确认执行买入"):
                            引擎.买入(策略信息['品种'], 行情数据.价格)
                            st.rerun()
                    elif 结果['最终信号'] == 'sell':
                        if st.button("✅ 确认执行卖出"):
                            引擎.卖出(策略信息['品种'], 行情数据.价格)
                            st.rerun()
                    
                    # 保存到 session
                    st.session_state['AI结果'] = 结果
                    
    with col2:
        if st.button("📜 查看分析历史", use_container_width=True):
            if 'AI结果' in st.session_state:
                st.write(st.session_state['AI结果'])
            else:
                st.info("暂无分析记录")
