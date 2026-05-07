# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
from 工具 import 数据库

def 显示():
    st.markdown("### ⚙️ 回测参数设置")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA"])
    with col2:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col3:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    with st.expander("📊 策略参数"):
        短周期 = st.slider("短期均线", 5, 50, 10)
        长周期 = st.slider("长期均线", 20, 200, 30)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", "AAPL": "AAPL", "TSLA": "TSLA"}
                代码 = 映射.get(品种, 品种)
                数据 = yf.download(代码, start=开始日期, end=结束日期, progress=False)
                
                if 数据.empty:
                    st.warning("使用模拟数据")
                    # 生成模拟数据
                    日期 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                    价格 = 100 * (1 + np.cumsum(np.random.randn(len(日期)) * 0.01))
                    数据 = pd.DataFrame({'Close': 价格}, index=日期)
                
                # 计算收益率
                开盘价 = float(数据['Close'].iloc[0])
                收盘价 = float(数据['Close'].iloc[-1])
                总收益率 = (收盘价 - 开盘价) / 开盘价
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(数据)}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(数据)}")
                
                # K线图
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=数据.index,
                    open=数据['Open'] if 'Open' in 数据.columns else 数据['Close'],
                    high=数据['High'] if 'High' in 数据.columns else 数据['Close'],
                    low=数据['Low'] if 'Low' in 数据.columns else 数据['Close'],
                    close=数据['Close']
                ))
                fig.update_layout(height=350, title="K线图", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {e}")
