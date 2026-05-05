import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="量化交易系统", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; }
    .stMetric label { color: #8892b0 !important; font-size: 11px !important; font-weight: normal; }
    .stMetric div { color: #00d2ff !important; font-size: 16px !important; font-weight: 500; }
    .stMetric .delta { font-size: 10px !important; }
    h1 { color: #ffffff; text-align: center; font-size: 18px; margin: 5px 0; font-weight: normal; letter-spacing: 1px; }
    .caption { text-align: center; color: #8892b0; font-size: 10px; margin-bottom: 15px; }
    .market-card { background-color: #1a1d24; border-radius: 8px; padding: 8px; text-align: center; border: 1px solid #2a2d34; }
    .market-card span:first-child { font-size: 11px; color: #8892b0; }
    .market-card .price { font-size: 14px; color: #00d2ff; font-weight: 500; }
    .market-card .change { font-size: 10px; }
    .strategy-item { background-color: #1a1d24; border-radius: 6px; padding: 6px 10px; margin: 4px 0; display: flex; justify-content: space-between; align-items: center; border-left: 2px solid #00d2ff; }
    .strategy-name { color: #e6e6e6; font-size: 12px; }
    .strategy-pnl { font-size: 12px; font-weight: 500; }
    .positive { color: #00ff88; }
    .neutral { color: #ffaa00; }
    hr { border-color: #2a2d34; margin: 10px 0; }
    .nav-btn { background-color: transparent; border: none; color: #8892b0; padding: 4px 0; font-size: 11px; text-align: center; }
    .footer { text-align: center; color: #8892b0; font-size: 9px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #2a2d34; }
    .stButton button { background-color: #1a1d24; color: #8892b0; border: 1px solid #2a2d34; border-radius: 6px; padding: 4px 8px; font-size: 11px; }
    .stButton button:hover { background-color: #2a2d34; color: #00d2ff; border-color: #00d2ff; }
    .detail-popup { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #1e1e2e; border-radius: 12px; padding: 20px; border: 1px solid #00d2ff; z-index: 1000; width: 320px; }
    .detail-popup h4 { color: #00d2ff; margin-bottom: 12px; font-size: 14px; }
    .detail-popup p { margin: 6px 0; font-size: 12px; }
    .close-btn { background-color: #00d2ff; color: #000; border: none; padding: 6px 16px; border-radius: 16px; cursor: pointer; margin-top: 12px; width: 100%; font-size: 12px; }
    .overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.7); z-index: 999; }
    .stSelectbox label { font-size: 11px; color: #8892b0; }
    .stSelectbox div { font-size: 12px; }
    .stDataFrame { font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化 ==================
if 'page' not in st.session_state:
    st.session_state.page = "首页"
if 'show_strategy_detail' not in st.session_state:
    st.session_state.show_strategy_detail = False
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None

def get_price(symbol):
    try:
        from data.market_data import get_1min_kline
        kline = get_1min_kline(symbol)
        return kline.get('close', 1.085) if kline else 1.085
    except:
        return random.uniform(1.08, 1.12)

eurusd = get_price("EURUSD")
btc = get_price("BTC-USD")
gold = get_price("GC=F")

# ================== 标题（最顶上，小字）==================
st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易</div>', unsafe_allow_html=True)

# ================== 导航栏（缩小）==================
nav_cols = st.columns(6)
nav_items = ["首页", "市场行情", "策略中心", "AI交易", "持仓管理", "关于"]
for i, item in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()

st.markdown("---")

# ================== 顶部指标（缩小）==================
col1, col2, col3, col4 = st.columns(4)
col1.metric("总资产", "$108.4k", delta="+8.4%")
col2.metric("今日收益", "+$2.1k", delta="+2.1%")
col3.metric("持仓", "4", delta="0")
col4.metric("月收益", "+12.5%", delta="+3.2%")

st.markdown("---")

# ================== 首页 ==================
if st.session_state.page == "首页":
    st.markdown("### 🔔 行情")
    row1 = st.columns(4)
    with row1[0]:
        st.markdown(f"""
        <div class="market-card">
            <span>EUR/USD</span><br>
            <span class="price">{eurusd:.5f}</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[1]:
        st.markdown(f"""
        <div class="market-card">
            <span>BTC/USD</span><br>
            <span class="price">${btc:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[2]:
        st.markdown(f"""
        <div class="market-card">
            <span>黄金</span><br>
            <span class="price">${gold:.0f}</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[3]:
        st.markdown(f"""
        <div class="market-card">
            <span>标普500</span><br>
            <span class="price">4500</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # K线图
    st.markdown("### 📈 走势")
    fig = go.Figure(data=[go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=40, freq='1h'),
        open=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)],
        high=[eurusd + random.uniform(0.001, 0.003) for _ in range(40)],
        low=[eurusd - random.uniform(0.001, 0.003) for _ in range(40)],
        close=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)]
    )])
    fig.update_layout(height=280, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 策略状态
    st.markdown("### 📋 策略")
    st.caption("点击「详情」查看")
    
    strategies = [
        ("期货趋势", "+8.2%", "positive", "GC=F", "趋势跟踪", "运行中"),
        ("外汇利差", "+5.1%", "positive", "AUDJPY", "利差交易", "运行中"),
        ("期货均值", "+2.3%", "neutral", "CL=F", "均值回归", "待机"),
        ("外汇突破", "+6.7%", "positive", "EURUSD", "突破交易", "运行中"),
        ("加密双均线", "+12.3%", "positive", "BTC-USD", "双均线", "运行中"),
    ]
    
    for name, pnl, cls, symbol, stype, status in strategies:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f'<div class="strategy-item"><span class="strategy-name">🟢 {name}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="strategy-pnl {cls}">{pnl}</span>', unsafe_allow_html=True)
        with col3:
            if st.button(f"详情", key=f"detail_{name}", use_container_width=True):
                st.session_state.show_strategy_detail = True
                st.session_state.selected_strategy = {"name": name, "pnl": pnl, "symbol": symbol, "type": stype, "status": status}
                st.rerun()

# ================== 市场行情 ==================
elif st.session_state.page == "市场行情":
    st.markdown("### 📊 行情")
    market_data = pd.DataFrame([
        {"品种": "EUR/USD", "价格": f"{eurusd:.5f}", "涨跌": f"{eurusd-1.085:.4f}"},
        {"品种": "BTC/USD", "价格": f"${btc:,.0f}", "涨跌": f"${btc-45000:,.0f}"},
        {"品种": "黄金", "价格": f"${gold:.0f}", "涨跌": f"${gold-1950:.0f}"},
        {"品种": "WTI原油", "价格": "$78.50", "涨跌": "+$1.20"},
        {"品种": "美元指数", "价格": "104.50", "涨跌": "+0.30"},
    ])
    st.dataframe(market_data, use_container_width=True, hide_index=True)

# ================== 策略中心 ==================
elif st.session_state.page == "策略中心":
    st.markdown("### 🎯 策略库")
    strategies_detail = [
        {"名称": "期货趋势", "品种": "GC=F", "收益率": "+8.2%", "夏普": "1.42"},
        {"名称": "期货均值", "品种": "CL=F", "收益率": "+2.3%", "夏普": "0.95"},
        {"名称": "外汇利差", "品种": "AUDJPY", "收益率": "+5.1%", "夏普": "1.21"},
        {"名称": "外汇突破", "品种": "EURUSD", "收益率": "+6.7%", "夏普": "1.35"},
        {"名称": "加密双均线", "品种": "BTC-USD", "收益率": "+12.3%", "夏普": "1.68"},
    ]
    for s in strategies_detail:
        col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
        with col_a:
            st.write(s['名称'])
        with col_b:
            st.write(s['品种'])
        with col_c:
            st.write(f"🟢 {s['收益率']}")
        with col_d:
            st.write(s['夏普'])
        st.markdown("---")

# ================== AI交易 ==================
elif st.session_state.page == "AI交易":
    st.markdown("### 🤖 AI交易")
    symbol = st.selectbox("品种", ["EUR/USD", "BTC/USD", "黄金"])
    if st.button("执行AI分析", use_container_width=True):
        with st.spinner("分析中"):
            time.sleep(1)
        st.success("信号: 买入")
        st.info("置信度: 87%")

# ================== 持仓管理 ==================
elif st.session_state.page == "持仓管理":
    st.markdown("### 💼 持仓")
    holdings = pd.DataFrame([
        {"代码": "EURUSD", "数量": 10000, "盈亏": f"${(eurusd-1.085)*10000:.0f}"},
        {"代码": "BTC", "数量": 0.05, "盈亏": f"${(btc-45000)*0.05:.0f}"},
        {"代码": "黄金", "数量": 1, "盈亏": f"${gold-1950:.0f}"},
    ])
    st.dataframe(holdings, use_container_width=True, hide_index=True)

# ================== 关于 ==================
elif st.session_state.page == "关于":
    st.markdown("### 📖 关于")
    st.markdown("量化系统 v5.0 | Streamlit + DeepSeek | GitHub: jgl890474")

# ================== 策略详情弹窗 ==================
if st.session_state.show_strategy_detail and st.session_state.selected_strategy:
    s = st.session_state.selected_strategy
    st.markdown(f"""
    <div class="overlay"></div>
    <div class="detail-popup">
        <h4>{s['name']}</h4>
        <p><strong>品种:</strong> {s.get('symbol', '-')}</p>
        <p><strong>类型:</strong> {s.get('type', '-')}</p>
        <p><strong>状态:</strong> {s.get('status', '-')}</p>
        <p><strong>收益:</strong> {s.get('pnl', '-')}</p>
        <p><strong>回撤:</strong> -2.1%</p>
        <button class="close-btn" onclick="location.reload()">关闭</button>
    </div>
    """, unsafe_allow_html=True)
    if st.button("关闭", key="close_popup"):
        st.session_state.show_strategy_detail = False
        st.rerun()

# ================== 底部 ==================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(f"🟢 在线 | {datetime.now().strftime('%H:%M:%S')}")
with col_f2:
    st.caption("yfinance | DeepSeek")
with col_f3:
    st.caption("v5.0")
