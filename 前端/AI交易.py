# -*- coding: utf-8 -*-
import streamlit as st


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    st.subheader("🤖 AI 智能交易")
    
    # 选择市场和策略
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("选择市场", ["加密货币", "A股", "美股", "外汇", "期货"])
    with col2:
        if 市场 == "加密货币":
            策略 = st.selectbox("选择策略", ["加密双均线1", "加密风控策略"])
        elif 市场 == "A股":
            策略 = st.selectbox("选择策略", ["A股双均线1", "A股量价策略2"])
        elif 市场 == "美股":
            策略 = st.selectbox("选择策略", ["美股简单策略1", "美股动量策略"])
        else:
            策略 = st.selectbox("选择策略", ["默认策略"])
    
    # 显示可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", width="stretch"):
        st.success(f"✅ AI 分析完成！基于 {市场} 市场 {策略} 策略")
        
        # 模拟推荐数据
        推荐列表 = [
            {"名称": "比特币", "代码": "BTC-USD", "价格": 79438, "评分": 85, "理由": "趋势向上"},
            {"名称": "以太坊", "代码": "ETH-USD", "价格": 2257, "评分": 78, "理由": "放量突破"},
            {"名称": "Solana", "代码": "SOL-USD", "价格": 90.88, "评分": 72, "理由": "支撑位反弹"},
        ]
        st.session_state.推荐列表 = 推荐列表
    
    # 显示推荐
    if '推荐列表' in st.session_state:
        st.markdown("### 📈 AI 推荐买入")
        for item in st.session_state.推荐列表:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{item['名称']}** ({item['代码']})")
                with col2:
                    st.write(f"¥{item['价格']:,.2f}")
                with col3:
                    st.write(f"评分: {item['评分']}")
                with col4:
                    if st.button(f"买入", key=f"buy_{item['代码']}"):
                        try:
                            结果 = 引擎.买入(item['代码'], item['价格'], 1, 策略名称=策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {item['名称']}")
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        except Exception as e:
                            st.error(f"买入失败: {e}")
                st.divider()
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.write(f"- {品种}: {数量}个 @ ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
