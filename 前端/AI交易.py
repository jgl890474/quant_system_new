# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场选择
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    # 根据市场显示可用策略
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "双均线策略", "动量策略"],
        "外汇": ["外汇利差策略", "趋势策略"],
        "加密货币": ["加密双均线", "波动率策略"],
        "期货": ["期货趋势策略"]
    }
    
    策略列表 = 策略映射.get(市场, ["默认策略"])
    策略类型 = st.selectbox("选择策略", 策略列表)
    
    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner(f"AI 正在分析{市场}..."):
            try:
                结果 = AI引擎.AI推荐(市场, 策略类型)
                
                if 结果.get("类型") == "股票池":
                    st.success(f"✅ AI 推荐完成！置信度: {结果.get('置信度', 0)}%")
                    推荐列表 = 结果.get("推荐", [])
                    
                    if 推荐列表:
                        st.markdown("### 📈 AI 推荐买入")
                        for 股票 in 推荐列表:
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"**{股票.get('名称', '未知')}** ({股票.get('代码', '')})")
                                with col2:
                                    st.markdown(f"价格: ${股票.get('价格', 0):.2f}")
                                with col3:
                                    if st.button(f"买入", key=f"buy_{股票['代码']}"):
                                        引擎.买入(股票['代码'], 股票.get('价格', 0), 100)
                                        st.rerun()
                                if 股票.get('理由'):
                                    st.caption(f"📝 {股票['理由']}")
                                st.divider()
                    else:
                        st.warning("暂无推荐股票")
                
                else:
                    # 固定品种分析结果
                    分析列表 = 结果.get("分析", [])
                    st.markdown("### 📊 品种分析")
                    for 品种 in 分析列表:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            with col1:
                                st.markdown(f"**{品种.get('名称', '未知')}**")
                            with col2:
                                st.markdown(f"价格: ${品种.get('价格', 0):.4f}")
                            with col3:
                                信号 = 品种.get('信号', 'hold')
                                if 信号 == 'buy':
                                    st.markdown("🟢 信号: BUY")
                                elif 信号 == 'sell':
                                    st.markdown("🔴 信号: SELL")
                                else:
                                    st.markdown("🟡 信号: HOLD")
                            with col4:
                                if 信号 == 'buy':
                                    if st.button(f"买入", key=f"buy_{品种['代码']}"):
                                        引擎.买入(品种['代码'], 品种.get('价格', 0), 1000)
                                        st.rerun()
                                elif 信号 == 'sell':
                                    if st.button(f"卖出", key=f"sell_{品种['代码']}"):
                                        引擎.卖出(品种['代码'], 品种.get('价格', 0), 1000)
                                        st.rerun()
                            if 品种.get('RSI'):
                                st.caption(f"RSI: {品种['RSI']} | 趋势: {品种.get('趋势', '未知')}")
                            st.divider()
                            
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
