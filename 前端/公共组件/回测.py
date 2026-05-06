# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from 回测.回测引擎 import 回测引擎
from 策略库.期货策略.期货趋势策略 import FuturesTrendStrategy


def 显示():
    st.markdown("### 📈 策略回测")
    
    col1, col2 = st.columns(2)
    
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "EURUSD", "GC=F"])
    
    with col2:
        周期 = st.selectbox("K线周期", ["1m", "5m", "15m", "30m", "1h", "1d"])
    
    col3, col4 = st.columns(2)
    
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=180))
    
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary"):
        with st.spinner("回测中..."):
            # 创建策略实例
            策略 = FuturesTrendStrategy("回测策略", 品种, 初始资金)
            
            # 运行回测
            引擎 = 回测引擎(初始资金)
            结果 = 引擎.运行回测(策略, 品种, 开始日期, 结束日期, 周期)
            
            if 结果.get("错误"):
                st.error(结果["错误"])
                return
            
            # 显示结果
            st.success("回测完成！")
            
            # 关键指标
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总收益率", f"{结果['总收益率']*100:.2f}%")
            col2.metric("年化收益率", f"{结果['年化收益率']*100:.2f}%")
            col3.metric("夏普比率", f"{结果['夏普比率']}")
            col4.metric("最大回撤", f"{结果['最大回撤率']*100:.2f}%")
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("胜率", f"{结果['胜率']*100:.2f}%")
            col6.metric("盈亏比", f"{结果['盈亏比']}")
            col7.metric("交易次数", f"{结果['交易次数']}")
            col8.metric("换手率", f"{结果['换手率']}")
            
            # 净值曲线
            if not 结果['净值曲线'].empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=结果['净值曲线']['日期'],
                    y=结果['净值曲线']['净值'],
                    mode='lines',
                    name='净值',
                    line=dict(color='#00d2ff', width=2)
                ))
                fig.update_layout(
                    title="净值曲线",
                    height=400,
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 交易记录
            if not 结果['交易记录'].empty:
                with st.expander("📋 交易记录"):
                    st.dataframe(结果['交易记录'], use_container_width=True)
