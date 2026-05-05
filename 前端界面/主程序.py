# ================== K线图（简化版）==================
st.subheader("📈 实时K线图")

# 生成模拟K线数据
import pandas as pd
import plotly.graph_objects as go
import time as tm

# 生成最近50个时间点的模拟价格
now = tm.time()
kline_data = []
base_price = 1.085
for i in range(50):
    ts = now - (50 - i) * 60
    price = base_price + (i * 0.0005) + (i % 5) * 0.0005
    kline_data.append({
        "timestamp": int(ts),
        "open": price,
        "high": price + 0.001,
        "low": price - 0.001,
        "close": price + 0.0002
    })

df = pd.DataFrame(kline_data)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

fig = go.Figure(data=[go.Candlestick(
    x=df['timestamp'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close']
)])

fig.update_layout(
    height=400,
    paper_bgcolor="#0e1117",
    plot_bgcolor="#1e1e1e",
    font_color="#ffffff",
    xaxis=dict(gridcolor="#333333"),
    yaxis=dict(gridcolor="#333333")
)

st.plotly_chart(fig, use_container_width=True)
