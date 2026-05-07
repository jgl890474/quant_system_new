# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器

def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 🎯 策略库")
    
    策略列表 = 策略加载器.获取策略()
    
    # ========== 调试信息：显示加载的策略数量 ==========
    st.caption(f"📊 共加载 {len(策略列表)} 个策略")
    
    if not 策略列表:
        st.info("暂无策略")
        return
    
    # 按类别分组
    分组 = {}
    for s in 策略列表:
        类别 = s.get("类别", "其他")
        if 类别 not in 分组:
            分组[类别] = []
        分组[类别].append(s)
    
    # ========== 调试信息：显示分组情况 ==========
    st.caption(f"📂 分组: {', '.join(分组.keys())}")
    
    # 紧凑楼梯式布局
    for 类别, 类别策略 in 分组.items():
        st.markdown(f"**📁 {类别} ({len(类别策略)})**")
        
        for idx, 策略 in enumerate(类别策略):
            col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 1, 1.5])
            with col1:
                st.caption(f"**{策略['名称']}**")
            with col2:
                st.caption(策略['类别'])
            with col3:
                st.caption("📈 +8.2%")
            with col4:
                st.caption("📉 -12.5%")
            with col5:
                if st.button("运行", key=f"run_{策略['名称']}_{idx}", use_container_width=True):
                    行情数据 = 行情获取.获取价格(策略['品种'])
                    信号 = 策略运行器.运行(策略, 行情数据)
                    策略信号[策略['名称']] = 信号
                    st.success(f"信号: {信号.upper()}")
                    st.rerun()
            
            # 显示信号
            if 策略['名称'] in 策略信号:
                信号 = 策略信号[策略['名称']]
                if 信号 == "buy":
                    st.caption("🟢 信号: BUY")
                    if st.button("买入", key=f"buy_{策略['名称']}_{idx}"):
                        引擎.买入(策略['品种'], 行情获取.获取价格(策略['品种']).价格)
                        st.rerun()
                elif 信号 == "sell":
                    st.caption("🔴 信号: SELL")
                    if st.button("卖出", key=f"sell_{策略['名称']}_{idx}"):
                        引擎.卖出(策略['品种'], 行情获取.获取价格(策略['品种']).价格)
                        st.rerun()
                else:
                    st.caption("🟡 信号: HOLD")
        
        st.divider()
