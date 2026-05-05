import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="QUANT SYSTEM", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1a1d24; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid #2a2d34; }
    .stMetric label { color: #888888 !important; font-size: 13px; }
    .stMetric div { color: #00d2ff !important; font-size: 24px; font-weight: bold; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 5px; }
    .main-title { text-align: center; margin-bottom: 20px; }
    .strategy-card { background-color: #1a1d24; border-radius: 10px; padding: 10px 15px; margin: 5px 0; border-left: 3px solid #00d2ff; }
    .status-green { color: #00ff88; }
    .status-yellow { color: #ffaa00; }
    hr { border-color: #2a2d34; margin: 15px 0; }
    .market-card { background-color: #1a1d24; border-radius: 10px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-title"><h1>🔷 QUANT SYSTEM v5.0</h1><p>多类目 · 多策略 · AI自动交易 · 实时监控</p></div>', unsafe_allow_html=True)

# ================== 顶部4个指标（一排显示）==================
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", "$105,420", delta="+5.4%")
col2.metric("📈 日盈亏", "+$2,140", delta="+2.1%")
col3.metric("📊 夏普比率", "1.42", delta="+0.12")
col4.metric("🎯 胜率", "71.4%", delta="+3.2%")

st.markdown("---")

# ================== 获取价格 ==================
def get_price(symbol):
    try:
        from data.market_data import get_1min_kline
        kline = get_1min_kline(symbol)
        return kline.get('close', random.uniform(1.08, 1.12)) if kline else random.uniform(1.08, 1.12)
    except:
        return random.uniform(1.08, 1.12)

eurusd_price = get_price("EURUSD")
btc_price = get_price("BTC-USD")
gold_price = get_price("GC=F")

# ================== 初始化session ==================
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False
if 'detail_title' not in st.session_state:
    st.session_state.detail_title = ""
if 'detail_content' not in st.session_state:
    st.session_state.detail_content = ""

# ================== 市场概览（3个卡片一排）==================
st.markdown("### 📈 市场概览")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"""
    <div class="market-card">
        <b>EUR/USD</b><br>
        <span style="font-size:24px; color:#00d2ff">{eurusd_price:.5f}</span><br>
        <span style="color:{"#00ff88" if eurusd_price-1.085>0 else "#ff4444"}">{eurusd_price-1.085:.4f}</span>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown(f"""
    <div class="market-card">
        <b>BTC-USD</b><br>
        <span style="font-size:24px; color:#00d2ff">${btc_price:,.0f}</span><br>
        <span style="color:{"#00ff88" if btc_price/45000-1>0 else "#ff4444"}">{(btc_price/45000-1)*100:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)
with col_c:
    st.markdown(f"""
    <div class="market-card">
        <b>黄金期货</b><br>
        <span style="font-size:24px; color:#00d2ff">${gold_price:.0f}</span><br>
        <span style="color:{"#00ff88" if gold_price/1950-1>0 else "#ff4444"}">{(gold_price/1950-1)*100:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================== K线图 + 侧边策略状态（左右布局）==================
col_kline, col_strategy = st.columns([2, 1])

with col_kline:
    st.markdown("### 📉 价格走势")
    fig = go.Figure(data=[go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=50, freq='1h'),
        open=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)],
        high=[eurusd_price + random.uniform(0.001, 0.003) for _ in range(50)],
        low=[eurusd_price - random.uniform(0.001, 0.003) for _ in range(50)],
        close=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)]
    )])
    fig.update_layout(height=380, paper_bgcolor="#0e1117", plot_bgcolor="#1a1d24", font_color="#ffffff", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_strategy:
    st.markdown("### 📋 策略状态")
    st.markdown("""
    <div class="strategy-card">🟢 期货趋势策略 <span style="float:right">+8.2%</span></div>
    <div class="strategy-card">🟢 外汇利差策略 <span style="float:right">+5.1%</span></div>
    <div class="strategy-card">🟡 期货均值回归 <span style="float:right">+2.3%</span></div>
    <div class="strategy-card">🟢 外汇突破策略 <span style="float:right">+6.7%</span></div>
    <div class="strategy-card">🟢 加密双均线 <span style="float:right">+12.3%</span></div>
    <div class="strategy-card">🟡 A股双均线 <span style="float:right">+1.8%</span></div>
    <div class="strategy-card">🟢 港股布林带 <span style="float:right">+3.2%</span></div>
    <div class="strategy-card">🟡 美股趋势 <span style="float:right">+4.5%</span></div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 查看全部策略", use_container_width=True):
        st.session_state.show_detail = True
        st.session_state.detail_title = "策略表现详情"
        st.session_state.detail_content = """
        - 期货趋势策略: +8.2% 🟢
        - 外汇利差策略: +5.1% 🟢
        - 期货均值回归: +2.3% 🟡
        - 外汇突破策略: +6.7% 🟢
        - 加密双均线: +12.3% 🟢
        - A股双均线: +1.8% 🟡
        - 港股布林带: +3.2% 🟢
        - 美股趋势: +4.5% 🟢
        - 综合收益率: +5.6%
        """

st.markdown("---")

# ================== 底部信息 ==================
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    st.caption(f"🟢 系统在线 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col_footer2:
    st.caption("📊 数据源: yfinance | AI: DeepSeek")
with col_footer3:
    st.caption("© 2026 QUANT SYSTEM v5.0")

# ================== 弹出详情对话框 ==================
if st.session_state.show_detail:
    with st.container():
        st.markdown(f"""
        <div style="position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background-color:#1e1e1e; border-radius:16px; padding:25px; border:1px solid #00d2ff; z-index:999; width:400px;">
            <h3 style="color:#00d2ff">{st.session_state.detail_title}</h3>
            <p style="white-space:pre-line">{st.session_state.detail_content}</p>
            <button onclick="location.reload()" style="background:#00d2ff; color:black; border:none; padding:8px 20px; border-radius:20px; cursor:pointer;">关闭</button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("关闭", key="close_popup"):
            st.session_state.show_detail = False
            st.rerun()
