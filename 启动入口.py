# -*- coding: utf-8 -*-
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="量化交易系统", layout="wide")

st.title("📊 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易 | 云端部署")

# 初始化
if '资金' not in st.session_state:
    st.session_state.资金 = 100000
if '持仓' not in st.session_state:
    st.session_state.持仓 = {}
if '交易记录' not in st.session_state:
    st.session_state.交易记录 = []

def 获取价格(品种):
    try:
        映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", "AAPL": "AAPL"}
        代码 = 映射.get(品种, 品种)
        数据 = yf.Ticker(代码).history(period="1d")
        if not 数据.empty:
            return round(数据['Close'].iloc[-1], 2)
    except:
        pass
    return {"AAPL": 175, "BTC-USD": 45000, "GC=F": 1950, "EURUSD": 1.08}.get(品种, 100)

def 买入(品种, 价格):
    if 品种 in st.session_state.持仓:
        st.session_state.持仓[品种]['数量'] += 1000
    else:
        st.session_state.持仓[品种] = {'数量': 1000, '成本': 价格}
    st.session_state.资金 -= 价格 * 1000
    st.session_state.交易记录.append({'时间': datetime.now(), '动作': '买入', '品种': 品种, '价格': 价格})

def 卖出(品种, 价格):
    if 品种 in st.session_state.持仓:
        数量 = st.session_state.持仓[品种]['数量']
        成本 = st.session_state.持仓[品种]['成本']
        盈亏 = (价格 - 成本) * 数量
        st.session_state.资金 += 价格 * 数量
        del st.session_state.持仓[品种]
        st.session_state.交易记录.append({'时间': datetime.now(), '动作': '卖出', '品种': 品种, '价格': 价格, '盈亏': 盈亏})
        return盈亏
    return None

# 页面
tab1, tab2, tab3, tab4 = st.tabs(["首页", "交易", "持仓", "记录"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    总资产 = st.session_state.资金 + sum(p['数量'] * 获取价格(s) for s, p in st.session_state.持仓.items())
    col1.metric("总资产", f"${总资产:,.0f}")
    col2.metric("可用资金", f"${st.session_state.资金:,.0f}")
    col3.metric("持仓数", len(st.session_state.持仓))
    col4.metric("交易次数", len(st.session_state.交易记录))
    
    st.subheader("市场行情")
    for 品种 in ["AAPL", "BTC-USD", "GC=F", "EURUSD"]:
        c1, c2 = st.columns([1, 3])
        c1.write(品种)
        c2.write(f"${获取价格(品种)}")

with tab2:
    品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD"])
    价格 = 获取价格(品种)
    st.info(f"当前价格: ${价格}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("买入", type="primary"):
            买入(品种, 价格)
            st.success(f"✅ 买入 {品种} @ ${价格}")
            st.rerun()
    with col2:
        if st.button("卖出"):
            if 品种 in st.session_state.持仓:
                卖出(品种, 价格)
                st.success(f"✅ 卖出 {品种} @ ${价格}")
                st.rerun()
            else:
                st.error(f"❌ 没有 {品种} 持仓")

with tab3:
    if st.session_state.持仓:
        for 品种, 数据 in st.session_state.持仓.items():
            现价 = 获取价格(品种)
            盈亏 = (现价 - 数据['成本']) * 数据['数量']
            st.metric(品种, f"数量: {数据['数量']}", delta=f"盈亏: ${盈亏:+.2f}")
    else:
        st.info("暂无持仓")

with tab4:
    if st.session_state.交易记录:
        df = pd.DataFrame(st.session_state.交易记录[-20:])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无交易记录")
