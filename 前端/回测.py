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
        品种 = st.selectbox("选择品种", ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "BTC-USD", "GC=F"])
    with col2:
        周期 = st.selectbox("K线周期", ["日线", "周线"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("生成回测数据..."):
            try:
                # 市场参数（基于真实历史表现）
                市场参数 = {
                    "AAPL": {"波动率": 0.25, "年化收益": 0.15, "当前价": 175},
                    "MSFT": {"波动率": 0.22, "年化收益": 0.18, "当前价": 330},
                    "GOOGL": {"波动率": 0.28, "年化收益": 0.12, "当前价": 130},
                    "TSLA": {"波动率": 0.45, "年化收益": 0.20, "当前价": 240},
                    "NVDA": {"波动率": 0.35, "年化收益": 0.25, "当前价": 120},
                    "BTC-USD": {"波动率": 0.50, "年化收益": 0.30, "当前价": 45000},
                    "GC=F": {"波动率": 0.15, "年化收益": 0.05, "当前价": 1950},
                }
                
                参数 = 市场参数.get(品种, {"波动率": 0.30, "年化收益": 0.10, "当前价": 100})
                
                # 生成日期序列
                if 周期 == "日线":
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                else:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                
                if len(日期列表) < 10:
                    st.warning("日期范围太短，自动扩展")
                    开始日期 = 结束日期 - timedelta(days=365)
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                
                # 使用几何布朗运动生成价格序列
                np.random.seed(hash(品种) % 10000)
                dt = 1 / 252
                n = len(日期列表)
                价格序列 = [参数["当前价"]]
                
                for i in range(1, n):
                    收益 = 参数["年化收益"] * dt + 参数["波动率"] * np.random.normal(0, 1) * np.sqrt(dt)
                    新价格 = 价格序列[-1] * (1 + 收益)
                    价格序列.append(max(新价格, 价格序列[-1] * 0.8))
                
                收盘价列表 = 价格序列
                
                if len(收盘价列表) < 5:
                    st.error(f"数据点不足: {len(收盘价列表)}")
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
                col_d.metric("年化波动率", f"{参数['波动率']*100:.1f}%")
                
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
                    title=f"{品种} 价格走势（模拟）",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="价格 (美元)"
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
                    line=dict(color='#00ff88', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig2.update_layout(
                    height=350, 
                    title="资产曲线",
                    paper_bgcolor="#0a0c10", 
                    plot_bgcolor="#15171a",
                    xaxis_title="日期",
                    yaxis_title="资产 (美元)"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # 均线策略
                with st.expander("📈 均线策略回测", expanded=True):
                    col_s1, col_s2 = st.columns(2)
                    with col_s1:
                        短周期 = st.slider("短期均线", 5, 50, 10, key="short")
                    with col_s2:
                        长周期 = st.slider("长期均线", 20, 200, 30, key="long")
                    
                    # 计算均线
                    df = pd.DataFrame({'价格': 收盘价列表}, index=日期列表)
                    df['短均线'] = df['价格'].rolling(window=短周期).mean()
                    df['长均线'] = df['价格'].rolling(window=长周期).mean()
                    
                    # 策略回测
                    策略资金 = 初始资金
                    持仓 = 0
                    策略净值 = [初始资金]
                    交易记录 = []
                    
                    for i in range(1, len(df)):
                        当前价格 = df['价格'].iloc[i]
                        
                        # 金叉买入
                        if df['短均线'].iloc[i] > df['长均线'].iloc[i] and df['短均线'].iloc[i-1] <= df['长均线'].iloc[i-1]:
                            if 持仓 == 0:
                                持仓 = 策略资金 / 当前价格
                                策略资金 = 0
                                交易记录.append({'日期': df.index[i], '动作': '买入', '价格': 当前价格})
                        # 死叉卖出
                        elif df['短均线'].iloc[i] < df['长均线'].iloc[i] and df['短均线'].iloc[i-1] >= df['长均线'].iloc[i-1]:
                            if 持仓 > 0:
                                策略资金 = 持仓 * 当前价格
                                盈亏 = 策略资金 - 初始资金
                                交易记录.append({'日期': df.index[i], '动作': '卖出', '价格': 当前价格, '盈亏': 盈亏})
                                持仓 = 0
                        
                        当前净值 = 策略资金 + 持仓 * 当前价格
                        策略净值.append(当前净值)
                    
                    策略收益率 = (策略净值[-1] - 初始资金) / 初始资金
                    
                    col_r1, col_r2 = st.columns(2)
                    col_r1.metric("策略收益率", f"{策略收益率*100:.2f}%", delta=f"vs 持有 {总收益率*100:.2f}%")
                    col_r2.metric("交易次数", len(交易记录))
                    
                    # 对比曲线
                    fig3 = go.Figure()
                    fig3.add_trace(go.Scatter(x=日期列表, y=策略净值, mode='lines', name='策略净值', line=dict(color='#ffaa00', width=2)))
                    fig3.add_trace(go.Scatter(x=日期列表, y=资产, mode='lines', name='持有净值', line=dict(color='#00ff88', width=2, line_dash='dot')))
                    fig3.update_layout(
                        height=350, 
                        title="策略 vs 持有",
                        paper_bgcolor="#0a0c10", 
                        plot_bgcolor="#15171a",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02)
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    if 交易记录:
                        with st.expander("交易记录"):
                            st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                
                # 数据说明
                st.caption(f"📊 数据说明：基于 {品种} 历史波动率 {参数['波动率']*100:.1f}% 和年化收益 {参数['年化收益']*100:.1f}% 生成")
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
