# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")

    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认"]))

    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []

    if st.button("🚀 AI 分析", type="primary"):
        with st.spinner("AI 按策略打分中..."):
            结果 = AI引擎.AI推荐(市场, 策略类型)
            st.session_state.ai_list = 结果.get("推荐", [])
            st.rerun()

    # ✅ 显示推荐（最多 5 只）
    if st.session_state.ai_list:
        st.markdown("### ✅ 优质推荐（按策略打分）")
        for idx, item in enumerate(st.session_state.ai_list):
            code = item["代码"]
            name = item["名称"]
            price = item["价格"]

            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{name} ({code})**  💰 {price:.4f}")
            col2.markdown(item["趋势"])

            if col3.button(f"买入", key=f"buy_{code}_{idx}"):
                引擎.买入(code, price, 100)
                st.success(f"✅ 已买入 {name}")
                st.rerun()
            st.caption(f"📊 理由：{item['理由']} ｜ 得分 {item['得分']}")
            st.divider()

    # 当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            持仓数据.append({
                "品种": sym,
                "数量": int(pos.数量),
                "成本": round(pos.平均成本, 4),
                "现价": round(pos.当前价格, 4)
            })
        st.dataframe(持仓数据, use_container_width=True)
    else:
        st.info("暂无持仓")
