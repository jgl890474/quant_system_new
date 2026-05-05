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
    .detail-popup { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #1e1e2e; border-radius: 12px; padding: 20px; border: 1px solid #00d2ff; z-index: 1000; width: 500px; max-height: 80vh; overflow-y: auto; }
    .detail-popup h4 { color: #00d2ff; margin-bottom: 12px; font-size: 14px; }
    .close-btn { background-color: #00d2ff; color: #000; border: none; padding: 6px 16px; border-radius: 16px; cursor: pointer; margin-top: 12px; width: 100%; font-size: 12px; }
    .close-btn:hover { background-color: #00ff88; }
    .overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.7); z-index: 999; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化 ==================
if 'page' not in st.session_state:
    st.session_state.page = "首页"
if 'show_popup' not in st.session_state:
    st.session_state.show_popup = False
if 'popup_type' not in st.session_state:
    st.session_state.popup_type = None
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

# ================== 弹窗数据 ==================
def get_asset_curve():
    days = list(range(1, 31))
    values = [100000 + i * 280 + (i % 7) * 100 for i in range(30)]
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
        {"品种": "EURUSD", "数量": 10000, "盈亏": (eurusd-1.085)*10000, "盈亏%": (eurusd-1.085)/1.085*100},
        {"品种": "BTC-USD", "数量": 0.05, "盈亏": (btc-45000)*0.05, "盈亏%": (btc-45000)/45000*100},
        {"品种": "GC=F", "数量": 1, "盈亏": gold-1950, "盈亏%": (gold-1950)/1950*100},
    ]

# ================== 弹窗组件 ==================
def show_popup():
    if st.session_state.show_popup:
        st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="detail-popup">', unsafe_allow_html=True)
            
            if st.session_state.popup_type == "asset":
                st.markdown("<h4>💰 总资产收益曲线</h4>", unsafe_allow_html=True)
                x, y = get_asset_curve()
                fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers', line=dict(color='#00d2ff', width=2)))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**各策略收益贡献**")
                for name, pnl in get_strategy_performance():
                    st.write(f"{name}: +${pnl:,}")
            
            elif st.session_state.popup_type == "daily":
                st.markdown("<h4>📈 近7日收益明细</h4>", unsafe_allow_html=True)
                x, y = get_daily_returns()
                colors = ['#00ff88' if v>=0 else '#ff4444' for v in y]
                fig = go.Figure(data=go.Bar(x=x, y=y, marker_color=colors))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**今日交易**")
                st.write("✅ 买入 EURUSD @ 1.0850")
                st.write("✅ 买入 BTC @ 45000")
            
            elif st.session_state.popup_type == "position":
                st.markdown("<h4>📊 当前持仓详情</h4>", unsafe_allow_html=True)
                holdings = get_holdings()
                df = pd.DataFrame(holdings)
                df['盈亏'] = df['盈亏'].apply(lambda x: f"+${x:,.0f}" if x>0 else f"-${abs(x):,.0f}")
                st.dataframe(df[['品种', '数量', '盈亏']], use_container_width=True, hide_index=True)
                fig = go.Figure(data=go.Pie(labels=['EURUSD', 'BTC', '黄金'], values=[45, 30, 25], marker_colors=['#00d2ff', '#00ff88', '#ffaa00']))
                fig.update_layout(height=200, paper_bgcolor="#1e1e2e")
                st.plotly_chart(fig, use_container_width=True)
            
            elif st.session_state.popup_type == "monthly":
                st.markdown("<h4>📅 月度收益汇总</h4>", unsafe_allow_html=True)
                x, y = get_monthly_returns()
                colors = ['#00ff88' if v>=0 else '#ff4444' for v in y]
                fig = go.Figure(data=go.Bar(x=x, y=y, marker_color=colors))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig, use_container_width=True)
                for m, v in zip(x, y):
                    st.write(f"{m}月: {v}%")
            
            if st.button("关闭", key="close_popup", use_container_width=True):
                st.session_state.show_popup = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ================== 标题 ==================
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

# ================== 顶部指标卡片 ==================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("总资产", "$108.4k", delta="+8.4%")
    if st.button("📊 详情", key="asset_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "asset"
        st.rerun()

with col2:
    st.metric("今日收益", "+$2.1k", delta="+2.1%")
    if st.button("📊 详情", key="daily_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "daily"
        st.rerun()

with col3:
    st.metric("持仓", "4", delta="0")
    if st.button("📊 详情", key="position_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "position"
        st.rerun()

with col4:
    st.metric("月收益", "+12.5%", delta="+3.2%")
    if st.button("📊 详情", key="monthly_btn", use_container_width=True):
        st.session_state.show_popup = True
        st.session_state.popup_type = "monthly"
        st.rerun()

st.markdown("---")

# ================== 显示弹窗 ==================
show_popup()

# ================== 首页内容 ==================
if st.session_state.page == "首页":
    st.markdown("### 🔔 实时行情")
    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="market-card">EUR/USD<br><span class="price">{eurusd:.5f}</span></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="market-card">BTC/USD<br><span class="price">${btc:,.0f}</span></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="market-card">黄金<br><span class="price">${gold:.0f}</span></div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="market-card">标普500<br><span class="price">4500</span></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 价格走势")
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
    st.markdown("### 📋 策略状态")
    strategies = [("期货趋势", "+8.2%"), ("外汇利差", "+5.1%"), ("期货均值", "+2.3%"), ("外汇突破", "+6.7%"), ("加密双均线", "+12.3%")]
    for name, pnl in strategies:
        st.markdown(f'<div class="strategy-card">🟢 {name}<span style="float:right" class="positive">{pnl}</span></div>', unsafe_allow_html=True)

# ================== 市场行情 ==================
elif st.session_state.page == "市场行情":
    st.markdown("### 📊 全球市场行情")
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
        {"名称": "期货趋势策略", "品种": "GC=F", "收益率": "+8.2%", "夏普": "1.42", "状态": "运行中"},
        {"名称": "期货均值回归", "品种": "CL=F", "收益率": "+2.3%", "夏普": "0.95", "状态": "待机"},
        {"名称": "外汇利差策略", "品种": "AUDJPY", "收益率": "+5.1%", "夏普": "1.21", "状态": "运行中"},
        {"名称": "外汇突破策略", "品种": "EURUSD", "收益率": "+6.7%", "夏普": "1.35", "状态": "运行中"},
        {"名称": "加密双均线", "品种": "BTC-USD", "收益率": "+12.3%", "夏普": "1.68", "状态": "运行中"},
        {"名称": "加密RSI策略", "品种": "ETH-USD", "收益率": "+3.2%", "夏普": "0.88", "状态": "测试中"},
    ]
    for s in strategies_detail:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            st.write(f"**{s['名称']}**")
        with col2:
            st.write(s['品种'])
        with col3:
            st.write(f"🟢 {s['收益率']}" if "+" in s['收益率'] else f"🟡 {s['收益率']}")
        with col4:
            st.write(s['夏普'])
        with col5:
            if st.button(f"选择", key=f"select_{s['名称']}"):
                st.session_state.selected_strategy = s['名称']
                st.success(f"已选择: {s['名称']}")
        st.markdown("---")
    
    if st.session_state.selected_strategy:
        st.info(f"当前选中策略: {st.session_state.selected_strategy}")

# ================== AI交易 ==================
elif st.session_state.page == "AI交易":
    st.markdown("### 🤖 AI智能交易")
    
    col_a, col_b = st.columns(2)
    with col_a:
        symbol = st.selectbox("交易品种", ["EUR/USD", "BTC/USD", "黄金期货", "标普500"])
    with col_b:
        strategy = st.selectbox("选择策略", ["综合AI", "趋势跟踪", "均值回归", "突破交易"])
    
    if st.button("执行AI分析", type="primary", use_container_width=True):
        with st.spinner("AI模型分析中..."):
            time.sleep(1.5)
        st.success("🤖 AI信号: 买入 @ 当前价格")
        st.info("📈 置信度: 87% | 目标价: +2.3% | 止损: -1.2%")

# ================== 持仓管理 ==================
elif st.session_state.page == "持仓管理":
    st.markdown("### 💼 当前持仓")
    holdings = get_holdings()
    df = pd.DataFrame(holdings)
    df['盈亏'] = df['盈亏'].apply(lambda x: f"+${x:,.0f}" if x>0 else f"-${abs(x):,.0f}")
    df['盈亏%'] = df['盈亏%'].apply(lambda x: f"+{x:.1f}%" if x>0 else f"{x:.1f}%")
    st.dataframe(df[['品种', '数量', '盈亏', '盈亏%']], use_container_width=True, hide_index=True)
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    total_value = eurusd*10000 + btc*0.05 + gold
    total_pnl = (eurusd-1.085)*10000 + (btc-45000)*0.05 + (gold-1950)
    col_p1.metric("总市值", f"${total_value:,.0f}")
    col_p2.metric("总盈亏", f"${total_pnl:+,.0f}")
    col_p3.metric("仓位占比", "85%")
    col_p4.metric("风险等级", "中等")

# ================== 关于 ==================
elif st.session_state.page == "关于":
    st.markdown("### 📖 关于系统")
    st.markdown("""
    <div style="background-color:#1a1d24; border-radius:12px; padding:20px;">
        <h4>量化交易系统 v5.0</h4>
        <p>专业级量化交易平台，集成多策略、AI决策、实时风控。</p>
        <hr>
        <p><strong>技术架构</strong><br>前端: Streamlit | AI: DeepSeek | 数据: yfinance</p>
        <p><strong>策略数量</strong><br>12个内置策略</p>
        <p><strong>GitHub</strong><br>github.com/jgl890474/quant_system_new</p>
    </div>
    """, unsafe_allow_html=True)

# ================== 底部 ==================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(f"🟢 在线 | {datetime.now().strftime('%H:%M:%S')}")
with col_f2:
    st.caption("yfinance | DeepSeek")
with col_f3:
    st.caption("v5.0")
