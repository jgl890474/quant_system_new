# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    st.caption("⚙️ 点击「参数」按钮，可以配置策略的均线、止损止盈等参数")
    
    # ========== 优先从策略加载器获取策略 ==========
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
            st.warning(f"从策略加载器获取策略失败: {e}")
    
    # 如果策略加载器没有数据，使用硬编码策略列表
    if not 策略列表:
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
        st.info("📋 使用默认策略列表")
    
    # ========== 初始化策略状态 ==========
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            st.session_state.策略状态[s["名称"]] = True
    
    # ========== 初始化参数面板显示状态 ==========
    if 'show_param_panel' not in st.session_state:
        st.session_state.show_param_panel = {}
    
    # ========== 按类别分组显示 ==========
    分组 = {}
    for s in 策略列表:
        类别 = s["类别"]
        if 类别 not in 分组:
            分组[类别] = []
        分组[类别].append(s)
    
    # ========== 显示策略 ==========
    for 类别, 策略组 in 分组.items():
        st.markdown(f"#### {类别}")
        for s in 策略组:
            名称 = s["名称"]
            品种 = s["品种"]
            启用 = st.session_state.策略状态.get(名称, True)
            
            # 使用expander包装每个策略
            with st.expander(f"{'🟢' if 启用 else '🔴'} {名称} - {品种}", expanded=False):
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**策略名称**")
                    st.caption(名称)
                
                with col2:
                    st.write(f"**交易品种**")
                    st.caption(品种)
                
                with col3:
                    st.write(f"**运行状态**")
                    if 启用:
                        st.success("🟢 运行中")
                    else:
                        st.error("🔴 已停止")
                
                with col4:
                    if 启用:
                        if st.button("⏸️ 停止", key=f"stop_{名称}"):
                            st.session_state.策略状态[名称] = False
                            st.rerun()
                    else:
                        if st.button("▶️ 启动", key=f"start_{名称}"):
                            st.session_state.策略状态[名称] = True
                            st.rerun()
                
                st.markdown("---")
                
                # ========== 参数配置按钮和面板 ==========
                if st.button("⚙️ 配置参数", key=f"param_btn_{名称}"):
                    if 名称 in st.session_state.show_param_panel:
                        st.session_state.show_param_panel[名称] = not st.session_state.show_param_panel[名称]
                    else:
                        st.session_state.show_param_panel[名称] = True
                    st.rerun()
                
                # 显示参数配置面板
                if st.session_state.show_param_panel.get(名称, False):
                    st.markdown("**📊 策略参数配置**")
                    
                    # 获取当前参数（优先从策略加载器获取）
                    当前参数 = {}
                    if 策略加载器 is not None and hasattr(策略加载器, '获取策略参数'):
                        当前参数 = 策略加载器.获取策略参数(名称)
                    
                    # 默认参数模板
                    默认参数 = {
                        "短期均线": 当前参数.get("短期均线", 5),
                        "长期均线": 当前参数.get("长期均线", 20),
                        "止损比例": 当前参数.get("止损比例", 0.05),
                        "止盈比例": 当前参数.get("止盈比例", 0.10),
                        "仓位比例": 当前参数.get("仓位比例", 0.3),
                    }
                    
                    参数更新 = {}
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        新短期 = st.number_input(
                            "短期均线周期", 
                            min_value=2, max_value=50, 
                            value=int(默认参数["短期均线"]), step=1,
                            key=f"param_{名称}_ma_short"
                        )
                        参数更新["短期均线"] = 新短期
                        
                        新止损 = st.number_input(
                            "止损比例 (%)", 
                            min_value=0.5, max_value=20.0, 
                            value=float(默认参数["止损比例"] * 100), step=0.5,
                            key=f"param_{名称}_stop_loss"
                        ) / 100
                        参数更新["止损比例"] = 新止损
                    
                    with col2:
                        新长期 = st.number_input(
                            "长期均线周期", 
                            min_value=10, max_value=200, 
                            value=int(默认参数["长期均线"]), step=5,
                            key=f"param_{名称}_ma_long"
                        )
                        参数更新["长期均线"] = 新长期
                        
                        新止盈 = st.number_input(
                            "止盈比例 (%)", 
                            min_value=1.0, max_value=50.0, 
                            value=float(默认参数["止盈比例"] * 100), step=1.0,
                            key=f"param_{名称}_take_profit"
                        ) / 100
                        参数更新["止盈比例"] = 新止盈
                    
                    新仓位 = st.slider(
                        "仓位比例 (%)", 
                        min_value=5, max_value=80, 
                        value=int(默认参数["仓位比例"] * 100), step=5,
                        key=f"param_{名称}_position"
                    ) / 100
                    参数更新["仓位比例"] = 新仓位
                    
                    st.caption(f"💰 仓位比例: {新仓位*100:.0f}% (可用资金的{新仓位*100:.0f}%用于开仓)")
                    
                    col_save, col_reset = st.columns(2)
                    with col_save:
                        if st.button("💾 保存参数", key=f"save_param_{名称}"):
                            if 策略加载器 is not None and hasattr(策略加载器, '更新策略参数'):
                                if 策略加载器.更新策略参数(名称, 参数更新):
                                    st.success(f"✅ 策略 {名称} 参数已保存")
                                    st.rerun()
                                else:
                                    st.error("保存失败")
                            else:
                                st.warning("策略加载器不支持参数保存")
                    
                    with col_reset:
                        if st.button("🔄 重置默认", key=f"reset_param_{名称}"):
                            if 策略加载器 is not None and hasattr(策略加载器, '更新策略参数'):
                                默认重置 = {
                                    "短期均线": 5,
                                    "长期均线": 20,
                                    "止损比例": 0.05,
                                    "止盈比例": 0.10,
                                    "仓位比例": 0.3,
                                }
                                if 策略加载器.更新策略参数(名称, 默认重置):
                                    st.success(f"✅ 策略 {名称} 已重置为默认参数")
                                    st.rerun()
                                else:
                                    st.error("重置失败")
                            else:
                                st.warning("策略加载器不支持参数重置")
    
    # ========== 统计信息 ==========
    st.markdown("---")
    st.markdown("### 📊 策略统计")
    
    总数 = len(策略列表)
    运行中 = sum(1 for name, status in st.session_state.策略状态.items() if status)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 策略总数", 总数)
    with col2:
        st.metric("🟢 运行中", 运行中)
    with col3:
        st.metric("🔴 已停止", 总数 - 运行中)
    
    # ========== 全局控制 ==========
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
    
    # ========== 刷新按钮 ==========
    if st.button("🔄 刷新策略列表", use_container_width=True):
        if 策略加载器 is not None and hasattr(策略加载器, '刷新'):
            策略加载器.刷新()
        st.success("策略列表已刷新")
        st.rerun()
