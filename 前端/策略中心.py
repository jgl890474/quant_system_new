# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 获取策略列表
    策略列表 = []
    if 策略加载器 is not None:
        try:
            策略列表 = 策略加载器.获取策略()
            st.success(f"✅ 已加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.error(f"加载策略失败: {e}")
    
    # 初始化策略状态
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            名称 = s.get("名称", "")
            if 名称:
                st.session_state.策略状态[名称] = True
    
    # 按类别分组
    分组策略 = {}
    for s in 策略列表:
        类别 = s.get("类别", "其他")
        if 类别 not in 分组策略:
            分组策略[类别] = []
        分组策略[类别].append(s)
    
    # 显示策略
    for 类别, 策略组 in 分组策略.items():
        st.markdown(f"#### {类别}")
        
        for s in 策略组:
            名称 = s.get("名称", "")
            品种 = s.get("品种", "")
            是否启用 = st.session_state.策略状态.get(名称, True)
            
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write(f"**{名称}**")
            with col2:
                st.write(f"品种: {品种}")
            with col3:
                if 是否启用:
                    st.markdown("🟢 **运行中**")
                else:
                    st.markdown("🔴 **已停止**")
            with col4:
                按钮文本 = "⏸️ 停止" if 是否启用 else "▶️ 启动"
                if st.button(按钮文本, key=f"strategy_{名称}"):
                    st.session_state.策略状态[名称] = not 是否启用
                    st.rerun()
            
            st.markdown("---")
    
    # 统计信息
    if 策略列表:
        运行中数量 = sum(1 for name, status in st.session_state.策略状态.items() if status)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 策略总数", len(策略列表))
        with col2:
            st.metric("🟢 运行中", 运行中数量)
        with col3:
            st.metric("🔴 已停止", len(策略列表) - 运行中数量)
        
        # 全局控制
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
    
    st.caption("💡 停止的策略不会在AI交易中产生信号")
