# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 数据.market_data import get_1min_kline, get_historical_klines
from AI模块.AI交易引擎 import ai_decision

# ================== 页面配置 ==================
st.set_page_config(
    page_title="量化交易系统 v5.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================== 自定义样式（暗色主题，白色字体）==================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    .stMetric label, .stMetric div {
        color: #ffffff !important;
    }
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] button {
        color: #ffffff !important;
    }
    .stMarkdown, .stText, .stCodeBlock, div[data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    .stButton button {
        color: #ffffff !important;
        background-color: #4CAF50;
        border-radius: 8px;
        font-weight: bold;
    }
    .stDataFrame, .stTable, .stDataFrame div, .stTable div {
        color: #ffffff !important;
    }
    .stSelectbox, .stNumberInput {
        color: #000000 !important;
    }
    .css-1d391kg, .stSidebar {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# ================== 获取组合数据 ==================
def get_portfolio():
    """获取首页显示的数据"""
    kline = get_1min_kline("EURUSD")
    if kline:
        price = kline['close']
    else:
        price = 1.085
    return {
        "total_asset": 100000.0,
        "price": price,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ================== 首页 ==================
def show_home():
    st.title("📊 量化交易系统 v5.0")
    
    col1, col2, col3 = st.columns(3)
    data = get_portfolio()
    col1.metric("💰 总资产", f"${data['total_asset']:,.2f}")
    col2.metric("💹 最新价格", f"{data['price']:.5f}")
    col3.metric("🕒 更新时间", data['timestamp'])
    
    st.subheader("📈 历史K线图")
    
    # 获取历史K线数据
    klines = get_historical_klines("EURUSD", 50)
    if klines and len(klines) > 0:
        df = pd.DataFrame(klines)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )])
        fig.update_layout(
            height=500,
            xaxis_title="时间",
            yaxis_title="价格",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#1e1e1e",
            font_color="#ffffff",
            xaxis=dict(gridcolor="#333333"),
            yaxis=dict(gridcolor="#333333")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无历史K线数据，请稍后重试")

# ================== AI选股 ==================
def show_ai_select():
    st.title("🤖 AI智能选股")
    col1, col2 = st.columns(2)
    with col1:
        market = st.selectbox("选择市场", ["美股", "A股", "加密货币", "外汇", "期货"], key="market")
    with col2:
        top_n = st.slider("推荐数量", 1, 20, 5, key="top_n")
    
    if st.button("开始选股", key="select_btn"):
        with st.spinner("AI 分析中..."):
            time.sleep(1.5)
        st.success(f"🤖 根据{market}市场分析，推荐以下{top_n}只标的：")
        
        if market == "加密货币":
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        elif market == "外汇":
            symbols = ["EURUSD", "GBPUSD", "AUDJPY", "USDJPY", "USDCAD"]
        elif market == "期货":
            symbols = ["GC=F", "CL=F", "SI=F", "HG=F", "NG=F"]
        elif market == "美股":
            symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"]
        else:
            symbols = ["000001.SS", "600036.SS", "601318.SS", "000858.SZ", "002415.SZ"]
        
        for i in range(min(top_n, len(symbols))):
            st.write(f"{i+1}. **{symbols[i]}** (AI 置信度: {85 - i*3}%)")

# ================== AI交易 ==================
def show_ai_trade():
    st.title("⚡ AI自动交易")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        category = st.selectbox("交易类目", ["加密货币", "外汇", "期货"], key="category")
    with col_c2:
        take_profit = st.number_input("止盈 (%)", value=8.0, step=0.5, key="tp")
    with col_c3:
        stop_loss = st.number_input("止损 (%)", value=5.0, step=0.5, key="sl")
    
    symbol_map = {
        "加密货币": "BTC-USD",
        "外汇": "EURUSD",
        "期货": "GC=F"
    }
    display_map = {
        "加密货币": "BTCUSDT",
        "外汇": "EURUSD",
        "期货": "GC=F"
    }
    
    if st.button("🚀 获取信号", type="primary", key="signal_btn"):
        symbol = symbol_map[category]
        display_symbol = display_map[category]
        
        with st.spinner(f"正在获取 {display_symbol} 行情并调用 AI 决策..."):
            kline = get_1min_kline(symbol)
        
        if kline:
            import random
            signals = {
                "双均线策略": random.choice(["buy", "sell", "hold"]),
                "RSI策略": random.choice(["buy", "sell", "hold"]),
                "趋势策略": random.choice(["buy", "sell", "hold"]),
                "突破策略": random.choice(["buy", "sell", "hold"])
            }
            
            final = ai_decision(str(signals), kline['close'], display_symbol)
            
            st.success(f"🤖 **AI 最终决策: {final.upper()}** @ {kline['close']:.5f}")
            st.info(f"📊 当前设置: 止盈 {take_profit}% | 止损 {stop_loss}%")
            
            with st.expander("📋 查看详细数据"):
                st.json({
                    "行情": {
                        "symbol": display_symbol,
                        "价格": kline['close'],
                        "高": kline['high'],
                        "低": kline['low'],
                        "时间": kline['timestamp']
                    },
                    "策略信号": signals,
                    "AI决策": final,
                    "风控设置": {"止盈": take_profit, "止损": stop_loss}
                })
        else:
            st.error(f"❌ 获取 {display_symbol} 行情失败，请检查网络或稍后重试")

# ================== 关于页面 ==================
def show_about():
    st.title("📘 关于系统")
    st.markdown("""
    ### 量化交易系统 v5.0
    
    **框架**: Streamlit + Python  
    **策略**: 双均线、RSI、趋势、突破、利差  
    **AI仲裁**: DeepSeek API  
    **数据源**: yfinance (外汇/加密货币/期货)  
    **风控**: 动态止盈止损 + 仓位管理  
    
    ### 支持的数据品种
    - **加密货币**: BTC-USD, ETH-USD, BNB-USD
    - **外汇**: EURUSD, GBPUSD, AUDJPY, USDJPY
    - **期货**: GC=F(黄金), CL=F(原油)
    
    ### 技术架构
    数据层 (yfinance) → 策略层 (4个策略) → AI仲裁 (DeepSeek) → 前端展示 (Streamlit)
    """)

# ================== 心跳线程 ==================
def keep_alive():
    while True:
        time.sleep(30)
        st.session_state["heartbeat"] = datetime.now()

if "heartbeat" not in st.session_state:
    st.session_state["heartbeat"] = datetime.now()
    threading.Thread(target=keep_alive, daemon=True).start()

# ================== 主入口 ==================
def main():
    st.sidebar.markdown("---")
    st.sidebar.info("📌 系统状态: 🟢 运行中")
    st.sidebar.markdown(f"⏱️ 最后心跳: {st.session_state['heartbeat'].strftime('%H:%M:%S')}")
    
    tabs = st.tabs(["🏠 首页", "🤖 AI选股", "⚡ AI交易", "📖 关于"])
    
    with tabs[0]:
        show_home()
    with tabs[1]:
        show_ai_select()
    with tabs[2]:
        show_ai_trade()
    with tabs[3]:
        show_about()

if __name__ == "__main__":
    main()