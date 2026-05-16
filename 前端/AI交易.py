# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 调试：检查策略加载器 ==========
    if 策略加载器 is None:
        st.error("❌ 策略加载器未传入！请检查启动入口")
        # 尝试从 session_state 获取
        if '策略加载器' in st.session_state:
            策略加载器 = st.session_state.策略加载器
            st.success("✅ 已从 session_state 获取策略加载器")
    
    # ========== 获取策略列表 ==========
    策略列表 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                策略列表 = 策略加载器.获取策略()
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
            elif hasattr(策略加载器, '获取策略列表'):
                策略列表 = 策略加载器.获取策略列表()
                st.success(f"✅ 成功加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.error(f"加载策略失败: {e}")
    
    # 如果还是没获取到，使用硬编码
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
        st.info("📋 使用硬编码策略列表")
    
    # 显示策略列表
    st.write("### 📊 可用策略")
    for s in 策略列表:
        st.caption(f"✅ {s.get('名称')} - {s.get('类别')} - {s.get('品种')}")
    
    # ... 后续代码保持不变 ...
