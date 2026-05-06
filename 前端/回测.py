# 前端/回测.py —— 干净无报错版
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def run():
    st.subheader("📊 回测中心")
    st.info("回测功能开发中...")

    # 示例图表（不报错）
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=30),
        "profit": [i*100 for i in range(30)]
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["profit"], mode="lines"))
    st.plotly_chart(fig)
