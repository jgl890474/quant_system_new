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
    .strategy-card { background-color: #1a1d24; border-radius: 6px; padding: 10px; margin: 5px 0; border-left: 3px solid #00d2ff; cursor: pointer; }
    .strategy-card:hover { background-color: #252a36; }
    .positive { color: #00ff88; }
    hr { border-color: #2a2d34; margin: 10px 0; }
    .footer { text-align: center; color: #8892b0; font-size: 9px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #2a2d34; }
    .stButton button { background-color: #1a1d24; color: #8892b0; border: 1px solid #2a2d34; border-radius: 6px; padding: 4px 8px; font-size: 11px; }

    /* 弹窗核心修复样式 */
    .overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.75);
        z-index: 999;
    }
    .detail-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: #1e1e2e;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #00d2ff;
        z-index: 1000;
        width: 550px;
        max-height: 85vh;
        overflow-y: auto;
    }
    .detail-popup h4 { 
        color: #00d2ff; 
        margin: 0 0 15px 0; 
        font-size: 15px;
    }
    .close-btn-wrap {
        margin-top: 20px;
    }
    .close-btn-wrap button {
        background: #00d2ff !important;
        color: #000 !important;
        font-weight: bold;
        border: none !important;
    }
    .close-btn-wrap button:hover {
        background: #00ff88 !important;
    }
</style>
""", unsafe_allow_html=True)

# ================== 初始化会话状态 ==================
if 'page' not in st.session_state:
    st.session_state.page = "首页"
if 'show_popup' not in st.session_state:
    st.session_state.show_popup = False
if 'popup_type' not in st.session_state:
    st.session_state.popup_type = ""
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = ""

# 模拟行情价格
def get_price(symbol):
    return round(random.uniform(1.08, 1.12), 5)

eurusd = get_price("EURUSD")
btc = round(random.uniform(44000, 46000), 0)
gold = round(random.uniform(1920, 1980), 2)

# ================== 弹窗图表数据 ==================
def get_asset_curve():
    days = list(range(1, 31))
    values = [100000 + i * 320 + random.randint(-150, 150) for i in range(30)]
    return days, values

def get_daily_returns():
    days = list(range(1, 8))
    values = [120, -80, 250, 180, -40, 320, 210]
    return days, values

def get_monthly_returns():
    months = [1, 2, 3, 4, 5, 6]
    values = [2.1, 3.5, -1.2, 4.2, 5.1, 3.2]
    return months, values

def get_strategy_performance():
    return [("期货趋势策略", 2140), ("外汇利差策略", 1280), ("加密双均线", 3450), ("外汇突破策略", 980), ("期货均值回归", 450)]

def get_holdings():
    return [
        {"品种": "EURUSD", "数量": 10000, "盈亏": round((eurusd-1.085)*10000,2), "盈亏%": round((eurusd-1.085)/1.085*100,2)},
        {"品种": "BTC-USD", "数量": 0.05, "盈亏": round((btc-45000)*0.05,2), "盈亏%": round((btc-45000)/45000*100,2)},
        {"品种": "GC=F", "数量": 1, "盈亏": round(gold-1950,2), "盈亏%": round((gold-1950)/1950*100,2)},
    ]

# ================== 弹窗渲染函数（修复可弹出+关闭按钮） ==================
def render_popup():
    if not st.session_state.show_popup:
        return

    # 遮罩层
    st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
    # 弹窗容器
    popup_html = '<div class="detail-popup">'
    st.markdown(popup_html, unsafe_allow_html=True)

    # 资产收益曲线弹窗
    if st.session_state.popup_type == "asset":
        st.subheader("💰 总资产收益曲线")
        x, y = get_asset_curve()
        fig = go.Figure(go.Scatter(
            x=x, y=y, 
            mode='lines+markers', 
            line=dict(color='#00d2ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(0,210,255,0.1)'
        ))
        fig.update_layout(
            height=280,
            paper_bgcolor="#1e1e2e",
            plot_bgcolor="#1a1d24",
            font_color="#e6e6e6",
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**各策略收益贡献**")
        for name, pnl in get_strategy_performance():
            st.write(f"{name}: +${pnl:,}")

    # 近7日收益
    elif st.session_state.popup_type == "daily":
        st.subheader("📈 近7日收益明细")
        x, y = get_daily_returns()
        colors = ['#00ff88' if v>=0 else '#ff4444' for v in y]
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors))
        fig.update_layout(
            height=280,
            paper_bgcolor="#1e1e2e",
            plot_bgcolor="#1a1d24",
            font_color="#e6e6e6"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 持仓详情
    elif st.session_state.popup_type == "position":
        st.subheader("📊 当前持仓详情")
        df = pd.DataFrame(get_holdings())
        st.dataframe(df, use_container_width=True, hide_index=True)

    # 月度收益
    elif st.session_state.popup_type == "monthly":
        st.subheader("📅 月度收益汇总")
        x, y = get_monthly_returns()
        colors = ['#00ff88' if v>=0 else '#ff4444' for v in y]
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors))
        fig.update_layout(
            height=280,
            paper_bgcolor="#1e1e2e",
            plot_bgcolor="#1a1d24",
            font_color="#e6e6e6"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 关闭按钮 固定显示
    st.markdown('<div class="close-btn-wrap">', unsafe_allow_html=True)
    if st.button("关闭弹窗", key="close_popup_btn", use_container_width=True):
        st.session_state.show_popup = False
        st.session_state.popup_type = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================== 顶部标题 ==================
st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易</div>', unsafe_allow_html=True)

# ================== 导航栏 ==================
nav_cols = st.columns(6)
nav_items = ["首页", "市场行情", "策略中心", "AI交易", "持仓管理", "关于"]
for i, item in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()

st.markdown("---")

# ================== 指标卡片 + 弹窗触发（修复绑定） ==================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总资产", "$108.4k", delta="+8.4%")
    if st.button("📊 详情", key="btn_asset"):
        st.session_state.show_popup = True
        st.session_state.popup_type = "asset"
        st.rerun()

with col2:
    st.metric("今日收益", "+$2.1k", delta="+2.1%")
    if st.button("📊 详情", key="btn_daily"):
        st.session_state.show_popup = True
        st.session_state.popup_type = "daily"
        st.rerun()

with col3:
    st.metric("持仓", "4", delta="0")
    if st.button("📊 详情", key="btn_position"):
        st.session_state.show_popup = True
        st.session_state.popup_type = "position"
        st.rerun()

with col4:
    st.metric("月收益", "+12.5%", delta="+3.2%")
    if st.button("📊 详情", key="btn_monthly"):
        st.session_state.show_popup = True
        st.session_state.popup_type = "monthly"
        st.rerun()

st.markdown("---")

# 渲染弹窗（必须放在卡片下方）
render_popup()

# ================== 页面内容 ==================
if st.session_state.page == "首页":
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="market-card">EUR/USD<br><span class="price">{eurusd:.5f}</span></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="market-card">BTC/USD<br><span class="price">${btc:,.0f}</span></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="market-card">黄金<br><span class="price">${gold:.0f}</span></div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="market-card">标普500<br><span class="price">4500</span></div>', unsafe_allow_html=True)

    st.markdown("---")
    fig = go.Figure(go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=40, freq='1h'),
        open=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)],
        high=[eurusd + random.uniform(0.001, 0.003) for _ in range(40)],
        low=[eurusd - random.uniform(0.001, 0.003) for _ in range(40)],
        close=[eurusd + random.uniform(-0.002, 0.002) for _ in range(40)]
    ))
    fig.update_layout(height=280, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "市场行情":
    market_data = pd.DataFrame([
        {"品种": "EUR/USD", "价格": f"{eurusd:.5f}"},
        {"品种": "BTC/USD", "价格": f"${btc:,.0f}"},
        {"品种": "黄金", "价格": f"${gold:.0f}"},
    ])
    st.dataframe(market_data, use_container_width=True, hide_index=True)

elif st.session_state.page == "策略中心":
    st.info("策略中心页面")
elif st.session_state.page == "AI交易":
    st.info("AI交易页面")
elif st.session_state.page == "持仓管理":
    hold_df = pd.DataFrame(get_holdings())
    st.dataframe(hold_df, use_container_width=True, hide_index=True)
elif st.session_state.page == "关于":
    st.info("关于系统 v5.0")

# 底部
st.markdown("---")
st.caption(f"运行时间：{datetime.now().strftime('%H:%M:%S')} | 量化交易系统")
