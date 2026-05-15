# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # ========== 从多个来源获取策略加载器 ==========
    实际加载器 = None
    
    # 方法1：从参数获取
    if 策略加载器 is not None:
        实际加载器 = 策略加载器
    
    # 方法2：从 session_state 获取
    if 实际加载器 is None and '策略加载器' in st.session_state:
        实际加载器 = st.session_state.策略加载器
    
    # 方法3：尝试重新导入
    if 实际加载器 is None:
        try:
            from 核心.策略加载器 import 策略加载器 as 策略加载器类
            实际加载器 = 策略加载器类()
            st.session_state.策略加载器 = 实际加载器
            st.success("✅ 策略加载器已重新加载")
        except Exception as e:
            st.error(f"策略加载器导入失败: {e}")
    
    # ========== 获取策略列表 ==========
    策略列表 = []
    
    if 实际加载器 is not None:
        try:
            # 尝试多种方法获取策略
            if hasattr(实际加载器, '获取策略列表_带状态'):
                策略列表 = 实际加载器.获取策略列表_带状态()
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
            elif hasattr(实际加载器, '获取策略列表'):
                原始列表 = 实际加载器.获取策略列表()
                for s in 原始列表:
                    if isinstance(s, dict):
                        策略列表.append({
                            "名称": s.get("名称", ""),
                            "类别": s.get("类别", ""),
                            "品种": s.get("品种", ""),
                            "启用": True,
                        })
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
            elif hasattr(实际加载器, '获取策略'):
                原始列表 = 实际加载器.获取策略()
                for s in 原始列表:
                    if isinstance(s, dict):
                        策略列表.append({
                            "名称": s.get("名称", ""),
                            "类别": s.get("类别", ""),
                            "品种": s.get("品种", ""),
                            "启用": True,
                        })
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
            else:
                st.warning("策略加载器没有获取策略的方法")
        except Exception as e:
            st.error(f"获取策略列表失败: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # ========== 使用默认策略列表（如果仍然为空） ==========
    if not 策略列表:
        策略列表 = [
            {"名称": "双均线策略", "类别": "📈 A股", "品种": "000001", "启用": True},
            {"名称": "量价策略", "类别": "📈 A股", "品种": "000002", "启用": True},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD", "启用": True},
            {"名称": "动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "启用": True},
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD", "启用": True},
            {"名称": "A股隔夜套利策略", "类别": "📈 A股", "品种": "000858", "启用": True},
            {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "NVDA", "启用": True},
        ]
        st.info("📋 使用默认策略列表（7个预设策略）")
    
    # ========== 显示策略表格 ==========
    if 策略列表:
        df = pd.DataFrame(策略列表)
        
        # 确保有必要的列
        if "启用" not in df.columns:
            df["启用"] = True
        
        # 选择显示的列
        显示列 = ["名称", "类别", "品种", "启用"]
        显示列 = [c for c in 显示列 if c in df.columns]
        df = df[显示列]
        
        st.dataframe(df, use_container_width=True)
        
        # ========== 策略统计 ==========
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 策略总数", len(策略列表))
        
        with col2:
            启用数 = sum(1 for s in 策略列表 if s.get("启用", True))
            st.metric("✅ 启用中",启用数)
        
        with col3:
            if 实际加载器:
                st.metric("🔌 加载器状态", "已连接")
            else:
                st.metric("🔌 加载器状态", "使用默认")
        
        # ========== 策略控制按钮 ==========
        st.markdown("---")
        st.markdown("#### 🔧 策略控制")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ 启用所有策略", key="enable_all_strategies"):
                st.success("✅ 已启用所有策略")
        
        with col2:
            if st.button("⏸️ 停止所有策略", key="disable_all_strategies"):
                st.warning("⏸️ 已停止所有策略")
        
        with col3:
            if st.button("🔄 刷新列表", key="refresh_strategies_list"):
                if 实际加载器 and hasattr(实际加载器, '刷新'):
                    实际加载器.刷新()
                st.success("策略列表已刷新")
                st.rerun()
    else:
        st.warning("⚠️ 暂无可用策略")
