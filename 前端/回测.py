# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def 显示():
    st.markdown("### 📈 策略回测系统")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD=X"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1wk"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                # 生成模拟数据（因为 yfinance 在云环境可能受限）
                st.info("使用模拟数据进行回测演示")
                
                # 生成日期范围
                日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                if len(日期列表) < 10:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                
                if len(日期列表) < 5:
                    st.error("日期范围太短，请选择更长的范围")
                    return
                
                # 生成模拟价格（上涨趋势 + 随机波动）
                np.random.seed(42)
                基础价格 = {"AAPL": 175, "BTC-USD": 45000, "GC=F": 1950, "EURUSD=X": 1.08}.get(品种, 100)
                涨幅 = np.random.randn(len(日期列表)) * 0.02
                价格序列 = 基础价格 * (1 + np.cumsum(涨幅) / 50)
                
                # 确保价格为正
                价格序列 = np.maximum(价格序列, 基础价格 * 0.5)
                
                if len(价格序列) < 2:
                    st.error("数据不足")
                    return
                
                # 计算收益率
                开盘价 = 价格序列[0]
                收盘价 = 价格序列[-1]
                总收益率 = (收盘价 - 开盘价) / 开盘价
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！（模拟数据）数据点: {len(价格序列)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(价格序列)}")
                
                # 净值曲线
                fig = go.Figure()
                净值 = [初始资金 * (1 + 总收益率 * i / max(len(价格序列), 1)) for i in range(len(价格序列))]
                fig.add_trace(go.Scatter(
                    x=日期列表, 
                    y=净值, 
                    mode='lines', 
                    name='净值',
                    line=dict(color='#00d2ff', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig.update_layout(
                    height=350,
                    title="净值曲线（模拟数据）",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 价格走势
                with st.expander("📊 价格走势（模拟）"):
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=日期列表,
                        y=价格序列,
                        mode='lines',
                        name='价格',
                        line=dict(color='#ffaa00', width=2)
                    ))
                    fig2.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig2, use_container_width=True)
                
                # 简单策略模拟
                with st.expander("📈 简单策略模拟"):
                    短周期 = st.slider("短周期", 2, 20, 5, key="short")
                    长周期 = st.slider("长周期", 10, 50, 20, key="long")
                    
                    # 计算均线
                    df = pd.DataFrame({'价格': 价格序列, '日期': 日期列表})
                    df['短均线'] = df['价格'].rolling(window=短周期).mean()
                    df['长均线'] = df['价格'].rolling(window=长周期).mean()
                    
                    # 生成信号
                    df['信号'] = 0
                    df.loc[df['短均线'] > df['长均线'], '信号'] = 1
                    df.loc[df['短均线'] <= df['长均线'], '信号'] = -1
                    
                    # 策略净值
                    策略资金 = 初始资金
                    持仓 = 0
                    策略净值列表 = [初始资金]
                    
                    for i in range(1, len(df)):
                        if df['信号'].iloc[i] == 1 and df['信号'].iloc[i-1] != 1:
                            if 持仓 == 0:
                                持仓 = 策略资金 / df['价格'].iloc[i]
                                策略资金 = 0
                        elif df['信号'].iloc[i] == -1 and df['信号'].iloc[i-1] != -1:
                            if 持仓 > 0:
                                策略资金 = 持仓 * df['价格'].iloc[i]
                                持仓 = 0
                        
                        当前净值 = 策略资金 + 持仓 * df['价格'].iloc[i]
                        策略净值列表.append(当前净值)
                    
                    # 策略收益率
                    策略收益率 = (策略净值列表[-1] - 初始资金) / 初始资金
                    st.metric("策略收益率", f"{策略收益率*100:.2f}%")
                    
                    # 策略曲线
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=df['日期'], y=策略净值列表, mode='lines', name='策略净值', line=dict(color='#00ff88', width=2)))
                    fig3.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig3, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
