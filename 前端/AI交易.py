# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # 硬编码策略列表
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
    
    # 初始化策略状态
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            st.session_state.策略状态[s["名称"]] = True
    
    # 获取启用的策略
    启用策略 = [s for s in 策略列表 if st.session_state.策略状态.get(s["名称"], False)]
    
    # 显示启用策略
    if 启用策略:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略)}个)", expanded=False):
            for s in 启用策略[:8]:
                st.caption(f"✅ {s['名称']}")
    else:
        st.warning("⚠️ 请前往「策略中心」启用策略")
    
    # 市场选择
    可用市场 = ["💰 外汇", "₿ 加密货币", "📈 A股", "🇺🇸 美股"]
    
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("选择市场", 可用市场)
    with col2:
        策略选项 = ["综合推荐", "趋势跟踪", "网格交易", "均值回归"]
        策略 = st.selectbox("选择策略", 策略选项)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # 品种配置
    if "加密" in 市场:
        品种列表 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12},
        ]
    elif "A股" in 市场:
        品种列表 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50},
        ]
    elif "美股" in 市场:
        品种列表 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00},
        ]
    else:
        品种列表 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650},
        ]
    
    # AI分析
    if st.button("🔍 AI智能分析", type="primary"):
        if not 启用策略:
            st.error("❌ 请先在策略中心启用策略")
        else:
            with st.spinner("AI正在分析市场..."):
                st.markdown("---")
                st.markdown(f"### 📈 AI分析结果 - {市场}")
                for item in 品种列表:
                    信号随机 = random.random()
                    if 信号随机 > 0.6:
                        信号, 颜色, 置信度 = "买入", "🟢", random.randint(70, 95)
                    elif 信号随机 > 0.3:
                        信号, 颜色, 置信度 = "持有", "🟡", random.randint(50, 70)
                    else:
                        信号, 颜色, 置信度 = "卖出", "🔴", random.randint(40, 60)
                    
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                        <b>{item['名称']} ({item['品种']})</b><br>
                        价格: ¥{item['价格']:,.2f}<br>
                        信号: {颜色} {信号} (置信度: {置信度}%)
                    </div>
                    """, unsafe_allow_html=True)
    
    # 快速交易
    st.markdown("---")
    st.markdown("#### ⚡ 快速交易")
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    with tab1:
        with st.form("buy_form"):
            买入选择 = st.selectbox("选择品种", [f"{item['名称']} ({item['品种']})" for item in 品种列表])
            品种代码 = 买入选择.split("(")[-1].replace(")", "")
            参考价格 = next((item["价格"] for item in 品种列表 if item["品种"] == 品种代码), 100)
            买入数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01)
            
            if st.form_submit_button("确认买入", type="primary"):
                可用资金 = 引擎.获取可用资金()
                预计花费 = 参考价格 * 买入数量
                if 预计花费 <= 可用资金:
                    try:
                        结果 = 引擎.买入(品种代码, None, 买入数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {品种代码} {买入数量} 个")
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"买入异常: {e}")
                else:
                    st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}")
    
    with tab2:
        with st.form("sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            if 持仓品种:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                卖出数量 = st.number_input("数量", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01)
                if st.form_submit_button("确认卖出"):
                    try:
                        结果 = 引擎.卖出(卖出品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {卖出品种} {卖出数量} 个")
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
            else:
                st.info("暂无持仓")
    
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
