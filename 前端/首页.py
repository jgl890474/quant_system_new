# -*- coding: utf-8 -*-
import streamlit as st
import os
from 核心 import 行情获取

def 显示(引擎):
    # 计算资金指标
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓市值 = 引擎.获取持仓市值()
    可用资金 = 引擎.获取可用资金()
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{(总盈亏/引擎.初始资金)*100:.1f}%")
    
    # 实时行情
    st.markdown("### 📈 实时行情")
    
    行情品种 = ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA", "NVDA"]
    行情列 = st.columns(len(行情品种))
    
    for i, 品种 in enumerate(行情品种):
        with 行情列[i]:
            try:
                价格 = 行情获取.获取价格(品种).价格
                st.metric(品种, f"${价格:.2f}")
            except:
                st.metric(品种, "—")
    
    # ========== 快捷交易 ==========
    st.markdown("### 🚀 快捷交易")
    
    col1, col2 = st.columns(2)
    
    # ========== 买入区域 ==========
    with col1:
        st.markdown("#### 买入")
        
        # 策略库品种列表（根据你的策略库）
        可买品种列表 = [
            "EURUSD",      # 外汇策略
            "BTC-USD",     # 加密货币策略
            "GC=F",        # 期货策略
            "000001.SS",   # A股策略
            "AAPL"         # 美股策略
        ]
        
        st.caption(f"📊 可交易品种: {可买品种列表}")
        
        买入品种 = st.selectbox("选择品种", 可买品种列表, key="buy_symbol")
        
        # 获取当前价格显示
        try:
            当前买入价 = 行情获取.获取价格(买入品种).价格
            st.caption(f"当前价格: ${当前买入价:.4f}")
        except:
            当前买入价 = 0
            st.caption("获取价格失败")
        
        # 根据品种类型显示不同的单位
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
            key="buy_qty"
        )
        
        # 计算预计花费
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
        
        if st.button("买入", type="primary", use_container_width=True):
            try:
                价格 = 行情获取.获取价格(买入品种).价格
                引擎.买入(买入品种, 价格, 买入数量)
                st.rerun()
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    # ========== 卖出区域 ==========
    with col2:
        st.markdown("#### 卖出")
        
        # 只显示有持仓的品种
        持仓品种列表 = list(引擎.持仓.keys())
        
        if 持仓品种列表:
            # 构建显示选项
            卖出选项 = [f"{品种} (持仓: {int(引擎.持仓[品种].数量)}股/单位)" for 品种 in 持仓品种列表]
            卖出选项索引 = st.selectbox(
                "选择持仓品种", 
                range(len(卖出选项)), 
                format_func=lambda i: 卖出选项[i], 
                key="sell_symbol"
            )
            卖品种 = 持仓品种列表[卖出选项索引]
            最大可卖数量 = int(引擎.持仓[卖品种].数量)
            
            st.caption(f"持仓成本: ${引擎.持仓[卖品种].平均成本:.4f}")
            
            try:
                当前卖出价 = 行情获取.获取价格(卖品种).价格
                st.caption(f"当前价格: ${当前卖出价:.4f}")
            except:
                当前卖出价 = 0
            
            卖出数量 = st.number_input(
                "数量", 
                min_value=1, 
                max_value=最大可卖数量, 
                value=min(100, 最大可卖数量), 
                step=10, 
                key="sell_qty"
            )
            
            预计收入 = 当前卖出价 * 卖出数量
            st.caption(f"预计收入: ¥{预计收入:,.0f}")
            
            if st.button("卖出", use_container_width=True):
                try:
                    价格 = 行情获取.获取价格(卖品种).价格
                    引擎.卖出(卖品种, 价格, 卖出数量)
                    st.rerun()
                except Exception as e:
                    st.error(f"卖出失败: {e}")
        else:
            st.info("暂无持仓")
            st.selectbox("选择持仓品种", ["无持仓"], disabled=True, key="sell_symbol_disabled")
            st.number_input("数量", min_value=1, value=100, disabled=True, key="sell_qty_disabled")
            st.button("卖出", disabled=True, use_container_width=True)
