# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 调试信息 ==========
    st.markdown("---")
    st.markdown("#### 🔍 调试信息")
    
    # 1. 检查策略加载器是否传入
    if 策略加载器 is None:
        st.error("❌ 策略加载器 = None (未传入)")
    else:
        st.success(f"✅ 策略加载器已传入，类型: {type(策略加载器).__name__}")
        
        # 2. 尝试获取策略
        try:
            if hasattr(策略加载器, '获取策略'):
                策略列表 = 策略加载器.获取策略()
                st.success(f"✅ 调用 获取策略() 成功，返回 {len(策略列表)} 个策略")
                
                # 显示策略详情
                for s in 策略列表:
                    if isinstance(s, dict):
                        st.write(f"   - {s.get('名称')} | {s.get('类别')} | {s.get('品种')}")
                    else:
                        st.write(f"   - {s}")
            else:
                st.error("❌ 策略加载器没有 获取策略 方法")
                st.write(f"可用方法: {dir(策略加载器)}")
        except Exception as e:
            st.error(f"❌ 获取策略失败: {e}")
    
    # 3. 检查 session_state
    st.markdown("---")
    st.markdown("#### 📦 session_state 中的策略加载器")
    if '策略加载器' in st.session_state:
        st.success("✅ session_state 中有策略加载器")
        sl = st.session_state.策略加载器
        if hasattr(sl, '获取策略'):
            try:
                策略列表2 = sl.获取策略()
                st.success(f"✅ 从 session_state 获取到 {len(策略列表2)} 个策略")
            except Exception as e:
                st.error(f"❌ 获取失败: {e}")
    else:
        st.error("❌ session_state 中没有策略加载器")
    
    # ========== 简单交易功能 ==========
    st.markdown("---")
    st.markdown("### 📊 交易")
    
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("市场", ["加密货币", "A股", "美股", "外汇"])
    with col2:
        品种 = st.selectbox("品种", ["BTC-USD", "ETH-USD", "AAPL"])
    
    st.metric("可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if st.button("买入测试"):
        st.success(f"测试买入: {品种}")
    
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
