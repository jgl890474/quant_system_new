# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 导入模块 ==========
from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测, 交易记录
from 核心 import 订单引擎
from 工具 import 数据库

# ========== 初始化数据库 ==========
数据库.初始化数据库()

# ========== 初始化 session_state ==========
INITIAL_CAPITAL = 1000000  # 100万

# 初始化订单引擎（兼容参数名）
if '订单引擎' not in st.session_state:
    try:
        # 尝试使用中文参数
        st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)
    except TypeError:
        try:
            # 尝试使用英文参数
            st.session_state.订单引擎 = 订单引擎(INITIAL_CAPITAL=INITIAL_CAPITAL)
        except TypeError:
            # 使用默认参数
            st.session_state.订单引擎 = 订单引擎()

# 初始化策略加载器（兼容处理）
if '策略加载器' not in st.session_state:
    try:
        from 核心.策略加载器 import 策略加载器
        st.session_state.策略加载器 = 策略加载器()
    except ImportError:
        # 如果策略加载器不存在，创建一个简单的替代
        class 简单策略加载器:
            def 获取策略列表(self):
                return []
            def 加载策略(self, 策略名):
                return None
        st.session_state.策略加载器 = 简单策略加载器()

# 初始化AI引擎（兼容处理）
if 'AI引擎' not in st.session_state:
    try:
        from 核心.AI引擎 import AI引擎
        st.session_state.AI引擎 = AI引擎()
    except ImportError:
        # 如果AI引擎不存在，创建一个简单的替代
        class 简单AI引擎:
            def 获取信号(self, 数据):
                return {"信号": "无", "置信度": 0, "理由": "AI引擎未配置"}
            def 分析市场(self):
                return {"建议": "无法获取AI分析"}
        st.session_state.AI引擎 = 简单AI引擎()

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

# ========== 初始化风控引擎（兼容处理） ==========
if '风控引擎' not in st.session_state:
    try:
        from 核心.风控引擎 import 风控引擎
        st.session_state.风控引擎 = 风控引擎()
    except ImportError:
        # 如果风控引擎不存在，创建一个简单的替代
        class 简单风控引擎:
            def __init__(self):
                self.止损比例 = 0.05
                self.止盈比例 = 0.03
                self.移动止损开关 = False
                self.移动止损回撤 = 0.02
            def 监控持仓(self, 引擎):
                return []
            def 执行自动平仓(self, 引擎):
                return []
        st.session_state.风控引擎 = 简单风控引擎()

风控 = st.session_state.风控引擎

