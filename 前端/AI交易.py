# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
from 核心 import 行情获取, 策略运行器
from 工具 import 数据库

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 获取策略列表
    策略列表 = 策略加载器.获取策略()
    策略名称列表 = [s["名称"] for s in 策略列表]
    
    if not 策略名称列表:
        st.warning("没有找到策略，请检查策略库")
        return
    
    # 选择策略
    选中策略 = st.selectbox("选择策略", 策略名称列表)
    
    # 获取策略信息
    策略信息 = 策略加载器.根据名称获取(选中策略)
    
    if 策略信息:
        # 显示当前行情
        行情数据 = 行情获取.获取价格(策略信息['品种'])
        当前价格 = 行情数据.价格
        
        st.info(f"📊 当前行情: {策略信息['品种']} = ${当前价格:.4f}")
        
        # 运行策略获取信号
        if st.button("🎯 运行策略信号", use_container_width=True):
            with st.spinner("运行策略中..."):
                策略信号 = 策略运行器.运行(策略信息, 行情数据)
                st.session_state['策略信号'] = 策略信号
                st.success(f"📡 策略信号: {策略信号.upper()}")
        
        # 显示策略信号
        if '策略信号' in st.session_state:
            st.markdown(f"### 策略信号: **{st.session_state['策略信号'].upper()}**")
        
        # AI 分析按钮
        st.markdown("---")
        st.markdown("### 🧠 AI 深度分析")
        
        if st.button("🚀 AI 分析并执行", type="primary", use_container_width=True):
            with st.spinner("AI 正在分析中..."):
                try:
                    # 获取策略信号
                    策略信号 = st.session_state.get('策略信号', 'hold')
                    
                    # 调用 AI 引擎
                    结果 = AI引擎.分析(策略信息['品种'], 当前价格, 策略信号)
                    
                    # 显示 AI 决策
                    st.success(f"🤖 AI 决策: **{结果['最终信号'].upper()}**")
                    st.info(f"📊 置信度: {结果['置信度']}%")
                    st.write(f"💡 分析理由: {结果['理由']}")
                    
                    # 保存 AI 决策到数据库
                    try:
                        数据库.保存AI决策(
                            策略信息['品种'], 
                            当前价格, 
                            策略信号, 
                            结果['最终信号'], 
                            结果['置信度'], 
                            结果['理由']
                        )
                    except:
                        pass
                    
                    # 根据 AI 决策显示执行按钮
                    if 结果['最终信号'] == 'buy':
                        if st.button("✅ 确认执行买入", use_container_width=True):
                            引擎.买入(策略信息['品种'], 当前价格)
                            st.rerun()
                    elif 结果['最终信号'] == 'sell':
                        if st.button("✅ 确认执行卖出", use_container_width=True):
                            引擎.卖出(策略信息['品种'], 当前价格)
                            st.rerun()
                    else:
                        st.info("⏸️ AI 建议观望，暂不执行交易")
                        
                except Exception as e:
                    st.error(f"AI 分析失败: {e}")
    
    # 显示 AI 决策历史
    st.markdown("---")
    st.markdown("### 📜 AI 决策历史")
    
    try:
        历史记录 = 数据库.获取AI决策历史(20)
        if not 历史记录.empty:
            # 显示最近5条
            st.dataframe(历史记录.head(10), use_container_width=True)
        else:
            st.info("暂无 AI 决策记录")
    except:
        st.info("暂无 AI 决策记录")
    
    # 强制买入测试按钮
    st.markdown("---")
    st.markdown("### 🧪 快速测试")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 强制买入 AAPL", use_container_width=True):
            try:
                价格 = 行情获取.获取价格("AAPL").价格
                引擎.买入("AAPL", 价格, 30)
                st.rerun()
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    with col2:
        if st.button("🟢 查看持仓", use_container_width=True):
            if 引擎.持仓:
                for 品种, pos in 引擎.持仓.items():
                    st.write(f"{品种}: {pos.数量} 股, 成本: {pos.平均成本:.2f}")
            else:
                st.info("暂无持仓")
