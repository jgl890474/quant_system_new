# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from datetime import datetime, timezone, timedelta

# 设置北京时间
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')

# 尝试导入行情获取
try:
    from 核心 import 行情获取
except ImportError:
    行情获取 = None

def 显示(引擎, 策略加载器=None, AI引擎=None):
    """
    首页 - 资金概览
    """
    
    # 生成唯一的会话ID
    if 'home_page_key' not in st.session_state:
        st.session_state.home_page_key = str(uuid.uuid4())[:8]
    
    # 强制从 session_state 获取最新引擎
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    # 刷新持仓
    if 引擎 and hasattr(引擎, '_恢复持仓'):
        try:
            引擎._恢复持仓()
            st.session_state.订单引擎 = 引擎
        except Exception:
            pass
    
    # 更新持仓价格
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                if 行情获取 and hasattr(行情获取, '获取价格'):
                    结果 = 行情获取.获取价格(品种)
                    if 结果 and hasattr(结果, '价格') and 结果.价格:
                        if 结果.价格 > 0 and 品种 in 引擎.持仓:
                            引擎.持仓[品种].当前价格 = 结果.价格
            except Exception:
                pass
    
    # 计算资产
    初始资金 = getattr(引擎, '初始资金', 1000000)
    
    if hasattr(引擎, '获取可用资金'):
        可用资金 = 引擎.获取可用资金()
    else:
        可用资金 = getattr(引擎, '可用资金', 1000000)
    
    总市值 = 0
    for 品种, pos in 引擎.持仓.items():
        数量 = getattr(pos, '数量', 0)
        成本价 = getattr(pos, '平均成本', 0)
        现价 = getattr(pos, '当前价格', 成本价)
        if 现价 <= 0:
            现价 = 成本价
        总市值 += 数量 * 现价
    
    持仓市值 = 总市值
    总资产 = 可用资金 + 持仓市值
    总盈亏 = 总资产 - 初始资金
    收益率 = (总盈亏 / 初始资金 * 100) if 初始资金 > 0 else 0
    
    # 资金概览卡片
    st.markdown("### 💼 资金概览")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 总资产", f"¥{总资产:,.2f}")
    with col2:
        st.metric("💵 可用资金", f"¥{可用资金:,.2f}")
    with col3:
        st.metric("📊 持仓市值", f"¥{持仓市值:,.2f}")
    with col4:
        st.metric("📈 总盈亏", f"¥{总盈亏:+,.2f}", delta=f"{收益率:+.1f}%")
    
    # 主要交易品种（去掉无关的GC=F、TSLA等）
    st.markdown("---")
    st.markdown("### 📊 主要市场")
    
    # 三列显示市场状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**₿ 加密货币**")
        st.caption("BTC-USD | 24h 交易")
        if 引擎.持仓.get("BTC-USD"):
            持仓量 = 引擎.持仓["BTC-USD"].数量
            st.caption(f"持仓: {持仓量:.4f}个")
        else:
            st.caption("持仓: 无")
    
    with col2:
        st.markdown("**📈 A股**")
        st.caption("000001.SS | 9:30-15:00")
        if 引擎.持仓.get("000001.SS"):
            持仓量 = 引擎.持仓["000001.SS"].数量
            st.caption(f"持仓: {int(持仓量)}股")
        else:
            st.caption("持仓: 无")
    
    with col3:
        st.markdown("**🇺🇸 美股**")
        st.caption("AAPL | 21:30-04:00")
        if 引擎.持仓.get("AAPL"):
            持仓量 = 引擎.持仓["AAPL"].数量
            st.caption(f"持仓: {int(持仓量)}股")
        else:
            st.caption("持仓: 无")
    
    # 快捷交易
    st.markdown("---")
    st.markdown("### 🚀 快捷交易")
    
    current_key = st.session_state.home_page_key
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    # 买入Tab
    with tab1:
        # 按市场分类的品种
        可买品种列表 = [
            "₿ BTC-USD (加密货币)",
            "₿ ETH-USD (加密货币)",
            "📈 000001.SS (A股)",
            "🇺🇸 AAPL (美股)",
            "🇺🇸 NVDA (美股)"
        ]
        
        买入选择 = st.selectbox(
            "选择品种", 
            可买品种列表, 
            key=f"home_buy_symbol_{current_key}"
        )
        
        # 提取品种代码
        if "BTC" in 买入选择:
            买入品种 = "BTC-USD"
            数量单位 = "个"
            默认数量 = 0.01
            步长 = 0.01
            数量格式 = "%.4f"
        elif "ETH" in 买入选择:
            买入品种 = "ETH-USD"
            数量单位 = "个"
            默认数量 = 0.01
            步长 = 0.01
            数量格式 = "%.4f"
        elif "000001" in 买入选择:
            买入品种 = "000001.SS"
            数量单位 = "股"
            默认数量 = 100
            步长 = 100
            数量格式 = "%.0f"
        else:
            买入品种 = "AAPL" if "AAPL" in 买入选择 else "NVDA"
            数量单位 = "股"
            默认数量 = 10
            步长 = 10
            数量格式 = "%.0f"
        
        st.caption(f"📌 品种: {买入品种}")
        
        买入数量 = st.number_input(
            f"数量 ({数量单位})", 
            min_value=0.01 if 数量单位 == "个" else 1, 
            value=默认数量, 
            step=步长,
            format=数量格式,
            key=f"home_buy_qty_{current_key}"
        )
        
        if st.button("✅ 买入", type="primary", key=f"home_buy_btn_{current_key}"):
            if 买入数量 <= 0:
                st.error("请输入大于0的数量")
            else:
                try:
                    结果 = 引擎.买入(买入品种, None, 买入数量)
                    if 结果.get("success"):
                        st.success(f"✅ 已买入 {买入品种} {买入数量} {数量单位}")
                        st.session_state.订单引擎 = 引擎
                        st.session_state.home_page_key = str(uuid.uuid4())[:8]
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"买入失败: {结果.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"买入异常: {e}")
    
    # 卖出Tab
    with tab2:
        if hasattr(引擎, '_恢复持仓'):
            try:
                引擎._恢复持仓()
                st.session_state.订单引擎 = 引擎
            except Exception:
                pass
        
        持仓品种列表 = list(引擎.持仓.keys())
        
        if 持仓品种列表:
            卖出品种 = st.selectbox(
                "选择持仓品种", 
                持仓品种列表,
                key=f"home_sell_symbol_{current_key}"
            )
            
            pos = 引擎.持仓[卖出品种]
            最大可卖数量 = getattr(pos, '数量', 0)
            平均成本 = getattr(pos, '平均成本', 0)
            
            st.caption(f"💰 持仓成本: ¥{平均成本:.2f}")
            
            if 卖出品种 in ["BTC-USD", "ETH-USD"]:
                st.caption(f"📊 可卖数量: {最大可卖数量:.4f}个")
                卖出数量 = st.number_input(
                    "数量 (个)", 
                    min_value=0.0, 
                    max_value=float(最大可卖数量), 
                    value=min(0.01, float(最大可卖数量)), 
                    step=0.01,
                    format="%.4f",
                    key=f"home_sell_qty_{current_key}"
                )
            else:
                st.caption(f"📊 可卖数量: {int(最大可卖数量)}股")
                卖出数量 = st.number_input(
                    "数量 (股)", 
                    min_value=1, 
                    max_value=int(最大可卖数量), 
                    value=min(100, int(最大可卖数量)), 
                    step=100,
                    key=f"home_sell_qty_{current_key}"
                )
            
            if st.button("🔴 卖出", key=f"home_sell_btn_{current_key}"):
                if 卖出数量 <= 0:
                    st.error("请输入大于0的数量")
                else:
                    try:
                        结果 = 引擎.卖出(卖出品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {卖出品种} {卖出数量} 单位")
                            if hasattr(引擎, '_恢复持仓'):
                                引擎._恢复持仓()
                            st.session_state.订单引擎 = 引擎
                            st.session_state.home_page_key = str(uuid.uuid4())[:8]
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
        else:
            st.info("📭 暂无持仓")
    
    # 持仓列表
    st.markdown("---")
    st.markdown("### 💼 当前持仓")
    
    if 引擎.持仓:
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本价 = getattr(pos, '平均成本', 0)
            现价 = getattr(pos, '当前价格', 成本价)
            市值 = 数量 * 现价
            盈亏 = (现价 - 成本价) * 数量
            盈亏率 = (盈亏 / (成本价 * 数量) * 100) if 成本价 > 0 and 数量 > 0 else 0
            
            # 格式化数量显示
            if 品种 in ["BTC-USD", "ETH-USD"]:
                数量显示 = f"{数量:.4f}个"
            else:
                数量显示 = f"{int(数量)}股"
            
            持仓数据.append({
                "品种": 品种,
                "数量": 数量显示,
                "成本价": f"¥{成本价:,.2f}",
                "现价": f"¥{现价:,.2f}",
                "市值": f"¥{市值:,.2f}",
                "盈亏": f"¥{盈亏:+,.2f}",
                "盈亏率": f"{盈亏率:+.1f}%"
            })
        
        st.dataframe(持仓数据, width="stretch", hide_index=True)
    else:
        st.info("暂无持仓")
    
    # 底部 - 北京时间
    st.markdown("---")
    st.caption(f"📅 北京时间: {get_beijing_time()}")
    st.caption("⚠️ 风险提示：量化交易存在风险，投资需谨慎。")
