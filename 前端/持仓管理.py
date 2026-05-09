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
                    现价 = 价格结果.价格
                elif hasattr(价格结果, 'price'):
                    现价 = 价格结果.price
                elif isinstance(价格结果, (int, float)):
                    现价 = 价格结果
                else:
                    现价 = pos.平均成本  # 失败时使用成本价
                
                # 更新持仓当前价格
                pos.当前价格 = 现价
                
                # 计算盈亏
                盈亏 = pos.数量 * (现价 - pos.平均成本)
                盈亏率 = (现价 / pos.平均成本 - 1) * 100 if pos.平均成本 > 0 else 0
                
                数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本": f"{pos.平均成本:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.1f}%"
                })
            except Exception as e:
                # 单个品种出错不影响其他品种
                st.caption(f"⚠️ 获取 {品种} 行情失败: {e}")
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
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 显示持仓汇总
            total_profit = sum([float(p["盈亏"].replace("¥", "").replace(",", "")) 
                               for p in 数据 if p["盈亏"] != "---"])
            st.caption(f"📊 持仓总盈亏: ¥{total_profit:+,.2f}")
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
            try:
                总资金 = 引擎.获取总资产()
                状态 = 风控.获取风控状态(引擎, 总资金)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("总仓位", 状态.get("总仓位比例", "0%"))
                col2.metric("单品种限制", 状态.get("单品种仓位限制", "30%"))
                col3.metric("止损/止盈", f"{状态.get('止损线', '-2%')} / {状态.get('止盈线', '+4%')}")
                col4.metric("今日盈亏", f"¥{getattr(风控, '今日盈亏', 0):+,.2f}")
                
                col5, col6, col7, col8 = st.columns(4)
                col5.metric("移动止损", "开启" if 移动止损 else "关闭")
                col6.metric("移动止损回撤", f"{移动止损回撤}%")
                col7.metric("今日交易次数", f"{状态.get('今日交易次数', 0)}")
                col8.metric("每日亏损上限", "-5%")
                
                # 显示移动止损记录
                if hasattr(风控, '移动止损记录') and 风控.移动止损记录:
                    st.markdown("**📈 移动止损跟踪**")
                    for 品种, record in 风控.移动止损记录.items():
                        st.caption(f"{品种}: 最高价 ¥{record.get('最高价', 0):.2f} | 移动止损 ¥{record.get('止损价', 0):.2f}")
            except Exception as e:
                st.caption(f"风控状态获取失败: {e}")
    
    # ========== 手动平仓按钮 ==========
    if 引擎.持仓:
        st.markdown("---")
        st.markdown("### 🗑️ 批量操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 一键平仓所有持仓", use_container_width=True, key="close_all"):
                success_count = 0
                fail_count = 0
                for 品种 in list(引擎.持仓.keys()):
                    try:
                        价格结果 = 行情获取.获取价格(品种)
                        if hasattr(价格结果, '价格'):
                            价格 = 价格结果.价格
                        elif hasattr(价格结果, 'price'):
                            价格 = 价格结果.price
                        else:
                            价格 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        
                        if 价格 > 0:
                            引擎.卖出(品种, 价格, 引擎.持仓[品种].数量)
                            success_count += 1
                    except Exception as e:
                        fail_count += 1
                
                if success_count > 0:
                    st.success(f"✅ 已平仓 {success_count} 个品种")
                if fail_count > 0:
                    st.warning(f"⚠️ {fail_count} 个品种平仓失败")
                st.rerun()
        
        with col2:
            if st.button("🔄 刷新持仓", use_container_width=True, key="refresh_positions"):
                st.rerun()
    
    # 显示最后更新时间
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
