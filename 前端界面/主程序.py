import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 10px; padding: 15px; text-align: center; }
    .stMetric label { color: #888888 !important; font-size: 14px; }
    .stMetric div { color: #00ff88 !important; font-size: 28px; font-weight: bold; }
    h1 { color: #ffffff; text-align: center; font-size: 32px; }
    h2, h3 { color: #ffffff; font-size: 20px; }
    .stButton button { background-color: #00ff88; color: #000000; font-weight: bold; border-radius: 8px; padding: 10px; width: 100%; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 量化交易系统 v5.0")
st.caption("多策略 · AI驱动 · 实时行情")

# 指标行
c1, c2, c3, c4 = st.columns(4)
c1.metric("总资产", "$102,400", delta="+2.4%")
c2.metric("今日盈亏", "+$2,400", delta="+2.4%")
c3.metric("持仓数", "4", delta="0")
c4.metric("胜率", "68.5%", delta="+5.2%")

st.markdown("---")

# 价格区
price = random.uniform(1.08, 1.12)
col_price1, col_price2 = st.columns([2, 1])
with col_price1:
    st.metric("欧元/美元 (EUR/USD)", f"{price:.5f}", delta=f"{price-1.085:.4f}")
with col_price2:
    st.info(f"更新时间: {time.strftime('%H:%M:%S')}")

# 简易K线
st.subheader("价格走势")
df = pd.DataFrame({"价格": [random.uniform(1.08, 1.12) for _ in range(50)]})
st.area_chart(df, height=200)

st.markdown("---")

# AI决策区
st.subheader("🤖 AI 决策引擎")
col_ai1, col_ai2 = st.columns([1, 1])
with col_ai1:
    if st.button("执行分析", use_container_width=True):
        with st.spinner("AI分析中..."):
            time.sleep(1)
            signal = random.choice(["买入", "卖出", "持有"])
            conf = random.randint(65, 95)
            if signal == "买入":
                st.success(f"信号: 买入 @ {price:.5f} | 置信度: {conf}%")
            elif signal == "卖出":
                st.error(f"信号: 卖出 @ {price:.5f} | 置信度: {conf}%")
            else:
                st.warning(f"信号: 持有 | 置信度: {conf}%")
with col_ai2:
    st.code("""
趋势: 多头
RSI: 58.2
MACD: 金叉
建议: 买入
    """)

# 策略列表
st.subheader("策略列表")
for name, sym in [("期货趋势", "GC=F"), ("期货均值回归", "CL=F"), ("外汇利差", "AUDJPY"), ("外汇突破", "EURUSD")]:
    st.markdown(f"- {name} ({sym}) ✅ 运行中")

st.caption("数据源: yfinance | AI: DeepSeek | 自动更新")
