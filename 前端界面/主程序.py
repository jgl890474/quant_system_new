import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="量化交易系统", layout="wide")

st.title("🚀 量化交易系统")
st.markdown("### 多策略 · 多品种 · 零本地依赖")

with st.sidebar:
    st.header("策略配置")
    策略名称 = st.selectbox("选择策略", ["双均线策略", "RSI策略"])
    交易品种 = st.selectbox("选择品种", ["BTCUSDT", "ETHUSDT"])
    初始资金 = st.number_input("初始资金", value=100000)
    
    if 策略名称 == "双均线策略":
        快线 = st.slider("快线周期", 5, 50, 10)
        慢线 = st.slider("慢线周期", 20, 200, 30)
    
    运行回测 = st.button("开始回测")

if 运行回测:
    with st.spinner("回测中..."):
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        np.random.seed(42)
        price = 50000 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, len(dates))))
        
        ma_fast = pd.Series(price).rolling(window=快线).mean()
        ma_slow = pd.Series(price).rolling(window=慢线).mean()
        signals = (ma_fast > ma_slow).astype(int).diff()
        
        cash = 初始资金
        position = 0
        values = []
        
        for i in range(len(price)):
            if signals.iloc[i] == 1 and cash > 0:
                position = cash / price[i]
                cash = 0
            elif signals.iloc[i] == -1 and position > 0:
                cash = position * price[i]
                position = 0
            values.append(cash + position * price[i])
        
        收益率 = (values[-1] - 初始资金) / 初始资金
        st.success(f"回测完成！收益率: {收益率:.2%}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='权益'))
        fig.update_layout(title="权益曲线", height=500)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.write("量化交易系统 v1.0")