# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
import random
import hashlib
import threading
import time
from datetime import datetime
from pathlib import Path

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
    from 脚本.自动交易 import 自动交易机器人, 获取机器人
    自动交易可用 = True
except ImportError:
    自动交易可用 = False

# ========== 导入定时任务模块 ==========
try:
    from 工具 import 定时任务 as 定时任务模块
    定时任务可用 = True
except ImportError:
    定时任务可用 = False

# ========== 导入消息推送模块 ==========
try:
    from 工具 import 消息推送 as 推送
    推送可用 = True
except ImportError:
    推送可用 = False

# ========== 导入策略调度器 ==========
try:
    from 自动化.策略调度器 import 获取策略调度器
    策略调度器可用 = True
except ImportError:
    策略调度器可用 = False

# ========== 初始化数据库 ==========
try:
    数据库.初始化数据库()
except Exception:
    pass

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

# ========== 初始化策略加载器 ==========
if '策略加载器' not in st.session_state:
    try:
        from 核心.策略加载器 import 策略加载器
        st.session_state.策略加载器 = 策略加载器()
    except Exception:
        class 简单策略加载器:
            def 获取策略(self):
                return [
                    {"名称": "加密双均线1", "类别": "₿ 加密货币", "品种": "BTC-USD"},
                    {"名称": "加密风控策略", "类别": "₿ 加密货币", "品种": "BTC-USD"},
                    {"名称": "A股隔夜套利策略3", "类别": "📈 A股", "品种": "000001.SS"},
                    {"名称": "A股双均线1", "类别": "📈 A股", "品种": "000001.SS"},
                    {"名称": "A股量价策略2", "类别": "📈 A股", "品种": "000001.SS"},
                    {"名称": "美股简单策略1", "类别": "🇺🇸 美股", "品种": "AAPL"},
                    {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
                ]
            def 获取策略列表(self):
                return self.获取策略()
            def 获取策略列表_带状态(self):
                return [{"名称": s["名称"], "类别": s["类别"], "品种": s["品种"], "启用": True} for s in self.获取策略()]
        st.session_state.策略加载器 = 简单策略加载器()

# ========== 初始化策略状态 ==========
try:
    if hasattr(st.session_state.策略加载器, '获取策略'):
        策略列表 = st.session_state.策略加载器.获取策略()
    else:
        策略列表 = []
    
    if 策略列表 and isinstance(策略列表, list):
        for 策略 in 策略列表:
            if isinstance(策略, dict):
                策略名称 = 策略.get("名称", "")
            elif isinstance(策略, str):
                策略名称 = 策略
            else:
                策略名称 = getattr(策略, "名称", str(策略))
            
            if 策略名称:
                if hasattr(策略运行器, '设置策略状态'):
                    策略运行器.设置策略状态(策略名称, True)
except Exception:
    pass

# ========== 初始化AI引擎 ==========
if 'AI引擎' not in st.session_state:
    class 简单AI引擎:
        def 获取信号(self, 数据):
            return {"信号": "无", "置信度": 0}
    st.session_state.AI引擎 = 简单AI引擎()

if '策略信号' not in st.session_state:
    st.session_state.策略信号 = {}

if '成功消息' not in st.session_state:
    st.session_state.成功消息 = None

if '错误消息' not in st.session_state:
    st.session_state.错误消息 = None

# ========== 自动交易器状态 ==========
if '自动交易器' not in st.session_state:
    st.session_state.自动交易器 = None

# ========== 从数据库读取自动交易开关状态 ==========
if '自动交易开关' not in st.session_state:
    try:
        保存的状态 = 数据库.读取自动交易状态()
        st.session_state.自动交易开关 = 保存的状态
        print(f"📂 从数据库读取自动交易状态: {'开启' if 保存的状态 else '关闭'}")
    except Exception as e:
        print(f"读取自动交易状态失败: {e}")
        st.session_state.自动交易开关 = False

if '后台服务已启动' not in st.session_state:
    st.session_state.后台服务已启动 = False

if '策略调度器' not in st.session_state:
    st.session_state.策略调度器 = None

# ========== 初始化引擎变量 ==========
引擎 = st.session_state.订单引擎
策略加载器 = st.session_state.策略加载器
AI引擎 = st.session_state.AI引擎

# ========== 初始化风控引擎 ==========
if '风控引擎' not in st.session_state:
    class 简单风控引擎:
        def __init__(self):
            self.止损比例 = 0.05
            self.止盈比例 = 0.03
    st.session_state.风控引擎 = 简单风控引擎()

风控 = st.session_state.风控引擎

# ========== 辅助函数 ==========
def get模拟价格(品种):
    价格映射 = {
        "BTC-USD": 79586.70,
        "ETH-USD": 2219.12,
        "AAPL": 185.50,
        "NVDA": 950.00,
        "EURUSD": 1.0850,
        "000001.SS": 1680.00,
    }
    return 价格映射.get(品种, 100)


def generate_ai_signal(策略名称, 当前价格, 策略加载器=None, 品种=None):
    """调用真实策略获取信号"""
    try:
        # 从策略加载器获取策略
        策略信息 = None
        if 策略加载器 and hasattr(策略加载器, '获取策略'):
            所有策略 = 策略加载器.获取策略()
            for s in 所有策略:
                if s.get("名称") == 策略名称:
                    策略信息 = s
                    break
        
        if 策略信息 and 策略信息.get("类"):
            # 创建策略实例
            策略实例 = 策略信息["类"](策略名称, 品种 or "BTC-USD", 100000)
            
            # 构造行情数据
            行情 = {'close': 当前价格, 'volume': 0, 'high': 当前价格, 'low': 当前价格, 'open': 当前价格}
            
            # 调用策略
            信号 = 策略实例.处理行情(行情)
            
            # 根据信号返回结果
            if 信号 == 'buy':
                return {
                    "信号": "买入", "置信度": 85,
                    "建议数量": round(100000 * 0.05 / 当前价格, 4),
                    "理由": f"{策略名称}策略发出买入信号"
                }
            elif 信号 == 'sell':
                return {
                    "信号": "卖出", "置信度": 75,
                    "建议数量": round(100000 * 0.05 / 当前价格, 4),
                    "理由": f"{策略名称}策略发出卖出信号"
                }
            else:
                return {
                    "信号": "持有", "置信度": 60,
                    "建议数量": 0,
                    "理由": f"{策略名称}策略建议观望"
                }
    except Exception as e:
        print(f"生成AI信号失败: {e}")
    
    # 默认返回持有
    return {"信号": "持有", "置信度": 50, "建议数量": 0, "理由": "无法获取策略信号"}


# ========== 初始化策略调度器 ==========
def 初始化策略调度器():
    if not 策略调度器可用:
        return
    if st.session_state.策略调度器 is None:
        try:
            st.session_state.策略调度器 = 获取策略调度器(引擎)
            if st.session_state.策略调度器:
                st.session_state.策略调度器.启动()
                return True
        except Exception:
            return False
    return True

def 初始化自动交易器():
    if not 自动交易可用:
        return
    if st.session_state.自动交易器 is None:
        try:
            st.session_state.自动交易器 = 获取机器人()
            if hasattr(st.session_state.自动交易器, '设置引擎'):
                st.session_state.自动交易器.设置引擎(引擎)
            # 恢复自动交易开关状态到机器人
            if hasattr(st.session_state.自动交易器, '设置自动交易'):
                st.session_state.自动交易器.设置自动交易(st.session_state.自动交易开关)
        except Exception:
            pass

def 启动后台调度器():
    if st.session_state.后台服务已启动:
        return
    if not 定时任务可用:
        return
    try:
        调度器 = 定时任务模块.获取调度器()
        def 自动交易检查():
            try:
                if st.session_state.get("自动交易开关", False):
                    auto_trader = st.session_state.get("自动交易器", None)
                    if auto_trader and hasattr(auto_trader, '止损止盈检查'):
                        auto_trader.止损止盈检查()
            except Exception:
                pass
        调度器.注册函数("自动交易检查", 自动交易检查)
        调度器.添加间隔任务(自动交易检查, 60, "自动交易检查")
        调度器.启动后台()
        st.session_state.后台服务已启动 = True
    except Exception:
        pass

# ========== 安全调用函数 ==========
def 安全调用(模块, 默认信息="模块开发中"):
    if 模块 is None:
        st.info(默认信息)
        return
    if not hasattr(模块, '显示'):
        st.info(默认信息)
        return
    _引擎 = st.session_state.get('订单引擎', 引擎)
    _策略加载器 = st.session_state.get('策略加载器', None)
    _AI引擎 = st.session_state.get('AI引擎', None)
    try:
        模块.显示(_引擎, _策略加载器, _AI引擎)
    except TypeError:
        try:
            模块.显示(_引擎, _策略加载器)
        except TypeError:
            try:
                模块.显示(_引擎)
            except Exception:
                st.info(默认信息)
    except Exception:
        st.info(默认信息)

# ========== 紧凑样式 ==========
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem !important; }
    .stApp { font-size: 12px; }
    .stButton button { font-size: 11px !important; padding: 3px 10px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; }
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
    
    if st.button("🗑️ 清空所有持仓", use_container_width=True):
        try:
            数据库.清空所有持仓()
            st.session_state.订单引擎 = 订单引擎(初始资金=INITIAL_CAPITAL)
            引擎 = st.session_state.订单引擎
            st.success("✅ 已清空")
            st.rerun()
        except Exception as e:
            st.error(f"清空失败: {e}")
    
    if st.button("🔄 刷新持仓", use_container_width=True):
        if hasattr(引擎, '_恢复持仓'):
            引擎._恢复持仓()
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🤖 自动交易控制")
    if 自动交易可用:
        初始化自动交易器()
        新开关 = st.checkbox("🔴 开启自动交易", value=st.session_state.自动交易开关)
        if 新开关 != st.session_state.自动交易开关:
            st.session_state.自动交易开关 = 新开关
            # 保存到数据库
            try:
                数据库.保存自动交易状态(新开关)
                print(f"💾 保存自动交易状态: {'开启' if 新开关 else '关闭'}")
            except Exception as e:
                print(f"保存状态失败: {e}")
            # 更新机器人状态
            if st.session_state.自动交易器 and hasattr(st.session_state.自动交易器, '设置自动交易'):
                st.session_state.自动交易器.设置自动交易(新开关)
            st.rerun()
        if st.session_state.自动交易器:
            状态 = st.session_state.自动交易器.获取状态() if hasattr(st.session_state.自动交易器, '获取状态') else {}
            st.caption(f"📊 今日交易: {状态.get('今日交易次数', 0)} 次")
            st.caption(f"💰 今日盈亏: ¥{状态.get('今日盈亏', 0):+,.2f}")
        if not st.session_state.后台服务已启动:
            启动后台调度器()
    
    st.markdown("---")
    
    st.markdown("### 💼 持仓监控")
    if hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            成本 = getattr(pos, '平均成本', 0)
            数量 = getattr(pos, '数量', 0)
            st.caption(f"{品种}: {数量:.4f}个 成本¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ========== 创建Tab ==========
tab_names = ["🏠 首页", "📊 策略中心", "🤖 AI交易", "💼 持仓管理", "💰 资金曲线", "📈 回测", "📋 交易记录"]
tabs = st.tabs(tab_names)

# 首页
with tabs[0]:
    安全调用(首页, "首页模块开发中")

# 策略中心
with tabs[1]:
    安全调用(策略中心, "策略中心模块开发中")

# AI交易
with tabs[2]:
    st.markdown("### 🤖 AI 智能交易")
    st.caption("选择策略，系统会自动分析市场并给出买入/卖出信号")
    
    # 获取策略列表
    策略数据 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                策略数据 = 策略加载器.获取策略()
        except Exception:
            pass
    
    if not 策略数据:
        st.warning("等待策略加载...")
    else:
        # 策略选择区域
        st.markdown("#### 📋 选择策略")
        
        策略分组 = {}
        for s in 策略数据:
            类别 = s.get('类别', '其他')
            if 类别 not in 策略分组:
                策略分组[类别] = []
            策略分组[类别].append(s)
        
        if 'selected_strategy' not in st.session_state:
            st.session_state.selected_strategy = None
        
        # 三列显示策略按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if "₿ 加密货币" in 策略分组:
                st.markdown("**₿ 加密货币**")
                for s in 策略分组["₿ 加密货币"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"crypto_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        with col2:
            if "📈 A股" in 策略分组:
                st.markdown("**📈 A股**")
                for s in 策略分组["📈 A股"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"stock_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        with col3:
            if "🇺🇸 美股" in 策略分组:
                st.markdown("**🇺🇸 美股**")
                for s in 策略分组["🇺🇸 美股"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"us_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        st.markdown("---")
        
        if st.session_state.selected_strategy:
            选中策略 = st.session_state.selected_strategy
            st.markdown(f"#### 🎯 当前选中策略: **{选中策略.get('名称')}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- 类别: {选中策略.get('类别')}")
                st.markdown(f"- 品种: {选中策略.get('品种')}")
            with col2:
                if st.session_state.自动交易开关:
                    st.markdown(f"- 自动交易: 🟢 运行中")
                else:
                    st.markdown(f"- 自动交易: 🔴 已停止")
            
            品种 = 选中策略.get('品种', 'BTC-USD')
            
            # 获取价格
            try:
                if 行情获取:
                    价格结果 = 行情获取.获取价格(品种)
                    if 价格结果 and hasattr(价格结果, '价格'):
                        当前价格 = 价格结果.价格
                    else:
                        当前价格 = get模拟价格(品种)
                else:
                    当前价格 = get模拟价格(品种)
            except:
                当前价格 = get模拟价格(品种)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 当前价格", f"¥{当前价格:,.2f}")
            with col2:
                st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
            with col3:
                if 品种 in 引擎.持仓:
                    持仓量 = getattr(引擎.持仓[品种], '数量', 0)
                    st.metric("📦 当前持仓", f"{持仓量:.4f}个")
                else:
                    st.metric("📦 当前持仓", "无")
            
            st.markdown("---")
            
            if st.session_state.自动交易开关:
                st.info("🤖 全局自动交易已开启，系统将自动执行策略信号")
            else:
                st.warning("⏸️ 全局自动交易已关闭，请在侧边栏开启")
            
            # 生成信号按钮
            if st.button("🔍 生成AI信号", type="primary", use_container_width=True):
                with st.spinner("AI正在分析市场..."):
                    # 调用真实策略获取信号（传入策略加载器和品种）
                    信号 = generate_ai_signal(选中策略.get('名称'), 当前价格, 策略加载器, 品种)
                    st.session_state.ai_signal = 信号
                    st.rerun()
            
            # 显示信号
            if 'ai_signal' in st.session_state and st.session_state.ai_signal:
                信号 = st.session_state.ai_signal
                
                if 信号['信号'] == "买入":
                    信号颜色 = "🟢"
                elif 信号['信号'] == "卖出":
                    信号颜色 = "🔴"
                else:
                    信号颜色 = "🟡"
                
                st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin:10px 0;">
                    <b>📈 AI分析结果</b><br>
                    策略: {选中策略.get('名称')}<br>
                    品种: {品种}<br>
                    当前价格: ¥{当前价格:,.2f}<br>
                    AI信号: {信号颜色} {信号['信号']}<br>
                    置信度: {信号['置信度']}%<br>
                    建议数量: {信号['建议数量']} 个<br>
                    理由: {信号['理由']}
                </div>
                """, unsafe_allow_html=True)
                
                # 手动执行（自动交易关闭时）
                if not st.session_state.自动交易开关:
                    col1, col2 = st.columns(2)
                    with col1:
                        if 信号['信号'] == "买入" and st.button("📈 执行买入建议", use_container_width=True):
                            可用资金 = 引擎.获取可用资金()
                            预计花费 = 当前价格 * 信号['建议数量']
                            if 预计花费 <= 可用资金:
                                结果 = 引擎.买入(品种, None, 信号['建议数量'])
                                if 结果.get("success"):
                                    st.success(f"✅ 已买入 {品种} {信号['建议数量']} 个")
                                    st.session_state.ai_signal = None
                                    st.rerun()
                                else:
                                    st.error(f"买入失败: {结果.get('error')}")
                            else:
                                st.error(f"资金不足")
                    with col2:
                        if 信号['信号'] == "卖出" and st.button("📉 执行卖出建议", use_container_width=True):
                            if 品种 in 引擎.持仓:
                                结果 = 引擎.卖出(品种, None, 信号['建议数量'])
                                if 结果.get("success"):
                                    st.success(f"✅ 已卖出 {品种} {信号['建议数量']} 个")
                                    st.session_state.ai_signal = None
                                    st.rerun()
                                else:
                                    st.error(f"卖出失败: {结果.get('error')}")
                            else:
                                st.error(f"没有持仓 {品种}")
            
            # 手动交易
            st.markdown("---")
            st.markdown("#### 📊 手动交易")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 买入")
                买入数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01, key="buy_qty")
                if st.button("📈 确认买入", type="primary", use_container_width=True):
                    可用资金 = 引擎.获取可用资金()
                    预计花费 = 当前价格 * 买入数量
                    if 预计花费 <= 可用资金:
                        结果 = 引擎.买入(品种, None, 买入数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {品种} {买入数量} 个")
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                    else:
                        st.error(f"资金不足")
            
            with col2:
                st.markdown("##### 卖出")
                卖出数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01, key="sell_qty")
                if st.button("📉 确认卖出", use_container_width=True):
                    if 品种 in 引擎.持仓:
                        结果 = 引擎.卖出(品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {品种} {卖出数量} 个")
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error')}")
                    else:
                        st.error(f"没有持仓 {品种}")
    
    # 显示持仓
    st.markdown("---")
    st.markdown("#### 💼 当前持仓")
    if 引擎.持仓:
        for 品种名, pos in 引擎.持仓.items():
            数量持仓 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.metric(label=f"{品种名}", value=f"{数量持仓:.4f}个", delta=f"成本 ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    if st.session_state.自动交易开关:
        st.success("🤖 全局自动交易运行中")
    else:
        st.info("💡 提示：开启侧边栏「自动交易」后，系统将自动执行策略信号")

# 持仓管理
with tabs[3]:
    安全调用(持仓管理, "持仓管理模块开发中")

# 资金曲线
with tabs[4]:
    安全调用(资金曲线, "资金曲线模块开发中")

# 回测
with tabs[5]:
    安全调用(回测, "回测模块开发中")

# 交易记录
with tabs[6]:
    安全调用(交易记录, "交易记录模块开发中")

# ========== 底部 ==========
st.markdown("---")
st.caption("⚠️ 风险提示：量化交易存在风险，历史回测结果不代表未来收益。")

# ========== 保存会话状态 ==========
auto_save_session()

# ========== 启动策略调度器 ==========
if 策略调度器可用 and st.session_state.策略调度器 is None:
    初始化策略调度器()
