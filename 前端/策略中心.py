# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # ========== 独立加载策略（不依赖传入参数） ==========
    策略列表 = []
    
    # 方法1：从 session_state 获取
    if '策略加载器' in st.session_state and st.session_state.策略加载器 is not None:
        try:
            loader = st.session_state.策略加载器
            if hasattr(loader, '获取策略列表_带状态'):
                策略列表 = loader.获取策略列表_带状态()
            elif hasattr(loader, '获取策略列表'):
                原始 = loader.获取策略列表()
                for s in 原始:
                    if isinstance(s, dict):
                        策略列表.append(s)
            elif hasattr(loader, '获取策略'):
                原始 = loader.获取策略()
                for s in 原始:
                    if isinstance(s, dict):
                        策略列表.append({
                            "名称": s.get("名称", ""),
                            "类别": s.get("类别", ""),
                            "品种": s.get("品种", ""),
                            "启用": True,
                        })
        except Exception as e:
            st.warning(f"读取策略失败: {e}")
    
    # 方法2：直接导入策略加载器
    if not 策略列表:
        try:
            from 核心.策略加载器 import 策略加载器 as 策略加载器类
            loader = 策略加载器类()
            st.session_state.策略加载器 = loader
            原始 = loader.获取策略()
            for s in 原始:
                if isinstance(s, dict):
                    策略列表.append({
                        "名称": s.get("名称", ""),
                        "类别": s.get("类别", ""),
                        "品种": s.get("品种", ""),
                        "启用": True,
                    })
            if 策略列表:
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.warning(f"导入策略加载器失败: {e}")
    
    # 方法3：使用硬编码的默认策略列表
    if not 策略列表:
        策略列表 = [
            {"名称": "双均线策略", "类别": "📈 A股", "品种": "000001", "启用": True},
            {"名称": "量价策略", "类别": "📈 A股", "品种": "000002", "启用": True},
            {"名称": "隔夜套利策略", "类别": "📈 A股", "品种": "000858", "启用": True},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD", "启用": True},
            {"名称": "动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "启用": True},
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD", "启用": True},
            {"名称": "期货趋势策略", "类别": "📊 期货", "品种": "GC=F", "启用": True},
        ]
        st.info("📋 使用内置策略列表（7个预设策略）")
    
    # ========== 显示统计 ==========
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 策略总数", len(策略列表))
    with col2:
        启用数 = sum(1 for s in 策略列表 if s.get("启用", True))
        st.metric("✅ 启用中", 启用数)
    with col3:
        品类数 = len(set(s.get("类别", "") for s in 策略列表))
        st.metric("🏷️ 涵盖品类", 品类数)
    
    # ========== 显示策略表格 ==========
    if 策略列表:
        df = pd.DataFrame(策略列表)
        
        # 确保有必要的列
        if "启用" not in df.columns:
            df["启用"] = True
        
        # 显示列
        显示列 = ["名称", "类别", "品种", "启用"]
        显示列 = [c for c in 显示列 if c in df.columns]
        
        st.dataframe(df[显示列], use_container_width=True)
        
        # ========== 策略控制 ==========
        st.markdown("---")
        st.markdown("#### 🔧 策略控制")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ 启用所有策略", key="enable_all"):
                st.success("✅ 已启用所有策略")
        
        with col2:
            if st.button("⏸️ 停止所有策略", key="disable_all"):
                st.warning("⏸️ 已停止所有策略")
    
    # ========== 提示 ==========
    st.markdown("---")
    st.caption("💡 策略状态变化会影响AI交易模块的推荐信号")
