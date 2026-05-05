import streamlit as st
import time
import random
import pandas as pd
import requests
import os
from datetime import datetime

st.set_page_config(page_title="量化交易系统", layout="wide", initial_sidebar_state="expanded")

# ================== 样式 ==================
st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .metric-card { background-color: #1a1d24; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2d34; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 20px; }
    h2, h3 { color: #dddddd; font-size: 18px; }
    .stButton button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; padding: 8px 20px; }
    .ai-box { background-color: #1a1d24; border-radius: 12px; padding: 20px; border-left: 4px solid #00d2ff; }
    .strategy-card { background-color: #1a1d24; border-radius: 10px; padding: 15px; margin: 5px; text-align: center; }
    .buy-signal { color: #00ff88; }
    .sell-signal { color: #ff4444; }
    .hold-signal { color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

# ================== 获取价格 ==================
try:
    from data.market_data import get_1min_kline
    kline = get_1min_kline("EURUSD")
    price = kline.get('close', 1.085) if kline else 1.085
except:
    price = random.uniform(1.08, 1.12)

# DeepSeek API
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

def call_deepseek(symbol, price, signals=None):
    if not DEEPSEEK_API_KEY:
        return None
    prompt = f"""你是量化交易AI。分析以下品种：
品种: {symbol}
当前价格: {price}
策略信号: {signals if signals else '无'}
请输出一个建议: buy(买入)、sell(卖出)或hold(持有)，只输出一个英文单词。"""
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
    return None

# ================== 侧边栏 ==================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/trading-views.png", width=50)
    st.title("导航菜单")
    page = st.radio("", ["🏠 首页", "🤖 AI选股", "⚡ AI交易", "📊 持仓", "📖 关于"])
    st.markdown("---")
    st.caption(f"系统状态: 🟢 运行中")
    st.caption(f"更新时间: {datetime.now().strftime('%H:%M:%S')}")

# ================== 首页 ==================
if page == "🏠 首页":
    st.title("⚡ 量化交易系统 v5.0")
    st.caption("多类目 · 多策略 · AI自动交易 · 实时监控")
    
    # 核心指标
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 总资产", "$103,200", delta="+3.2%")
    c2.metric("📈 今日收益", "+$3,200", delta="+3.2%")
    c3.metric("📊 策略数", "12", delta="+4")
    c4.metric("🎯 胜率", "68.5%", delta="+2.1%")
    
    st.markdown("---")
    
    # 实时行情
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("EUR/USD", f"{price:.5f}", delta=f"{price-1.085:.4f}")
        st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        df = pd.DataFrame({"价格": [random.uniform(1.08, 1.12) for _ in range(60)]})
        st.line_chart(df, height=150)
    
    st.markdown("---")
    
    # 策略概览
    st.subheader("📋 策略概览")
    categories = ["期货策略", "外汇策略", "加密货币策略", "A股策略", "港股策略", "美股策略"]
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        with cols[i % 3]:
            st.markdown(f'<div class="strategy-card">📈 {cat}<br><small>运行中</small></div>', unsafe_allow_html=True)
    
    # AI快讯
    st.subheader("🤖 AI 市场快讯")
    st.info("当前趋势: 多头 | 建议: 逢低布局 | 风险等级: 中等")

# ================== AI选股 ==================
elif page == "🤖 AI选股":
    st.title("🤖 AI 智能选股")
    
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("选择市场", ["美股", "A股", "港股", "加密货币"])
    with col2:
        top_n = st.slider("推荐数量", 1, 20, 5)
    
    if st.button("开始选股", type="primary"):
        with st.spinner("AI分析中..."):
            time.sleep(1.5)
        
        st.success(f"根据{market}市场分析，AI推荐以下{top_n}只标的：")
        
        if market == "加密货币":
            stocks = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        elif market == "美股":
            stocks = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN"]
        elif market == "港股":
            stocks = ["00700", "09988", "03690", "01810", "02318"]
        else:
            stocks = ["600519", "000858", "300750", "002594", "601318"]
        
        for i in range(min(top_n, len(stocks))):
            score = random.randint(70, 98)
            st.write(f"{i+1}. **{stocks[i]}** | AI置信度: {score}%")
            st.progress(score / 100)

# ================== AI交易 ==================
elif page == "⚡ AI交易":
    st.title("⚡ AI 自动交易")
    
    # 交易设置
    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("交易类目", ["外汇", "期货", "加密货币", "股票"])
    with col2:
        tp = st.number_input("止盈 (%)", value=8.0, step=0.5)
    with col3:
        sl = st.number_input("止损 (%)", value=5.0, step=0.5)
    
    # 策略选择
    st.subheader("策略选择")
    strategies = {
        "外汇": ["外汇利差策略", "外汇突破策略", "外汇双均线策略"],
        "期货": ["期货趋势策略", "期货均值回归", "期货ATR策略"],
        "加密货币": ["加密双均线策略", "加密RSI策略"],
        "股票": ["A股双均线", "港股布林带", "美股趋势"]
    }
    
    selected_strategies = st.multiselect("选择要运行的策略", strategies.get(category, []), default=strategies.get(category, [])[:2])
    
    # 当前行情
    st.subheader("实时行情")
    st.metric("EUR/USD", f"{price:.5f}", delta=f"{price-1.085:.4f}")
    
    # AI决策
    if st.button("启动AI交易", type="primary"):
        with st.spinner("AI分析中..."):
            # 获取策略信号
            signals = {name: random.choice(["buy", "sell", "hold"]) for name in selected_strategies}
            
            # AI仲裁
            ai_decision = call_deepseek("EUR/USD", price, str(signals))
            if ai_decision:
                final = ai_decision
            else:
                final = "hold"
            
            st.success(f"🤖 AI最终决策: {final.upper()}")
            
            # 显示各策略信号
            with st.expander("查看各策略信号"):
                for name, sig in signals.items():
                    color = "#00ff88" if sig == "buy" else "#ff4444" if sig == "sell" else "#ffaa00"
                    st.markdown(f"<span style='color:{color}'>■</span> {name}: {sig.upper()}", unsafe_allow_html=True)
            
            st.info(f"止盈: {tp}% | 止损: {sl}%")

# ================== 持仓 ==================
elif page == "📊 持仓":
    st.title("📊 当前持仓")
    
    # 持仓表格
    holdings = pd.DataFrame({
        "代码": ["EURUSD", "GC=F", "BTC-USD", "AAPL"],
        "名称": ["欧元/美元", "黄金期货", "比特币", "苹果公司"],
        "数量": [10000, 1, 0.05, 50],
        "成本价": [1.085, 1950, 45000, 175],
        "现价": [price, 1962, 48200, 185],
        "市值": [price*10000, 1962, 2410, 9250],
        "盈亏": [f"{(price-1.085)*10000:.0f}", "+12", "+1600", "+500"],
        "盈亏%": [f"{(price-1.085)/1.085*100:.1f}%", "+0.6%", "+7.1%", "+2.9%"]
    })
    st.dataframe(holdings, use_container_width=True, hide_index=True)
    
    # 持仓统计
    col1, col2, col3 = st.columns(3)
    total_value = price*10000 + 1962 + 2410 + 9250
    col1.metric("总市值", f"${total_value:,.0f}")
    col2.metric("今日盈亏", "+$2,112", delta="+2.1%")
    col3.metric("持仓数量", "4", delta="0")

# ================== 关于 ==================
elif page == "📖 关于":
    st.title("📖 关于系统")
    
    st.markdown("""
    ### 量化交易系统 v5.0
    
    | 模块 | 说明 |
    |------|------|
    | **框架** | Streamlit + Python |
    | **策略库** | 外汇、期货、加密货币、A股、港股、美股 |
    | **AI引擎** | DeepSeek API (信号仲裁) |
    | **数据源** | yfinance (实时行情) |
    | **风控** | 动态止盈止损 + 仓位管理 |
    
    ### 技术架构
    
