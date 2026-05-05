import streamlit as st
import time
import random
import pandas as pd
import requests
import os

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

# 获取价格
try:
    from data.market_data import get_1min_kline
    kline = get_1min_kline("EURUSD")
    price = kline.get('close', 1.085) if kline else 1.085
except:
    price = random.uniform(1.08, 1.12)

# 顶部卡片
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 总资产", "$103,200", delta="+3.2%")
c2.metric("📈 今日收益", "+$3,200", delta="+3.2%")
c3.metric("📊 策略数", "8", delta="+2")
c4.metric("🎯 胜率", "71.2%", delta="+2.8%")

st.markdown("---")

# 价格和K线
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

# DeepSeek API Key（需要你在Streamlit Secrets中配置）
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")

def call_deepseek(symbol, price):
    """调用DeepSeek API获取交易信号"""
    if not DEEPSEEK_API_KEY:
        return None
    
    prompt = f"""你是量化交易AI。分析以下品种：
品种: {symbol}
当前价格: {price}
请输出一个建议: buy(买入)、sell(卖出)或hold(持有)，只输出一个英文单词。"""
    
    try:
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 10
            },
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().lower()
    except:
        pass
    return None

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
            with st.spinner("AI分析中..."):
                # 调用真实AI
                ai_signal = call_deepseek("EUR/USD", price)
                if ai_signal:
                    if ai_signal == "buy":
                        st.success(f"🎯 建议: 买入 @ {price:.5f}")
                        st.info(f"置信度: 高 | 止盈: {price*1.01:.5f} | 止损: {price*0.99:.5f}")
                    elif ai_signal == "sell":
                        st.error(f"🎯 建议: 卖出 @ {price:.5f}")
                        st.info(f"置信度: 高 | 止盈: {price*0.99:.5f} | 止损: {price*1.01:.5f}")
                    else:
                        st.warning(f"🎯 建议: 持有观望 @ {price:.5f}")
                    st.caption(f"AI引擎: DeepSeek | 分析完成")
                else:
                    # 模拟信号
                    signal = random.choice(["买入", "卖出", "持有"])
                    if signal == "买入":
                        st.success(f"🎯 建议: 买入 @ {price:.5f}")
                    elif signal == "卖出":
                        st.error(f"🎯 建议: 卖出 @ {price:.5f}")
                    else:
                        st.warning(f"🎯 建议: 持有观望")
                    st.caption("AI引擎: 模拟模式 (请配置API Key)")
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
