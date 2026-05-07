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

if '成功消息' not in st.session_state:
    st.session_state.成功消息 = None

if '错误消息' not in st.session_state:
    st.session_state.错误消息 = None

# ========== 初始化风控引擎 ==========
if '风控引擎' not in st.session_state:
    from 核心.风控引擎 import 风控引擎
    st.session_state.风控引擎 = 风控引擎()

# ========== 页面配置 ==========
st.set_page_config(page_title="量化交易系统 v5.0", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ========== 主标题 ==========
st.markdown("""
<div style="text-align:center; padding:0.5rem 0;">
    <h1 style="color:#3b82f6; font-size:28px; margin:0;">📊 量化交易系统 v5.0</h1>
    <p style="color:#94a3b8; font-size:13px; margin:0;">多类目 · 多策略 · AI自动交易 | 云端部署</p>
</div>
""", unsafe_allow_html=True)

# ========== 紧凑样式 ==========
st.markdown("""
<style>
    .stApp { font-size: 12px; }
    .stMetric label { font-size: 11px !important; }
    .stMetric value { font-size: 18px !important; }
    .stButton button { font-size: 11px !important; padding: 3px 10px !important; }
    .dataframe td, .dataframe th { font-size: 11px !important; padding: 2px 6px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 4px 12px !important; }
    .block-container { padding-top: 0.2rem !important; padding-bottom: 0.2rem !important; }
    .element-container { margin-bottom: 4px !important; }
    hr { margin: 4px 0 !important; }
    .stAlert, .stInfo { font-size: 11px !important; padding: 4px !important; }
    .stSelectbox label, .stNumberInput label { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ========== 显示消息 ==========
if st.session_state.成功消息:
    st.success(st.session_state.成功消息)
    st.session_state.成功消息 = None

if st.session_state.错误消息:
    st.error(st.session_state.错误消息)
    st.session_state.错误消息 = None

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("### 🛠️ 系统工具")
    if st.button("🗑️ 清空所有持仓数据", use_container_width=True):
        数据库.清空所有持仓()
        st.success("✅ 已清空")
        st.rerun()
    st.caption(f"当前时间: {数据库.获取当前时间()}")

# ========== Tab ==========
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
