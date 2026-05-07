# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
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
                策略信号值 = 策略运行器.运行(策略信息, 行情数据)
                st.session_state['策略信号'] = 策略信号值
                st.success(f"📡 策略信号: {策略信号值.upper()}")
                st.rerun()
        
        # ========== 显示策略信号（彻底修复） ==========
        显示信号 = st.session_state.get('策略信号', None)
        if 显示信号 is not None:
            st.markdown(f"### 策略信号: **{显示信号.upper()}**")
        else:
            st.markdown("### 策略信号: 未运行")
        
        # AI 分析按钮
        st.markdown("---")
        st.markdown("### 🧠 AI 深度分析")
        
        if st.button("🚀 AI 分析并执行", type="primary", use_container_width=True):
            with st.spinner("AI 正在分析中..."):
                try:
                    # 获取策略信号
                    策略信号值 = st.session_state.get('策略信号', 'hold')
                    if 策略信号值 is None:
                        策略信号值 = 'hold'
                    
                    # 调用 AI 引擎
                    结果 = AI引擎.分析(策略信息['品种'], 当前价格, 策略信号值)
                    
                    # 保存到 session_state
                    st.session_state['AI原始数据'] = 结果
                    
                    # 显示 AI 决策
                    st.success(f"🤖 AI 决策: **{结果.get('最终信号', 'hold').upper()}**")
                    st.info(f"📊 置信度: {结果.get('置信度', 0)}%")
                    st.write(f"💡 分析理由: {结果.get('理由', '无')}")
                    
                    # 显示额外信息
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("建议仓位", f"{结果.get('建议仓位', 'N/A')}")
                    with col2:
                        止损价 = 结果.get('止损价', 0)
                        if 止损价 and 止损价 > 0:
                            st.metric("建议止损", f"${止损价:.2f}")
                        else:
                            st.metric("建议止损", "—")
                    with col3:
                        止盈价 = 结果.get('止盈价', 0)
                        if 止盈价 and 止盈价 > 0:
                            st.metric("建议止盈", f"${止盈价:.2f}")
                        else:
                            st.metric("建议止盈", "—")
                    
                    风险提示 = 结果.get('风险提示', '')
                    if 风险提示:
                        st.warning(f"⚠️ {风险提示}")
                    
                    # 根据 AI 决策显示执行按钮
                    最终信号 = 结果.get('最终信号', 'hold')
                    if 最终信号 == 'buy':
                        if st.button("✅ 确认执行买入", use_container_width=True):
                            引擎.买入(策略信息['品种'], 当前价格)
                            st.rerun()
                    elif 最终信号 == 'sell':
                        if st.button("✅ 确认执行卖出", use_container_width=True):
                            引擎.卖出(策略信息['品种'], 当前价格)
                            st.rerun()
                    else:
                        st.info("⏸️ AI 建议观望，暂不执行交易")
                        
                except Exception as e:
                    st.error(f"AI 分析失败: {e}")
    
    # ========== AI 决策详情 ==========
    st.markdown("---")
    st.markdown("### 📋 AI 决策详情")
    
    if st.session_state.get('AI原始数据'):
        数据 = st.session_state['AI原始数据']
        st.json({
            "最终信号": 数据.get('最终信号', 'N/A'),
            "置信度": f"{数据.get('置信度', 0)}%",
            "理由": 数据.get('理由', 'N/A'),
            "建议仓位": 数据.get('建议仓位', 'N/A'),
            "止损价": f"${数据.get('止损价', 0):.2f}" if 数据.get('止损价', 0) > 0 else "N/A",
            "止盈价": f"${数据.get('止盈价', 0):.2f}" if 数据.get('止盈价', 0) > 0 else "N/A",
            "风险提示": 数据.get('风险提示', 'N/A')
        })
    else:
        st.info("暂无AI决策数据，请先点击「AI 分析并执行」")
    
    # 快速测试
    st.markdown("---")
    st.markdown("### 🧪 快速测试")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 强制买入 100股 AAPL", use_container_width=True):
            try:
                价格 = 行情获取.获取价格("AAPL").price
                引擎.买入("AAPL", 价格, 100)
                st.rerun()
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    with col2:
        if st.button("🟢 查看持仓", use_container_width=True):
            if 引擎.持仓:
                for 品种, pos in 引擎.持仓.items():
                    st.write(f"{品种}: {int(pos.数量)} 股, 成本: {pos.平均成本:.2f}")
            else:
                st.info("暂无持仓")
