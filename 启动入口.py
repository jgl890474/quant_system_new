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
</style>
""", unsafe_allow_html=True)

st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 | 云端部署</div>', unsafe_allow_html=True)

# ========== 创建6个Tab ==========
tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线", "回测"])

引擎 = st.session_state.订单引擎
策略加载器 = st.session_state.策略加载器
AI引擎 = st.session_state.AI引擎
策略信号 = st.session_state.策略信号

with tabs[0]:
    首页.显示(引擎)

with tabs[1]:
    策略中心.显示(引擎, 策略加载器, 策略信号)

with tabs[2]:
    AI交易.显示(引擎, 策略加载器, AI引擎)

with tabs[3]:
    持仓管理.显示(引擎, 策略加载器, AI引擎)

with tabs[4]:
    资金曲线.显示(引擎)

with tabs[5]:
    回测.显示()
