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
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD=X", "MSFT", "GOOGL", "TSLA", "NVDA"])
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
                # 直接使用选择的品种代码（已包含正确格式）
                代码 = 品种
                
                st.info(f"正在获取数据: {代码}")
                
                # 下载数据
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期, progress=False)
                
                if 数据.empty:
                    st.error(f"无法获取数据: {代码}")
                    st.info("提示：BTC-USD 可能需要使用 'BTC-USD'，EURUSD 需要使用 'EURUSD=X'")
                    return
                
                # 提取收盘价
                if 'Close' in 数据.columns:
                    收盘价 = 数据['Close']
                else:
                    st.error("无法获取收盘价")
                    return
                
                if len(收盘价) < 2:
                    st.error(f"数据不足，仅 {len(收盘价)} 个点")
                    return
                
                # 计算收益率
                收盘价_开始 = float(收盘价.iloc[0])
                收盘价_结束 = float(收盘价.iloc[-1])
                总收益率 = (收盘价_结束 - 收盘价_开始) / 收盘价_开始
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(收盘价)}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(收盘价)}")
                
                # 净值曲线
                fig = go.Figure()
                净值 = [初始资金 * (1 + 总收益率 * i / len(收盘价)) for i in range(len(收盘价))]
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
                
                # 价格走势
                with st.expander("📊 价格走势"):
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=数据.index,
                        y=收盘价,
                        mode='lines',
                        name='收盘价',
                        line=dict(color='#ffaa00', width=1.5)
                    ))
                    fig2.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
