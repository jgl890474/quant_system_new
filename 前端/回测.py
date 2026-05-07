# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示(引擎):
    st.markdown("### ⚙️ 回测参数设置")
    
    # ========== 获取持仓品种 ==========
    持仓品种列表 = list(引擎.持仓.keys())
    
    if not 持仓品种列表:
        st.warning("⚠️ 当前没有持仓，请先在首页或策略中心买入股票后再进行回测")
        st.info("回测功能会基于你持有的股票进行历史数据分析")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        # 只显示持仓中的品种
        品种 = st.selectbox("选择持仓品种", 持仓品种列表, help="只显示当前持仓的股票")
        
        # 显示持仓信息
        if 品种 in 引擎.持仓:
            pos = 引擎.持仓[品种]
            st.caption(f"📊 当前持仓: {pos.数量}股 | 成本: ¥{pos.平均成本:.2f}")
    
    with col2:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    with st.expander("📊 策略参数"):
        st.caption("参数仅供参考，不影响回测数据")
        短周期 = st.slider("短期均线", 5, 50, 10)
        长周期 = st.slider("长期均线", 20, 200, 30)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner(f"正在获取 {品种} 真实历史数据..."):
            try:
                # ========== 使用 yfinance 获取真实数据 ==========
                # 品种代码映射
                代码映射 = {
                    "AAPL": "AAPL",
                    "BTC-USD": "BTC-USD",
                    "GC=F": "GC=F", 
                    "EURUSD": "EURUSD=X",
                    "TSLA": "TSLA",
                    "NVDA": "NVDA",
                    "MSFT": "MSFT",
                    "GOOGL": "GOOGL"
                }
                
                股票代码 = 代码映射.get(品种, 品种)
                st.info(f"正在获取 {品种} ({股票代码}) 真实历史数据...")
                
                # 下载真实历史数据
                股票 = yf.Ticker(股票代码)
                历史数据 = 股票.history(start=开始日期, end=结束日期, interval="1d")
                
                if 历史数据.empty:
                    st.error(f"无法获取 {品种} 的真实历史数据")
                    st.info("请尝试选择其他品种或调整日期范围")
                    return
                
                # 提取收盘价
                价格序列 = 历史数据['Close'].values
                日期列表 = 历史数据.index
                
                if len(价格序列) < 5:
                    st.error(f"数据点不足: {len(价格序列)}")
                    return
                
                # 计算净值
                净值 = 初始资金 * (价格序列 / 价格序列[0])
                
                # 计算收益率
                最终净值 = 净值[-1]
                总收益率 = (最终净值 - 初始资金) / 初始资金
                
                # 计算动态回撤
                累计最大值 = np.maximum.accumulate(净值)
                动态回撤 = (累计最大值 - 净值) / 累计最大值 * 100
                
                # 计算回撤统计
                最大回撤 = np.min(动态回撤)
                平均回撤 = np.mean(动态回撤)
                当前回撤 = 动态回撤[-1]
                回撤持续时间 = np.sum(动态回撤 < -5)
                
                # 显示结果卡片
                st.success(f"✅ 回测完成！数据点: {len(价格序列)} (真实历史数据)")
                
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
                col8.metric("数据点", f"{len(价格序列)}")
                
                # ========== 动态回测曲线（双轴） ==========
                st.markdown("### 📈 动态回测曲线")
                
                fig = go.Figure()
                
                # 添加净值曲线（左轴）
                fig.add_trace(go.Scatter(
                    x=日期列表,
                    y=净值,
                    mode='lines',
                    name=f'{品种} 资产净值',
                    line=dict(color='#00d2ff', width=2),
                    yaxis="y1"
                ))
                
                # 添加动态回撤曲线（右轴）
                fig.add_trace(go.Scatter(
                    x=日期列表,
                    y=动态回撤,
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
                    title=f"{品种} 净值 vs 动态回撤 (真实历史数据)",
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
                
                # ========== 价格走势图 ==========
                st.markdown("### 📊 真实价格走势")
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(
                    x=日期列表,
                    y=价格序列,
                    mode='lines',
                    name=f'{品种} 收盘价',
                    line=dict(color='#f59e0b', width=1.5)
                ))
                fig_price.update_layout(
                    height=300,
                    title=f"{品种} 真实历史价格",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="价格 (美元)"
                )
                st.plotly_chart(fig_price, use_container_width=True)
                
                # ========== 回撤分析图表 ==========
                st.markdown("### 📉 回撤分析")
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    # 回撤分布直方图
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=动态回撤,
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
                    for val in 动态回撤:
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
                        "日期": 日期列表,
                        "真实价格": 价格序列,
                        "资产净值": 净值,
                        "动态回撤": 动态回撤,
                        "日收益率": np.diff(np.append([净值[0]], 净值)) / np.append([净值[0]], 净值[:-1]) * 100
                    })
                    回测数据["真实价格"] = 回测数据["真实价格"].apply(lambda x: f"${x:.2f}")
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
                
                # 数据来源说明
                st.caption(f"📊 数据来源: Yahoo Finance | 品种: {股票代码} | 真实历史K线数据")
                
            except Exception as e:
                st.error(f"获取真实数据失败: {str(e)}")
                st.info("提示：请检查网络连接或稍后重试")
