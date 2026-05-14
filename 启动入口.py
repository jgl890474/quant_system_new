# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ========== 导入模块 ==========
try:
    from 前端 import 首页, 策略中心, AI交易, 持仓管理, 资金曲线, 回测, 交易记录
except Exception as e:
    st.error(f"❌ 前端模块导入失败: {e}")
    st.stop()

try:
    from 核心 import 订单引擎
except Exception as e:
    st.error(f"❌ 订单引擎导入失败，请检查核心/订单引擎.py文件")
    st.code(f"错误详情: {e}")
    st.stop()

try:
    from 工具 import 数据库
except Exception as e:
    st.error(f"❌ 数据库模块导入失败: {e}")
    st.stop()

# ========== 导入行情获取 ==========
try:
    from 核心 import 行情获取
except ImportError:
    行情获取 = None
    st.warning("⚠️ 行情获取模块导入失败")

# ========== 导入策略运行器（用于策略状态管理） ==========
try:
    from 核心.策略运行器 import 策略运行器
except ImportError:
    # 如果策略运行器不存在，创建一个简单的兼容类
    class 策略运行器:
        _策略状态 = {}
        @classmethod
        def 设置策略状态(cls, 名称, 状态): pass
        @classmethod
        def 获取策略状态(cls, 名称): return True
    st.warning("⚠️ 策略运行器模块导入失败，使用兼容模式")

# ========== 初始化数据库 ==========
try:
    数据库.初始化数据库()
except Exception as e:
    st.warning(f"数据库初始化警告: {e}")

# ========== 初始化 session_state ==========
INITIAL_CAPITAL = 1000000

if '订单引擎' not in st.session_state:
    st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)

# 初始化策略加载器（兼容处理）
if '策略加载器' not in st.session_state:
    try:
        from 核心.策略加载器 import 策略加载器
        st.session_state.策略加载器 = 策略加载器()
    except ImportError:
        class 简单策略加载器:
            def 获取策略列表(self):
                return []
            def 加载策略(self, 策略名):
                return None
        st.session_state.策略加载器 = 简单策略加载器()

# ========== 初始化策略状态（所有策略默认启用） ==========
try:
    策略列表 = st.session_state.策略加载器.获取策略()
    for 策略 in 策略列表:
        策略名称 = 策略.get("名称", "")
        if 策略名称:
            策略运行器.设置策略状态(策略名称, True)
    print(f"✅ 已初始化 {len(策略列表)} 个策略状态")
except Exception as e:
    print(f"策略状态初始化失败: {e}")

