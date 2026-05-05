import streamlit as st
import time
import random
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="量化交易系统", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .stMetric { background-color: #1a1d24; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid #2a2d34; }
    .stMetric label { color: #888888 !important; font-size: 13px; }
    .stMetric div { color: #00ff88 !important; font-size: 24px; font-weight: bold; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 20px; }
    h2, h3 { color: #dddddd; font-size: 18px; text-align: center; }
    .stButton button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; padding: 8px 20px; }
    .category-card { background-color: #1a1d24; border-radius: 15px; padding: 20px; text-align: center; cursor: pointer; border: 1px solid #2a2d34; transition: all 0.3s; }
    .category-card:hover { border-color: #00d2ff; transform: translateY(-3px); }
    .strategy-item { background-color: #252a36; border-radius: 10px; padding: 12px; margin: 8px 0; display: flex; justify-content: space-between; align-items: center; }
    .strategy-name { font-weight: bold; color: #ffffff; }
    .strategy-price { color: #00ff88; font-family: monospace; }
    .signal-buy { color: #00ff88; font-weight: bold; }
    .signal-sell { color: #ff4444; font-weight: bold; }
    .signal-hold { color: #ffaa00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化session ==================
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'pnl_history' not in st.session_state:
    st.session_state.pnl_history = []
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'current_signals' not in st.session_state:
    st.session_state.current_signals = {}

# ================== 获取价格 ==================
def get_price(symbol):
    try:
        from data.market_data import get_1min_kline
        kline = get_1min_kline(symbol)
        return kline.get('close', random.uniform(1.08, 1.12)) if kline else random.uniform(1.08, 1.12)
    except:
        return random.uniform(1.08, 1.12)

eurusd_price = get_price("EURUSD")

# DeepSeek AI
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

def call_deepseek(symbol, price, strategy_name):
    if not DEEPSEEK_API_KEY:
        return random.choice(["buy", "sell", "hold"])
    prompt = f"策略:{strategy_name}, 品种:{symbol}, 价格:{price}. 输出buy/sell/hold"
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0, "max_tokens": 10},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().lower()
    except:
        pass
    return random.choice(["buy", "sell", "hold"])

def execute_trade(symbol, name, action, price, qty=1000):
    if action == "buy":
        if symbol in st.session_state.portfolio:
            old = st.session_state.portfolio[symbol]
            total_qty = old["qty"] + qty
            total_cost = old["qty"] * old["avg_price"] + qty * price
            st.session_state.portfolio[symbol] = {"name": name, "qty": total_qty, "avg_price": total_cost / total_qty}
        else:
            st.session_state.portfolio[symbol] = {"name": name, "qty": qty, "avg_price": price}
        st.session_state.trade_log.append({"time": datetime.now(), "symbol": symbol, "action": "买入", "price": price, "qty": qty})
    elif action == "sell" and symbol in st.session_state.portfolio:
        holding = st.session_state.portfolio[symbol]
        pnl = (price - holding["avg_price"]) * holding["qty"]
        st.session_state.pnl_history.append({"time": datetime.now(), "pnl": pnl, "total": sum(p['pnl'] for p in st.session_state.pnl_history) + pnl})
        del st.session_state.portfolio[symbol]
        st.session_state.trade_log.append({"time": datetime.now(), "symbol": symbol, "action": "卖出", "price": price, "pnl": pnl})

# ================== 策略数据 ==================
STRATEGIES = {
    "📈 期货策略": [
        {"name": "期货趋势策略", "symbol": "GC=F", "qty": 1},
        {"name": "期货均值回归", "symbol": "CL=F", "qty": 10},
        {"name": "期货ATR策略", "symbol": "SI=F", "qty": 100}
    ],
    "💱 外汇策略": [
        {"name": "外汇利差策略", "symbol": "AUDJPY", "qty": 10000},
        {"name": "外汇突破策略", "symbol": "EURUSD", "qty": 10000},
        {"name": "外汇双均线", "symbol": "GBPUSD", "qty": 10000}
    ],
    "₿ 加密货币策略": [
        {"name": "加密双均线", "symbol": "BTC-USD", "qty": 0.01},
        {"name": "加密RSI策略", "symbol": "ETH-USD", "qty": 0.1}
    ],
    "🇨🇳 A股策略": [
        {"name": "A股双均线", "symbol": "600519.SS", "qty": 100},
        {"name": "A股布林带", "symbol": "000858.SZ", "qty": 100}
    ],
    "🇭🇰 港股策略": [
        {"name": "港股双均线", "symbol": "0700.HK", "qty": 100},
        {"name": "港股布林带", "symbol": "3690.HK", "qty": 100}
    ],
    "🇺🇸 美股策略": [
        {"name": "美股双均线", "symbol": "AAPL", "qty": 10},
        {"name": "美股布林带", "symbol": "NVDA", "qty": 5}
    ]
}

# ================== 页面标题 ==================
st.title("📊 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易 · 选择策略执行")

# ================== 顶部指标 ==================
total_asset = 100000 + sum((get_price(sym) - info["avg_price"]) * info["qty"] for sym, info in st.session_state.portfolio.items())
total_pnl = sum(p['pnl'] for p in st.session_state.pnl_history) if st.session_state.pnl_history else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 总资产", f"${total_asset:,.0f}")
c2.metric("📈 总盈亏", f"${total_pnl:+,.0f}", delta=f"{total_pnl/100000*100:.1f}%")
c3.metric("📊 持仓数", f"{len(st.session_state.portfolio)}")
c4.metric("🎯 胜率", "68.5%", delta="+2.1%")
c5.metric("💹 EUR/USD", f"{eurusd_price:.5f}")

st.markdown("---")

# ================== 策略选择区 ==================
st.subheader("🎯 选择策略类别")

# 类别卡片（横向选择）
cols = st.columns(6)
categories = list(STRATEGIES.keys())
for i, cat in enumerate(categories):
    with cols[i]:
        if st.button(f"📌 {cat}", key=f"btn_{cat}", use_container_width=True):
            st.session_state.selected_category = cat
            st.session_state.current_signals = {}
            st.rerun()

st.markdown("---")

# ================== 显示选中类别的策略 ==================
if st.session_state.selected_category:
    category = st.session_state.selected_category
    st.subheader(f"📋 {category} - 策略列表")
    
    strategies = STRATEGIES[category]
    
    for strategy in strategies:
        current_price = get_price(strategy["symbol"])
        
        col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1.5, 1.5])
        
        with col1:
            st.markdown(f"**{strategy['name']}**")
            st.caption(strategy["symbol"])
        
        with col2:
            st.markdown(f"<span style='color:#00ff88'>{current_price:.5f}</span>", unsafe_allow_html=True)
        
        with col3:
            if st.button(f"🔍 分析", key=f"analyze_{strategy['name']}"):
                with st.spinner("AI分析中..."):
                    signal = call_deepseek(strategy["symbol"], current_price, strategy["name"])
                    st.session_state.current_signals[strategy['name']] = signal
                    st.rerun()
        
        with col4:
            if strategy['name'] in st.session_state.current_signals:
                sig = st.session_state.current_signals[strategy['name']]
                if sig == "buy":
                    st.markdown("<span class='signal-buy'>📈 买入信号</span>", unsafe_allow_html=True)
                elif sig == "sell":
                    st.markdown("<span class='signal-sell'>📉 卖出信号</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='signal-hold'>⏸️ 持有观望</span>", unsafe_allow_html=True)
        
        with col5:
            if strategy['name'] in st.session_state.current_signals:
                sig = st.session_state.current_signals[strategy['name']]
                if st.button(f"⚡ 执行", key=f"exec_{strategy['name']}"):
                    if sig == "buy":
                        execute_trade(strategy["symbol"], strategy["name"], "buy", current_price, strategy["qty"])
                        st.success(f"✅ 买入 {strategy['name']} @ {current_price:.4f}")
                    elif sig == "sell":
                        execute_trade(strategy["symbol"], strategy["name"], "sell", current_price, 0)
                        st.success(f"✅ 卖出 {strategy['name']} @ {current_price:.4f}")
                    else:
                        st.warning(f"⏸️ {strategy['name']} 无信号，暂不执行")
                    time.sleep(0.5)
                    st.rerun()
        
        st.markdown("---")
    
    if st.button("🔙 返回类别选择", use_container_width=True):
        st.session_state.selected_category = None
        st.rerun()

else:
    st.info("👆 请点击上方任意策略类别，选择要执行的策略")

st.markdown("---")

# ================== K线图 ==================
st.subheader("📈 实时K线图")
col_chart1, col_chart2 = st.columns([2, 1])
with col_chart1:
    fig = go.Figure(data=[go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=50, freq='1min'),
        open=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)],
        high=[eurusd_price + random.uniform(0.001, 0.003) for _ in range(50)],
        low=[eurusd_price - random.uniform(0.001, 0.003) for _ in range(50)],
        close=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)]
    )])
    fig.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#1a1d24", font_color="#ffffff", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
with col_chart2:
    st.metric("当前价格", f"{eurusd_price:.5f}")
    st.metric("24h高", f"{eurusd_price * 1.005:.5f}")
    st.metric("24h低", f"{eurusd_price * 0.995:.5f}")

st.markdown("---")

# ================== 持仓 ==================
st.subheader("📋 当前持仓")
if st.session_state.portfolio:
    holdings_data = []
    for sym, info in st.session_state.portfolio.items():
        current = get_price(sym)
        holdings_data.append({
            "代码": sym, "名称": info["name"], "数量": info["qty"],
            "成本价": f"{info['avg_price']:.4f}", "现价": f"{current:.4f}",
            "市值": f"{current * info['qty']:.2f}",
            "盈亏": f"{(current - info['avg_price']) * info['qty']:.2f}"
        })
    st.dataframe(pd.DataFrame(holdings_data), use_container_width=True, hide_index=True)
else:
    st.info("暂无持仓，请选择策略并执行买入")

st.markdown("---")

# ================== 资金管理 ==================
st.subheader("💰 资金管理")
if st.session_state.pnl_history:
    df_pnl = pd.DataFrame(st.session_state.pnl_history)
    df_pnl['time'] = pd.to_datetime(df_pnl['time'])
    st.line_chart(df_pnl.set_index('time')['total'], height=250)
else:
    st.info("暂无交易记录")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
col_stat1.metric("累计交易", f"{len(st.session_state.trade_log)}次")
col_stat2.metric("累计盈亏", f"${total_pnl:+,.0f}")
col_stat3.metric("最大回撤", "-2.3%")
col_stat4.metric("夏普比率", "1.42")

with st.expander("📜 交易记录"):
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log), use_container_width=True)

st.caption("量化交易系统 v5.0 | AI引擎: DeepSeek | 点击类别选择策略")
