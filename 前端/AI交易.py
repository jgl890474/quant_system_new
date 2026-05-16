# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # 市场和策略
    市场选项 = ["加密货币", "A股", "美股"]
    策略映射 = {
        "加密货币": ["加密双均线1", "加密风控策略"],
        "A股": ["A股双均线1", "A股量价策略2", "A股隔夜套利策略3", "简单策略"],
        "美股": ["美股简单策略1", "美股动量策略"],
    }
    
    col1, col2 = st.columns(2)
    with col1:
        选中市场 = st.selectbox("选择市场", 市场选项, key=f"market_{st.session_state.page_key}")
    with col2:
        策略选项 = 策略映射.get(选中市场, ["默认策略"])
        选中策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", width="stretch", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{选中市场}市场..."):
            推荐列表 = 获取推荐(选中市场, 可用资金)
            st.session_state[f"recommend_{st.session_state.page_key}"] = 推荐列表
            st.success(f"✅ 分析完成！共推荐 {len(推荐列表)} 个品种")
            st.rerun()
    
    # 显示推荐
    rec_key = f"recommend_{st.session_state.page_key}"
    if rec_key in st.session_state:
        推荐列表 = st.session_state[rec_key]
        
        if 推荐列表:
            st.markdown("### 📈 推荐买入")
            for idx, item in enumerate(推荐列表):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
                with col1:
                    st.write(f"**{item['名称']}**")
                    st.caption(item['代码'])
                with col2:
                    st.write(f"¥{item['价格']:.2f}")
                with col3:
                    st.write(f"评分: {item['评分']}")
                with col4:
                    if st.button(f"买入", key=f"buy_{idx}"):
                        结果 = 引擎.买入(item['代码'], item['价格'], item['建议数量'], 策略名称=选中策略)
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {item['名称']}")
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                st.divider()
        else:
            st.info("暂无推荐，请点击「AI分析」按钮")
    else:
        st.info("👈 请点击「AI分析」按钮获取推荐")
    
    # 持仓显示
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            st.write(f"- {品种}: {pos.数量:.4f}个 @ ¥{pos.平均成本:.2f}")
    else:
        st.info("暂无持仓")


def 获取推荐(市场, 可用资金):
    """获取推荐列表"""
    推荐列表 = []
    
    if 市场 == "A股":
        品种数据 = [
            ("600519.SS", "贵州茅台", 88, 1450, 100),
            ("000858.SZ", "五粮液", 85, 128, 200),
            ("300750.SZ", "宁德时代", 82, 180, 200),
            ("000333.SZ", "美的集团", 80, 80, 200),
            ("600036.SS", "招商银行", 78, 38, 300),
            ("002415.SZ", "海康威视", 75, 35, 300),
            ("002594.SZ", "比亚迪", 78, 265, 100),
        ]
    elif 市场 == "加密货币":
        品种数据 = [
            ("BTC-USD", "比特币", 85, 45000, 0.01),
            ("ETH-USD", "以太坊", 82, 2300, 0.1),
            ("SOL-USD", "Solana", 78, 95, 1),
        ]
    else:
        品种数据 = [
            ("AAPL", "苹果", 88, 175, 5),
            ("NVDA", "英伟达", 85, 120, 8),
            ("MSFT", "微软", 82, 330, 3),
        ]
    
    for 代码, 名称, 评分, 价格, 默认数量 in 品种数据:
        推荐列表.append({
            "代码": 代码,
            "名称": 名称,
            "价格": 价格,
            "评分": 评分,
            "建议数量": 默认数量,
        })
    
    return 推荐列表
