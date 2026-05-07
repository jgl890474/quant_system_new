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
                价格序列 = np.maximum(价格序列, 80)
                价格序列 = np.minimum(价格序列, 120)
                
                # 转换为 pandas Series
                价格序列_series = pd.Series(价格序列, index=日期列表)
                
                # 计算净值
                净值 = 初始资金 * (价格序列_series / 价格序列_series.iloc[0])
                
                # 计算收益率
                最终净值 = 净值.iloc[-1]
                总收益率 = (最终净值 - 初始资金) / 初始资金
                
                # 计算动态回撤
                累计最大值 = 净值.cummax()
                动态回撤 = (净值 - 累计最大值) / 累计最大值 * 100
                
                # 计算回撤统计
                最大回撤 = 动态回撤.min()
                平均回撤 = 动态回撤.mean()
                当前回撤 = 动态回撤.iloc[-1]
                回撤持续时间 = (动态回撤 < -5).sum()
                
                # 显示结果卡片
                st.markdown("### 📊 回测结果")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("总收益率", f"{总收益率*100:.2f}%", delta=f"{总收益率*100:.2f}%")
                col2.metric("初始资金", f"${初始资金:,.0f}")
                col3.metric("最终净值", f"${最终净值:,.0f}")
                col4.metric("最大回撤", f"{最大回撤:.2f}%", delta=f"最低 {最大回撤:.2f}%")
                
                col5, col6, col7, col8 = st.columns(4)
                col5.metric("平均回撤", f"{平均回撤:.2f}%")
                col6.metric("当前回撤", f"{当前回撤:.2f}%")
                col7.metric("回撤>5%天数", f"{回撤持续时间}天")
                col8.metric("数据点", f"{len(日期列表)}")
                
                # ========== 动态回测曲线（双轴） ==========
                st.markdown("### 📈 动态回测曲线")
                
                fig = go.Figure()
                
                # 添加净值曲线（左轴）
                fig.add_trace(go.Scatter(
                    x=净值.index,
                    y=净值.values,
                    mode='lines',
                    name='资产净值',
                    line=dict(color='#00d2ff', width=2),
                    yaxis="y1"
                ))
                
                # 添加动态回撤曲线（右轴）
                fig.add_trace(go.Scatter(
                    x=动态回撤.index,
                    y=动态回撤.values,
                    mode='lines',
                    name='动态回撤',
                    line=dict(color='#ef4444', width=1.5, dash='dot'),
                    yaxis="y2",
                    fill='tozeroy',
                    fillcolor='rgba(239,68,68,0.1)'
                ))
                
                # 添加参考线
                fig.add_hline(y=初始资金, line_dash="dash", line_color="#10b981", yref="y1", annotation_text="初始资金")
                fig.add_hline(y=-5, line_dash="dot", line_color="#f59e0b", yref="y2", annotation_text="-5% 警戒线")
                fig.add_hline(y=-10, line_dash="dot", line_color="#ef4444", yref="y2", annotation_text="-10% 风险线")
                
                # 双轴布局
                fig.update_layout(
                    height=450,
                    title="净值 vs 动态回撤",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    xaxis=dict(
                        title="日期",
                        tickformat="%Y-%m",
                        tickangle=-45,
                        showgrid=True,
                        gridwidth=0.5,
                        gridcolor='#2a2e3a'
                    ),
                    yaxis=dict(
                        title="资产净值 (美元)",
                        tickformat="$,.0f",
                        showgrid=True,
                        gridwidth=0.5,
                        gridcolor='#2a2e3a',
                        side="left"
                    ),
                    yaxis2=dict(
                        title="动态回撤 (%)",
                        tickformat=".1f",
                        showgrid=False,
                        side="right",
                        overlaying="y",
                        ticksuffix="%"
                    ),
                    margin=dict(l=60, r=60, t=60, b=80)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # ========== 回撤分析图表 ==========
                st.markdown("### 📉 回撤分析")
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    # 回撤分布直方图
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=动态回撤.values,
                        nbinsx=20,
                        marker_color='#ef4444',
                        opacity=0.7
                    ))
                    fig_hist.update_layout(
                        height=300,
                        title="回撤分布",
                        paper_bgcolor="#0a0c10",
                        plot_bgcolor="#15171a",
                        font_color="#e6e6e6",
                        xaxis_title="回撤 (%)",
                        yaxis_title="频次"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col_right:
                    # 回撤持续期
                    回撤持续期数据 = []
                    持续期 = 0
                    for val in 动态回撤.values:
                        if val < -5:
                            持续期 += 1
                        else:
                            if 持续期 > 0:
                                回撤持续期数据.append(持续期)
                            持续期 = 0
                    
                    if 回撤持续期数据:
                        fig_duration = go.Figure()
                        fig_duration.add_trace(go.Bar(
                            x=list(range(1, len(回撤持续期数据)+1)),
                            y=回撤持续期数据,
                            marker_color='#f59e0b'
                        ))
                        fig_duration.update_layout(
                            height=300,
                            title="回撤持续期（>5%）",
                            paper_bgcolor="#0a0c10",
                            plot_bgcolor="#15171a",
                            font_color="#e6e6e6",
                            xaxis_title="回撤次数",
                            yaxis_title="持续天数"
                        )
                        st.plotly_chart(fig_duration, use_container_width=True)
                    else:
                        st.info("无超过5%的回撤")
                
                # ========== 回测数据表 ==========
                with st.expander("📋 详细回测数据"):
                    回测数据 = pd.DataFrame({
                        "日期": 净值.index,
                        "资产净值": 净值.values,
                        "动态回撤": 动态回撤.values,
                        "日收益率": 净值.pct_change().fillna(0).values * 100
                    })
                    回测数据["资产净值"] = 回测数据["资产净值"].apply(lambda x: f"${x:,.0f}")
                    回测数据["动态回撤"] = 回测数据["动态回撤"].apply(lambda x: f"{x:.2f}%")
                    回测数据["日收益率"] = 回测数据["日收益率"].apply(lambda x: f"{x:+.2f}%")
                    st.dataframe(回测数据.tail(30), use_container_width=True)
                
                # 下载功能
                csv = 回测数据.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 下载回测数据 (CSV)",
                    data=csv,
                    file_name=f"回测数据_{品种}_{开始日期}_{结束日期}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
