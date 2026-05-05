import streamlit as st
import time
import random

st.set_page_config(page_title="Quant System", layout="wide")

st.title("Quant Trading System v5.0")
st.caption("Multi-Category · Multi-Strategy · AI Auto Trading")

price = random.uniform(1.08, 1.12)

col1, col2, col3 = st.columns(3)
col1.metric("Total Assets", "$100,000")
col2.metric("Latest Price", f"{price:.5f}")
col3.metric("Update Time", time.strftime("%Y-%m-%d %H:%M:%S"))

st.subheader("Strategy Status")
st.success("System Ready")

st.write("### Strategy List")
st.write("1. Futures Trend Strategy (GC=F)")
st.write("2. Futures Mean Reversion (CL=F)")
st.write("3. Forex Carry Trade (AUDJPY)")
st.write("4. Forex Breakout Strategy (EURUSD)")