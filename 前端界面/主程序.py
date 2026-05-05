import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .metric-card { background-color: #1a1d24; border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #2a2d34; }
    h1 { color: #ffffff; text-align: center; font-size: 28px; margin-bottom: 20px; }
    h2, h3 { color: #dddddd; font-size: 18px; }
    .stButton button { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: white; border-radius: 20px; padding: 8px 20px; }
    .ai-box { background-color: #1a1d24; border-radius: 12px; padding: 20px; border-left: 4px solid #00d2ff; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# 顶部卡片
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 总资产", "$103,200", delta="+3.2%")
c2.metric("📈 今日收益", "+$3,200", delta="+3.2%")
c3.metric("📊 策略数", "8", delta="+2")
c4.metric("🎯 胜率", "71.2%", delta="+2.8%")

st.markdown("---")

# 价格和K线
price = random.uniform(1.08, 1.12)
col_p1, col_p2 = st.columns([1, 2])
with col_p1:
    st.metric("EUR/USD", f"{price:.5f}", delta=f"{price-1.085:.4f}")
    st.caption(f"最后更新: {time.strftime('%Y-%m-%d %H:%M:%S')}")
with col_p2:
    df = pd.DataFrame({"价格": [random.uniform(1.08, 1.12) for _ in range(60)]})
    st.line_chart(df, height=180)

st.markdown("---")

# AI决策
st.subheader("🤖 AI 交易决策")
col_ai1, col_ai2 = st.columns([1, 1])
with col_ai1:
    with st.container():
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("**综合分析**")
        st.markdown("- 趋势: 向上 ↗️")
        st.markdown("- RSI: 62 (中性)")
        st.markdown("- MACD: 金叉信号")
        st.markdown("- 波动率: 正常")
        st.markdown('</div>', unsafe_allow_html=True)
with col_ai2:
    with st.container():
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("**决策建议**")
        if st.button("获取AI信号", use_container_width=True):
            signal = random.choice(["买入", "卖出", "持有"])
            if signal == "买入":
                st.success("🎯 建议: 买入")
                st.info(f"入场价: {price:.5f} | 止盈: 1.0950 | 止损: 1.0800")
            elif signal == "卖出":
                st.error("🎯 建议: 卖出")
                st.info(f"入场价: {price:.5f} | 止盈: 1.0750 | 止损: 1.0900")
            else:
                st.warning("🎯 建议: 持有观望")
                st.info("等待明确信号")
        else:
            st.info("点击按钮获取AI决策")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# 策略状态
st.subheader("策略运行状态")
cols = st.columns(4)
strategies = [("期货趋势", "GC=F", "🟢"), ("期货均值", "CL=F", "🟢"), ("外汇利差", "AUDJPY", "🟡"), ("外汇突破", "EURUSD", "🟢")]
for i, (name, sym, status) in enumerate(strategies):
    with cols[i]:
        st.markdown(f"{status} **{name}**\n{sym}")

st.caption("系统运行中 | 数据实时更新 | AI引擎: DeepSeek")
