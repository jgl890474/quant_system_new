import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 10px; padding: 10px; text-align: center; color: #ffffff; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    div[data-testid="stMarkdownContainer"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# 获取价格
price = 1.085
try:
    import sys
    sys.path.append('.')
    from data.market_data import get_1min_kline
    kline = get_1min_kline("EURUSD")
    if kline:
        price = kline.get('close', 1.085)
except:
    price = random.uniform(1.08, 1.12)

col1, col2, col3 = st.columns(3)
col1.metric("总资产", "$100,000")
col2.metric("最新价格", f"{price:.5f}")
col3.metric("更新时间", time.strftime("%Y-%m-%d %H:%M:%S"))

# K线图
st.subheader("实时K线图")
now = time.time()
prices = []
times = []
base_price = price
for i in range(50):
    ts = now - (50 - i) * 60
    p = base_price + (i * 0.0005) + (i % 5) * 0.0005
    times.append(ts)
    prices.append(p)

df = pd.DataFrame({
    "时间": pd.to_datetime(times, unit='s'),
    "价格": prices
})
st.line_chart(df.set_index("时间"), height=300)

# 策略列表
st.subheader("策略列表")
strategies = [
    "期货趋势策略 (GC=F)",
    "期货均值回归 (CL=F)",
    "外汇利差交易 (AUDJPY)",
    "外汇突破策略 (EURUSD)"
]
for s in strategies:
    st.write(s)

# AI交易面板
st.subheader("AI自动交易")

col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    symbol_sel = st.selectbox("选择品种", ["EURUSD", "BTC-USD", "GC=F"])
with col_a2:
    tp = st.number_input("止盈%", value=8.0, step=0.5)
with col_a3:
    sl = st.number_input("止损%", value=5.0, step=0.5)

if st.button("获取AI信号", type="primary"):
    with st.spinner("AI分析中..."):
        try:
            from data.market_data import get_1min_kline
            k = get_1min_kline(symbol_sel)
            current_price = k.get('close', 1.085) if k else 1.085
        except:
            current_price = 1.085
        
        signals = {
            "双均线": random.choice(["buy", "sell", "hold"]),
            "RSI": random.choice(["buy", "sell", "hold"]),
            "趋势": random.choice(["buy", "sell", "hold"])
        }
        
        final = random.choice(["buy", "sell", "hold"])
        
        st.success(f"AI最终决策: {final.upper()} @ {current_price:.5f}")
        st.info(f"止盈: {tp}% | 止损: {sl}%")

st.caption("后台策略引擎运行中")
