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
                代码 = 品种
                st.info(f"正在获取 {代码} 真实数据...")
                
                # 下载数据 - 使用更稳定的方式
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期, progress=False)
                
                if 数据.empty:
                    st.warning(f"无法获取 {代码} 真实数据")
                    return
                
                # 安全提取收盘价 - 关键修复
                if 'Close' in 数据.columns:
                    收盘价原始 = 数据['Close']
                elif 'Adj Close' in 数据.columns:
                    收盘价原始 = 数据['Adj Close']
                else:
                    st.error("没有价格数据")
                    return
                
                # 转换为简单列表（解决 Series 问题）
                收盘价列表 = []
                日期列表 = []
                
                for idx, val in 收盘价原始.items():
                    try:
                        # 处理各种数据类型
                        if hasattr(val, 'iloc'):
                            val = val.iloc[0]
                        if hasattr(val, 'values'):
                            val = val.values[0] if len(val.values) > 0 else val
                        if hasattr(val, 'item'):
                            val = val.item()
                        价格数值 = float(val)
                        收盘价列表.append(价格数值)
                        日期列表.append(idx)
                    except:
                        continue
                
                if len(收盘价列表) < 5:
                    st.warning(f"数据点不足: {len(收盘价列表)}")
                    return
                
                # 计算收益率
                开盘价_真实 = 收盘价列表[0]
                收盘价_真实 = 收盘价列表[-1]
                总收益率 = (收盘价_真实 - 开盘价_真实) / 开盘价_真实
                最终资金 = 初始资金 * (1 + 总收益率)
                
                st.success(f"✅ 回测完成！数据点: {len(收盘价列表)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(收盘价列表)}")
                
                # 价格曲线
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=日期列表, 
                    y=收盘价列表, 
                    mode='lines', 
                    name=品种,
                    line=dict(color='#00d2ff', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig.update_layout(
                    height=350,
                    title=f"{品种} 价格走势",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 资产曲线
                fig2 = go.Figure()
                资产 = [初始资金 * (收盘价_真实 / 开盘价_真实) ** (i / max(len(收盘价列表), 1)) for i in range(len(收盘价列表))]
                fig2.add_trace(go.Scatter(
                    x=日期列表,
                    y=资产,
                    mode='lines',
                    name='资产',
                    line=dict(color='#00ff88', width=2)
                ))
                fig2.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig2, use_container_width=True)
                
                # 简单策略
                with st.expander("📈 均线策略回测"):
                    短周期 = st.slider("短周期", 5, 30, 10, key="short")
                    长周期 = st.slider("长周期", 20, 100, 30, key="long")
                    
                    df = pd.DataFrame({'价格': 收盘价列表}, index=日期列表)
                    df['短均线'] = df['价格'].rolling(window=短周期).mean()
                    df['长均线'] = df['价格'].rolling(window=长周期).mean()
                    
                    # 策略回测
                    策略资金 = 初始资金
                    持仓 = 0
                    持仓价 = 0
                    策略净值 = [初始资金]
                    
                    for i in range(1, len(df)):
                        当前价格 = df['价格'].iloc[i]
                        
                        # 金叉买入
                        if df['短均线'].iloc[i] > df['长均线'].iloc[i] and df['短均线'].iloc[i-1] <= df['长均线'].iloc[i-1]:
                            if 持仓 == 0:
                                持仓 = 策略资金 / 当前价格
                                策略资金 = 0
                                持仓价 = 当前价格
                        # 死叉卖出
                        elif df['短均线'].iloc[i] < df['长均线'].iloc[i] and df['短均线'].iloc[i-1] >= df['长均线'].iloc[i-1]:
                            if 持仓 > 0:
                                策略资金 = 持仓 * 当前价格
                                持仓 = 0
                        
                        当前净值 = 策略资金 + 持仓 * 当前价格
                        策略净值.append(当前净值)
                    
                    策略收益率 = (策略净值[-1] - 初始资金) / 初始资金
                    st.metric("策略收益率", f"{策略收益率*100:.2f}%")
                    
                    # 对比曲线
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=日期列表, y=策略净值, mode='lines', name='策略净值', line=dict(color='#ffaa00', width=2)))
                    fig3.add_trace(go.Scatter(x=日期列表, y=资产, mode='lines', name='持有净值', line=dict(color='#00ff88', width=2, line_dash='dot')))
                    fig3.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig3, use_container_width=True)
                
            except Exception as e:
                st.error(f"获取数据失败: {str(e)}")
                st.info("请尝试选择 AAPL 或缩短日期范围")
