# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")

    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    策略映射 = {
        "A股": ["量价策略", "双均线策略"],
        "美股": ["量价策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认策略"]))

    if "ai_rec" not in st.session_state:
        st.session_state.ai_rec = []

    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner("AI 分析中..."):
            结果 = AI引擎.AI推荐(市场, 策略类型)
            st.session_state.ai_rec = 结果.get("推荐", [])
            st.rerun()

    # ✅ 显示推荐并买入
    if st.session_state.ai_rec:
        st.markdown("### 📈 AI 推荐")
        for idx, item in enumerate(st.session_state.ai_rec):
            code = item["代码"]
            name = item["名称"]
            price = item["价格"]

            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{name} ({code})**  💰 ${price:.4f}")
            col2.markdown(item.get("趋势", ""))

            if col3.button(f"买入 {name}", key=f"buy_{code}_{idx}"):
                st.info(f"📌 正在买入 {name}...")
                引擎.买入(code, price, 100)
                st.success(f"✅ 买入请求已发送")
                st.rerun()
            st.divider()

    # ✅ 显示当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        data = []
        for sym, pos in 引擎.持仓.items():
            data.append({
                "品种": sym,
                "数量": int(pos.数量),
                "成本": f"{pos.平均成本:.4f}",
                "现价": f"{pos.当前价格:.4f}"
            })
        st.dataframe(data, use_container_width=True)
    else:
        st.info("暂无持仓")

    # ✅ 保留测试买入（验证引擎）
    st.markdown("---")
    st.markdown("### 🧪 测试买入（验证引擎）")
    if st.button("测试买入 AAPL"):
        引擎.买入("AAPL", 287.44, 10)
        st.rerun()
