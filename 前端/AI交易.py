# ✅ 前端/AI交易.py（修复AI推荐买入）
# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")

    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "双均线策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认策略"]))

    # 存储AI推荐结果
    if "ai_recommend" not in st.session_state:
        st.session_state.ai_recommend = []

    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner("AI 分析中..."):
            结果 = AI引擎.AI推荐(市场, 策略类型)
            st.session_state.ai_recommend = 结果.get("推荐", [])
            st.rerun()

    # ✅ 显示AI推荐并绑定买入
    if st.session_state.ai_recommend:
        st.markdown("### 📈 AI 推荐买入")
        for idx, item in enumerate(st.session_state.ai_recommend):
            代码 = item["代码"]
            名称 = item["名称"]
            价格 = item["价格"]

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**{名称} ({代码})**  💰 ${价格:.2f}")
                col2.markdown(item.get("趋势", ""))

                # ✅ 最可靠的买入按钮
                if col3.button(f"买入 {名称}", key=f"buy_ai_{代码}_{idx}"):
                    st.info(f"📌 正在买入 {名称} ({代码}) @ ${价格:.2f}")
                    引擎.买入(代码, 价格, 100)
                    st.success(f"✅ 买入请求已发送")
                    st.rerun()
                st.divider()

    # 当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        data = []
        for 品种, pos in 引擎.持仓.items():
            data.append({
                "品种": 品种,
                "数量": int(pos.数量),
                "成本": f"{pos.平均成本:.2f}",
                "现价": f"{pos.当前价格:.2f}"
            })
        st.dataframe(data, use_container_width=True)
    else:
        st.info("暂无持仓")

    # ✅ 测试买入区（保留，用于验证）
    st.markdown("---")
    st.markdown("### 🧪 测试买入（用于验证订单引擎）")
    if st.button("测试买入 AAPL"):
        引擎.买入("AAPL", 287.44, 100)
        st.rerun()
