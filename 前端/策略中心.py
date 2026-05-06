# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 🎯 策略库")
    
    策略列表 = 策略加载器.获取策略()
    
    # ========== 调试：打印策略数量 ==========
    st.info(f"📊 共加载 {len(策略列表)} 个策略")
    
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
    
    # ========== 调试：显示分组信息 ==========
    st.write(f"📂 分组: {list(分组.keys())}")
    
    for 类别, 类别策略 in 分组.items():
        st.markdown(f'<div class="category-title">📁 {类别} ({len(类别策略)})</div>', unsafe_allow_html=True)
        for idx, 策略信息 in enumerate(类别策略):
            with st.container():
                st.markdown(f"**{策略信息['名称']}** - {策略信息['品种']} - {策略信息['类别']}")
                
                if st.button(f"▶ 运行信号", key=f"run_{策略信息['名称']}_{idx}"):
                    行情数据 = 行情获取.获取价格(策略信息['品种'])
                    信号 = 策略运行器.运行(策略信息, 行情数据)
                    策略信号[策略信息['名称']] = 信号
                    st.success(f"📡 {策略信息['名称']} 信号: {信号.upper()}")
                    st.rerun()
                
                if 策略信息['名称'] in 策略信号:
                    信号 = 策略信号[策略信息['名称']]
                    
                    if 信号 == "buy":
                        st.markdown(f"<span style='color:#00ff88;font-weight:bold'>📈 信号: BUY</span>", unsafe_allow_html=True)
                        if st.button(f"💸 执行买入", key=f"buy_{策略信息['名称']}_{idx}"):
                            行情数据 = 行情获取.获取价格(策略信息['品种'])
                            引擎.买入(策略信息['品种'], 行情数据.价格)
                            st.rerun()
                    elif 信号 == "sell":
                        st.markdown(f"<span style='color:#ff4444;font-weight:bold'>📉 信号: SELL</span>", unsafe_allow_html=True)
                        if st.button(f"💸 执行卖出", key=f"sell_{策略信息['名称']}_{idx}"):
                            行情数据 = 行情获取.获取价格(策略信息['品种'])
                            引擎.卖出(策略信息['品种'], 行情数据.价格)
                            st.rerun()
                    else:
                        st.markdown(f"<span style='color:#ffaa00;font-weight:bold'>⏸️ 信号: HOLD</span>", unsafe_allow_html=True)
                
                st.markdown("---")
