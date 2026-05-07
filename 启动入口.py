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

# ========== 临时修复：清空错误持仓数据 ==========
if '数据已修复' not in st.session_state:
    try:
        持仓 = 数据库.获取所有持仓()
        if 持仓:
            # 检查是否有异常数据（持仓市值异常大）
            总资产 = 100000
            for 品种, 数据 in 持仓.items():
                if 数据['数量'] > 10000 or 数据['平均成本'] > 10000:
                    数据库.清空所有持仓()
                    st.warning("⚠️ 已清空异常持仓数据，请刷新页面")
                    break
        st.session_state['数据已修复'] = True
    except:
        pass

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

# ========== 全局样式 ==========
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric value { color: #f8fafc !important; }
    .stButton > button { background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; border: none; border-radius: 0.5rem; }
    .stButton > button:hover { transform: translateY(-1px); }
    .stTabs [data-baseweb="tab-list"] { background: #1e293b; border-radius: 0.75rem; }
    .stTabs [aria-selected="true"] { background: #3b82f6; color: white; }
    [data-testid="stSidebar"] { background: #1e293b; border-right: 1px solid #334155; }
    .dataframe { background: #1e293b !important; border-radius: 0.75rem !important; }
    .dataframe th { background: #334155 !important; color: #f8fafc !important; }
    .dataframe td { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align:center; color:#3b82f6">📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#94a3b8">多类目 · 多策略 · AI自动交易 | 云端部署</p>', unsafe_allow_html=True)

# ========== 显示消息 ==========
if st.session_state.成功消息:
    st.success(st.session_state.成功消息)
    st.session_state.成功消息 = None

if st.session_state.错误消息:
    st.error(st.session_state.错误消息)
    st.session_state.错误消息 = None

# ========== 菜单栏添加清空数据按钮 ==========
with st.sidebar:
    st.markdown("### 🛠️ 系统工具")
    if st.button("🗑️ 清空所有持仓数据", use_container_width=True):
        数据库.清空所有持仓()
        st.success("✅ 已清空所有持仓数据，请重启应用")
        st.session_state['数据已修复'] = False
        st.rerun()
    
    st.markdown("---")
    st.caption(f"当前时间: {数据库.获取当前时间()}")
    st.caption(f"数据版本: v5.0")

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
