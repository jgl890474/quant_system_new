# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from 工具.会话持久化 import auto_restore_session, auto_save_session
from 工具 import 数据库
from 核心 import 订单引擎

# 页面配置
st.set_page_config(page_title="量化交易系统", page_icon="📈", layout="wide")
auto_restore_session()

# 初始化引擎
if '订单引擎' not in st.session_state:
    st.session_state.订单引擎 = 订单引擎(初始资金=1000000)
引擎 = st.session_state.订单引擎

# 侧边栏
with st.sidebar:
    st.markdown("### 💼 账户")
    st.metric("可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if 引擎.持仓:
        st.markdown("### 📦 持仓")
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.caption(f"{品种}: {数量:.4f}个 @ ¥{成本:.2f}")

# 主页面
st.title("📊 量化交易系统")
st.caption("多类目 · 多策略 · AI自动交易")

# Tab
tab1, tab2, tab3, tab4 = st.tabs(["🏠 首页", "🤖 AI交易", "📋 持仓", "⚙️ 设置"])

with tab1:
    st.markdown("欢迎使用量化交易系统")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总资产", f"¥{引擎.获取总资产():,.0f}" if hasattr(引擎, '获取总资产') else "计算中")
    with col2:
        st.metric("可用资金", f"¥{引擎.获取可用资金():,.0f}")
    with col3:
        st.metric("持仓数量", len(引擎.持仓))

with tab2:
    st.markdown("### 🤖 AI 交易")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("品种", ["BTC-USD", "ETH-USD", "AAPL", "EURUSD"])
    with col2:
        操作 = st.selectbox("操作", ["买入", "卖出"])
    
    数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01)
    
    if st.button("执行交易", type="primary"):
        if 操作 == "买入":
            结果 = 引擎.买入(品种, None, 数量)
            if 结果.get("success"):
                st.success(f"✅ 买入 {品种} {数量} 个")
                st.rerun()
            else:
                st.error(f"失败: {结果.get('error')}")
        else:
            if 品种 in 引擎.持仓:
                结果 = 引擎.卖出(品种, None, 数量)
                if 结果.get("success"):
                    st.success(f"✅ 卖出 {品种} {数量} 个")
                    st.rerun()
                else:
                    st.error(f"失败: {结果.get('error')}")
            else:
                st.error(f"没有持仓 {品种}")
    
    st.markdown("---")
    if 引擎.持仓:
        st.markdown("### 当前持仓")
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.metric(品种, f"{数量:.4f}个", delta=f"成本 ¥{成本:.2f}")

with tab3:
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.metric(品种, f"{数量:.4f}个", delta=f"成本 ¥{成本:.2f}")
    else:
        st.info("暂无持仓")

with tab4:
    st.markdown("### 系统设置")
    if st.button("清空所有持仓"):
        数据库.清空所有持仓()
        st.session_state.订单引擎 = 订单引擎(初始资金=1000000)
        st.success("已清空")
        st.rerun()

auto_save_session()
