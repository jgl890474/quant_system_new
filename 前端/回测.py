# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

def 显示():
    st.markdown("### 📈 策略回测系统")
    st.markdown("使用历史数据回测策略表现")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "000001.SS"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1h", "30m", "15m", "5m"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    # 策略参数
    with st.expander("策略参数"):
        短周期 = st.slider("短周期", 5, 50, 10)
        长周期 = st.slider("长周期", 20, 200, 30)
    
    if st.button("🚀 开始回测", type="primary"):
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", "AAPL": "AAPL", "000001.SS": "000001.SS"}
                代码 = 映射.get(品种, 品种)
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期)
                
                if 数据.empty:
                    st.error("无法获取数据")
                    return
                
                # 双均线策略回测
                数据['短均线'] = 数据['Close'].rolling(window=短周期).mean()
                数据['长均线'] = 数据['Close'].rolling(window=长周期).mean()
                数据['信号'] = 0
                数据.loc[数据['短均线'] > 数据['长均线'], '信号'] = 1
                数据.loc[数据['短均线'] <= 数据['长均线'], '信号'] = -1
                
                # 计算交易信号
                数据['持仓'] = 数据['信号'].diff()
                
                # 回测计算
                资金 = 初始资金
                持仓 = 0
                交易记录 = []
                净值 = [初始资金]
                
                for i in range(len(数据)):
                    if 数据['持仓'].iloc[i] == 2:  # 买入信号
                        价格 = 数据['Close'].iloc[i]
                        数量 = 资金 // 价格
                        if 数量 > 0:
                            持仓 += 数量
                            资金 -= 数量 * 价格
                            交易记录.append({'日期': 数据.index[i], '动作': '买入', '价格': 价格})
                    elif 数据['持仓'].iloc[i] == -2:  # 卖出信号
                        if 持仓 > 0:
                            价格 = 数据['Close'].iloc[i]
                            资金 += 持仓 * 价格
                            交易记录.append({'日期': 数据.index[i], '动作': '卖出', '价格': 价格, '盈亏': 持仓 * (价格 - 交易记录[-1]['价格'] if 交易记录 else 0)})
                            持仓 = 0
                    
                    当前净值 = 资金 + 持仓 * 数据['Close'].iloc[i]
                    净值.append(当前净值)
                
                最终净值 = 资金 + 持仓 * 数据['Close'].iloc[-1]
                总收益率 = (最终净值 - 初始资金) / 初始资金
                
                # 显示结果
                st.success(f"回测完成！最终资金: ${最终净值:,.0f}")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("总收益率", f"{总收益率*100:.2f}%")
                c2.metric("交易次数", len(交易记录))
                c3.metric("初始资金", f"${初始资金:,.0f}")
                c4.metric("最终资金", f"${最终净值:,.0f}")
                
                # 净值曲线
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=数据.index, y=净值[1:], mode='lines', name='净值', line=dict(color='#00d2ff', width=2)))
                fig.add_hline(y=初始资金, line_dash="dash", line_color="gray", annotation_text=f"初始资金 ${初始资金:,.0f}")
                fig.update_layout(title="净值曲线", height=400, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                st.plotly_chart(fig, use_container_width=True)
                
                # 交易记录
                if 交易记录:
                    with st.expander("交易记录"):
                        st.dataframe(pd.DataFrame(交易记录), use_container_width=True)
                        
            except Exception as e:
                st.error(f"回测出错: {e}")
