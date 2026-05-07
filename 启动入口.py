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

# ========== 全局样式 ==========
st.markdown("""
<style>
    /* 全局字体缩小 */
    .stApp { font-size: 13px; }
    
    /* 指标卡片字体 */
    .stMetric label { font-size: 12px !important; }
    .stMetric value { font-size: 20px !important; }
    
    /* 标题缩小 */
    h1 { font-size: 22px !important; }
    h3 { font-size: 16px !important; }
    h4 { font-size: 14px !important; }
    
    /* 按钮缩小 */
    .stButton button { font-size: 12px !important; padding: 4px 12px !important; }
    
    /* 表格字体 */
    .dataframe td, .dataframe th { font-size: 12px !important; padding: 4px 8px !important; }
    
    /* 选择框字体 */
    .stSelectbox label, .stNumberInput label { font-size: 12px !important; }
    
    /* 信息框字体 */
    .stAlert, .stInfo, .stWarning, .stSuccess { font-size: 12px !important; padding: 8px !important; }
    
    /* 指标卡片间距 */
    .stMetric { padding: 8px !important; }
    
    /* 行列间距 */
    .row-widget { margin-bottom: 8px !important; }
    
    /* 分割线样式 */
    hr { margin: 8px 0 !important; border-color: #334155 !important; }
    
    /* 标签页字体 */
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; padding: 6px 16px !important; }
    
    /* 侧边栏字体 */
    [data-testid="stSidebar"] { font-size: 12px !important; }
    
    /* 展开器字体 */
    .streamlit-expanderHeader { font-size: 13px !important; }
    
    /* 代码块字体 */
    code { font-size: 11px !important; }
    
    /* 紧凑布局 */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; }
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
        st.success("✅ 已清空所有持仓数据")
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
