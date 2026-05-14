# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """首页 - 资金概览"""
    
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    # 更新持仓价格
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                结果 = 行情获取.获取价格(品种)
                if 结果 and hasattr(结果, '价格'):
                    引擎.持仓[品种].当前价格 = 结果.价格
            except:
                pass
    
    # 计算资产
    初始资金 = getattr(引擎, '初始资金', 1000000)
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    
    总市值 = 0
    for 品种, pos in 引擎.持仓.items():
        数量 = getattr(pos, '数量', 0)
        成本价 = getattr(pos, '平均成本', 0)
        现价 = getattr(pos, '当前价格', 成本价)
        总市值 += 数量 * 现价
    
    总资产 = 可用资金 + 总市值
    总盈亏 = 总资产 - 初始资金
    收益率 = (总盈亏 / 初始资金 * 100) if 初始资金 > 0 else 0
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{总市值:,.0f}")
    with col4:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{收益率:+.1f}%")
    
    # 实时行情
    st.markdown("### 📈 实时行情")
    行情品种 = ["BTC-USD", "ETH-USD", "AAPL", "TSLA"]
    行情列 = st.columns(len(行情品种))
    for i, 品种 in enumerate(行情品种):
        with 行情列[i]:
            try:
                价格 = 行情获取.获取价格(品种)
                if 价格 and hasattr(价格, '价格'):
                    st.metric(品种, f"¥{价格.价格:.2f}")
                else:
                    st.metric(品种, "—")
            except:
                st.metric(品种, "—")
    
    # 快捷交易
    st.markdown("### 🚀 快捷交易")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 买入")
        品种 = st.selectbox("品种", ["BTC-USD", "ETH-USD", "AAPL"], key="buy_symbol")
        数量 = st.number_input("数量", min_value=0.01, value=0.01, step=0.01, key="buy_qty")
        if st.button("买入", type="primary", key="buy_btn"):
            try:
                结果 = 引擎.买入(品种, None, 数量, 策略名称="手动买入")
                if 结果.get("success"):
                    st.success(f"✅ 已买入 {品种} {数量}")
                    st.rerun()
                else:
                    st.error(f"买入失败: {结果.get('error')}")
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    with col2:
        st.markdown("#### 卖出")
        if 引擎.持仓:
            持仓品种 = list(引擎.持仓.keys())
            卖品种 = st.selectbox("品种", 持仓品种, key="sell_symbol")
            pos = 引擎.持仓[卖品种]
            st.caption(f"持仓: {pos.数量}")
            if st.button("卖出", key="sell_btn"):
                try:
                    结果 = 引擎.卖出(卖品种, None, pos.数量, 策略名称="手动卖出")
                    if 结果.get("success"):
                        st.success(f"✅ 已卖出 {卖品种}")
                        st.rerun()
                    else:
                        st.error(f"卖出失败: {结果.get('error')}")
                except Exception as e:
                    st.error(f"卖出失败: {e}")
        else:
            st.info("暂无持仓")
