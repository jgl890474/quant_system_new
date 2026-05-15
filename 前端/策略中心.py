# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 初始化策略状态存储
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
    
    # 策略列表
    策略列表 = [
        {"名称": "外汇利差策略1", "类别": "💰 外汇", "品种": "EURUSD"},
        {"名称": "加密双均线1", "类别": "₿ 加密货币", "品种": "BTC-USD"},
        {"名称": "加密风控策略", "类别": "₿ 加密货币", "品种": "BTC-USD"},
        {"名称": "A股隔夜套利策略3", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "A股双均线1", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "A股量价策略2", "类别": "📈 A股", "品种": "000001.SS"},
        {"名称": "美股简单策略1", "类别": "🇺🇸 美股", "品种": "AAPL"},
        {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
    ]
    
    # 初始化状态
    for s in 策略列表:
        if s["名称"] not in st.session_state.策略状态:
            st.session_state.策略状态[s["名称"]] = True
    
    # 按类别分组显示
    for 类别 in set(s["类别"] for s in 策略列表):
        st.markdown(f"#### {类别}")
        
        类别策略 = [s for s in 策略列表 if s["类别"] == 类别]
        
        for 策略 in 类别策略:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"**{策略['名称']}**")
            with col2:
                st.write(f"品种: {策略['品种']}")
            with col3:
                是否启用 = st.session_state.策略状态[策略["名称"]]
                if 是否启用:
                    st.markdown("状态: 🟢 **运行中**")
                else:
                    st.markdown("状态: 🔴 **已停止**")
            with col4:
                按钮文本 = "⏸️ 停止" if st.session_state.策略状态[策略["名称"]] else "▶️ 启动"
                if st.button(按钮文本, key=f"btn_{策略['名称']}"):
                    # 切换状态
                    st.session_state.策略状态[策略["名称"]] = not st.session_state.策略状态[策略["名称"]]
                    
                    # 同步到策略运行器（如果可用）
                    if 策略加载器 and hasattr(策略加载器, '设置策略状态'):
                        策略加载器.设置策略状态(策略["名称"], st.session_state.策略状态[策略["名称"]])
                    
                    st.rerun()
            
            st.markdown("---")
    
    # 统计信息
    st.markdown("### 📊 策略统计")
    运行中数量 = sum(1 for name, status in st.session_state.策略状态.items() if status)
    总数量 = len(st.session_state.策略状态)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 策略总数", 总数量)
    with col2:
        st.metric("🟢 运行中", 运行中数量)
    with col3:
        st.metric("🔴 已停止", 总数量 - 运行中数量)
    
    # 全局控制
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 启用所有策略"):
            for name in st.session_state.策略状态:
                st.session_state.策略状态[name] = True
            st.rerun()
    with col2:
        if st.button("⏸️ 停止所有策略"):
            for name in st.session_state.策略状态:
                st.session_state.策略状态[name] = False
            st.rerun()
    
    st.caption("💡 停止的策略不会在AI交易中产生信号，也不会被自动交易执行")
