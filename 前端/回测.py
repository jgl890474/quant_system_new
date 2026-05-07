# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from 工具 import 数据库

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
    
    with st.expander("📊 策略参数"):
        if 策略类型 == "双均线策略":
            短周期 = st.slider("短期均线", 5, 50, 10)
            长周期 = st.slider("长期均线", 20, 200, 30)
        else:
            rsi周期 = st.slider("RSI周期", 7, 21, 14)
            rsi超卖 = st.slider("超卖线", 20, 40, 30)
            rsi超买 = st.slider("超买线", 60, 80, 70)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("生成回测数据..."):
            try:
                # 生成日期
                日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                if len(日期列表) < 10:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                if len(日期列表) < 5:
                    st.error("日期范围太短")
                    return
                
                # 品种参数
                品种参数 = {
                    "AAPL": {"初始价": 175, "波动率": 0.25},
                    "MSFT": {"初始价": 330, "波动率": 0.22},
                    "GOOGL": {"初始价": 130, "波动率": 0.28},
                    "TSLA": {"初始价": 240, "波动率": 0.45},
                    "NVDA": {"初始价": 120, "波动率": 0.35},
                }
                参数 = 品种参数.get(品种, {"初始价": 100, "波动率": 0.30})
                初始价 = 参数["初始价"]
                波动率 = 参数["波动率"]
                
                # 生成价格
                n = len(日期列表)
                np.random.seed(42)
                收益率 = np.random.normal(0.0003, 波动率/np.sqrt(252), n)
                价格序列 = 初始价 * np.exp(np.cumsum(收益率))
                价格序列 = np.maximum(价格序列, 初始价 * 0.6)
                价格序列 = np.minimum(价格序列, 初始价 * 1.8)
                
                # 创建DataFrame
                df = pd.DataFrame({'Close': 价格序列}, index=日期列表)
                df['Open'] = df['Close'].shift(1).fillna(df['Close'])
                df['High'] = df[['Close', 'Open']].max(axis=1) * 1.01
                df['Low'] = df[['Close', 'Open']].min(axis=1) * 0.99
                
                # 生成信号
                if 策略类型 == "双均线策略":
                    df['短均线'] = df['Close'].rolling(window=短周期).mean()
                    df['长均线'] = df['Close'].rolling(window=长周期).mean()
                    df['信号'] = 0
                    df.loc[df['短均线'] > df['长均线'], '信号'] = 1
                    df.loc[df['短均线'] <= df['长均线'], '信号'] = -1
                else:
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
                
                # 回测
                资金 = 初始资金
                持仓 = 0
                交易记录 = []
                净值 = [初始资金]
                
                for i in range(1, len(df)):
                    当前价格 = df['Close'].iloc[i]
                    信号 = df['信号'].iloc[i]
                    
                    if 信号 == 1 and 持仓 == 0:
                        持仓 = 资金 / 当前价格
                        资金 = 0
                        交易记录.append({'日期': df.index[i].strftime('%Y-%m-%d'), '动作': '买入', '价格': round(当前价格, 2)})
                    elif 信号 == -1 and 持仓 > 0:
                        资金 = 持仓 * 当前价格 * (1 - 手续费)
                        交易记录.append({'日期': df.index[i].strftime('%Y-%m-%d'), '动作': '卖出', '价格': round(当前价格, 2)})
                        持仓 = 0
                    
                    净值.append(资金 + 持仓 * 当前价格)
                
                if 持仓 > 0:
                    资金 = 持仓 * df['Close'].iloc[-1] * (1 - 手续费)
                
                最终资金 = 资金
                总收益率 = (最终资金 - 初始资金) / 初始资金
                
                # 保存回测结果到数据库
                try:
                    数据库.保存回测结果(
                        品种=品种,
                        策略类型=策略类型,
                        开始日期=开始日期.strftime('%Y-%m-%d'),
                        结束日期=结束日期.strftime('%Y-%m-%d'),
                        初始资金=初始资金,
                        最终资金=最终资金,
                        总收益率=总收益率,
                        年化收益=总收益率,
                        最大回撤=0,
                        胜率=0,
                        交易次数=len(交易记录),
                        参数={"短周期": 短周期, "长周期": 长周期} if 策略类型 == "双均线策略" else {"rsi周期": rsi周期}
                    )
                except:
                    pass
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(df)}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("交易次数", len(交易记录))
                
                # 净值曲线
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=净值[1:], mode='lines', name='策略净值', line=dict(color='#00d2ff', width=2)))
                fig.update_layout(height=400, title="净值曲线", paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示历史回测记录
                with st.expander("📋 历史回测记录"):
                    历史回测 = 数据库.获取回测历史(20)
                    if not 历史回测.empty:
                        st.dataframe(历史回测, use_container_width=True)
                    else:
                        st.info("暂无历史回测记录")
                
                # 交易记录
                if 交易记录:
                    with st.expander(f"📋 本次回测交易记录 ({len(交易记录)} 笔)"):
                        st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
