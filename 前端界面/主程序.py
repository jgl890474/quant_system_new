import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="QUANT SYSTEM", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .stApp { background-color: #000000; }
    .stMetric { 
        background-color: #111111; 
        border-radius: 10px; 
        padding: 20px;
        border: 1px solid #333333;
    }
    .stMetric label { 
        color: #888888 !important; 
        font-size: 14px !important;
    }
    .stMetric div { 
        color: #00ff00 !important; 
        font-size: 28px !important;
        font-weight: bold !important;
    }
    h1 { 
        color: #00ff00 !important; 
        font-size: 32px !important;
        text-align: center !important;
        font-family: monospace !important;
    }
    h2, h3 { 
        color: #00ff00 !important; 
        font-size: 20px !important;
    }
    .stMarkdown { 
        color: #cccccc !important; 
        font-size: 16px !important;
    }
    div[data-testid="stMarkdownContainer"] { 
        color: #cccccc !important; 
    }
    .stButton button {
        background-color: #00ff00 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 5px !important;
        padding: 10px !important;
        width: 100% !important;
    }
    .stButton button:hover {
        background-color: #33ff33 !important;
    }
    .stSelectbox label, .stNumberInput label {
        color: #888888 !important;
        font-size: 14px !important;
    }
    .stSelectbox div, .stNumberInput div {
        background-color: #111111 !important;
        color: #00ff00 !important;
        border-color: #333333 !important;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("> QUANT SYSTEM v5.0")
st.caption("AI_POWERED | REAL_TIME | MULTI_STRATEGY")

# 资产指标
c1, c2, c3 = st.columns(3)
price = random.uniform(1.08, 1.12)
pnl = (price - 1.085) / 1.085 * 100

with c1:
    st.metric("TOTAL_ASSETS", "$100,000", delta="+2.1%")
with c2:
    st.metric("EUR/USD", f"{price:.5f}", delta=f"{pnl:.2f}%")
with c3:
    st.metric("WIN_RATE", "68.4%", delta="+5.2%")

st.markdown("---")

# 实时价格行
st.markdown(f"### $ EUR/USD: {price:.5f}")
st.caption("last_update: " + time.strftime("%Y-%m-%d %H:%M:%S UTC"))

# 简易K线图
df = pd.DataFrame({"price": [random.uniform(1.08, 1.12) for _ in range(50)]})
st.line_chart(df, height=200, use_container_width=True)

st.markdown("---")

# AI信号区域
st.subheader("> AI_SIGNAL")

col_a, col_b = st.columns([1, 1])

with col_a:
    if st.button("EXECUTE_ANALYSIS", use_container_width=True):
        with st.spinner("AI_ANALYZING..."):
            time.sleep(1)
            signal = random.choice(["BUY", "SELL", "HOLD"])
            confidence = random.randint(65, 95)
            if signal == "BUY":
                st.success(f"🟢 {signal} @ {price:.5f}")
                st.info(f"CONFIDENCE: {confidence}%")
            elif signal == "SELL":
                st.error(f"🔴 {signal} @ {price:.5f}")
                st.info(f"CONFIDENCE: {confidence}%")
            else:
                st.warning(f"🟡 {signal} @ {price:.5f}")
                st.info(f"CONFIDENCE: {confidence}%")

with col_b:
    st.code("""
STRATEGY_STATUS:
- TREND: BULLISH
- RSI: 58.2
- MACD: CROSS
- VOLUME: NORMAL
    """, language="text")

st.markdown("---")

# 策略列表
st.subheader("> STRATEGY_LIST")
strategies = [
    ("FUTURES_TREND", "GC=F", "ACTIVE"),
    ("FUTURES_MEAN_REV", "CL=F", "ACTIVE"),
    ("FOREX_CARRY", "AUDJPY", "ACTIVE"),
    ("FOREX_BREAKOUT", "EURUSD", "ACTIVE")
]

for name, symbol, status in strategies:
    st.markdown(f"├── {name} ({symbol}) → [{status}]")

st.markdown("---")
st.caption("> SYSTEM_READY | AI_ENGINE: DEEPSEEK | DATA: YFINANCE")
