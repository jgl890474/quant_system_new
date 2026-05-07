# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 💼 当前持仓")
    
    if 引擎.持仓:
        数据 = []
        for 品种, pos in 引擎.持仓.items():
            价格 = 行情获取.获取价格(品种).价格
            pos.当前价格 = 价格
            盈亏 = pos.数量 * (价格 - pos.平均成本)
            盈亏率 = (价格 / pos.平均成本 - 1) * 100
            数据.append({
                "品种": 品种,
                "数量": f"{pos.数量:.0f}",
                "成本": f"{pos.平均成本:.2f}",
                "现价": f"{价格:.2f}",
                "盈亏": f"¥{盈亏:+,.2f}",
                "盈亏率": f"{盈亏率:+.1f}%"
            })
        st.dataframe(pd.DataFrame(数据), use_container_width=True, hide_index=True)
    else:
        st.caption("暂无持仓")
    
    # ========== 止损止盈设置 ==========
    st.markdown("### 🛡️ 止损止盈设置")
    
    # 获取当前风控参数
    if '风控引擎' in st.session_state:
        风控 = st.session_state.风控引擎
        当前止损 = 风控.止损比例 * 100
        当前止盈 = 风控.止盈比例 * 100
        当前移动止损 = 风控.移动止损开关
        当前回撤 = 风控.移动止损回撤 * 100
    else:
        当前止损 = 2.0
        当前止盈 = 4.0
        当前移动止损 = True
        当前回撤 = 2.0
    
    # 参数设置界面
    col1, col2, col3 = st.columns(3)
    with col1:
        止损比例 = st.number_input(
            "止损比例 (%)", 
            min_value=0.5, 
            max_value=20.0, 
            value=当前止损, 
            step=0.5,
            key="stop_loss_input",
            help="亏损达到此比例时自动卖出"
        )
    with col2:
        止盈比例 = st.number_input(
            "止盈比例 (%)", 
            min_value=0.5, 
            max_value=50.0, 
            value=当前止盈, 
            step=0.5,
            key="take_profit_input",
            help="盈利达到此比例时自动卖出"
        )
    with col3:
        移动止损 = st.checkbox(
            "开启移动止损", 
            value=当前移动止损,
            key="trailing_stop",
            help="盈利后动态上调止损价，锁定利润"
        )
    
    # 移动止损回撤设置（仅当移动止损开启时显示）
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input(
                "移动止损回撤 (%)", 
                min_value=0.5, 
                max_value=10.0, 
                value=当前回撤, 
                step=0.5,
                key="trailing_stop_back",
                help="从最高点回撤此比例时触发移动止损"
            )
    
    # 应用按钮
    if st.button("应用风控参数", use_container_width=True, key="apply_risk"):
        if '风控引擎' in st.session_state:
            st.session_state.风控引擎.止损比例 = 止损比例 / 100
            st.session_state.风控引擎.止盈比例 = 止盈比例 / 100
            st.session_state.风控引擎.移动止损开关 = 移动止损
            if 移动止损:
                st.session_state.风控引擎.移动止损回撤 = 移动止损回撤 / 100
            st.success(f"✅ 风控参数已更新\n止损: {止损比例}% | 止盈: {止盈比例}% | 移动止损: {'开启' if 移动止损 else '关闭'}")
            st.rerun()
    
    st.markdown("---")
    
    # ========== 风控状态显示 ==========
    with st.expander("📊 风控状态详情"):
        if '风控引擎' in st.session_state:
            风控 = st.session_state.风控引擎
            总资金 = 引擎.获取总资产()
            状态 = 风控.获取风控状态(引擎, 总资金)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总仓位", 状态["总仓位比例"])
            col2.metric("单品种限制", 状态["单品种仓位限制"])
            col3.metric("止损/止盈", f"{状态['止损线']} / {状态['止盈线']}")
            col4.metric("今日盈亏", f"¥{风控.今日盈亏:+,.2f}")
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("移动止损", 状态.get("移动止损", "关闭"))
            col6.metric("移动止损回撤", 状态.get("移动止损回撤", "0%"))
            col7.metric("今日交易次数", f"{状态.get('今日交易次数', 0)}")
            col8.metric("每日亏损上限", 状态.get("每日亏损上限", "-5%"))
            
            # 显示移动止损记录
            if 风控.移动止损记录:
                st.markdown("**📈 移动止损跟踪**")
                for 品种, record in 风控.移动止损记录.items():
                    st.caption(f"{品种}: 最高价 ¥{record.get('最高价', 0):.2f} | 移动止损 ¥{record.get('止损价', 0):.2f}")
    
    # ========== 手动平仓按钮 ==========
    if 引擎.持仓:
        st.markdown("---")
        st.markdown("### 🗑️ 批量操作")
        if st.button("🗑️ 一键平仓所有持仓", use_container_width=True):
            for 品种 in list(引擎.持仓.keys()):
                try:
                    价格 = 行情获取.获取价格(品种).价格
                    引擎.卖出(品种, 价格, 引擎.持仓[品种].数量)
                except:
                    pass
            st.success("✅ 已执行一键平仓")
            st.rerun()
