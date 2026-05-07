# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示():
    st.markdown("### ⚙️ 回测参数设置")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "GC=F", "EURUSD", "TSLA"])
    with col2:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col3:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    with st.expander("📊 策略参数"):
        短周期 = st.slider("短期均线", 5, 50, 10)
        长周期 = st.slider("长期均线", 20, 200, 30)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                # 生成模拟数据
                日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                if len(日期列表) < 10:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                
                if len(日期列表) < 5:
                    st.error("日期范围太短")
                    return
                
                # 生成模拟价格序列
                np.random.seed(42)
                n = len(日期列表)
                收益率 = np.random.randn(n) * 0.015
                价格序列 = 100 * (1 + np.cumsum(收益率) / 25)
                价格序列 = np.maximum(价格序列, 70)
                价格序列 = np.minimum(价格序列, 130)
                
                # 计算净值
                净值 = 初始资金 * (价格序列 / 价格序列[0])
                
                # 计算最大回撤
                累计最大值 = np.maximum.accumulate(净值)
                回撤 = (累计最大值 - 净值) / 累计最大值 * 100
                
                # 计算收益率
                最终资金 = 净值[-1]
                总收益率 = (最终资金 - 初始资金) / 初始资金
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(日期列表)}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("最大回撤", f"{回撤.max():.2f}%")
                
                # ========== 动态回撤曲线 ==========
                fig = go.Figure()
                
                # 添加回撤曲线（填充）
                fig.add_trace(go.Scatter(
                    x=日期列表,
                    y=回撤,
                    mode='lines',
                    name='回撤曲线',
                    line=dict(color='#ef4444', width=2, shape='spline'),
                    fill='tozeroy',
                    opacity=0.3
                ))
                
                # 添加0%参考线
                fig.add_hline(
                    y=0,
                    line_dash="dash",
                    line_color="#10b981",
                    annotation_text="0% 基准线",
                    annotation_font_color="#e6e6e6"
                )
                
                # 添加临界线
                fig.add_hline(
                    y=-10,
                    line_dash="dot",
                    line_color="#ffaa00",
                    annotation_text="风险线 -10%",
                    annotation_font_color="#e6e6e6"
                )
                
                fig.update_layout(
                    height=350,
                    title="动态回撤曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="回撤 (%)",
                    xaxis=dict(
                        tickformat="%Y-%m",
                        tickangle=-45,
                        showgrid=True,
                        gridwidth=0.5,
                        gridcolor='#2a2e3a'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridwidth=0.5,
                        gridcolor='#2a2e3a',
                        ticksuffix="%"
                    ),
                    margin=dict(l=50, r=40, t=50, b=80)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 回撤统计
                st.markdown("### 📊 回撤统计")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("最大回撤", f"{回撤.max():.2f}%")
                with col2:
                    st.metric("平均回撤", f"{回撤.mean():.2f}%")
                with col3:
                    st.metric("当前回撤", f"{回撤[-1]:.2f}%")
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
