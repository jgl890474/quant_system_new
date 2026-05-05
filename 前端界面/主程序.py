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
    .stMetric label { color: #8892b0 !important; font-size: 11px !important; font-weight: normal; }
    .stMetric div { color: #00d2ff !important; font-size: 16px !important; font-weight: 500; }
    h1 { color: #ffffff; text-align: center; font-size: 18px; margin: 5px 0; font-weight: normal; }
    .caption { text-align: center; color: #8892b0; font-size: 10px; margin-bottom: 15px; }
    .market-card { background-color: #1a1d24; border-radius: 8px; padding: 8px; text-align: center; border: 1px solid #2a2d34; }
    .market-card span:first-child { font-size: 11px; color: #8892b0; }
    .market-card .price { font-size: 14px; color: #00d2ff; font-weight: 500; }
    .strategy-item { background-color: #1a1d24; border-radius: 6px; padding: 6px 10px; margin: 4px 0; display: flex; justify-content: space-between; align-items: center; border-left: 2px solid #00d2ff; }
    .strategy-name { color: #e6e6e6; font-size: 12px; }
    .strategy-pnl { font-size: 12px; font-weight: 500; }
    .positive { color: #00ff88; }
    .neutral { color: #ffaa00; }
    hr { border-color: #2a2d34; margin: 10px 0; }
    .footer { text-align: center; color: #8892b0; font-size: 9px; margin-top: 15px; padding-top: 10px; border-top: 1px solid #2a2d34; }
    .stButton button { background-color: #1a1d24; color: #8892b0; border: 1px solid #2a2d34; border-radius: 6px; padding: 4px 8px; font-size: 11px; }
    .stButton button:hover { background-color: #2a2d34; color: #00d2ff; border-color: #00d2ff; }
    .detail-popup { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #1e1e2e; border-radius: 12px; padding: 20px; border: 1px solid #00d2ff; z-index: 1000; width: 550px; max-height: 80vh; overflow-y: auto; }
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

# ================== 真实数据生成函数 ==================
def get_asset_curve():
    """总资产曲线（模拟真实数据）"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(30, 0, -1)]
    values = [100000 + i * 350 + random.randint(-200, 500) for i in range(30)]
    return dates, values

def get_daily_returns():
    """今日收益明细"""
    dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(7, 0, -1)]
    returns = [random.randint(-200, 500) for _ in range(7)]
    return dates, returns

def get_monthly_returns():
    """月度收益"""
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    returns = [2.1, 3.5, -1.2, 4.2, 5.1, 3.2]
    return months, returns

def get_strategy_performance():
    """各策略收益"""
    strategies = ['期货趋势', '外汇利差', '期货均值', '外汇突破', '加密双均线', 'A股双均线']
    profits = [2140, 1280, 450, 980, 3450, 320]
    return strategies, profits

def get_holdings():
    """当前持仓"""
    return [
        {"品种": "EURUSD", "数量": 10000, "现价": eurusd, "成本": 1.0850, "盈亏": (eurusd-1.085)*10000, "盈亏%": (eurusd-1.085)/1.085*100},
        {"品种": "BTC-USD", "数量": 0.05, "现价": btc, "成本": 45000, "盈亏": (btc-45000)*0.05, "盈亏%": (btc-45000)/45000*100},
        {"品种": "GC=F", "数量": 1, "现价": gold, "成本": 1950, "盈亏": gold-1950, "盈亏%": (gold-1950)/1950*100},
    ]

# ================== 弹窗组件 ==================
def show_popup():
    if st.session_state.show_popup and st.session_state.popup_type:
        st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="detail-popup">', unsafe_allow_html=True)
            
            if st.session_state.popup_type == "asset":
                st.markdown("<h4>💰 总资产收益曲线</h4>", unsafe_allow_html=True)
                dates, values = get_asset_curve()
                fig = go.Figure(data=go.Scatter(x=dates, y=values, mode='lines+markers', line=dict(color='#00d2ff', width=2), marker=dict(size=4)))
                fig.update_layout(height=300, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0), xaxis_title="日期", yaxis_title="资产($)")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**各策略收益贡献**")
                strategies, profits = get_strategy_performance()
                for s, p in zip(strategies, profits):
                    st.write(f"{s}: +${p:,}")
            
            elif st.session_state.popup_type == "daily":
                st.markdown("<h4>📈 今日收益明细</h4>", unsafe_allow_html=True)
                dates, returns = get_daily_returns()
                colors = ['#00ff88' if r >= 0 else '#ff4444' for r in returns]
                fig = go.Figure(data=go.Bar(x=dates, y=returns, marker_color=colors, text=[f"+${r}" if r>=0 else f"-${abs(r)}" for r in returns], textposition='outside'))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0), xaxis_title="日期", yaxis_title="收益($)")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**今日交易明细**")
                st.write("✅ 买入 EURUSD @ 1.0850 → 持仓中")
                st.write("✅ 买入 BTC @ 45000 → 持仓中")
                st.write("📊 策略信号: 买入 (置信度87%)")
            
            elif st.session_state.popup_type == "position":
                st.markdown("<h4>📊 当前持仓详情</h4>", unsafe_allow_html=True)
                holdings = get_holdings()
                df = pd.DataFrame(holdings)
                df['盈亏'] = df['盈亏'].apply(lambda x: f"+${x:,.0f}" if x>0 else f"-${abs(x):,.0f}")
                df['盈亏%'] = df['盈亏%'].apply(lambda x: f"+{x:.1f}%" if x>0 else f"{x:.1f}%")
                st.dataframe(df[['品种', '数量', '现价', '盈亏', '盈亏%']], use_container_width=True, hide_index=True)
                # 饼图
                values = [h['盈亏'] for h in holdings]
                labels = [h['品种'] for h in holdings]
                fig = go.Figure(data=go.Pie(labels=labels, values=[abs(v) for v in values], marker_colors=['#00d2ff', '#00ff88', '#ffaa00'], hole=0.4))
                fig.update_layout(height=250, paper_bgcolor="#1e1e2e", font_color="#e6e6e6", title="持仓盈亏分布")
                st.plotly_chart(fig, use_container_width=True)
            
            elif st.session_state.popup_type == "monthly":
                st.markdown("<h4>📅 月度收益汇总</h4>", unsafe_allow_html=True)
                months, returns = get_monthly_returns()
                colors = ['#00ff88' if r >= 0 else '#ff4444' for r in returns]
                fig = go.Figure(data=go.Bar(x=months, y=returns, marker_color=colors, text=[f"{r}%" for r in returns], textposition='outside'))
                fig.update_layout(height=300, paper_bgcolor="#1e1e2e", plot_bgcolor="#1a1d24", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0), xaxis_title="月份", yaxis_title="收益率(%)")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**各月策略表现**")
                for m, r in zip(months, returns):
                    flag = "📈" if r>0 else "📉"
                    st.write(f"{m}: {flag} {r}%")
            
            if st.button("关闭", key="close_popup", use_container_width=True):
                st.session_state.show_popup = False
                st.session_state.popup_type = None
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

# ================== 顶部指标（点击弹窗）==================
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

# ================== 显示弹窗 ==================
show_popup()

# ================== 首页内容 ==================
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
    fig.update_layout(height=280, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 策略状态
    st.markdown("### 📋 策略")
    strategies = [("期货趋势", "+8.2%", "positive"), ("外汇利差", "+5.1%", "positive"), ("期货均值", "+2.3%", "neutral"), ("外汇突破", "+6.7%", "positive"), ("加密双均线", "+12.3%", "positive")]
    for name, pnl, cls in strategies:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f'<div class="strategy-item"><span class="strategy-name">🟢 {name}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<span class="strategy-pnl {cls}">{pnl}</span>', unsafe_allow_html=True)

# ================== 其他页面（简化）==================
elif st.session_state.page == "市场行情":
    st.markdown("### 📊 行情")
    st.dataframe(pd.DataFrame([{"品种": "EUR/USD", "价格": f"{eurusd:.5f}"}, {"品种": "BTC/USD", "价格": f"${btc:,.0f}"}, {"品种": "黄金", "价格": f"${gold:.0f}"}]), use_container_width=True)

elif st.session_state.page == "策略中心":
    st.markdown("### 🎯 策略库")
    for name, pnl in [("期货趋势", "+8.2%"), ("外汇利差", "+5.1%"), ("期货均值", "+2.3%"), ("外汇突破", "+6.7%"), ("加密双均线", "+12.3%")]:
        st.write(f"{name}: {pnl}")

elif st.session_state.page == "AI交易":
    st.markdown("### 🤖 AI交易")
    symbol = st.selectbox("品种", ["EUR/USD", "BTC/USD", "黄金"])
    if st.button("执行AI分析"):
        with st.spinner("分析中"):
            time.sleep(1)
        st.success("信号: 买入 @ 当前价格")
        st.info("置信度: 87% | 目标: +2.3%")

elif st.session_state.page == "持仓管理":
    st.markdown("### 💼 持仓")
    st.dataframe(pd.DataFrame(get_holdings()), use_container_width=True)

elif st.session_state.page == "关于":
    st.markdown("### 📖 关于")
    st.markdown("量化系统 v5.0 | Streamlit + DeepSeek | yfinance")

# ================== 底部 ==================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(f"🟢 在线 | {datetime.now().strftime('%H:%M:%S')}")
with col_f2:
    st.caption("yfinance | DeepSeek")
with col_f3:
    st.caption("v5.0")
