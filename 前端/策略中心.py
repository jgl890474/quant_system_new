# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 🎯 策略库")
    
    策略列表 = 策略加载器.获取策略()
    
    if not 策略列表:
        st.info("暂无策略，请检查策略库文件夹")
        return
    
    # 按类别分组
    分组 = {}
    for s in 策略列表:
        类别 = s.get("类别", "其他")
        if 类别 not in 分组:
            分组[类别] = []
        分组[类别].append(s)
    
    for 类别, 类别策略 in 分组.items():
        st.markdown(f'<div class="category-title">📁 {类别} ({len(类别策略)})</div>', unsafe_allow_html=True)
        for idx, 策略信息 in enumerate(类别策略):
            col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 1.5])
            col1.write(f"**{策略信息['名称']}**")
            col2.write(策略信息['品种'])
            col3.write(策略信息['类别'])
            
            # 运行信号按钮
            if col4.button(f"▶ 运行信号", key=f"运行_{策略信息['名称']}_{idx}"):
                行情数据 = 行情获取.获取价格(策略信息['品种'])
                信号 = 策略运行器.运行(策略信息, 行情数据)
                策略信号[策略信息['名称']] = 信号
                st.success(f"📡 {策略信息['名称']} 信号: {信号.upper()}")
                st.rerun()
            
            # 显示信号和执行按钮
            if 策略信息['名称'] in 策略信号:
                信号 = 策略信号[策略信息['名称']]
                信号列, 执行列 = st.columns([1, 3])
                
                if 信号 == "buy":
                    信号列.markdown(f"<span style='color:#00ff88;font-weight:bold'>📈 信号: BUY</span>", unsafe_allow_html=True)
                    # 执行买入按钮 - 使用独立的session状态避免重复触发
                    button_key = f"买入_{策略信息['名称']}_{idx}"
                    if 执行列.button(f"💸 执行买入", key=button_key):
                        价格 = 行情获取.获取价格(策略信息['品种']).price
                        # 直接调用引擎买入
                       引擎.买入(策略信息['品种'], 价格)
                        st.rerun()
                        
                elif 信号 == "sell":
                    信号列.markdown(f"<span style='color:#ff4444;font-weight:bold'>📉 信号: SELL</span>", unsafe_allow_html=True)
                    button_key = f"卖出_{策略信息['名称']}_{idx}"
                    if 执行列.button(f"💸 执行卖出", key=button_key):
                        价格 = 行情获取.获取价格(策略信息['品种']).price
                        引擎.卖出(策略信息['品种'], 价格)
                        st.rerun()
                        
                else:
                    信号列.markdown(f"<span style='color:#ffaa00;font-weight:bold'>⏸️ 信号: HOLD</span>", unsafe_allow_html=True)
            
            st.markdown("---")
