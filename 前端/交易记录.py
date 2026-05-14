# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # 选择市场和策略
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("市场", ["加密货币", "A股", "美股"], key=f"market_{st.session_state.page_key}")
    with col2:
        策略 = st.selectbox("策略", ["加密双均线1", "量价策略", "趋势跟踪"], key=f"strategy_{st.session_state.page_key}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{市场}市场..."):
            try:
                # 调用真正的AI引擎
                if AI引擎 and hasattr(AI引擎, 'AI推荐'):
                    result = AI引擎.AI推荐(市场, 策略)
                    推荐列表 = result.get("推荐", [])
                else:
                    # 备用：手动获取
                    推荐列表 = 手动获取推荐(市场)
                
                st.session_state[f"recommend_{st.session_state.page_key}"] = 推荐列表
                st.success(f"✅ 分析完成，推荐 {len(推荐列表)} 个品种")
            except Exception as e:
                st.error(f"分析失败: {e}")
    
    # 显示推荐
    rec_key = f"recommend_{st.session_state.page_key}"
    if rec_key in st.session_state:
        st.markdown("### 📈 AI推荐买入")
        for idx, item in enumerate(st.session_state[rec_key]):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
            with col1:
                st.write(f"**{item.get('名称', item.get('代码', ''))}**")
                st.caption(item.get('代码', ''))
            with col2:
                价格 = item.get('价格', 0)
                st.write(f"¥{价格:.2f}" if 价格 > 0 else "价格获取中")
            with col3:
                得分 = item.get('得分', item.get('评分', 50))
                st.write(f"评分: {得分}")
            with col4:
                if st.button(f"买入", key=f"buy_{idx}_{item.get('代码', '')}"):
                    代码 = item.get('代码', '')
                    if 代码:
                        try:
                            结果 = 引擎.买入(代码, None, 1, 策略名称=策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {item.get('名称', 代码)}")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        except Exception as e:
                            st.error(f"买入出错: {e}")
            st.divider()


def 手动获取推荐(市场):
    """备用推荐逻辑"""
    推荐列表 = []
    if 市场 == "加密货币":
        品种 = [("BTC-USD", "比特币"), ("ETH-USD", "以太坊"), ("SOL-USD", "Solana")]
    elif 市场 == "A股":
        品种 = [("600519.SS", "贵州茅台"), ("000858.SZ", "五粮液"), ("300750.SZ", "宁德时代")]
    else:
        品种 = [("AAPL", "苹果"), ("NVDA", "英伟达"), ("TSLA", "特斯拉")]
    
    for 代码, 名称 in 品种:
        推荐列表.append({"代码": 代码, "名称": 名称, "价格": 0, "得分": 70})
    return 推荐列表
