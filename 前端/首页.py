# -*- coding: utf-8 -*-
import streamlit as st
import os
from 核心 import 行情获取

def 显示(引擎, 策略加载器=None, AI引擎=None):
    # 计算资金指标
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓市值 = 引擎.获取持仓市值()
    可用资金 = 引擎.获取可用资金()
    初始资金 = 引擎.获取初始资金() if hasattr(引擎, '获取初始资金') else 1000000
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        收益率 = (总盈亏 / 初始资金) * 100 if 初始资金 > 0 else 0
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{收益率:+.1f}%")
    
    # 实时行情
    st.markdown("### 📈 实时行情")
    
    行情品种 = ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA"]
    行情列 = st.columns(len(行情品种))
    
    for i, 品种 in enumerate(行情品种):
        with 行情列[i]:
            try:
                结果 = 行情获取.获取价格(品种)
                if 结果 and hasattr(结果, '价格'):
                    价格 = 结果.价格
                else:
                    价格 = None
                if 价格:
                    st.metric(品种, f"${价格:.2f}")
                else:
                    st.metric(品种, "—")
            except:
                st.metric(品种, "—")
    
    # ========== 快捷交易 ==========
    st.markdown("### 🚀 快捷交易")
    
    col1, col2 = st.columns(2)
    
    # ========== 买入区域 ==========
    with col1:
        st.markdown("#### 买入")
        
        可买品种列表 = [
            "EURUSD",
            "BTC-USD",
            "GC=F",
            "000001.SS",
            "AAPL"
        ]
        
        st.caption(f"📊 可交易品种: {可买品种列表}")
        
        买入品种 = st.selectbox("选择品种", 可买品种列表, key="buy_symbol_select")
        
        try:
            行情结果 = 行情获取.获取价格(买入品种)
            if 行情结果 and hasattr(行情结果, '价格'):
                当前买入价 = 行情结果.价格
            else:
                当前买入价 = 0
            st.caption(f"当前价格: ${当前买入价:.4f}" if 当前买入价 > 0 else "获取价格失败")
        except:
            当前买入价 = 0
            st.caption("获取价格失败")
        
        if 买入品种 == "000001.SS":
            单位提示 = "手 (1手=100股)"
            默认数量 = 1
            步长 = 1
        elif 买入品种 == "EURUSD":
            单位提示 = "手 (1手=10000单位)"
            默认数量 = 1
            步长 = 1
        elif 买入品种 == "BTC-USD":
            单位提示 = "个"
            默认数量 = 1
            步长 = 1
        else:
            单位提示 = "股"
            默认数量 = 100
            步长 = 10
        
        买入数量 = st.number_input(
            f"数量 ({单位提示})", 
            min_value=1, 
            value=默认数量, 
            step=步长, 
            key="buy_qty_input"
        )
        
        if 买入品种 == "000001.SS":
            实际股数 = 买入数量 * 100
            预计花费 = 当前买入价 * 实际股数
            st.caption(f"预计花费: ¥{预计花费:,.0f} (实际股数: {实际股数}股)")
        elif 买入品种 == "EURUSD":
            实际单位 = 买入数量 * 10000
            预计花费 = 当前买入价 * 实际单位
            st.caption(f"预计花费: ¥{预计花费:,.0f} (实际单位: {实际单位})")
        else:
            预计花费 = 当前买入价 * 买入数量
            st.caption(f"预计花费: ¥{预计花费:,.0f}")
        
        if st.button("买入", type="primary", use_container_width=True, key="buy_button"):
            if 当前买入价 <= 0:
                st.error("无法获取价格，请稍后再试")
            else:
                try:
                    引擎.买入(买入品种, 当前买入价, 买入数量)
                    st.success(f"✅ 已买入 {买入品种} {买入数量} 单位")
                    st.rerun()
                except Exception as e:
                    st.error(f"买入失败: {e}")
    
    # ========== 卖出区域 ==========
    with col2:
        st.markdown("#### 卖出")
        
        持仓品种列表 = list(引擎.持仓.keys())
        
        if 持仓品种列表:
            卖出选项 = [f"{品种} (持仓: {int(引擎.持仓[品种].数量)}股/单位)" for 品种 in 持仓品种列表]
            卖出选项索引 = st.selectbox(
                "选择持仓品种", 
                range(len(卖出选项)), 
                format_func=lambda i: 卖出选项[i], 
                key="sell_symbol_select"
            )
            卖品种 = 持仓品种列表[卖出选项索引]
            最大可卖数量 = int(引擎.持仓[卖品种].数量)
            
            st.caption(f"持仓成本: ${引擎.持仓[卖品种].平均成本:.4f}")
            
            try:
                行情结果 = 行情获取.获取价格(卖品种)
                if 行情结果 and hasattr(行情结果, '价格'):
                    当前卖出价 = 行情结果.价格
                else:
                    当前卖出价 = 0
                st.caption(f"当前价格: ${当前卖出价:.4f}" if 当前卖出价 > 0 else "获取价格失败")
            except:
                当前卖出价 = 0
                st.caption("获取价格失败")
            
            卖出数量 = st.number_input(
                "数量", 
                min_value=1, 
                max_value=最大可卖数量, 
                value=min(100, 最大可卖数量), 
                step=10, 
                key="sell_qty_input"
            )
            
            预计收入 = 当前卖出价 * 卖出数量
            st.caption(f"预计收入: ¥{预计收入:,.0f}")
            
            if st.button("卖出", use_container_width=True, key="sell_button"):
                if 当前卖出价 <= 0:
                    st.error("无法获取价格，请稍后再试")
                else:
                    try:
                        引擎.卖出(卖品种, 当前卖出价, 卖出数量)
                        st.success(f"✅ 已卖出 {卖品种} {卖出数量} 单位")
                        st.rerun()
                    except Exception as e:
                        st.error(f"卖出失败: {e}")
        else:
            st.info("暂无持仓")
            st.selectbox("选择持仓品种", ["无持仓"], disabled=True, key="sell_symbol_disabled")
            st.number_input("数量", min_value=1, value=100, disabled=True, key="sell_qty_disabled")
            st.button("卖出", disabled=True, use_container_width=True, key="sell_button_disabled")
