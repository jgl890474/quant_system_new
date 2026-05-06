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
        品种 = st.selectbox("选择品种", ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "BTC-USD", "GC=F"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1wk"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("正在获取真实数据..."):
            try:
                # 直接使用选择的品种
                代码 = 品种
                
                st.info(f"正在获取 {代码} 真实数据...")
                
                # 下载真实数据
                数据 = yf.download(
                    代码, 
                    start=开始日期, 
                    end=结束日期, 
                    interval=周期, 
                    progress=False,
                    auto_adjust=True
                )
                
                if 数据.empty:
                    st.warning(f"无法获取 {代码} 真实数据，请尝试其他品种")
                    return
                
                # 提取收盘价
                if 'Close' in 数据.columns:
                    收盘价 = 数据['Close']
                elif 'Adj Close' in 数据.columns:
                    收盘价 = 数据['Adj Close']
                else:
                    st.error("没有价格数据")
                    return
                
                if len(收盘价) < 5:
                    st.warning(f"数据点不足: {len(收盘价)}，请选择更长的日期范围")
                    return
                
                # 计算真实收益率
                开盘价_真实 = float(收盘价.iloc[0])
                收盘价_真实 = float(收盘价.iloc[-1])
                总收益率 = (收盘价_真实 - 开盘价_真实) / 开盘价_真实
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示成功信息
                st.success(f"✅ 回测完成！使用真实数据，数据点: {len(收盘价)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%", delta=f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(收盘价)}")
                
                # 净值曲线
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=收盘价.index, 
                    y=收盘价, 
                    mode='lines', 
                    name=品种,
                    line=dict(color='#00d2ff', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig.update_layout(
                    height=350,
                    title=f"{品种} 价格走势（真实数据）",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="价格 (美元)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 资产曲线
                fig2 = go.Figure()
                资产 = [初始资金 * (收盘价_真实 / 开盘价_真实) ** (i / max(len(收盘价), 1)) for i in range(len(收盘价))]
                fig2.add_trace(go.Scatter(
                    x=收盘价.index,
                    y=资产,
                    mode='lines',
                    name='资产',
                    line=dict(color='#00ff88', width=2)
                ))
                fig2.update_layout(
                    height=350,
                    title="资产曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # 简单均线策略
                with st.expander("📈 均线策略回测"):
                    短周期 = st.slider("短周期", 5, 30, 10, key="short")
                    长周期 = st.slider("长周期", 20, 100, 30, key="long")
                    
                    # 计算均线
                    df = pd.DataFrame({'价格': 收盘价})
                    df['短均线'] = df['价格'].rolling(window=短周期).mean()
                    df['长均线'] = df['价格'].rolling(window=长周期).mean()
                    
                    # 生成信号
                    df['信号'] = 0
                    df.loc[df['短均线'] > df['长均线'], '信号'] = 1
                    df.loc[df['短均线'] <= df['长均线'], '信号'] = -1
                    
                    # 策略回测
                    策略资金 = 初始资金
                    持仓 = 0
                    策略净值 = [初始资金]
                    
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
                        策略净值.append(当前净值)
                    
                    策略收益率 = (策略净值[-1] - 初始资金) / 初始资金
                    st.metric("策略收益率", f"{策略收益率*100:.2f}%", delta=f"vs 持仓收益 {总收益率*100:.2f}%")
                    
                    # 策略曲线
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=收盘价.index, y=策略净值, mode='lines', name='策略净值', line=dict(color='#ffaa00', width=2)))
                    fig3.add_trace(go.Scatter(x=收盘价.index, y=资产, mode='lines', name='持仓净值', line=dict(color='#00ff88', width=2, line_dash='dot')))
                    fig3.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig3, use_container_width=True)
                
                # 显示数据源信息
                st.caption(f"数据源: Yahoo Finance | 品种: {代码} | 数据点: {len(收盘价)}")
                
            except Exception as e:
                st.error(f"获取真实数据失败: {str(e)}")
                st.info("请检查网络连接或稍后重试")
