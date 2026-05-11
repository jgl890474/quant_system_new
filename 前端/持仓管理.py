# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取
from datetime import datetime


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理页面"""
    
    st.markdown("### 💼 当前持仓")
    
    # ========== 持仓显示 ==========
    if 引擎.持仓:
        数据 = []
        持仓列表 = list(引擎.持仓.items())
        
        for 品种, pos in 持仓列表:
            try:
                # 获取实时价格（带容错）
                价格结果 = 行情获取.获取价格(品种)
                
                # 兼容不同的返回格式
                if hasattr(价格结果, '价格'):
                    现价 = float(价格结果.价格)
                elif hasattr(价格结果, 'price'):
                    现价 = float(价格结果.price)
                elif isinstance(价格结果, (int, float)):
                    现价 = float(价格结果)
                else:
                    现价 = float(pos.平均成本)
                
                # 更新持仓当前价格
                pos.当前价格 = 现价
                
                # 计算盈亏
                成本价 = float(pos.平均成本)
                数量 = float(pos.数量)
                盈亏 = 数量 * (现价 - 成本价)
                盈亏率 = (现价 / 成本价 - 1) * 100 if 成本价 > 0 else 0
                
                数据.append({
                    "品种": 品种,
                    "数量": f"{数量:.0f}",
                    "成本": f"{成本价:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%"
                })
            except Exception as e:
                数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本": f"{pos.平均成本:.2f}",
                    "现价": "获取失败",
                    "盈亏": "---",
                    "盈亏率": "---"
                })
        
        if 数据:
            df = pd.DataFrame(数据)
            # 修复：use_container_width=True -> width='stretch'
            st.dataframe(df, width='stretch', hide_index=True)
            
            # 显示总盈亏
            总盈亏 = 0.0
            for d in 数据:
                if d["盈亏"] != "---":
                    try:
                        总盈亏 += float(d["盈亏"].replace("¥", "").replace(",", ""))
                    except:
                        pass
            st.caption(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
    else:
        st.caption("暂无持仓")
    
    st.markdown("---")
    
    # ========== 止损止盈设置 ==========
    st.markdown("### 🛡️ 止损止盈设置")
    
    # 获取当前风控参数
    if '风控引擎' in st.session_state:
        风控 = st.session_state.风控引擎
        当前止损 = getattr(风控, '止损比例', 0.02) * 100
        当前止盈 = getattr(风控, '止盈比例', 0.04) * 100
        当前移动止损 = getattr(风控, '移动止损开关', True)
        当前回撤 = getattr(风控, '移动止损回撤', 0.02) * 100
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
            key="stop_loss_input"
        )
    with col2:
        止盈比例 = st.number_input(
            "止盈比例 (%)", 
            min_value=0.5, 
            max_value=50.0, 
            value=当前止盈, 
            step=0.5,
            key="take_profit_input"
        )
    with col3:
        移动止损 = st.checkbox(
            "开启移动止损", 
            value=当前移动止损,
            key="trailing_stop"
        )
    
    # 移动止损回撤设置
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input(
                "移动止损回撤 (%)", 
                min_value=0.5, 
                max_value=10.0, 
                value=当前回撤, 
                step=0.5,
                key="trailing_stop_back"
            )
    
    # 修复：use_container_width=True -> width='stretch'
    if st.button("应用风控参数", width='stretch', key="apply_risk"):
        if '风控引擎' in st.session_state:
            st.session_state.风控引擎.止损比例 = 止损比例 / 100
            st.session_state.风控引擎.止盈比例 = 止盈比例 / 100
            st.session_state.风控引擎.移动止损开关 = 移动止损
            if 移动止损:
                st.session_state.风控引擎.移动止损回撤 = 移动止损回撤 / 100
            st.success("✅ 风控参数已更新")
            st.rerun()
    
    st.markdown("---")
    
    # ========== 手动平仓按钮 ==========
    if 引擎.持仓:
        # 修复：use_container_width=True -> width='stretch'
        if st.button("🗑️ 一键平仓所有持仓", width='stretch', key="close_all"):
            for 品种 in list(引擎.持仓.keys()):
                try:
                    价格结果 = 行情获取.获取价格(品种)
                    if hasattr(价格结果, '价格'):
                        现价 = 价格结果.价格
                    else:
                        现价 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                    if 现价 > 0:
                        引擎.卖出(品种, 现价, 引擎.持仓[品种].数量)
                except:
                    pass
            st.success("✅ 已执行一键平仓")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
