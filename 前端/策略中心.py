# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 🎯 策略库")
    
    # 自定义按钮样式
    st.markdown("""
    <style>
    div.stButton > button {
        background-color: #00d2ff;
        color: #0a0c10;
        border-radius: 20px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0099cc;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        st.markdown(f"##### 📁 {类别} ({len(类别策略)})")
        
        for idx, 策略信息 in enumerate(类别策略):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
                col1.markdown(f"**{策略信息['名称']}**")
                col2.code(策略信息['品种'])
                col3.caption(策略信息['类别'])
                
                if col4.button(f"运行信号", key=f"run_{策略信息['名称']}_{idx}", use_container_width=True):
                    with st.spinner("获取行情中..."):
                        行情数据 = 行情获取.获取价格(策略信息['品种'])
                        信号 = 策略运行器.运行(策略信息, 行情数据)
                        策略信号[策略信息['名称']] = 信号
                        st.success(f"📡 {策略信息['名称']} 信号: {信号.upper()}")
                        st.rerun()
                
                if 策略信息['名称'] in 策略信号:
                    信号 = 策略信号[策略信息['名称']]
                    
                    if 信号 == "buy":
                        st.markdown("🟢 **信号: BUY**")
                        if st.button(f"执行买入", key=f"buy_{策略信息['名称']}_{idx}", use_container_width=True):
                            with st.spinner("执行中..."):
                                行情数据 = 行情获取.获取价格(策略信息['品种'])
                                引擎.买入(策略信息['品种'], 行情数据.价格)
                                st.rerun()
                    elif 信号 == "sell":
                        st.markdown("🔴 **信号: SELL**")
                        if st.button(f"执行卖出", key=f"sell_{策略信息['名称']}_{idx}", use_container_width=True):
                            with st.spinner("执行中..."):
                                行情数据 = 行情获取.获取价格(策略信息['品种'])
                                引擎.卖出(策略信息['品种'], 行情数据.价格)
                                st.rerun()
                    else:
                        st.markdown("🟡 **信号: HOLD**")
                
                st.divider()
