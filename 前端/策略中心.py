# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 优先从策略加载器获取策略
    策略列表 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                原始策略 = 策略加载器.获取策略()
                for s in 原始策略:
                    if isinstance(s, dict):
                        策略列表.append({
                            "名称": s.get("名称", ""),
                            "类别": s.get("类别", ""),
                            "品种": s.get("品种", ""),
                        })
        except Exception as e:
            st.warning(f"获取策略失败: {e}")
    
    # 如果策略加载器没有数据，使用硬编码
    if not 策略列表:
        策略列表 = [
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
    
    # 显示策略（每个策略单独一行，带停止/启动按钮）
    for 类别, 策略组 in 分组.items():
        st.markdown(f"#### {类别}")
        
        for s in 策略组:
            名称 = s["名称"]
            品种 = s["品种"]
            启用 = st.session_state.策略状态.get(名称, True)
            
            # 使用列布局
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1.5])
            
            with col1:
                st.write(f"**{名称}**")
            with col2:
                st.write(f"品种: {品种}")
            with col3:
                if 启用:
                    st.markdown("🟢 **运行中**")
                else:
                    st.markdown("🔴 **已停止**")
            with col4:
                if 启用:
                    if st.button("⏸️ 停止", key=f"stop_{名称}", use_container_width=True):
                        st.session_state.策略状态[名称] = False
                        # 同步到策略运行器
                        try:
                            from 核心.策略运行器 import 策略运行器
                            策略运行器.设置策略状态(名称, False)
                        except:
                            pass
                        st.rerun()
                else:
                    if st.button("▶️ 启动", key=f"start_{名称}", use_container_width=True):
                        st.session_state.策略状态[名称] = True
                        # 同步到策略运行器
                        try:
                            from 核心.策略运行器 import 策略运行器
                            策略运行器.设置策略状态(名称, True)
                        except:
                            pass
                        st.rerun()
            
            st.markdown("---")
    
    # 统计信息
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
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 启用所有策略", use_container_width=True):
            for s in 策略列表:
                st.session_state.策略状态[s["名称"]] = True
            st.rerun()
    with col2:
        if st.button("⏸️ 停止所有策略", use_container_width=True):
            for s in 策略列表:
                st.session_state.策略状态[s["名称"]] = False
            st.rerun()
    
    # 刷新按钮
    if st.button("🔄 刷新策略列表", use_container_width=True):
        if 策略加载器 is not None and hasattr(策略加载器, '刷新'):
            策略加载器.刷新()
        st.rerun()
    
    # 显示策略状态说明
    st.markdown("---")
    st.caption("💡 停止的策略在「AI交易」中不会显示信号")
