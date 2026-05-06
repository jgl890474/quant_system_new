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
        品种 = st.selectbox("选择品种", ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"])
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col2:
        策略类型 = st.selectbox("策略类型", ["双均线策略", "RSI策略"])
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
        else:
            rsi周期 = st.slider("RSI周期", 7, 21, 14)
            rsi超卖 = st.slider("超卖线", 20, 40, 30)
            rsi超买 = st.slider("超买线", 60, 80, 70)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                代码 = 品种
                st.info(f"获取 {代码} 数据...")
                
                # 下载数据
                数据 = yf.download(代码, start=开始日期, end=结束日期, progress=False)
                
                if 数据.empty:
                    st.warning("无法获取真实数据，使用模拟数据")
                    # 生成模拟数据
                    日期 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                    np.random.seed(42)
                    收益率 = np.random.randn(len(日期)) * 0.02
                    价格 = 100 * (1 + np.cumsum(收益率) / 50)
                    数据 = pd.DataFrame({'Open': 价格, 'High': 价格*1.02, 'Low': 价格*0.98, 'Close': 价格}, index=日期)
                
                # 安全提取收盘价 - 关键修复
                if 'Close' in 数据.columns:
                    收盘价原始 = 数据['Close']
                else:
                    收盘价原始 = 数据['close'] if 'close' in 数据.columns else None
                
                if 收盘价原始 is None:
                    st.error("无法获取收盘价")
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
                
                if len(收盘价列表) < 10:
                    st.error(f"数据点不足: {len(收盘价列表)}")
                    return
                
                # 创建DataFrame用于计算
                df = pd.DataFrame({'Close': 收盘价列表}, index=日期列表)
                df['Open'] = df['Close'].shift(1).fillna(df['Close'])
                df['High'] = df['Close'] * 1.02
                df['Low'] = df['Close'] * 0.98
                
                # 根据策略生成信号
                if 策略类型 == "双均线策略":
                    df['短均线'] = df['Close'].rolling(window=短周期).mean()
                    df['长均线'] = df['Close'].rolling(window=长周期).mean()
                    df['信号'] = 0
                    df.loc[df['短均线'] > df['长均线'], '信号'] = 1
                    df.loc[df['短均线'] <= df['长均线'], '信号'] = -1
                    
                else:  # RSI策略
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
                
                fig2.update_layout(height=500, title="K线图", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig2, use_container_width=True)
                
                # 交易记录
                if 交易记录:
                    with st.expander(f"📋 交易记录 ({len(交易记录)} 笔)"):
                        st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
