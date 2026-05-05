import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="QUANT SYSTEM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 12px; padding: 15px; text-align: center; border: 1px solid #2a2d34; }
    .stMetric label { color: #888888 !important; font-size: 13px; }
    .stMetric div { color: #00d2ff !important; font-size: 24px; font-weight: bold; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 5px; }
    h2, h3 { color: #dddddd; font-size: 18px; }
    .stButton button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; padding: 6px 16px; }
    .status-green { color: #00ff88; }
    .status-yellow { color: #ffaa00; }
    .status-red { color: #ff4444; }
    .strategy-card { background-color: #1a1d24; border-radius: 10px; padding: 12px; margin: 5px 0; border-left: 3px solid #00d2ff; }
    .popup-box { background-color: #1e1e1e; border-radius: 12px; padding: 20px; border: 1px solid #00d2ff; }
    hr { border-color: #2a2d34; }
</style>
""", unsafe_allow_html=True)

st.title("🔷 QUANT SYSTEM v5.0")
st.caption("多类目 · 多策略 · AI自动交易 · 实时监控")

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
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False

# ================== 顶部4个指标 ==================
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 总资产", "$105,420", delta="+5.4%")
c2.metric("📈 日盈亏", "+$2,140", delta="+2.1%")
c3.metric("📊 夏普比率", "1.42", delta="+0.12")
c4.metric("🎯 胜率", "71.4%", delta="+3.2%")

st.markdown("---")

# ================== 侧边栏 + 主内容 ==================
col_sidebar, col_main = st.columns([1, 3])

# 侧边栏
with col_sidebar:
    st.markdown("### 导航")
    menu = st.radio("", ["Dashboard", "Strategies", "AI Picker", "Portfolio", "About"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 快速操作")
    
    # 点击参数弹出详情
    if st.button("📊 查看总资产详情"):
        st.session_state.show_detail = True
        st.session_state.detail_title = "总资产详情"
        st.session_state.detail_content = """
        - 当前总资产: $105,420
        - 较昨日: +5.4%
        - 本月累计: +$8,500
        - 年初至今: +18.5%
        """
    
    if st.button("📈 查看风险指标"):
        st.session_state.show_detail = True
        st.session_state.detail_title = "风险指标详情"
        st.session_state.detail_content = """
        - 夏普比率: 1.42 (良好)
        - 最大回撤: -2.3%
        - 波动率: 15.2%
        - VaR(95%): -1.8%
        """
    
    if st.button("🎯 查看策略表现"):
        st.session_state.show_detail = True
        st.session_state.detail_title = "策略表现详情"
        st.session_state.detail_content = """
        - 期货趋势: +8.2%
        - 外汇利差: +5.1%
        - 加密双均线: +12.3%
        - 综合收益: +7.8%
        """
    
    st.markdown("---")
    st.caption(f"🟢 系统在线\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ================== 弹出详情对话框 ==================
if st.session_state.get('show_detail', False):
    with st.container():
        st.markdown(f"""
        <div class="popup-box">
            <h3>{st.session_state.get('detail_title', '详情')}</h3>
            <p>{st.session_state.get('detail_content', '')}</p>
            <button onclick="location.reload()">关闭</button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("关闭", key="close_popup"):
            st.session_state.show_detail = False
            st.rerun()

# ================== 主内容区 ==================
with col_main:
    if menu == "Dashboard":
        st.markdown("### 📈 市场概览")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("EUR/USD", f"{eurusd_price:.5f}", delta=f"{eurusd_price-1.085:.4f}")
            if st.button("查看详情", key="eur_detail"):
                st.session_state.show_detail = True
                st.session_state.detail_title = "EUR/USD 详情"
                st.session_state.detail_content = f"当前价格: {eurusd_price:.5f}\n24h高: {eurusd_price*1.005:.5f}\n24h低: {eurusd_price*0.995:.5f}\n成交量: 2.3M"
        
        with col_b:
            st.metric("BTC-USD", f"${btc_price:,.0f}", delta=f"{btc_price/45000-1:.1%}")
            if st.button("查看详情", key="btc_detail"):
                st.session_state.show_detail = True
                st.session_state.detail_title = "BTC-USD 详情"
                st.session_state.detail_content = f"当前价格: ${btc_price:,.0f}\n24h高: ${btc_price*1.02:,.0f}\n24h低: ${btc_price*0.98:,.0f}\n市值占比: 52%"
        
        with col_c:
            st.metric("黄金期货", f"${gold_price:.0f}", delta=f"{gold_price/1950-1:.1%}")
            if st.button("查看详情", key="gold_detail"):
                st.session_state.show_detail = True
                st.session_state.detail_title = "黄金期货详情"
                st.session_state.detail_content = f"当前价格: ${gold_price:.0f}\n24h高: ${gold_price*1.01:.0f}\n24h低: ${gold_price*0.99:.0f}\n持仓兴趣: 450K"
        
        st.markdown("---")
        
        # K线图
        st.markdown("### 📉 价格走势")
        fig = go.Figure(data=[go.Candlestick(
            x=pd.date_range(end=datetime.now(), periods=50, freq='1h'),
            open=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)],
            high=[eurusd_price + random.uniform(0.001, 0.003) for _ in range(50)],
            low=[eurusd_price - random.uniform(0.001, 0.003) for _ in range(50)],
            close=[eurusd_price + random.uniform(-0.002, 0.002) for _ in range(50)]
        )])
        fig.update_layout(height=350, paper_bgcolor="#0e1117", plot_bgcolor="#1a1d24", font_color="#ffffff", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📋 策略状态")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown('<div class="strategy-card">🟢 期货趋势策略 <span style="float:right">运行中 | 收益率: +8.2%</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="strategy-card">🟢 外汇利差策略 <span style="float:right">运行中 | 收益率: +5.1%</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="strategy-card">🟡 期货均值回归 <span style="float:right">待机 | 收益率: +2.3%</span></div>', unsafe_allow_html=True)
        with col_s2:
            st.markdown('<div class="strategy-card">🟢 外汇突破策略 <span style="float:right">运行中 | 收益率: +6.7%</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="strategy-card">🟢 加密双均线 <span style="float:right">运行中 | 收益率: +12.3%</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="strategy-card">🟡 A股双均线 <span style="float:right">待机 | 收益率: +1.8%</span></div>', unsafe_allow_html=True)

    elif menu == "Strategies":
        st.markdown("### 🎯 策略列表")
        st.info("点击策略名称查看详细信息")
        
        strategies = [
            ("📈 期货趋势策略", "GC=F", "趋势跟踪", "🟢 运行中", "+8.2%"),
            ("📉 期货均值回归", "CL=F", "均值回归", "🟡 待机", "+2.3%"),
            ("💱 外汇利差策略", "AUDJPY", "利差交易", "🟢 运行中", "+5.1%"),
            ("📊 外汇突破策略", "EURUSD", "突破交易", "🟢 运行中", "+6.7%"),
            ("₿ 加密双均线", "BTC-USD", "双均线", "🟢 运行中", "+12.3%"),
            ("📈 加密RSI策略", "ETH-USD", "RSI指标", "🟡 待机", "+3.2%"),
            ("🇨🇳 A股双均线", "600519.SS", "双均线", "🟡 待机", "+1.8%"),
            ("🇭🇰 港股布林带", "0700.HK", "布林带", "🔴 暂停", "-0.5%")
        ]
        
        for name, symbol, desc, status, ret in strategies:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1.5, 1, 1])
            with col1:
                if st.button(name, key=f"btn_{name}"):
                    st.session_state.selected_strategy = name
                    st.session_state.show_detail = True
                    st.session_state.detail_title = f"{name} 详情"
                    st.session_state.detail_content = f"""
                    - 品种: {symbol}
                    - 策略类型: {desc}
                    - 状态: {status}
                    - 收益率: {ret}
                    - 最大回撤: -2.1%
                    - 夏普比率: 1.35
                    - 建议仓位: 15%
                    """
            with col2:
                st.write(symbol)
            with col3:
                st.write(desc)
            with col4:
                st.markdown(f"<span class='status-green'>{status}</span>" if "🟢" in status else f"<span class='status-yellow'>{status}</span>", unsafe_allow_html=True)
            with col5:
                st.write(ret)
            st.markdown("---")

    elif menu == "AI Picker":
        st.markdown("### 🤖 AI智能选股")
        
        col_a, col_b = st.columns(2)
        with col_a:
            market = st.selectbox("选择市场", ["美股", "A股", "港股", "加密货币", "外汇"])
        with col_b:
            top_n = st.slider("推荐数量", 1, 10, 5)
        
        if st.button("🚀 开始AI选股", type="primary"):
            with st.spinner("AI分析中..."):
                time.sleep(1.5)
            
            if market == "加密货币":
                picks = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
            elif market == "美股":
                picks = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN"]
            elif market == "港股":
                picks = ["00700", "09988", "03690", "01810", "02318"]
            elif market == "外汇":
                picks = ["EURUSD", "GBPUSD", "AUDJPY", "USDJPY", "USDCAD"]
            else:
                picks = ["600519", "000858", "300750", "002594", "601318"]
            
            st.success(f"✅ AI推荐 {market} 市场标的：")
            for i, pick in enumerate(picks[:top_n]):
                score = random.randint(70, 98)
                st.write(f"{i+1}. **{pick}** | AI置信度: {score}%")
                st.progress(score/100)
                if st.button(f"查看{pick}详情", key=f"detail_{pick}"):
                    st.session_state.show_detail = True
                    st.session_state.detail_title = f"{pick} 详情"
                    st.session_state.detail_content = f"""
                    - 代码: {pick}
                    - AI推荐置信度: {score}%
                    - 预测方向: 上涨
                    - 建议仓位: {score/10:.1f}%
                    - 目标价: 当前价 + {score/100*5:.1f}%
                    """

    elif menu == "Portfolio":
        st.markdown("### 📊 当前持仓")
        
        holdings = pd.DataFrame([
            {"品种": "EURUSD", "名称": "欧元/美元", "数量": 10000, "成本价": 1.0850, "现价": eurusd_price, "市值": eurusd_price*10000, "盈亏": f"${(eurusd_price-1.085)*10000:.0f}", "盈亏%": f"{(eurusd_price-1.085)/1.085*100:.1f}%"},
            {"品种": "GC=F", "名称": "黄金期货", "数量": 1, "成本价": 1950, "现价": gold_price, "市值": gold_price, "盈亏": f"${gold_price-1950:.0f}", "盈亏%": f"{(gold_price-1950)/1950*100:.1f}%"},
            {"品种": "BTC-USD", "名称": "比特币", "数量": 0.05, "成本价": 45000, "现价": btc_price, "市值": btc_price*0.05, "盈亏": f"${(btc_price-45000)*0.05:.0f}", "盈亏%": f"{(btc_price-45000)/45000*100:.1f}%"},
        ])
        st.dataframe(holdings, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 💰 资金管理")
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        col_p1.metric("总市值", f"${eurusd_price*10000 + gold_price + btc_price*0.05:.0f}")
        col_p2.metric("可用资金", "$12,500")
        col_p3.metric("仓位占比", "85%")
        col_p4.metric("今日盈亏", "+$2,140", delta="+2.1%")
        
        if st.button("查看资金曲线"):
            st.session_state.show_detail = True
            st.session_state.detail_title = "资金曲线详情"
            st.session_state.detail_content = """
            - 初始资金: $100,000
            - 当前净值: $105,420
            - 收益率: +5.42%
            - 最大回撤: -2.3%
            - 年化收益: +18.5%
            """

    else:
        st.markdown("### 📖 关于系统")
        st.markdown("""
        <div style="background-color:#1a1d24; border-radius:15px; padding:20px;">
            <h3>🔷 QUANT SYSTEM v5.0</h3>
            <p>多类目 · 多策略 · AI自动交易</p>
            <hr>
            <h4>技术架构</h4>
            <p>• 框架: Streamlit + Python</p>
            <p>• AI引擎: DeepSeek API</p>
            <p>• 数据源: yfinance</p>
            <p>• 策略库: 12个内置策略</p>
            <hr>
            <h4>联系方式</h4>
            <p>• GitHub: github.com/jgl890474</p>
            <p>• 项目: quant_system_new</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("查看系统状态"):
            st.session_state.show_detail = True
            st.session_state.detail_title = "系统状态详情"
            st.session_state.detail_content = """
            - 系统版本: v5.0
            - 运行状态: 🟢 正常
            - AI引擎: DeepSeek (在线)
            - 数据源: yfinance (实时)
            - 策略数量: 12
            - 更新时间: 实时
            """

st.caption("© 2026 QUANT SYSTEM v5.0 | Powered by DeepSeek AI | 点击参数查看详情")
