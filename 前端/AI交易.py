# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 交易信号")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📈 **AI预测: 看涨**\n\n置信度: 85%")
    with col2:
        st.warning("📊 **建议仓位: 30%**\n\n可配置资金: ¥300,000")
    with col3:
        st.error("⚠️ **风险等级: 中风险**\n\n建议止损: -5%")
    
    st.markdown("### 📝 AI 决策日志")
    日志数据 = [
        {"时间": "09:30", "品种": "AAPL", "信号": "BUY", "置信度": "85%"},
        {"时间": "10:15", "品种": "BTC", "信号": "HOLD", "置信度": "60%"},
    ]
    st.dataframe(pd.DataFrame(日志数据), use_container_width=True)
    
    if st.button("🚀 AI分析", type="primary", use_container_width=True):
        with st.spinner("AI分析中..."):
            策略列表 = 策略加载器.获取策略()
            if 策略列表:
                策略 = 策略列表[0]
                行情数据 = 行情获取.获取价格(策略['品种'])
                策略信号 = 策略运行器.运行(策略, 行情数据)
                结果 = AI引擎.分析(策略['品种'], 行情数据.价格, 策略信号)
                st.success(f"AI决策: {结果['最终信号'].upper()}")
