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
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "MSFT", "GOOGL", "TSLA"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1wk", "1mo"])
    
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
                映射 = {
                    "EURUSD": "EURUSD=X", 
                    "BTC-USD": "BTC-USD", 
                    "GC=F": "GC=F", 
                    "AAPL": "AAPL", 
                    "MSFT": "MSFT", 
                    "GOOGL": "GOOGL",
                    "TSLA": "TSLA"
                }
                代码 = 映射.get(品种, 品种)
                
                # 下载数据
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期, progress=False)
                
                if 数据.empty:
                    st.error("无法获取数据，请尝试其他品种或日期范围")
                    return
                
                # 确保Close列是数值类型
                收盘价系列 = pd.to_numeric(数据['Close'], errors='coerce').dropna()
                if len(收盘价系列) < 2:
                    st.error("数据不足，请选择更长的日期范围")
                    return
                
                # 计算收益率（修复关键：使用数值而不是Series）
                收盘价_开始 = float(收盘价系列.iloc[0])
                收盘价_结束 = float(收盘价系列.iloc[-1])
                
                if 收盘价_开始 == 0:
                    st.error("起始价格为零，无法计算")
                    return
                
                总收益率 = (收盘价_结束 - 收盘价_开始) / 收盘价_开始
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("K线数量", f"{len(收盘价系列)}")
                
                # 净值曲线
                fig = go.Figure()
                净值 = [初始资金 * (1 + 总收益率 * i / len(收盘价系列)) for i in range(len(收盘价系列))]
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
                    font_color="#e6e6e6",
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 简单策略信号图（可选）
                with st.expander("📊 价格走势"):
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=数据.index,
                        y=收盘价系列,
                        mode='lines',
                        name='收盘价',
                        line=dict(color='#ffaa00', width=1.5)
                    ))
                    fig2.update_layout(
                        height=300,
                        paper_bgcolor="#0a0c10",
                        plot_bgcolor="#15171a",
                        font_color="#e6e6e6"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
                st.info("提示：请尝试选择其他品种或更长的日期范围")
