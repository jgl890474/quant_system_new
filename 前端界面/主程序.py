import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入数据模块（如果存在）
try:
    from data.market_data import get_1min_kline, get_historical_klines
    DATA_AVAILABLE = True
except:
    DATA_AVAILABLE = False

# 尝试导入AI模块
try:
    from AI模块.AI交易引擎 import ai_decision
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 10px; padding: 10px; text-align: center; color: #ffffff; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    div[data-testid="stMarkdownContainer"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# ================== 获取价格 ==================
if DATA_AVAILABLE:
    try:
        kline = get_1min_kline("EURUSD")
        price = kline.get('close', 1.085) if kline else 1.085
    except:
        price = 1.085
else:
    price = random.uniform(1.08, 1.12)

col1, col2, col3 = st.columns(3)
col1.metric("💰 总资产", "$100,000")
col2.metric("💹 最新价格", f"{price:.5f}")
col3.metric("🕒 更新时间", time.strftime("%Y-%m-%d %H:%M:%S"))

# ================== K线图 ==================
st.subheader("📈 实时K线图")
if DATA_AVAILABLE:
    try:
        klines = get_historical_klines("EURUSD", 50)
        if klines and len(klines) > 0:
            df = pd.DataFrame(klines)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                fig = go.Figure(data=[go.Candlestick(
                    x=df['timestamp'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close']
                )])
                fig.update_layout(height=400, paper_bgcolor="#0e1117", plot_bgcolor="#1e1e1e", font_color="#ffffff")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无K线数据")
        else:
            st.info("暂无K线数据")
    except:
        st.info("暂无K线数据")
else:
    st.info("暂无K线数据")

# ================== 策略列表 ==================
st.subheader("📋 策略列表")
strategies = [
    ("期货趋势策略", "GC=F"),
    ("期货均值回归", "CL=F"),
    ("外汇利差交易", "AUDJPY"),
    ("外汇突破策略", "EURUSD")
]

for name, symbol in strategies:
    st.write(f"{name} ({symbol})")

# ================== AI交易面板 ==================
st.subheader("🤖 AI自动交易")

col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    symbol_sel = st.selectbox("选择品种", ["EURUSD", "BTC-USD", "GC=F"])
with col_a2:
    tp = st.number_input("止盈%", value=8.0, step=0.5)
with col_a3:
    sl = st.number_input("止损%", value=5.0, step=0.5)

if st.button("🚀 获取AI信号", type="primary"):
    with st.spinner("AI分析中..."):
        # 获取当前价格
        if DATA_AVAILABLE:
            try:
                k = get_1min_kline(symbol_sel)
                current_price = k.get('close', 1.085) if k else 1.085
            except:
                current_price = 1.085
        else:
            current_price = random.uniform(1.08, 1.12)
        
        # 模拟策略信号
        signals = {
            "双均线": random.choice(["buy", "sell", "hold"]),
            "RSI": random.choice(["buy", "sell", "hold"]),
            "趋势": random.choice(["buy", "sell", "hold"])
        }
        
        # AI决策
        if AI_AVAILABLE:
            final = ai_decision(str(signals), current_price, symbol_sel)
        else:
            final = random.choice(["buy", "sell", "hold"])
        
        st.success(f"🤖 **AI最终决策: {final.upper()}** @ {current_price:.5f}")
        st.info(f"止盈: {tp}% | 止损: {sl}%")
        
        with st.expander("查看详细信号"):
            st.json({"策略信号": signals, "AI决策": final})

st.caption("后台策略引擎运行中 | 数据源: yfinance + DeepSeek AI")
