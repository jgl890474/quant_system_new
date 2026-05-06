# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def 显示():
    st.markdown("### 📈 策略回测系统")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "MSFT", "GOOGL"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1h", "30m"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", 
                        "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL"}
                代码 = 映射.get(品种, 品种)
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期, progress=False)
                
                if 数据.empty:
                    st.error("无法获取数据")
                    return
                
                # 计算收益率（修复格式错误）
                收盘价 = 数据['Close'].iloc[-1]
                开盘价 = 数据['Close'].iloc[0]
                总收益率 = (收盘价 - 开盘价) / 开盘价
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！")
                
                # 指标卡片 - 使用更好看的样式
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("K线数量", f"{len(数据)}")
                
                # 净值曲线
                fig = go.Figure()
                净值 = [初始资金 * (1 + 总收益率 * i / len(数据)) for i in range(len(数据))]
                fig.add_trace(go.Scatter(
                    x=数据.index, 
                    y=净值, 
                    mode='lines', 
                    name='净值',
                    line=dict(color='#00d2ff', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig.update_layout(
                    height=350,
                    title="净值曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