# 初始化AI引擎（兼容处理）
if 'AI引擎' not in st.session_state:
    try:
        from 核心.AI引擎 import AI引擎
        st.session_state.AI引擎 = AI引擎()
    except ImportError:
        class 简单AI引擎:
            def 获取信号(self, 数据):
                return {"信号": "无", "置信度": 0, "理由": "AI引擎未配置"}
            def 分析市场(self):
                return {"建议": "无法获取AI分析"}
            def AI推荐(self, 市场, 策略类型):
                return {"推荐": []}
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
    
    if st.button("🗑️ 清空所有持仓数据", width="stretch"):
        try:
            数据库.清空所有持仓()
            st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)
            引擎 = st.session_state.订单引擎
            st.success("✅ 已清空")
            st.rerun()
        except:
            st.error("清空失败")
    
    if st.button("🔄 刷新策略列表", width="stretch"):
        try:
            if hasattr(st.session_state.策略加载器, '刷新'):
                st.session_state.策略加载器.刷新()
            st.success("✅ 策略列表已刷新")
            st.rerun()
        except Exception as e:
            st.error(f"刷新失败: {e}")
    
    if st.button("🔄 强制刷新持仓", width="stretch"):
        try:
            if hasattr(引擎, '_恢复持仓'):
                引擎._恢复持仓()
            st.session_state.订单引擎 = 引擎
            st.success(f"✅ 持仓已刷新，当前持仓: {len(引擎.持仓)} 个品种")
            st.rerun()
        except Exception as e:
            st.error(f"刷新失败: {e}")
    
    st.markdown("---")
    
    # ========== 持仓监控 ==========
    st.markdown("### 💼 持仓监控")
    
    if hasattr(引擎, '持仓') and 引擎.持仓:
        st.caption(f"📊 当前持仓数量: {len(引擎.持仓)}")
        
        # 计算实时总资产
        实时总资产 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', INITIAL_CAPITAL)
        
        for 品种, pos in 引擎.持仓.items():
            平均成本 = getattr(pos, '平均成本', 0)
            数量 = getattr(pos, '数量', 0)
            
            # 获取实时价格
            try:
                if 行情获取:
                    价格结果 = 行情获取.获取价格(品种)
                    if 价格结果 and hasattr(价格结果, '价格'):
                        现价 = 价格结果.价格
                    else:
                        现价 = 平均成本
                else:
                    现价 = 平均成本
            except Exception:
                现价 = 平均成本
            
            # 更新持仓当前价格
            if hasattr(pos, '当前价格'):
                pos.当前价格 = 现价
            
            # 计算盈亏
            盈亏 = (现价 - 平均成本) * 数量
            实时总资产 += 数量 * 现价
            
            # 格式化数量显示
            if 品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                数量显示 = f"{数量:.4f}个"
            else:
                数量显示 = f"{int(数量)}股"
            
            st.metric(
                label=f"{品种}",
                value=数量显示,
                delta=f"成本: ¥{平均成本:.2f} | 盈亏: ¥{盈亏:+.2f}"
            )
        
        st.markdown("---")
        
        # 显示总资产和可用资金（使用实时计算）
        st.metric("💰 总资产", f"¥{实时总资产:,.0f}")
        st.metric("💵 可用资金", f"¥{引擎.获取可用资金():,.0f}" if hasattr(引擎, '获取可用资金') else f"¥{getattr(引擎, '可用资金', 0):,.0f}")
    else:
        st.info("暂无持仓")
        if hasattr(引擎, '交易记录') and 引擎.交易记录:
            with st.expander("📋 最近交易记录", expanded=False):
                for t in 引擎.交易记录[-5:]:
                    st.write(f"{t['时间']} - {t['动作']} {t['品种']} {t['数量']}股 @ {t['价格']}")
    
    st.markdown("---")
    st.markdown("### 🛡️ 风控设置")
    
    自动风控 = st.checkbox("🔴 开启自动止损止盈监控", value=False, help="开启后会自动检查持仓并执行止损止盈")
    
    if hasattr(风控, '止损比例'):
        st.caption(f"止损: {风控.止损比例*100:.0f}% | 止盈: {风控.止盈比例*100:.0f}%")
    
    st.markdown("---")
    try:
        st.caption(f"当前时间: {数据库.获取当前时间()}")
    except:
        st.caption(f"当前时间: 获取失败")

# ========== 安全调用函数包装器（修复回测模块参数问题） ==========
def 安全调用(模块, 默认信息="模块开发中"):
    """
    安全调用模块的显示函数
    自动适配不同模块的参数签名
    """
    if 模块 is None:
        st.info(默认信息)
        return
    
    if not hasattr(模块, '显示'):
        st.info(默认信息)
        return
    
    # 获取显示函数的参数签名
    import inspect
    try:
        sig = inspect.signature(模块.显示)
        params = list(sig.parameters.keys())
        
        # 根据参数数量决定传入什么
        if len(params) == 0:
            # 无参数
            模块.显示()
        elif len(params) == 1:
            # 只接受引擎参数
            模块.显示(引擎)
        elif len(params) == 2:
            # 接受引擎和策略加载器
            模块.显示(引擎, 策略加载器)
        elif len(params) >= 3:
            # 接受三个或更多参数
            try:
                模块.显示(引擎, 策略加载器, AI引擎)
            except:
                模块.显示(引擎, 策略加载器)
        else:
            模块.显示()
            
    except Exception as e:
        # 如果获取签名失败，尝试最常见的调用方式
        try:
            模块.显示(引擎)
        except TypeError:
            try:
                模块.显示(引擎, 策略加载器)
            except TypeError:
                try:
                    模块.显示(引擎, 策略加载器, AI引擎)
                except:
                    st.info(默认信息)

# ========== 页面刷新监听 ==========
query_params = st.query_params
if query_params.get("refresh") == "true":
    if hasattr(引擎, '_恢复持仓'):
        引擎._恢复持仓()
        st.session_state.订单引擎 = 引擎
    st.query_params.clear()

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

# ========== 底部风险提示 ==========
st.markdown("---")
st.caption("⚠️ 风险提示：量化交易存在风险，历史回测结果不代表未来收益。请理性投资，注意风险控制。")
