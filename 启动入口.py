# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测
from 核心 import 订单引擎, 策略加载器, AI引擎

# ========== 初始化数据库 ==========
from 工具 import 数据库
数据库.初始化数据库()

# ========== 初始化 session_state ==========
if '订单引擎' not in st.session_state:
    st.session_state.订单引擎 = 订单引擎()

if '策略加载器' not in st.session_state:
    st.session_state.策略加载器 = 策略加载器()

if 'AI引擎' not in st.session_state:
    st.session_state.AI引擎 = AI引擎()

if '策略信号' not in st.session_state:
    st.session_state.策略信号 = {}

# ========== 初始化风控引擎 ==========
if '风控引擎' not in st.session_state:
    from 核心.风控引擎 import 风控引擎
    st.session_state.风控引擎 = 风控引擎()

# ========== 页面配置 ==========
st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 10px; text-align: center; }
    h1 { color: white; text-align: center; font-size: 24px; }
    .caption { text-align: center; color: #8892b0; font-size: 12px; margin-bottom: 20px; }
    .category-title { color: #00d2ff; font-size: 16px; margin-top: 20px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 | 云端部署</div>', unsafe_allow_html=True)

# ========== 创建7个Tab ==========
tab_names = ["首页", "策略中心", "AI交易", "持仓管理", "资金曲线", "回测", "快速交易"]
tabs = st.tabs(tab_names)

引擎 = st.session_state.订单引擎
策略加载器 = st.session_state.策略加载器
AI引擎 = st.session_state.AI引擎
策略信号 = st.session_state.策略信号

# Tab 0: 首页
with tabs[0]:
    首页.显示(引擎)

# Tab 1: 策略中心
with tabs[1]:
    策略中心.显示(引擎, 策略加载器, 策略信号)

# Tab 2: AI交易
with tabs[2]:
    AI交易.显示(引擎, 策略加载器, AI引擎)

# Tab 3: 持仓管理
with tabs[3]:
    持仓管理.显示(引擎, 策略加载器, AI引擎)

# Tab 4: 资金曲线
with tabs[4]:
    资金曲线.显示(引擎)

# Tab 5: 回测
with tabs[5]:
    回测.显示()

# Tab 6: 快速交易
with tabs[6]:
    st.markdown("### 快速交易")
    
    品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD"])
    
    try:
        from 核心 import 行情获取
        行情数据 = 行情获取.获取价格(品种)
        当前价格 = 行情数据.价格
    except Exception as e:
        当前价格 = 100
        st.warning(f"获取价格失败: {e}")
    
    st.info(f"当前价格: {当前价格:.4f}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("买入", type="primary"):
            引擎.买入(品种, 当前价格)
            st.rerun()
    with col2:
        if st.button("卖出"):
            引擎.卖出(品种, 当前价格)
            st.rerun()
