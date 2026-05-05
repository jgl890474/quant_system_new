import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ================== 页面配置 ==================
st.set_page_config(
    page_title="量化交易系统",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== 样式 ==================
st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; }
    .stMetric label { color: #8892b0 !important; font-size: 11px !important; }
    .stMetric div { color: #00d2ff !important; font-size: 16px !important; }
    h1 { color: #ffffff; text-align: center; font-size: 18px; margin: 5px 0; }
    .caption { text-align: center; color: #8892b0; font-size: 10px; margin-bottom: 15px; }
    .market-card { background-color: #1a1d24; border-radius: 8px; padding: 8px; text-align: center; border: 1px solid #2a2d34; }
    .market-card .price { font-size: 14px; color: #00d2ff; }
    .strategy-card { background-color: #1a1d24; border-radius: 6px; padding: 10px; margin: 5px 0; border-left: 3px solid #00d2ff; }
    .positive { color: #00ff88; }
    .negative { color: #ff4444; }
    hr { border-color: #2a2d34; margin: 10px 0; }
    .footer { text-align: center; color: #8892b0; font-size: 9px; margin-top: 15px; }
    .stButton button { background-color: #1a1d24; color: #fff; border: 1px solid #2a2d34; border-radius: 6px; padding: 4px 8px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化账户 ==================
if "init" not in st.session_state:
    st.session_state.init = True

    # 基础资金
    st.session_state.balance = 100000
    st.session_state.total_assets = 100000
    st.session_state.daily_pnl = 0
    st.session_state.monthly_pnl = 0

    # 行情价格
    st.session_state.eurusd = 1.0850
    st.session_state.btc = 45000
    st.session_state.gold = 1950

    # 持仓
    st.session_state.positions = []

    # 历史记录
    st.session_state.history = []
    st.session_state.asset_history = [100000]

# ================== 自动刷新价格（模拟） ==================
def refresh_price():
    st.session_state.eurusd = round(1.0850 + random.uniform(-0.0015, 0.0015), 5)
    st.session_state.btc = round(45000 + random.uniform(-800, 800), 0)
    st.session_state.gold = round(1950 + random.uniform(-30, 30), 2)

refresh_price()

# ================== 计算持仓盈亏 ==================
def calc_pnl():
    total_pnl = 0
    for p in st.session_state.positions:
        symbol = p["symbol"]
        amount = p["amount"]
        cost = p["price"]

        if symbol == "EURUSD":
            now = st.session_state.eurusd
            pnl = (now - cost) * amount * 10000
        elif symbol == "BTCUSD":
            now = st.session_state.btc
            pnl = (now - cost) * amount
        elif symbol == "GOLD":
            now = st.session_state.gold
            pnl = (now - cost) * amount * 100
        else:
            pnl = 0

        p["pnl"] = round(pnl, 2)
        p["now"] = now
        total_pnl += pnl

    st.session_state.daily_pnl = round(total_pnl, 2)
    st.session_state.total_assets = round(st.session_state.balance + total_pnl, 2)

calc_pnl()

# ================== 买入函数 ==================
def buy(symbol, amount):
    price_map = {
        "EURUSD": st.session_state.eurusd,
        "BTCUSD": st.session_state.btc,
        "GOLD": st.session_state.gold
    }
    price = price_map[symbol]
    cost = 0

    if symbol == "EURUSD":
        cost = price * amount * 10000
    elif symbol == "BTCUSD":
        cost = price * amount
    elif symbol == "GOLD":
        cost = price * amount * 100

    if st.session_state.balance < cost:
        return "❌ 资金不足"

    st.session_state.balance -= cost
    st.session_state.positions.append({
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "pnl": 0,
        "now": price
    })
    st.session_state.history.append({
        "时间": datetime.now().strftime("%m-%d %H:%M:%S"),
        "类型": "买入",
        "品种": symbol,
        "价格": price,
        "数量": amount
    })
    return "✅ 买入成功"

# ================== 卖出全部 ==================
def sell_all(symbol):
    keep = []
    total_sell = 0
    for p in st.session_state.positions:
        if p["symbol"] == symbol:
            total_sell += p["pnl"] + (p["price"] * p["amount"] * (10000 if symbol == "EURUSD" else 1 if symbol == "BTCUSD" else 100))
        else:
            keep.append(p)
    st.session_state.positions = keep
    st.session_state.balance += total_sell
    st.session_state.history.append({
        "时间": datetime.now().strftime("%m-%d %H:%M:%S"),
        "类型": "卖出",
        "品种": symbol,
        "价格": st.session_state[symbol.lower()],
        "数量": "全部"
    })

# ================== 页面导航 ==================
st.markdown('<h1>📊 量化交易系统 v5.0（完整版可运行）</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">模拟交易 · 自动行情 · 持仓盈亏 · 策略交易</div>', unsafe_allow_html=True)

nav_cols = st.columns(6)
pages = ["首页", "行情", "交易", "持仓", "历史", "资产"]
for i, p in enumerate(pages):
    if nav_cols[i].button(p, use_container_width=True):
        st.session_state.page = p

page = st.session_state.get("page", "首页")
st.markdown("---")

# ================== 顶部仪表盘 ==================
col1, col2, col3, col4 = st.columns(4)
col1.metric("总资产", f"${st.session_state.total_assets:,.0f}")
col2.metric("可用资金", f"${st.session_state.balance:,.0f}")
col3.metric("今日盈亏", f"{st.session_state.daily_pnl:+,.0f}$")
col4.metric("持仓数", len(st.session_state.positions))

st.markdown("---")

# ================== 首页 ==================
if page == "首页":
    st.markdown("### 🌍 实时行情")
    r1, r2, r3 = st.columns(3)
    r1.markdown(f'<div class="market-card">EUR/USD<br><span class="price">{st.session_state.eurusd:.5f}</span></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="market-card">BTC/USD<br><span class="price">${st.session_state.btc:,.0f}</span></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="market-card">黄金<br><span class="price">${st.session_state.gold:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 价格走势（模拟K线）")
    times = pd.date_range(end=datetime.now(), periods=30, freq='5min')
    base = st.session_state.eurusd
    opens = [base + random.uniform(-0.001, 0.001) for _ in range(30)]
    highs = [o + random.uniform(0, 0.0005) for o in opens]
    lows = [o - random.uniform(0, 0.0005) for o in opens]
    closes = [base + random.uniform(-0.001, 0.001) for _ in range(30)]

    fig = go.Figure(data=[go.Candlestick(x=times, open=opens, high=highs, low=lows, close=closes)])
    fig.update_layout(height=260, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="white", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ================== 行情 ==================
elif page == "行情":
    st.markdown("### 📊 行情面板")
    df = pd.DataFrame([
        {"品种": "EUR/USD", "价格": st.session_state.eurusd, "涨跌": round(st.session_state.eurusd - 1.0850, 4)},
        {"品种": "BTC/USD", "价格": st.session_state.btc, "涨跌": int(st.session_state.btc - 45000)},
        {"品种": "黄金", "价格": st.session_state.gold, "涨跌": round(st.session_state.gold - 1950, 2)}
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

# ================== 交易 ==================
elif page == "交易":
    st.markdown("### 🤖 策略交易")
    symbol = st.selectbox("品种", ["EURUSD", "BTCUSD", "GOLD"])
    amount = st.number_input("数量", min=0.01, value=1.0, step=0.01)
    c1, c2 = st.columns(2)

    if c1.button("✅ 买入", use_container_width=True, type="primary"):
        msg = buy(symbol, amount)
        st.success(msg)
        time.sleep(0.5)
        st.rerun()

    if c2.button("❌ 卖出全部", use_container_width=True):
        sell_all(symbol)
        st.warning("已卖出全部")
        time.sleep(0.5)
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📌 内置策略（一键交易）")
    if st.button("🚀 趋势策略 → 一键买入EURUSD", use_container_width=True):
        buy("EURUSD", 1)
        st.success("趋势策略已执行")
        st.rerun()

    if st.button("🚀 震荡策略 → 一键买入BTC", use_container_width=True):
        buy("BTCUSD", 0.01)
        st.success("震荡策略已执行")
        st.rerun()

# ================== 持仓 ==================
elif page == "持仓":
    st.markdown("### 💼 当前持仓")
    if not st.session_state.positions:
        st.info("暂无持仓")
    else:
        show = []
        for p in st.session_state.positions:
            show.append({
                "品种": p["symbol"],
                "数量": p["amount"],
                "开仓价": p["price"],
                "当前价": p["now"],
                "盈亏": f"{p['pnl']:+,.0f}$"
            })
        st.dataframe(pd.DataFrame(show), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 仓位分布")
    labels = [p["symbol"] for p in st.session_state.positions] or ["空仓"]
    values = [1 for _ in st.session_state.positions] or [1]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=["#00d2ff","#00ff88","#ffaa00"])])
    fig.update_layout(paper_bgcolor="#0a0c10", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ================== 历史 ==================
elif page == "历史":
    st.markdown("### 📜 交易历史")
    if not st.session_state.history:
        st.info("暂无交易")
    else:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)

# ================== 资产 ==================
elif page == "资产":
    st.markdown("### 📈 资产曲线")
    if len(st.session_state.asset_history) < 2:
        for i in range(20):
            st.session_state.asset_history.append(st.session_state.asset_history[-1] + random.randint(-2000, 3000))

    fig = go.Figure(data=go.Scatter(y=st.session_state.asset_history, line=dict(color="#00d2ff")))
    fig.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("起始资金", "$100000")
    c2.metric("总收益", f"{st.session_state.total_assets - 100000:+,.0f}$")
    c3.metric("收益率", f"{((st.session_state.total_assets/100000)-1)*100:.1f}%")

# ================== 底部 ==================
st.markdown("---")
st.caption(f"✅ 系统正常运行 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
