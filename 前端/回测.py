# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def 显示():
    st.markdown("### ⚙️ 回测参数设置")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "BTC-USD", "GC=F"])
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col2:
        策略类型 = st.selectbox("策略类型", ["双均线策略", "RSI策略", "布林带策略"])
        结束日期 = st.date_input("结束日期", datetime.now())
    
    col3, col4 = st.columns(2)
    with col3:
        初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    with col4:
        手续费 = st.number_input("手续费 (%)", value=0.05, step=0.01, format="%.2f") / 100
    
    # 策略参数
    with st.expander("📊 策略参数"):
        if 策略类型 == "双均线策略":
            短周期 = st.slider("短期均线", 5, 50, 10)
            长周期 = st.slider("长期均线", 20, 200, 30)
        elif 策略类型 == "RSI策略":
            rsi周期 = st.slider("RSI周期", 7, 21, 14)
            rsi超卖 = st.slider("超卖线", 20, 40, 30)
            rsi超买 = st.slider("超买线", 60, 80, 70)
        else:
            bb周期 = st.slider("布林带周期", 10, 50, 20)
            bb标准差 = st.slider("标准差倍数", 1.0, 3.0, 2.0, 0.5)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("生成回测数据..."):
            try:
                # 生成模拟价格数据（基于几何布朗运动）
                np.random.seed(42)
                日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                
                if len(日期列表) < 10:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                
                if len(日期列表) < 5:
                    st.error("日期范围太短，请选择更大的范围")
                    return
                
                # 品种基础参数
                品种参数 = {
                    "AAPL": {"初始价": 175, "波动率": 0.25, "趋势": 0.0003},
                    "MSFT": {"初始价": 330, "波动率": 0.22, "趋势": 0.0004},
                    "GOOGL": {"初始价": 130, "波动率": 0.28, "趋势": 0.0002},
                    "TSLA": {"初始价": 240, "波动率": 0.45, "趋势": 0.0005},
                    "NVDA": {"初始价": 120, "波动率": 0.35, "趋势": 0.0006},
                    "BTC-USD": {"初始价": 45000, "波动率": 0.50, "趋势": 0.0002},
                    "GC=F": {"初始价": 1950, "波动率": 0.15, "趋势": 0.0001},
                }
                
                参数 = 品种参数.get(品种, {"初始价": 100, "波动率": 0.30, "趋势": 0.0002})
                初始价 = 参数["初始价"]
                波动率 = 参数["波动率"]
                趋势 = 参数["趋势"]
                
                # 生成价格序列
                n = len(日期列表)
                收益率 = np.random.normal(趋势, 波动率/np.sqrt(252), n)
                价格序列 = 初始价 * np.exp(np.cumsum(收益率))
                
                # 确保价格合理
                价格序列 = np.maximum(价格序列, 初始价 * 0.5)
                价格序列 = np.minimum(价格序列, 初始价 * 2)
                
                # 创建DataFrame
                df = pd.DataFrame({
                    'Close': 价格序列,
                    'Open': 价格序列 * (1 + np.random.randn(n) * 0.005),
                    'High': 价格序列 * (1 + abs(np.random.randn(n)) * 0.01),
                    'Low': 价格序列 * (1 - abs(np.random.randn(n)) * 0.01),
                }, index=日期列表)
                
                df['Open'] = df['Open'].shift(1).fillna(df['Close'])
                df['High'] = df[['High', 'Open', 'Close']].max(axis=1)
                df['Low'] = df[['Low', 'Open', 'Close']].min(axis=1)
                
                # 根据策略生成信号
                if 策略类型 == "双均线策略":
                    df['短均线'] = df['Close'].rolling(window=短周期).mean()
                    df['长均线'] = df['Close'].rolling(window=长周期).mean()
                    df['信号'] = 0
                    df.loc[df['短均线'] > df['长均线'], '信号'] = 1
                    df.loc[df['短均线'] <= df['长均线'], '信号'] = -1
                    
                elif 策略类型 == "RSI策略":
                    delta = df['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=rsi周期).mean()
                    avg_loss = loss.rolling(window=rsi周期).mean()
                    rs = avg_gain / avg_loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    df['信号'] = 0
                    df.loc[df['RSI'] < rsi超卖, '信号'] = 1
                    df.loc[df['RSI'] > rsi超买, '信号'] = -1
                    
                else:  # 布林带策略
                    data_mean = df['Close'].rolling(window=bb周期).mean()
                    data_std = df['Close'].rolling(window=bb周期).std()
                    df['上轨'] = data_mean + bb标准差 * data_std
                    df['下轨'] = data_mean - bb标准差 * data_std
                    df['信号'] = 0
                    df.loc[df['Close'] < df['下轨'], '信号'] = 1
                    df.loc[df['Close'] > df['上轨'], '信号'] = -1
                
                # 回测计算
                资金 = 初始资金
                持仓 = 0
                交易记录 = []
                净值 = [初始资金]
                
                for i in range(1, len(df)):
                    当前价格 = df['Close'].iloc[i]
                    信号 = df['信号'].iloc[i]
                    
                    # 买入信号
                    if 信号 == 1 and 持仓 == 0:
                        持仓 = 资金 / 当前价格
                        资金 = 0
                        交易记录.append({'日期': df.index[i].strftime('%Y-%m-%d'), '动作': '买入', '价格': f"{当前价格:.2f}"})
                    
                    # 卖出信号
                    elif 信号 == -1 and 持仓 > 0:
                        资金 = 持仓 * 当前价格 * (1 - 手续费)
                        盈亏 = 资金 - 初始资金
                        交易记录.append({'日期': df.index[i].strftime('%Y-%m-%d'), '动作': '卖出', '价格': f"{当前价格:.2f}", '盈亏': f"${盈亏:+.2f}"})
                        持仓 = 0
                    
                    当前净值 = 资金 + 持仓 * 当前价格
                    净值.append(当前净值)
                
                # 最终结算
                if 持仓 > 0:
                    资金 = 持仓 * df['Close'].iloc[-1] * (1 - 手续费)
                   净值.append(资金)
                
                最终资金 = 资金
                总收益率 = (最终资金 - 初始资金) / 初始资金
                年化收益率 = (1 + 总收益率) ** (252 / len(df)) - 1 if len(df) > 0 else 0
                
                # 计算最大回撤
                净值系列 = pd.Series(净值)
                累计最大值 = 净值系列.expanding().max()
                回撤 = (净值系列 - 累计最大值) / 累计最大值
                最大回撤 = 回撤.min()
                
                # 计算胜率
                卖出记录 = [t for t in 交易记录 if t['动作'] == '卖出']
                盈利交易 = [t for t in 卖出记录 if '+' in t.get('盈亏', '')]
                胜率 = len(盈利交易) / len(卖出记录) if 卖出记录 else 0
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(df)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("年化收益", f"{年化收益率*100:.2f}%")
                col_c.metric("最大回撤", f"{最大回撤*100:.2f}%")
                col_d.metric("胜率", f"{胜率*100:.1f}%")
                
                col_e, col_f, col_g, col_h = st.columns(4)
                col_e.metric("初始资金", f"${初始资金:,.0f}")
                col_f.metric("最终资金", f"${最终资金:,.0f}")
                col_g.metric("交易次数", len(交易记录))
                col_h.metric("夏普比率", f"{(总收益率/0.15):.2f}")
                
                # 净值曲线
                fig1 = go.Figure()
                fig1.add_trace(go.Scatter(x=df.index, y=净值[1:], mode='lines', name='策略净值', line=dict(color='#00d2ff', width=2)))
                fig1.add_trace(go.Scatter(x=df.index, y=[初始资金]*len(df), mode='lines', name='初始资金', line=dict(color='gray', dash='dash')))
                fig1.update_layout(height=400, title="净值曲线", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig1, use_container_width=True)
                
                # K线图
                fig2 = go.Figure()
                fig2.add_trace(go.Candlestick(
                    x=df.index, 
                    open=df['Open'], 
                    high=df['High'], 
                    low=df['Low'], 
                    close=df['Close'], 
                    name='K线'
                ))
                
                # 添加均线
                if 策略类型 == "双均线策略":
                    fig2.add_trace(go.Scatter(x=df.index, y=df['短均线'], mode='lines', name=f'MA{短周期}', line=dict(color='#ffaa00', width=1)))
                    fig2.add_trace(go.Scatter(x=df.index, y=df['长均线'], mode='lines', name=f'MA{长周期}', line=dict(color='#00ff88', width=1)))
                elif 策略类型 == "布林带策略":
                    fig2.add_trace(go.Scatter(x=df.index, y=df['上轨'], mode='lines', name='上轨', line=dict(color='#ff4444', width=1, dash='dash')))
                    fig2.add_trace(go.Scatter(x=df.index, y=df['下轨'], mode='lines', name='下轨', line=dict(color='#00ff88', width=1, dash='dash')))
                
                fig2.update_layout(height=500, title="K线图", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig2, use_container_width=True)
                
                # 交易记录
                if 交易记录:
                    with st.expander(f"📋 交易记录 ({len(交易记录)} 笔)"):
                        st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
