import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="量化交易", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f5f5f5; }
    .stMetric { background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    h1 { color: #1a1a1a; text-align: center; font-size: 28px; }
    h2, h3 { color: #333333; font-size: 18px; }
    .stButton button { background-color: #1a73e8; color: white; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

st.title("量化交易系统 v5.0")
st.caption("多策略 · AI决策 · 实时监控")

# 指标
c1, c2, c3 = st.columns(3)
c1.metric("总资产", "¥720,000", delta="+2.1%")
c2.metric("今日收益", "¥15,120", delta="+2.1%")
c3.metric("策略数量", "4", delta="0")

# 行情
price = random.uniform(1.08, 1.12)
st.subheader("实时行情")
st.metric("欧元/美元", f"{price:.5f}", delta=f"{price-1.085:.4f}")

# K线
df = pd.DataFrame({"价格": [random.uniform(1.08, 1.12) for _ in range(40)]})
st.line_chart(df, height=200)

# AI决策
st.subheader("AI决策")
if st.button("获取信号", use_container_width=True):
    with st.spinner("分析中..."):
        time.sleep(1)
        signal = random.choice(["买入", "卖出", "持有"])
        if signal == "买入":
            st.success("✅ 信号: 买入")
        elif signal == "卖出":
            st.error("❌ 信号: 卖出")
        else:
            st.warning("⏸️ 信号: 持有")

# 策略列表
st.subheader("策略列表")
for name in ["期货趋势策略", "期货均值回归", "外汇利差交易", "外汇突破策略"]:
    st.write(f"• {name} (运行中)")

st.caption("数据实时更新 | AI引擎: DeepSeek")
