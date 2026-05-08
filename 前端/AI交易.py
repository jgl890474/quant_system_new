# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场选择
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    # 策略映射
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "双均线策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    
    策略列表 = 策略映射.get(市场, ["默认策略"])
    策略类型 = st.selectbox("选择策略", 策略列表)
    
    # 存储推荐结果的session
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner(f"AI 正在分析{市场}..."):
            try:
                结果 = AI引擎.AI推荐(市场, 策略类型)
                st.session_state.ai_recommendations = 结果.get("推荐", [])
                st.success(f"✅ AI 推荐完成！共 {len(st.session_state.ai_recommendations)} 只")
                st.rerun()
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # 显示推荐结果
    if st.session_state.ai_recommendations:
        st.markdown("### 📈 AI 推荐列表")
        
        for idx, 股票 in enumerate(st.session_state.ai_recommendations):
            代码 = 股票.get("代码", "")
            名称 = 股票.get("名称", "未知")
            价格 = 股票.get("价格", 0)
            
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{名称}** ({代码})")
                    st.caption(f"价格: ${价格:.2f}")
                with col2:
                    if 价格 > 0:
                        # 使用独立的表单来确保按钮触发
                        with st.form(key=f"buy_form_{代码}_{idx}"):
                            if st.form_submit_button(f"💰 买入 {名称}", use_container_width=True):
                                st.info(f"正在买入 {名称}...")
                                引擎.买入(代码, 价格, 100)
                                st.success(f"✅ 已买入 {名称} 100股")
                                st.rerun()
                    else:
                        st.warning("价格无效")
                with col3:
                    st.caption(f"推荐")
                st.divider()
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📊 当前持仓")
    
    if 引擎.持仓:
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            持仓数据.append({
                "品种": 品种,
                "数量": int(pos.数量),
                "成本": f"{pos.平均成本:.2f}",
                "现价": f"{pos.当前价格:.2f}"
            })
        st.dataframe(持仓数据, use_container_width=True)
    else:
        st.info("暂无持仓")
    
    # 手动测试按钮
    st.markdown("---")
    st.markdown("### 🧪 快速测试")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("测试买入 AAPL", use_container_width=True):
            引擎.买入("AAPL", 287.44, 100)
            st.rerun()
    with col2:
        if st.button("测试买入 贵州茅台", use_container_width=True):
            引擎.买入("600519.SS", 1372.99, 100)
            st.rerun()
