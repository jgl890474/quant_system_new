# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 导入会话持久化 ==========
from 工具.会话持久化 import auto_restore_session, auto_save_session

# ========== 导入模块 ==========
try:
    from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测, 交易记录
except Exception as e:
    st.error(f"❌ 前端模块导入失败: {e}")
    st.stop()

try:
    from 核心 import 订单引擎
except Exception as e:
    st.error(f"❌ 订单引擎导入失败: {e}")
    st.stop()

try:
    from 工具 import 数据库
except Exception as e:
    st.error(f"❌ 数据库模块导入失败: {e}")
    st.stop()

try:
    from 核心 import 行情获取
except ImportError:
    行情获取 = None

# ========== 导入策略运行器 ==========
try:
    from 核心.策略运行器 import 策略运行器
except ImportError:
    class 策略运行器:
        _策略状态 = {}
        @classmethod
        def 设置策略状态(cls, 名称, 状态): pass
        @classmethod
        def 获取策略状态(cls, 名称): return True

# ========== 导入自动交易模块 ==========
try:
    from 脚本.自动交易 import 获取机器人
    自动交易可用 = True
except ImportError:
    自动交易可用 = False

# ========== 导入策略调度器 ==========
try:
    from 自动化.策略调度器 import 获取策略调度器
    策略调度器可用 = True
except ImportError:
    策略调度器可用 = False

# ========== 导入策略加载器 ==========
from 核心.策略加载器 import 策略加载器 as 策略加载器类

# ========== 页面配置 ==========
st.set_page_config(
    page_title="量化交易系统 v5.0", 
    page_icon="📈", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ========== 恢复会话状态 ==========
auto_restore_session()

# ========== 初始化 session_state ==========
INITIAL_CAPITAL = 1000000

if '订单引擎' not in st.session_state:
    st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)

if '策略加载器' not in st.session_state:
    st.session_state.策略加载器 = 策略加载器类()

if 'AI引擎' not in st.session_state:
    class 简单AI引擎:
        def 获取信号(self, 数据):
            return {"信号": "无", "置信度": 0}
        def AI推荐(self, 市场, 策略类型):
            return {"推荐": []}
    st.session_state.AI引擎 = 简单AI引擎()

if '策略信号' not in st.session_state:
    st.session_state.策略信号 = {}

if '成功消息' not in st.session_state:
    st.session_state.成功消息 = None

if '错误消息' not in st.session_state:
    st.session_state.错误消息 = None

if '自动交易器' not in st.session_state:
    st.session_state.自动交易器 = None

if '自动交易开关' not in st.session_state:
    st.session_state.自动交易开关 = False

if '后台服务已启动' not in st.session_state:
    st.session_state.后台服务已启动 = False

if '策略调度器' not in st.session_state:
    st.session_state.策略调度器 = None

# ========== 初始化风控引擎 ==========
if '风控引擎' not in st.session_state:
    class 简单风控引擎:
        def __init__(self):
            self.止损比例 = 0.05
            self.止盈比例 = 0.03
    st.session_state.风控引擎 = 简单风控引擎()

# ========== 获取变量 ==========
引擎 = st.session_state.订单引擎
策略加载器 = st.session_state.策略加载器
AI引擎 = st.session_state.AI引擎
风控 = st.session_state.风控引擎

# ========== 紧凑样式 ==========
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem !important; }
    .stApp { font-size: 12px; }
    .stButton button { font-size: 11px !important; padding: 3px 10px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

# ========== 主标题 ==========
st.markdown('<h1 style="text-align:center; color:#3b82f6; font-size:28px;">📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#94a3b8;">多类目 · 多策略 · AI自动交易 | 云端部署</p>', unsafe_allow_html=True)

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
    
    if st.button("🗑️ 清空所有持仓数据", width="stretch"):
        try:
            数据库.清空所有持仓()
            st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)
            引擎 = st.session_state.订单引擎
            st.success("✅ 已清空")
            st.rerun()
        except Exception as e:
            st.error(f"清空失败: {e}")
    
    if st.button("🔄 刷新持仓", width="stretch"):
        if hasattr(引擎, '_恢复持仓'):
            引擎._恢复持仓()
        st.rerun()
    
    st.markdown("---")
    
    # 自动交易控制
    st.markdown("### 🤖 自动交易")
    新开关 = st.checkbox("开启自动交易", value=st.session_state.自动交易开关)
    if 新开关 != st.session_state.自动交易开关:
        st.session_state.自动交易开关 = 新开关
        st.rerun()
    
    st.caption(f"📊 今日交易: 0 次")
    
    st.markdown("---")
    
    # 持仓监控
    st.markdown("### 💼 持仓")
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            st.caption(f"{品种}: {数量:.4f}" if 数量 < 1 else f"{品种}: {int(数量)}股")
    else:
        st.info("暂无持仓")
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ========== 安全调用函数 ==========
def 安全调用(模块, 默认信息="模块开发中"):
    if 模块 is None:
        st.info(默认信息)
        return
    
    if not hasattr(模块, '显示'):
        st.info(默认信息)
        return
    
    # 每次都从 session_state 获取最新值
    _引擎 = st.session_state.订单引擎
    _策略加载器 = st.session_state.策略加载器
    _AI引擎 = st.session_state.AI引擎
    
    # 直接调用
    try:
        模块.显示(_引擎, _策略加载器, _AI引擎)
    except TypeError:
        try:
            模块.显示(_引擎, _策略加载器)
        except TypeError:
            try:
                模块.显示(_引擎)
            except Exception as e:
                st.info(f"{默认信息} - {e}")

# ========== Tab导航 ==========
tabs = st.tabs(["🏠 首页", "📊 策略中心", "🤖 AI交易", "💼 持仓管理", "💰 资金曲线", "📈 回测", "📋 交易记录"])

with tabs[0]:
    安全调用(首页, "首页模块开发中")

with tabs[1]:
    安全调用(策略中心, "策略中心模块开发中")

with tabs[2]:
    安全调用(AI交易, "AI交易模块开发中")

with tabs[3]:
    安全调用(持仓管理, "持仓管理模块开发中")

with tabs[4]:
    安全调用(资金曲线, "资金曲线模块开发中")

with tabs[5]:
    安全调用(回测, "回测模块开发中")

with tabs[6]:
    安全调用(交易记录, "交易记录模块开发中")

# ========== 底部 ==========
st.markdown("---")
st.caption("⚠️ 风险提示：量化交易存在风险，历史回测结果不代表未来收益。")

# ========== 保存会话状态 ==========
auto_save_session()