# ========== 页面配置 ==========
st.set_page_config(
    page_title="量化交易系统 v5.0", 
    page_icon="📈", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

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
    if st.button("🗑️ 清空所有持仓数据", width="stretch"):
        数据库.清空所有持仓()
        st.success("✅ 已清空")
        st.rerun()
    
    # 刷新策略列表按钮
    if st.button("🔄 刷新策略列表", width="stretch"):
        try:
            if hasattr(st.session_state.策略加载器, '刷新'):
                st.session_state.策略加载器.刷新()
            st.success("✅ 策略列表已刷新")
            st.rerun()
        except Exception as e:
            st.error(f"刷新失败: {e}")
    
    st.markdown("---")
    
    # ========== 持仓监控显示 ==========
    st.markdown("### 💼 持仓监控")
    
    if hasattr(引擎, '持仓') and 引擎.持仓:
        st.caption(f"📊 当前持仓数量: {len(引擎.持仓)}")
        
        # 显示持仓明细
        for 品种, pos in 引擎.持仓.items():
            # 计算当前盈亏
            现价 = getattr(pos, '当前价格', getattr(pos, '平均成本', 0))
            平均成本 = getattr(pos, '平均成本', 0)
            数量 = getattr(pos, '数量', 0)
            盈亏 = (现价 - 平均成本) * 数量
            st.metric(
                label=f"{品种}",
                value=f"{数量}股",
                delta=f"成本: ¥{平均成本:.2f} | 盈亏: ¥{盈亏:+.2f}"
            )
        
        # 显示总资产和可用资金
        st.markdown("---")
        try:
            st.metric("💰 总资产", f"¥{引擎.获取总资产():,.0f}")
            st.metric("💵 可用资金", f"¥{引擎.获取可用资金():,.0f}")
        except:
            st.metric("💰 总资产", "计算中")
            st.metric("💵 可用资金", "计算中")
    else:
        st.info("暂无持仓")
    
    st.markdown("---")
    
    # ========== 风控设置 ==========
    st.markdown("### 🛡️ 风控设置")
    
    自动风控 = st.checkbox("🔴 开启自动止损止盈监控", value=False, help="开启后会自动检查持仓并执行止损止盈（谨慎使用）")
    
    if hasattr(风控, '止损比例'):
        st.caption(f"止损: {风控.止损比例*100:.0f}% | 止盈: {风控.止盈比例*100:.0f}%")
        if hasattr(风控, '移动止损开关'):
            st.caption(f"移动止损: {'开启' if 风控.移动止损开关 else '关闭'} | 回撤: {风控.移动止损回撤*100:.0f}%")
    
    st.markdown("---")
    st.caption(f"当前时间: {数据库.获取当前时间()}")

# ========== 创建前端模块的兼容包装 ==========

# 如果某个前端模块不存在或函数不兼容，创建默认显示函数
def 创建默认显示(模块名):
    def 默认显示(*args, **kwargs):
        st.info(f"⚠️ 模块 '{模块名}' 尚未配置")
        st.markdown("### 📌 使用说明")
        st.markdown(f"请创建 `前端/{模块名}.py` 文件，并实现 `显示()` 函数。")
        st.markdown("**示例代码：**")
        st.code(f"""
# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    st.subheader("{模块名}")
    st.info("功能开发中...")
        """, language="python")
    return 默认显示

# 安全获取前端模块的显示函数
def 安全获取显示函数(模块, 模块名):
    if hasattr(模块, '显示'):
        return 模块.显示
    else:
        return 创建默认显示(模块名)

# ========== Tab ==========
tabs = st.tabs(["🏠 首页", "📊 策略中心", "🤖 AI交易", "💼 持仓管理", "💰 资金曲线", "📈 回测", "📋 交易记录"])

# 获取各模块的显示函数
首页显示 = 安全获取显示函数(首页, "首页")
策略中心显示 = 安全获取显示函数(策略中心, "策略中心")
AI交易显示 = 安全获取显示函数(AI交易, "AI交易")
持仓管理显示 = 安全获取显示函数(持仓管理, "持仓管理")
资金曲线显示 = 安全获取显示函数(资金曲线, "资金曲线")
回测显示 = 安全获取显示函数(回测, "回测")
交易记录显示 = 安全获取显示函数(交易记录, "交易记录")

with tabs[0]:
    try:
        首页显示(引擎, 策略加载器, AI引擎)
    except TypeError:
        try:
            首页显示(引擎, 策略加载器)
        except TypeError:
            try:
                首页显示(引擎)
            except:
                首页显示()

with tabs[1]:
    try:
        策略中心显示(引擎, 策略加载器, 策略信号)
    except TypeError:
        try:
            策略中心显示(引擎, 策略加载器)
        except TypeError:
            try:
                策略中心显示(引擎)
            except:
                策略中心显示()

with tabs[2]:
    try:
        AI交易显示(引擎, 策略加载器, AI引擎)
    except TypeError:
        try:
            AI交易显示(引擎, 策略加载器)
        except TypeError:
            try:
                AI交易显示(引擎)
            except:
                AI交易显示()

with tabs[3]:
    try:
        持仓管理显示(引擎, 策略加载器, AI引擎)
    except TypeError:
        try:
            持仓管理显示(引擎, 策略加载器)
        except TypeError:
            try:
                持仓管理显示(引擎)
            except:
                持仓管理显示()

with tabs[4]:
    try:
        资金曲线显示(引擎)
    except TypeError:
        资金曲线显示()

with tabs[5]:
    try:
        回测显示(引擎)
    except TypeError:
        回测显示()

with tabs[6]:
    try:
        交易记录显示()
    except TypeError:
        交易记录显示(引擎)

# ========== 页脚 ==========
st.markdown("---")
st.caption("⚠️ 风险提示：量化交易存在风险，历史回测结果不代表未来收益。请理性投资，注意风险控制。")
