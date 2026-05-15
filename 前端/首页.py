# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from datetime import datetime

# 尝试导入行情获取
try:
    from 核心 import 行情获取
    from 核心.行情获取 import 获取价格 as 获取实时价格
except ImportError:
    行情获取 = None
    print("⚠️ 行情获取模块导入失败")


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """
    首页 - 资金概览和实时行情
    """
    
    # ==================== 生成唯一的会话ID用于key ====================
    if 'home_page_key' not in st.session_state:
        st.session_state.home_page_key = str(uuid.uuid4())[:8]
    
    # ==================== 强制从 session_state 获取最新引擎 ====================
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    # ==================== 先刷新持仓（从数据库恢复） ====================
    if 引擎 and hasattr(引擎, '_恢复持仓'):
        try:
            引擎._恢复持仓()
            st.session_state.订单引擎 = 引擎
        except Exception as e:
            print(f"恢复持仓失败: {e}")
    
    # ==================== 更新持仓价格 ====================
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                if 行情获取 and hasattr(行情获取, '获取价格'):
                    结果 = 行情获取.获取价格(品种)
                    if 结果 and hasattr(结果, '价格') and 结果.价格:
                        当前价格 = 结果.价格
                        if 当前价格 > 0 and 品种 in 引擎.持仓:
                            引擎.持仓[品种].当前价格 = 当前价格
            except Exception as e:
                print(f"更新价格失败 {品种}: {e}")
    
    # ==================== 计算资产 ====================
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
    
    # ==================== 指标卡片 ====================
    st.markdown("### 💼 资金概览")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("💵 可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("📊 持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("📈 总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{收益率:+.1f}%")
    
    # ==================== 实时行情 ====================
    st.markdown("### 📈 实时行情")
    
    行情品种配置 = [
        {"显示名": "AAPL", "代码": "AAPL"},
        {"显示名": "BTC-USD", "代码": "BTC-USD"},
        {"显示名": "GC=F", "代码": "GC=F"},
        {"显示名": "EURUSD", "代码": "EURUSD=X"},
        {"显示名": "TSLA", "代码": "TSLA"},
        {"显示名": "NVDA", "代码": "NVDA"},
    ]
    
    行情列 = st.columns(len(行情品种配置))
    for i, 品种 in enumerate(行情品种配置):
        with 行情列[i]:
            try:
                价格 = 获取行情价格(品种["代码"])
                if 价格 and 价格 > 0:
                    if "BTC" in 品种["代码"]:
                        st.metric(品种["显示名"], f"¥{价格:,.0f}")
                    else:
                        st.metric(品种["显示名"], f"¥{价格:.2f}")
                else:
                    st.metric(品种["显示名"], "—")
            except Exception:
                st.metric(品种["显示名"], "—")
    
    # ==================== 快捷交易 ====================
    st.markdown("### 🚀 快捷交易")
    
    # 生成当前页面的唯一key
    current_key = st.session_state.home_page_key
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    # ========== 买入 Tab ==========
    with tab1:
        可买品种列表 = ["BTC-USD", "ETH-USD", "AAPL", "NVDA", "EURUSD"]
        
        买入品种 = st.selectbox(
            "选择品种", 
            可买品种列表, 
            key=f"home_buy_symbol_{current_key}"
        )
        
        # 获取参考价格
        参考价格 = 获取行情价格(买入品种)
        if 参考价格 and 参考价格 > 0:
            st.caption(f"📌 参考价格: ¥{参考价格:.4f}")
        else:
            st.caption("📌 参考价格: 获取中...")
        
        # 设置数量单位提示
        if 买入品种 in ["BTC-USD", "ETH-USD"]:
            数量单位 = "个"
            默认数量 = 0.01
            步长 = 0.01
            数量格式 = "%.4f"
        else:
            数量单位 = "股"
            默认数量 = 1
            步长 = 1
            数量格式 = "%.0f"
        
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
                        # 刷新页面
                        st.session_state.home_page_key = str(uuid.uuid4())[:8]
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"买入失败: {结果.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"买入异常: {e}")
    
    # ========== 卖出 Tab ==========
    with tab2:
        # 刷新持仓
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
            
            st.caption(f"💰 持仓成本: ¥{平均成本:.4f}")
            st.caption(f"📊 可卖数量: {最大可卖数量:.4f}" if 最大可卖数量 < 1 else f"📊 可卖数量: {int(最大可卖数量)}")
            
            # 获取参考价格
            参考价格 = 获取行情价格(卖出品种)
            if 参考价格 and 参考价格 > 0:
                st.caption(f"📌 参考价格: ¥{参考价格:.4f}")
            else:
                st.caption("📌 参考价格: 获取中...")
            
            # 设置数量输入
            if 最大可卖数量 < 1:
                卖出数量 = st.number_input(
                    "数量", 
                    min_value=0.0, 
                    max_value=float(最大可卖数量), 
                    value=min(0.01, float(最大可卖数量)), 
                    step=0.01,
                    format="%.4f",
                    key=f"home_sell_qty_{current_key}"
                )
            else:
                卖出数量 = st.number_input(
                    "数量", 
                    min_value=1, 
                    max_value=int(最大可卖数量), 
                    value=min(1, int(最大可卖数量)), 
                    step=1,
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
                            # 刷新页面
                            st.session_state.home_page_key = str(uuid.uuid4())[:8]
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
        else:
            st.info("📭 暂无持仓")
    
    # ==================== 持仓列表 ====================
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
            
            持仓数据.append({
                "品种": 品种,
                "数量": f"{数量:.4f}" if 数量 < 1 else str(int(数量)),
                "成本价": f"¥{成本价:.2f}",
                "现价": f"¥{现价:.2f}",
                "市值": f"¥{市值:,.0f}",
                "盈亏": f"¥{盈亏:+,.0f}",
                "盈亏率": f"{盈亏率:+.1f}%"
            })
        
        # 修复 use_container_width 警告
        st.dataframe(持仓数据, width="stretch", hide_index=True)
    else:
        st.info("暂无持仓，去上面买入吧～")
    
    # ==================== 底部 ====================
    st.markdown("---")
    st.caption(f"📅 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("⚠️ 风险提示：量化交易存在风险，历史回测结果不代表未来收益。")


def 获取行情价格(代码):
    """获取行情价格"""
    try:
        if 行情获取 is None:
            return None
        
        if hasattr(行情获取, '获取价格'):
            结果 = 行情获取.获取价格(代码)
            if 结果 and hasattr(结果, '价格'):
                return 结果.价格
        elif hasattr(行情获取, 'get_price'):
            结果 = 行情获取.get_price(代码)
            if 结果 and hasattr(结果, 'price'):
                return 结果.price
        return None
    except Exception as e:
        print(f"获取价格失败 {代码}: {e}")
        return None
