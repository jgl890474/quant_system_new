import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="量化交易系统", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; cursor: pointer; transition: all 0.2s; }
    .stMetric:hover { border-color: #00d2ff; background-color: #252a36; }
    .stMetric label { color: #8892b0 !important; font-size: 11px !important; }
    .stMetric div { color: #00d2ff !important; font-size: 16px !important; }
    h1 { color: #ffffff; text-align: center; font-size: 18px; margin: 5px 0; }
    .caption { text-align: center; color: #8892b0; font-size: 10px; margin-bottom: 15px; }
    .market-card { background-color: #1a1d24; border-radius: 8px; padding: 8px; text-align: center; border: 1px solid #2a2d34; }
    .market-card .price { font-size: 14px; color: #00d2ff; }
    .strategy-item { background-color: #1a1d24; border-radius: 6px; padding: 6px 10px; margin: 4px 0; display: flex; justify-content: space-between; border-left: 2px solid #00d2ff; }
    .positive { color: #00ff88; }
    hr { border-color: #2a2d34; margin: 10px 0; }
    .footer { text-align: center; color: #8892b0; font-size: 9px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #2a2d34; }
    .stButton button { background-color: #1a1d24; color: #8892b0; border: 1px solid #2a2d34; border-radius: 6px; padding: 4px 8px; font-size: 11px; }
    .detail-popup { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #1e1e2e; border-radius: 12px; padding: 20px; border: 1px solid #00d2ff; z-index: 1000; width: 500px; max-height: 80vh; overflow-y: auto; }
    .detail-popup h4 { color: #00d2ff; margin-bottom: 12px; font-size: 14px; }
    .close-btn { background-color: #00d2ff; color: #000; border: none; padding: 6px 16px; border-radius: 16px; cursor: pointer; margin-top: 12px; width: 100%; font-size: 12px; }
    .close-btn:hover { background-color: #00ff88; }
    .overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.7); z-index: 999; }
</style>
""", unsafe_allow_html=True)

# 初始化
if 'show_popup' not in st.session_state:
    st.session_state.show_popup = False
if 'popup_type' not in st.session_state:
    st.session_state.popup_type = None
if 'page' not in st.session_state:
    st.session_state.page = "首页"

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

# 数据函数
def get_curve():
    days = list(range(1, 31))
    values = [100000 + i * 280 for i in range(30)]
    return days, values

def get_daily():
    days = list(range(1, 8))
    values = [120, -80, 250, 180, -40, 320, 210]
    return days, values

def get_monthly():
    months = [1, 2, 3, 4, 5, 6]
    values = [2.1, 3.5, -1.2, 4.2, 5.1, 3.2]
    return months, values

# 弹窗
def show_popup():
    if st.session_state.show_popup:
        st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="detail-popup">', unsafe_allow_html=True)
            
            if st.session_state.popup_type == "asset":
                st.markdown("<h4>💰 总资产曲线</h4>", unsafe_allow_html=True)
                x, y = get_curve()
                fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers', line=dict(color='#00d2ff', width=2)))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.write("期货趋势: +$2,140")
                st.write("外汇利差: +$1,280")
                st.write("加密双均线: +$3,450")
            
            elif st.session_state.popup_type == "daily":
                st.markdown("<h4>📈 近7日收益</h4>", unsafe_allow_html=True)
                x, y = get_daily()
                fig = go.Figure(data=go.Bar(x=x, y=y, marker_color='#00d2ff'))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.write("今日交易: 买入 EURUSD, 买入 BTC")
            
            elif st.session_state.popup_type == "position":
                st.markdown("<h4>📊 持仓详情</h4>", unsafe_allow_html=True)
                holdings = pd.DataFrame([
                    {"品种": "EURUSD", "盈亏": f"${(eurusd-1.085)*10000:.0f}"},
                    {"品种": "BTC", "盈亏": f"${(btc-45000)*0.05:.0f}"},
                    {"品种": "黄金", "盈亏": f"${gold-1950:.0f}"},
                ])
                st.dataframe(holdings, use_container_width=True, hide_index=True)
                fig = go.Figure(data=go.Pie(labels=['EURUSD', 'BTC', '黄金'], values=[45, 30, 25], marker_colors=['#00d2ff', '#00ff88', '#ffaa00']))
                fig.update_layout(height=200, paper_bgcolor="#1e1e2e")
                st.plotly_chart(fig, use_container_width=True)
            
            elif st.session_state.popup_type == "monthly":
                st.markdown("<h4>📅 月度收益</h4>", unsafe_allow_html=True)
                x, y = get_monthly()
                colors = ['#00ff88' if v>0 else '#ff4444' for v in y]
                fig = go.Figure(data=go.Bar(x=x, y=y, marker_color=colors))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                for m, v in zip(x, y):
                    st.write(f"{m}月: {v}%")
            
            if st.button("关闭", key="close_btn", use_container_width=True):
                st.session_state.show_popup = False
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# 标题
st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易</div>', unsafe_allow_html=True)

# 导航
nav_cols = st.columns(6)
nav_items = ["首页", "市场行情", "策略中心", "AI交易", "持仓管理", "关于"]
for i, item in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()

st.markdown("---")

# 指标卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总资产", "$108.4k", delta="+8.4%")
    if st.button("查看详情", key="asset_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "asset"
        st.rerun()

with col2:
    st.metric("今日收益", "+$2.1k", delta="+2.1%")
    if st.button("查看详情", key="daily_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "daily"
        st.rerun()

with col3:
    st.metric("持仓", "4", delta="0")
    if st.button("查看详情", key="position_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "position"
        st.rerun()

with col4:
    st.metric("月收益", "+12.5%", delta="+3.2%")
    if st.button("查看详情", key="monthly_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "monthly"
        st.rerun()

st.markdown("---")

# 显示弹窗
show_popup()

# 首页内容
if st.session_state.page == "首页":
    st.markdown("### 🔔 行情")
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="market-card">EUR/USD<br><span class="price">{eurusd:.5f}</span></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="market-card">BTC/USD<br><span class="price">${btc:,.0f}</span></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="market-card">黄金<br><span class="price">${gold:.0f}</span></div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="market-card">标普500<br><span class="price">4500</span></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 走势")
    fig = go.Figure(data=[go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=40, freq='1h'),
        open=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)],
        high=[eurusd + random.uniform(0.001, 0.003) for _ in range(40)],
        low=[eurusd - random.uniform(0.001, 0.003) for _ in range(40)],
        close=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)]
    )])
    fig.update_layout(height=280, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📋 策略")
    for name, pnl in [("期货趋势", "+8.2%"), ("外汇利差", "+5.1%"), ("期货均值", "+2.3%"), ("外汇突破", "+6.7%"), ("加密双均线", "+12.3%")]:
        st.markdown(f'<div class="strategy-item"><span>🟢 {name}</span><span class="positive">{pnl}</span></div>', unsafe_allow_html=True)

elif st.session_state.page == "市场行情":
    st.markdown("### 📊 行情")
    st.dataframe(pd.DataFrame([{"品种": "EUR/USD", "价格": f"{eurusd:.5f}"}, {"品种": "BTC/USD", "价格": f"${btc:,.0f}"}, {"品种": "黄金", "价格": f"${gold:.0f}"}]), use_container_width=True)

elif st.session_state.page == "策略中心":
    st.markdown("### 🎯 策略库")
    for name, pnl in [("期货趋势", "+8.2%"), ("外汇利差", "+5.1%"), ("期货均值", "+2.3%"), ("外汇突破", "+6.7%"), ("加密双均线", "+12.3%")]:
        st.write(f"{name}: {pnl}")

elif st.session_state.page == "AI交易":
    st.markdown("### 🤖 AI交易")
    if st.button("执行AI分析"):
        with st.spinner("分析中"):
            time.sleep(1)
        st.success("信号: 买入")
        st.info("置信度: 87%")

elif st.session_state.page == "持仓管理":
    st.markdown("### 💼 持仓")
    st.dataframe(pd.DataFrame([{"品种": "EURUSD", "盈亏": (eurusd-1.085)*10000}, {"品种": "BTC", "盈亏": (btc-45000)*0.05}, {"品种": "黄金", "盈亏": gold-1950}]), use_container_width=True)

elif st.session_state.page == "关于":
    st.markdown("### 📖 关于")
    st.markdown("量化系统 v5.0 | Streamlit + DeepSeek")

# 底部
st.markdown("---")
st.caption(f"🟢 在线 | {datetime.now().strftime('%H:%M:%S')}")
