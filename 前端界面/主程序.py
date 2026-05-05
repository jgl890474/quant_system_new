import streamlit as st
import sys
import os
import time
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据模块
from data.market_data import get_1min_kline

# 导入 AI 决策模块
from AI模块.AI交易引擎 import ai_decision

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 10px; padding: 10px; text-align: center; color: #ffffff; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    div[data-testid="stMarkdownContainer"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# 获取实时价格
price = 1.085
try:
    kline = get_1min_kline("EURUSD")
    if kline:
        price = kline.get('close', 1.085)
except:
    pass

col1, col2, col3 = st.columns(3)
col1.metric("💰 总资产", "$100,000")
col2.metric("💹 最新价格", f"{price:.5f}")
col3.metric("🕒 更新时间", time.strftime("%Y-%m-%d %H:%M:%S"))

st.subheader("📈 策略运行状态")
st.success(f"✅ 系统已就绪 | 当前价格: {price}")

tab1, tab2, tab3 = st.tabs(["📋 策略列表", "🤖 AI交易", "⚙️ 配置"])

with tab1:
    st.write("1. 期货趋势策略 (GC=F)")
    st.write("2. 期货均值回归 (CL=F)")
    st.write("3. 外汇利差交易 (AUDJPY)")
    st.write("4. 外汇突破策略 (EURUSD)")

with tab2:
    st.subheader("🤖 AI 自动交易决策")
    
    # 选择交易对
    symbol_map = {
        "比特币": "BTC-USD",
        "以太坊": "ETH-USD",
        "欧元/美元": "EURUSD",
        "英镑/美元": "GBPUSD",
        "黄金期货": "GC=F",
        "原油期货": "CL=F"
    }
    
    selected = st.selectbox("选择交易品种", list(symbol_map.keys()))
    symbol = symbol_map[selected]
    
    if st.button("🚀 获取AI信号", type="primary"):
        with st.spinner(f"正在获取 {selected} 行情并调用 DeepSeek AI 决策..."):
            # 获取实时行情
            kline = get_1min_kline(symbol)
            if kline:
                current_price = kline['close']
                
                # 模拟4个策略的信号（实际可从策略库获取）
                signals = {
                    "双均线策略": random.choice(["buy", "sell", "hold"]),
                    "RSI策略": random.choice(["buy", "sell", "hold"]),
                    "趋势策略": random.choice(["buy", "sell", "hold"]),
                    "突破策略": random.choice(["buy", "sell", "hold"])
                }
                
                # 调用 DeepSeek AI 仲裁
                final = ai_decision(str(signals), current_price, selected)
                
                st.success(f"🤖 **AI 最终决策: {final.upper()}**")
                st.metric("当前价格", f"{current_price:.5f}")
                
                with st.expander("查看详细信号"):
                    st.write("策略信号:")
                    for name, sig in signals.items():
                        color = "green" if sig == "buy" else "red" if sig == "sell" else "gray"
                        st.markdown(f"- {name}: <span style='color:{color}'>{sig.upper()}</span>", unsafe_allow_html=True)
                    st.write(f"🤖 AI 最终决策: **{final.upper()}**")
            else:
                st.error(f"获取 {selected} 行情失败，请稍后重试")

with tab3:
    st.info("后台引擎运行中 | 推送 GitHub 自动部署")
    st.caption("AI 决策使用 DeepSeek API")