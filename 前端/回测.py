# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
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
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", 
                        "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL", "TSLA": "TSLA", "NVDA": "NVDA"}
                代码 = 映射.get(品种, 品种)
                
                # 下载数据
                数据 = yf.download(代码, start=开始日期, end=结束日期, progress=False)
                
                if 数据.empty:
                    st.warning("无法获取数据，使用模拟数据")
                    # 生成模拟数据
                    日期 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                    价格 = 100 * (1 + np.cumsum(np.random.randn(len(日期)) * 0.01))
                    数据 = pd.DataFrame({'Close':价格}, index=日期)
                
                # 根据策略生成信号
                收盘价 = 数据['Close']
                
                if 策略类型 == "双均线策略":
                    数据['短均线'] = 收盘价.rolling(window=短周期).mean()
                    数据['长均线'] = 收盘价.rolling(window=长周期).mean()
                    数据['信号'] = 0
                    数据.loc[数据['短均线'] > 数据['长均线'], '信号'] = 1
                    数据.loc[数据['短均线'] <= 数据['长均线'], '信号'] = -1
                    
                elif 策略类型 == "RSI策略":
                    # 计算RSI
                    delta = 收盘价.diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=rsi周期).mean()
                    avg_loss = loss.rolling(window=rsi周期).mean()
                    rs = avg_gain / avg_loss
                    数据['RSI'] = 100 - (100 / (1 + rs))
                    数据['信号'] = 0
                    数据.loc[数据['RSI'] < rsi超卖, '信号'] = 1
                    数据.loc[数据['RSI'] > rsi超买, '信号'] = -1
                    
                else:  # 布林带策略
                    data = 收盘价
                    data_mean = data.rolling(window=bb周期).mean()
                    data_std = data.rolling(window=bb周期).std()
                    数据['上轨'] = data_mean + bb标准差 * data_std
                    数据['下轨'] = data_mean - bb标准差 * data_std
                    数据['信号'] = 0
                    数据.loc[收盘价 < 数据['下轨'], '信号'] = 1
                    数据.loc[收盘价 > 数据['上轨'], '信号'] = -1
                
                # 回测计算
                资金 = 初始资金
                持仓 = 0
                持仓价 = 0
                交易记录 = []
                净值 = [初始资金]
                
                for i in range(1, len(数据)):
                    当前价格 = float(收盘价.iloc[i])
                    信号 = 数据['信号'].iloc[i]
                    
                    # 买入信号
                    if 信号 == 1 and 持仓 == 0:
                        持仓 = 资金 / 当前价格
                        持仓价 = 当前价格
                        资金 = 0
                        交易记录.append({'日期': 数据.index[i], '动作': '买入', '价格': 当前价格})
                    
                    # 卖出信号
                    elif 信号 == -1 and 持仓 > 0:
                        资金 = 持仓 * 当前价格 * (1 - 手续费)
                        交易记录.append({'日期': 数据.index[i], '动作': '卖出', '价格': 当前价格, '盈亏': 资金 - 初始资金})
                        持仓 = 0
                    
                    当前净值 = 资金 + 持仓 * 当前价格
                    净值.append(当前净值)
                
                # 最终结算
                if 持仓 > 0:
                    资金 = 持仓 * float(收盘价.iloc[-1]) * (1 - 手续费)
                
                最终资金 = 资金
                总收益率 = (最终资金 - 初始资金) / 初始资金
                年化收益率 = (1 + 总收益率) ** (252 / len(数据)) - 1 if len(数据) > 0 else 0
                
                # 计算最大回撤
                净值系列 = pd.Series(净值)
                累计最大值 =净值系列.expanding().max()
                回撤 = (净值系列 - 累计最大值) / 累计最大值
                最大回撤 = 回撤.min()
                
                # 计算胜率
                盈利交易 = [t for t in 交易记录 if t.get('盈亏', 0) > 0]
                胜率 = len(盈利交易) / len([t for t in 交易记录 if '盈亏' in t]) if 交易记录 else 0
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(数据)}")
                
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
                fig1.add_trace(go.Scatter(x=数据.index, y=净值[1:], mode='lines', name='策略净值', line=dict(color='#00d2ff', width=2)))
                fig1.add_trace(go.Scatter(x=数据.index, y=[初始资金]*len(数据), mode='lines', name='初始资金', line=dict(color='gray', dash='dash')))
                fig1.update_layout(height=400, title="净值曲线", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig1, use_container_width=True)
                
                # K线图 + 信号
                fig2 = go.Figure()
                fig2.add_trace(go.Candlestick(x=数据.index, open=数据['Open'], high=数据['High'], low=数据['Low'], close=数据['Close'], name='K线'))
                
                # 添加均线
                if 策略类型 == "双均线策略":
                    fig2.add_trace(go.Scatter(x=数据.index, y=数据['短均线'], mode='lines', name=f'MA{短周期}', line=dict(color='#ffaa00', width=1)))
                    fig2.add_trace(go.Scatter(x=数据.index, y=数据['长均线'], mode='lines', name=f'MA{长周期}', line=dict(color='#00ff88', width=1)))
                
                fig2.update_layout(height=500, title="K线图与信号", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig2, use_container_width=True)
                
                # 交易记录
                if 交易记录:
                    with st.expander(f"📋 交易记录 ({len(交易记录)} 笔)"):
                        st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
