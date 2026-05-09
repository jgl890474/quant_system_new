# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测, 交易记录
from 核心 import 订单引擎, 策略加载器, AI引擎

# ========== 初始化数据库 ==========
from 工具 import 数据库
数据库.初始化数据库()

# ========== 初始化 session_state ==========
# 修改初始资金为 100万
if '订单引擎' not in st.session_state:
    st.session_state.订单引擎 = 订单引擎(初始资金=1000000)

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

# ========== 初始化引擎变量 ==========
引擎 = st.session_state.订单引擎
策略加载器 = st.session_state.策略加载器
AI引擎 = st.session_state.AI引擎
策略信号 = st.session_state.策略信号

# ✅ 调试：显示从数据库恢复的持仓数量
st.info(f"🔍 调试信息: 从数据库恢复 {len(引擎.持仓)} 个持仓")
if 引擎.持仓:
    for 品种, pos in 引擎.持仓.items():
        st.write(f"   {品种}: {pos.数量}股, 成本{pos.平均成本:.2f}")

# ========== 初始化风控引擎 ==========
if '风控引擎' not in st.session_state:
    from 核心.风控引擎 import 风控引擎
    st.session_state.风控引擎 = 风控引擎()

风控 = st.session_state.风控引擎

# ========== 页面配置 ==========
st.set_page_config(page_title="量化交易系统 v5.0", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# ========== 紧凑样式 ==========
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem !important;
    }
    header {
        background-color: transparent !important;
    }
    .stApp { font-size: 12px; }
    .stMetric label { font-size: 11px !important; }
    .stMetric value { font-size: 18px !important; }
    .stButton button { font-size: 11px !important; padding: 3px 10px !important; }
    .dataframe td, .dataframe th { font-size: 11px !important; padding: 2px 6px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 4px 12px !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.2rem !important; }
    .element-container { margin-bottom: 4px !important; }
    hr { margin: 4px 0 !important; }
    .stAlert, .stInfo { font-size: 11px !important; padding: 4px !important; }
    .stSelectbox label, .stNumberInput label { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ========== 主标题 ==========
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<h1 style="text-align:center; color:#3b82f6; font-size:28px; margin:0;">📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#94a3b8; font-size:14px; margin-top:5px;">多类目 · 多策略 · AI自动交易 | 云端部署</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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
    
    # 清空数据按钮
    if st.button("🗑️ 清空所有持仓数据", use_container_width=True):
        数据库.清空所有持仓()
        st.success("✅ 已清空")
        st.rerun()
    
    # 刷新策略列表按钮
    if st.button("🔄 刷新策略列表", use_container_width=True):
        try:
            # 清除策略缓存
            if '策略加载器' in st.session_state:
                del st.session_state['策略加载器']
            st.session_state.策略加载器 = 策略加载器()
            # 更新变量
            策略加载器 = st.session_state.策略加载器
            st.success("✅ 策略列表已刷新")
            st.rerun()
        except Exception as e:
            st.error(f"刷新失败: {e}")
    
    st.markdown("---")
    
    # ========== 风控设置 ==========
    st.markdown("### 🛡️ 风控设置")
    
    # 自动监控开关
    自动风控 = st.checkbox("🔴 开启自动止损止盈监控", value=True, help="开启后会自动检查持仓并执行止损止盈")
    
    # 风控参数显示
    if 风控:
        st.caption(f"止损: {风控.止损比例*100:.0f}% | 止盈: {风控.止盈比例*100:.0f}%")
        st.caption(f"移动止损: {'开启' if 风控.移动止损开关 else '关闭'} | 回撤: {风控.移动止损回撤*100:.0f}%")
    
    # ========== 自动监控执行 ==========
    if 自动风控 and 风控:
        try:
            # 监控持仓
            触发 = 风控.监控持仓(引擎)
            
            if 触发:
                st.markdown("### ⚠️ 风控警报")
                for t in 触发:
                    st.warning(f"{t['品种']}: {t['类型']} 触发 (盈亏率: {t['盈亏率']*100:.2f}%)")
                
                # 自动执行平仓
                平仓记录 = 风控.执行自动平仓(引擎)
                if 平仓记录:
                    for r in 平仓记录:
                        st.error(f"✅ 已自动平仓 {r['品种']} ({r['类型']})")
                    st.rerun()
        except Exception as e:
            # 静默处理错误
            pass
    
    st.markdown("---")
    st.caption(f"当前时间: {数据库.获取当前时间()}")

# ========== Tab ==========
tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线", "回测", "交易记录"])

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
    回测.显示(引擎)

with tabs[6]:
    交易记录.显示()
