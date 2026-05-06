# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def 显示():
    st.markdown("""
    <style>
        .backtest-title { font-size: 20px; font-weight: bold; color: #00d2ff; margin-bottom: 20px; }
        .metric-box { background-color: #1a1d24; border-radius: 10px; padding: 15px; text-align: center; }
        .metric-label { font-size: 12px; color: #8892b0; }
        .metric-value { font-size: 22px; font-weight: bold; color: #00d2ff; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="backtest-title">📈 策略回测系统</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "MSFT", "GOOGL"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1h", "30m", "15m", "5m"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    with st.expander("⚙️ 策略参数"):
        短周期 = st.slider("短期均线周期", 5, 50, 10)
        长周期 = st.slider("长期均线周期", 20, 200, 30)
        止损比例 = st.slider("止损比例 (%)", 1, 20, 5) / 100
        止盈比例 = st.slider("止盈比例 (%)", 5, 50, 15) / 100
    
    if st.button("🚀 开始回测", type="primary"):
        with st.spinner("回测运行中..."):
            try:
                # 获取数据
                映射 = {"EURUSD": "EURUSD=X", "BTC-USD": "BTC-USD", "GC=F": "GC=F", 
                        "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL"}
                代码 = 映射.get(品种, 品种)
                数据 = yf.download(代码, start=开始日期, end=结束日期, interval=周期, progress=False)
                
                if 数据.empty:
                    st.error("无法获取数据")
                    return
                
                # 计算均线
                数据['短均线'] = 数据['Close'].rolling(window=短周期).mean()
                数据['长均线'] = 数据['Close'].rolling(window=长周期).mean()
                
                # 生成信号
                数据['信号'] = 0
                数据.loc[数据['短均线'] > 数据['长均线'], '信号'] = 1
                数据.loc[数据['短均线'] <= 数据['长均线'], '信号'] = -1
                
                # 回测计算
                资金 = 初始资金
                持仓 = 0
                持仓价 = 0
                交易记录 = []
                净值 = [初始资金]
                最高净值 = 初始资金
                最大回撤 = 0
                
                for i in range(len(数据)):
                    当前价格 = float(数据['Close'].iloc[i])
                    信号 = 数据['信号'].iloc[i]
                    
                    # 止损止盈检查
                    if 持仓 > 0:
                        盈亏率 = (当前价格 - 持仓价) / 持仓价
                        if 盈亏率 <= -止损比例:  # 止损
                            资金 += 持仓 * 当前价格
                            盈亏 = 持仓 * (当前价格 - 持仓价)
                            交易记录.append({'日期': 数据.index[i], '动作': '止损卖出', '价格': 当前价格, '盈亏': 盈亏})
                            持仓 = 0
                         elif 盈亏率 >= 止盈比例:  # 止盈
                            资金 += 持仓 * 当前价格
                            盈亏 = 持仓 * (当前价格 - 持仓价)
                            交易记录.append({'日期': 数据.index[i], '动作': '止盈卖出', '价格': 当前价格, '盈亏': 盈亏})
                            持仓 = 0
                    
                    # 新信号
                    if 信号 == 1 and 持仓 == 0:  # 买入
                        持仓量 = 资金 // 当前价格
                        if 持仓量 > 0:
                            持仓 = 持仓量
                            持仓价 = 当前价格
                            资金 -= 持仓 * 当前价格
                            交易记录.append({'日期': 数据.index[i], '动作': '买入', '价格': 当前价格, '数量': 持仓})
                    
                    elif 信号 == -1 and 持仓 > 0:  # 卖出
                        资金 += 持仓 * 当前价格
                        盈亏 = 持仓 * (当前价格 - 持仓价)
                        交易记录.append({'日期': 数据.index[i], '动作': '卖出', '价格': 当前价格, '盈亏': 盈亏})
                        持仓 = 0
                    
                    # 计算净值
                    当前净值 = 资金 + 持仓 * 当前价格
                    净值.append(当前净值)
                    
                    # 计算最大回撤
                    if 当前净值 > 最高净值:
                        最高净值 = 当前净值
                    回撤 = (最高净值 - 当前净值) / 最高净值
                    if 回撤 > 最大回撤:
                        最大回撤 = 回撤
                
                # 最终结算
                if 持仓 > 0:
                    最终价格 = float(数据['Close'].iloc[-1])
                    资金 += 持仓 * 最终价格
                
                最终净值 = 资金
                总收益率 = (最终净值 - 初始资金) / 初始资金
                年化收益率 = (1 + 总收益率) ** (252 / len(数据)) - 1 if len(数据) > 0 else 0
                夏普比率 = 总收益率 / 0.15 if 总收益率 > 0 else 0
                交易次数 = len([t for t in 交易记录 if t['动作'] in ['买入', '卖出']])
                胜率 = len([t for t in 交易记录 if t.get('盈亏', 0) > 0]) / len([t for t in 交易记录 if '盈亏' in t]) if 交易记录 else 0
                
                # 显示结果
                st.success(f"✅ 回测完成！")
                
                # 指标卡片
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("总收益率", f"{总收益率*100:.2f}%")
                col2.metric("年化收益率", f"{年化收益率*100:.2f}%")
                col3.metric("夏普比率", f"{夏普比率:.2f}")
                col4.metric("最大回撤", f"{最大回撤*100:.2f}%")
                
                col5, col6, col7, col8 = st.columns(4)
                col5.metric("交易次数", f"{交易次数}")
                col6.metric("胜率", f"{胜率*100:.1f}%")
                col7.metric("初始资金", f"${初始资金:,.0f}")
                col8.metric("最终资金", f"${最终净值:,.0f}")
                
                # 净值曲线图
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=数据.index,
                    y=净值[1:],
                    mode='lines',
                    name='净值',
                    line=dict(color='#00d2ff', width=2)
                ))
                fig.add_hline(y=初始资金, line_dash="dash", line_color="gray", annotation_text=f"初始资金 ${初始资金:,.0f}")
                fig.update_layout(height=400, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
                st.plotly_chart(fig, use_container_width=True)
                
                # 交易记录
                if 交易记录:
                    with st.expander(f"📋 交易记录 ({len(交易记录)} 笔)"):
                        df_trades = pd.DataFrame(交易记录)
                        st.dataframe(df_trades, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {e}")
