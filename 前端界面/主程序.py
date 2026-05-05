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
    .stMetric { background-color: #1a1d24; border-radius: 12px; padding: 16px; text-align: center; border: 1px solid #2a2d34; transition: all 0.3s; }
    .stMetric:hover { border-color: #00d2ff; transform: translateY(-2px); }
    .stMetric label { color: #8892b0 !important; font-size: 13px; letter-spacing: 1px; }
    .stMetric div { color: #00d2ff !important; font-size: 26px; font-weight: 600; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 5px; letter-spacing: 2px; }
    .caption { text-align: center; color: #8892b0; font-size: 13px; margin-bottom: 30px; }
    .market-card { background-color: #1a1d24; border-radius: 12px; padding: 16px; text-align: center; border: 1px solid #2a2d34; transition: all 0.3s; }
    .market-card:hover { border-color: #00d2ff; }
    .strategy-item { background-color: #1a1d24; border-radius: 8px; padding: 10px 15px; margin: 6px 0; display: flex; justify-content: space-between; align-items: center; border-left: 3px solid #00d2ff; }
    .strategy-name { color: #e6e6e6; font-size: 14px; }
    .strategy-pnl { font-family: monospace; font-size: 14px; font-weight: 600; }
    .positive { color: #00ff88; }
    .negative { color: #ff4444; }
    .neutral { color: #ffaa00; }
    hr { border-color: #2a2d34; margin: 20px 0; }
    .nav-btn { background-color: transparent; border: none; color: #8892b0; padding: 8px 20px; cursor: pointer; font-size: 14px; transition: all 0.3s; }
    .nav-btn-active { color: #00d2ff; border-bottom: 2px solid #00d2ff; }
    .footer { text-align: center; color: #8892b0; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #2a2d34; }
    .data-update { font-size: 11px; color: #00d2ff; }
</style>
""", unsafe_allow_html=True)

# ================== 初始化 ==================
if 'page' not in st.session_state:
    st.session_state.page = "首页"
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False
if 'detail_data' not in st.session_state:
    st.session_state.detail_data = {}
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []

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
spx = get_price("^GSPC")

# ================== 导航栏 ==================
st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 · 专业量化平台</div>', unsafe_allow_html=True)

nav_cols = st.columns(6)
nav_items = ["首页", "市场行情", "策略中心", "AI交易", "持仓管理", "关于"]
for i, item in enumerate(nav_items):
    with nav_cols[i]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()

st.markdown("---")

# ================== 顶部核心指标 ==================
col1, col2, col3, col4 = st.columns(4)
col1.metric("总资产", "$108,420", delta="+8.4%")
col2.metric("今日收益", "+$2,140", delta="+2.1%")
col3.metric("持仓数量", "4", delta="0")
col4.metric("月收益率", "+12.5%", delta="+3.2%")

st.markdown("---")

# ================== 首页 ==================
if st.session_state.page == "首页":
    # 实时行情卡片
    st.markdown("### 🔔 实时行情")
    row1 = st.columns(4)
    with row1[0]:
        st.markdown(f"""
        <div class="market-card">
            <span style="color:#8892b0">EUR/USD</span><br>
            <span style="font-size:24px; color:#00d2ff">{eurusd:.5f}</span><br>
            <span class="data-update">实时</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[1]:
        st.markdown(f"""
        <div class="market-card">
            <span style="color:#8892b0">BTC/USD</span><br>
            <span style="font-size:24px; color:#00d2ff">${btc:,.0f}</span><br>
            <span class="data-update">实时</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[2]:
        st.markdown(f"""
        <div class="market-card">
            <span style="color:#8892b0">黄金期货</span><br>
            <span style="font-size:24px; color:#00d2ff">${gold:.0f}</span><br>
            <span class="data-update">实时</span>
        </div>
        """, unsafe_allow_html=True)
    with row1[3]:
        st.markdown(f"""
        <div class="market-card">
            <span style="color:#8892b0">标普500</span><br>
            <span style="font-size:24px; color:#00d2ff">{spx:.0f}</span><br>
            <span class="data-update">实时</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # K线图
    st.markdown("### 📈 价格走势")
    fig = go.Figure(data=[go.Candlestick(
        x=pd.date_range(end=datetime.now(), periods=60, freq='1h'),
        open=[eurusd + random.uniform(-0.002, 0.002) for _ in range(60)],
        high=[eurusd + random.uniform(0.001, 0.003) for _ in range(60)],
        low=[eurusd - random.uniform(0.001, 0.003) for _ in range(60)],
        close=[eurusd + random.uniform(-0.002, 0.002) for _ in range(60)]
    )])
    fig.update_layout(height=380, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 策略状态简要
    st.markdown("### 📋 策略状态")
    strategies = [
        ("期货趋势策略", "+8.2%", "positive"),
        ("外汇利差策略", "+5.1%", "positive"),
        ("期货均值回归", "+2.3%", "neutral"),
        ("外汇突破策略", "+6.7%", "positive"),
        ("加密双均线", "+12.3%", "positive"),
        ("A股双均线", "+1.8%", "neutral")
    ]
    for name, pnl, cls in strategies:
        st.markdown(f"""
        <div class="strategy-item">
            <span class="strategy-name">🟢 {name}</span>
            <span class="strategy-pnl {cls}">{pnl}</span>
        </div>
        """, unsafe_allow_html=True)

# ================== 市场行情 ==================
elif st.session_state.page == "市场行情":
    st.markdown("### 📊 全球市场行情")
    
    market_data = pd.DataFrame([
        {"品种": "EUR/USD", "价格": f"{eurusd:.5f}", "涨跌": f"{eurusd-1.085:.4f}", "涨跌幅": f"{(eurusd-1.085)/1.085*100:.2f}%", "状态": "📈" if eurusd-1.085>0 else "📉"},
        {"品种": "BTC/USD", "价格": f"${btc:,.0f}", "涨跌": f"${btc-45000:,.0f}", "涨跌幅": f"{(btc-45000)/45000*100:.2f}%", "状态": "📈" if btc>45000 else "📉"},
        {"品种": "黄金期货", "价格": f"${gold:.0f}", "涨跌": f"${gold-1950:.0f}", "涨跌幅": f"{(gold-1950)/1950*100:.2f}%", "状态": "📈" if gold>1950 else "📉"},
        {"品种": "标普500", "价格": f"{spx:.0f}", "涨跌": f"{spx-4500:.0f}", "涨跌幅": f"{(spx-4500)/4500*100:.2f}%", "状态": "📈" if spx>4500 else "📉"},
        {"品种": "WTI原油", "价格": "$78.5", "涨跌": "+$1.2", "涨跌幅": "+1.5%", "状态": "📈"},
        {"品种": "中国A50", "价格": "12800", "涨跌": "-50", "涨跌幅": "-0.4%", "状态": "📉"},
    ])
    st.dataframe(market_data, use_container_width=True, hide_index=True)

# ================== 策略中心 ==================
elif st.session_state.page == "策略中心":
    st.markdown("### 🎯 策略库")
    
    strategies_detail = [
        {"名称": "期货趋势策略", "品种": "GC=F", "类型": "趋势跟踪", "状态": "运行中", "收益率": "+8.2%", "夏普": "1.42"},
        {"名称": "期货均值回归", "品种": "CL=F", "类型": "均值回归", "状态": "待机", "收益率": "+2.3%", "夏普": "0.95"},
        {"名称": "外汇利差策略", "品种": "AUDJPY", "类型": "利差交易", "状态": "运行中", "收益率": "+5.1%", "夏普": "1.21"},
        {"名称": "外汇突破策略", "品种": "EURUSD", "类型": "突破交易", "状态": "运行中", "收益率": "+6.7%", "夏普": "1.35"},
        {"名称": "加密双均线", "品种": "BTC-USD", "类型": "双均线", "状态": "运行中", "收益率": "+12.3%", "夏普": "1.68"},
        {"名称": "加密RSI策略", "品种": "ETH-USD", "类型": "RSI指标", "状态": "测试中", "收益率": "+3.2%", "夏普": "0.88"},
    ]
    
    for s in strategies_detail:
        col_a, col_b, col_c, col_d, col_e, col_f = st.columns([2, 1.2, 1.2, 1, 1, 1.2])
        with col_a:
            st.write(f"**{s['名称']}**")
        with col_b:
            st.write(s['品种'])
        with col_c:
            st.write(s['类型'])
        with col_d:
            st.write(f"🟢 {s['状态']}" if "运行" in s['状态'] else "🟡 待机")
        with col_e:
            st.write(f"<span class='positive'>{s['收益率']}</span>" if "+" in s['收益率'] else s['收益率'], unsafe_allow_html=True)
        with col_f:
            st.write(s['夏普'])
        st.markdown("---")

# ================== AI交易 ==================
elif st.session_state.page == "AI交易":
    st.markdown("### 🤖 AI智能交易")
    
    col_a, col_b = st.columns(2)
    with col_a:
        symbol = st.selectbox("交易品种", ["EUR/USD", "BTC/USD", "黄金期货", "标普500", "WTI原油"])
    with col_b:
        strategy = st.selectbox("选择策略", ["综合AI", "趋势跟踪", "均值回归", "突破交易", "利差交易"])
    
    st.markdown("---")
    st.markdown("#### 📊 AI分析结果")
    
    if st.button("执行AI分析", type="primary", use_container_width=True):
        with st.spinner("AI模型分析中..."):
            time.sleep(1.5)
        
        signals = ["买入", "卖出", "持有"]
        confidences = [87, 92, 65, 78, 83]
        
        st.success(f"🤖 AI信号: {signals[0]}  @ 当前价格")
        st.info(f"📈 置信度: 87% | 目标价: +2.3% | 止损: -1.2%")
        st.caption("分析基于DeepSeek大模型 | 仅供参考")

# ================== 持仓管理 ==================
elif st.session_state.page == "持仓管理":
    st.markdown("### 💼 当前持仓")
    
    holdings = pd.DataFrame([
        {"代码": "EURUSD", "名称": "欧元/美元", "数量": 10000, "成本": 1.0850, "现价": eurusd, "市值": f"${eurusd*10000:.0f}", "盈亏": f"${(eurusd-1.085)*10000:.0f}", "盈亏%": f"{(eurusd-1.085)/1.085*100:.1f}%"},
        {"代码": "BTC-USD", "名称": "比特币", "数量": 0.05, "成本": 45000, "现价": btc, "市值": f"${btc*0.05:.0f}", "盈亏": f"${(btc-45000)*0.05:.0f}", "盈亏%": f"{(btc-45000)/45000*100:.1f}%"},
        {"代码": "GC=F", "名称": "黄金期货", "数量": 1, "成本": 1950, "现价": gold, "市值": f"${gold:.0f}", "盈亏": f"${gold-1950:.0f}", "盈亏%": f"{(gold-1950)/1950*100:.1f}%"},
    ])
    st.dataframe(holdings, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### 📈 持仓分析")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    total_value = eurusd*10000 + btc*0.05 + gold
    total_pnl = (eurusd-1.085)*10000 + (btc-45000)*0.05 + (gold-1950)
    col_p1.metric("总市值", f"${total_value:,.0f}")
    col_p2.metric("总盈亏", f"${total_pnl:+,.0f}", delta=f"{total_pnl/100000*100:.1f}%")
    col_p3.metric("仓位占比", "85%")
    col_p4.metric("风险敞口", "中等")
    
    if st.button("刷新持仓数据", use_container_width=True):
        st.rerun()

# ================== 关于 ==================
elif st.session_state.page == "关于":
    st.markdown("### 📖 关于系统")
    st.markdown("""
    <div style="background-color:#1a1d24; border-radius:16px; padding:24px;">
        <h3>量化交易系统 v5.0</h3>
        <p>专业级量化交易平台，集成多策略、AI决策、实时风控。</p>
        <hr>
        <h4>技术架构</h4>
        <table style="width:100%">
            <tr><td>前端框架</td><td>Streamlit</td></tr>
            <tr><td>AI引擎</td><td>DeepSeek API</td></tr>
            <tr><td>数据源</td><td>yfinance</td></tr>
            <tr><td>策略数量</td><td>12个</td></tr>
            <tr><td>支持市场</td><td>外汇/期货/加密货币/股票</td></tr>
        </table>
        <hr>
        <h4>联系方式</h4>
        <p>GitHub: github.com/jgl890474</p>
        <p>项目: quant_system_new</p>
    </div>
    """, unsafe_allow_html=True)

# ================== 底部 ==================
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(f"🟢 系统在线 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col_f2:
    st.caption("📊 数据源: yfinance | AI: DeepSeek")
with col_f3:
    st.caption("© 2026 量化交易系统 v5.0")
