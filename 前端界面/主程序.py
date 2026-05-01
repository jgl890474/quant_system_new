import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="量化交易系统", layout="wide")

# 导入模块
from 数据接入模块 import 获取股票列表
from AI模块.AI多策略 import AI自动交易

# 初始化
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AI自动交易()
if '当前页面' not in st.session_state:
    st.session_state.当前页面 = "首页"

# 顶部
st.title("🚀 量化交易系统")
st.caption("多策略 · 多类目 · AI智能交易")

# 导航
nav_items = ["首页", "AI交易", "持仓", "关于"]
cols = st.columns(len(nav_items))
for col, item in zip(cols, nav_items):
    with col:
        if st.button(item, use_container_width=True):
            st.session_state.当前页面 = item
            st.rerun()

st.markdown("---")

# ==================== 首页 ====================
if st.session_state.当前页面 == "首页":
    st.info("🤖 AI智能交易系统已就绪")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("支持类目", "股票/加密货币/外汇/期货")
    with col2:
        st.metric("策略数量", "6个")
    with col3:
        st.metric("状态", "🟢 运行中")

# ==================== AI交易 ====================
elif st.session_state.当前页面 == "AI交易":
    st.subheader("🤖 AI自动交易")
    
    engine = st.session_state.ai_engine
    
    # 显示当前类目
    st.info(f"📊 当前交易类目: {engine.当前类目}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        策略列表 = ["双均线策略 (股票)", "布林带策略 (股票)", "加密网格 (加密货币)", "加密趋势跟踪 (加密货币)"]
        选中策略 = st.selectbox("选择策略", 策略列表)
        
        if st.button("🚀 启动AI交易", use_container_width=True):
            engine.注册策略(None, 选中策略)
            engine.启动()
            st.success(f"AI交易已启动 | 策略: {选中策略}")
        
        if st.button("⏸️ 停止AI交易", use_container_width=True):
            engine.停止()
            st.warning("AI交易已停止")
    
    with col2:
        初始资金 = st.number_input("初始资金", value=100000)
        if st.button("更新资金", use_container_width=True):
            engine.设置资金(初始资金)
            st.success("资金已更新")
        
        if st.button("🔄 手动执行一轮", use_container_width=True):
            with st.spinner("分析中..."):
                result = engine.手动执行一轮()
                if result:
                    st.success(f"决策: {result.get('action', 'hold')} | {result.get('reason', '')}")
                else:
                    st.info("无交易信号")
    
    st.markdown("---")
    
    # 状态显示
    状态 = engine.获取状态()
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("运行状态", 状态.get('运行状态', '已停止'))
    with col_b:
        st.metric("总资产", f"{状态.get('总资产', 0):,.0f}")
    with col_c:
        st.metric("收益率", f"{状态.get('收益率', 0)}%")
    with col_d:
        st.metric("交易次数", 状态.get('交易次数', 0))
    
    # 显示类目详情
    st.markdown("---")
    st.subheader("📋 类目风控参数")
    col_e, col_f, col_g, col_h = st.columns(4)
    with col_e:
        st.metric("股票", "止盈5% / 止损3%")
    with col_f:
        st.metric("加密货币", "止盈8% / 止损5%")
    with col_g:
        st.metric("外汇", "止盈3% / 止损2%")
    with col_h:
        st.metric("期货", "止盈6% / 止损4%")

# ==================== 持仓 ====================
elif st.session_state.当前页面 == "持仓":
    st.subheader("💰 当前持仓")
    engine = st.session_state.ai_engine
    if engine.持仓:
        持仓数据 = []
        for code, info in engine.持仓.items():
            持仓数据.append({
                "代码": code,
                "名称": info.get('名称', code),
                "数量": info['数量'],
                "成本": info['买入价'],
                "买入时间": info.get('买入时间', '')
            })
        st.dataframe(pd.DataFrame(持仓数据), use_container_width=True)
        
        # 显示持仓统计
        total_value = sum([info['数量'] * info['买入价'] for info in engine.持仓.values()])
        st.metric("持仓市值", f"{total_value:,.0f}")
    else:
        st.info("暂无持仓，请启动AI交易")
    
    # 显示交易记录
    st.markdown("---")
    st.subheader("📝 交易记录")
    if engine.交易记录:
        st.dataframe(pd.DataFrame(engine.交易记录[-10:]), use_container_width=True)
    else:
        st.info("暂无交易记录")

# ==================== 关于 ====================
elif st.session_state.当前页面 == "关于":
    st.subheader("📖 系统说明")
    st.markdown("""
    ### 量化交易系统 v4.0
    
    **支持类目及风控参数：**
    
    | 类目 | 止盈 | 止损 | 数据源 |
    |------|------|------|--------|
    | 股票 | 5% | 3% | 腾讯财经 |
    | 加密货币 | 8% | 5% | 币安API |
    | 外汇 | 3% | 2% | ExchangeRate-API |
    | 期货 | 6% | 4% | 东方财富 |
    
    **使用步骤：**
    1. 点击「AI交易」
    2. 选择策略（系统自动识别类目）
    3. 启动AI交易
    4. AI自动分析并交易
    5. 查看持仓和交易记录
    
    **AI会根据选择的策略自动：**
    - 识别交易类目
    - 获取对应数据源
    - 使用对应的止盈止损参数
    - 自动买卖决策
    """)

st.markdown("---")
st.caption("量化交易系统 v4.0 | 全自动AI交易 | 多类目支持")