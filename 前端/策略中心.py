# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 硬编码策略列表
    策略列表 = [
        {"名称": "外汇利差策略1", "类别": "💰 外汇", "品种": "EURUSD"},
        {"名称": "加密双均线1", "类别": "₿ 加密货币", "品种": "BTC-USD"},
        {"名称": "加密风控策略", "类别": "₿ 加密货币", "品种": "BTC-USD"},
        {"名称": "A股双均线1", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "A股量价策略2", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "A股隔夜套利策略3", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "美股简单策略1", "类别": "🇺🇸 美股", "品种": "AAPL"},
        {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
    ]
    
    # 初始化策略状态
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            st.session_state.策略状态[s["名称"]] = True
    
    # 按类别分组
    分组 = {}
    for s in 策略列表:
        类别 = s["类别"]
        if 类别 not in 分组:
            分组[类别] = []
        分组[类别].append(s)
    
    # 显示策略
    for 类别, 策略组 in 分组.items():
        st.markdown(f"#### {类别}")
        for s in 策略组:
            名称 = s["名称"]
            品种 = s["品种"]
            启用 = st.session_state.策略状态.get(名称, True)
            
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{名称}**")
            with col2:
                st.write(f"品种: {品种}")
            with col3:
                st.write("🟢 运行中" if 启用 else "🔴 已停止")
            with col4:
                按钮文字 = "⏸️ 停止" if 启用 else "▶️ 启动"
                if st.button(按钮文字, key=f"btn_{名称}"):
                    st.session_state.策略状态[名称] = not 启用
                    st.rerun()
            st.markdown("---")
    
    # 统计
    总数 = len(策略列表)
    运行中 = sum(1 for name, status in st.session_state.策略状态.items() if status)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 策略总数", 总数)
    with col2:
        st.metric("🟢 运行中", 运行中)
    with col3:
        st.metric("🔴 已停止", 总数 - 运行中)
    
    # 全局控制
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 启用所有"):
            for s in 策略列表:
                st.session_state.策略状态[s["名称"]] = True
            st.rerun()
    with col2:
        if st.button("⏸️ 停止所有"):
            for s in 策略列表:
                st.session_state.策略状态[s["名称"]] = False
            st.rerun()
