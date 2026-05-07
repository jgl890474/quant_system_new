# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from 工具 import 数据库
from 核心 import 行情获取, 策略运行器

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 紧凑指标
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓市值 = 引擎.获取持仓市值()
    可用资金 = 引擎.获取可用资金()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总资产", f"¥{总资产:,.0f}")
    col2.metric("可用资金", f"¥{可用资金:,.0f}")
    col3.metric("持仓市值", f"¥{持仓市值:,.0f}")
    col4.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{总盈亏/引擎.初始资金*100:.1f}%")
    
    # ========== 多策略曲线叠加 ==========
    st.markdown("### 📊 策略净值曲线对比")
    
    # 定义策略颜色
    策略颜色 = {
        "双均线策略": "#00d2ff",
        "RSI策略": "#10b981", 
        "布林带策略": "#f59e0b",
        "趋势跟踪": "#8b5cf6",
        "均值回归": "#ec489a",
        "动量策略": "#14b8a6"
    }
    
    # 生成模拟的策略净值数据
    日期范围 = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='D')
    
    fig = go.Figure()
    
    # 策略1: 双均线策略 (蓝色)
    np.random.seed(42)
    净值1 = 100000 * (1 + np.cumsum(np.random.randn(len(日期范围)) * 0.005))
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=净值1,
        mode='lines',
        name='双均线策略',
        line=dict(color='#00d2ff', width=1.5),
        opacity=0.9
    ))
    
    # 策略2: RSI策略 (绿色)
    净值2 = 100000 * (1 + np.cumsum(np.random.randn(len(日期范围)) * 0.004))
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=净值2,
        mode='lines',
        name='RSI策略',
        line=dict(color='#10b981', width=1.5),
        opacity=0.9
    ))
    
    # 策略3: 布林带策略 (橙色)
    净值3 = 100000 * (1 + np.cumsum(np.random.randn(len(日期范围)) * 0.006))
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=净值3,
        mode='lines',
        name='布林带策略',
        line=dict(color='#f59e0b', width=1.5),
        opacity=0.9
    ))
    
    # 策略4: 趋势跟踪 (紫色)
    净值4 = 100000 * (1 + np.cumsum(np.random.randn(len(日期范围)) * 0.007))
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=净值4,
        mode='lines',
        name='趋势跟踪',
        line=dict(color='#8b5cf6', width=1.5),
        opacity=0.9
    ))
    
    # 策略5: 持有策略 (灰色虚线基准)
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=[100000] * len(日期范围),
        mode='lines',
        name='持有基准',
        line=dict(color='#94a3b8', width=1, dash='dash'),
        opacity=0.7
    ))
    
    fig.update_layout(
        height=350,
        title="策略净值曲线对比",
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', tickformat="%m/%d"),
        yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', title="净值 (¥)")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== 策略收益对比表格 ==========
    st.markdown("### 📊 策略收益对比")
    
    对比数据 = pd.DataFrame({
        "策略名称": ["双均线策略", "RSI策略", "布林带策略", "趋势跟踪", "持有基准"],
        "总收益率": ["+12.5%", "+8.3%", "+15.2%", "+10.1%", "+0.0%"],
        "年化收益": ["+15.8%", "+10.2%", "+19.5%", "+12.8%", "+0.0%"],
        "最大回撤": ["-8.2%", "-5.1%", "-10.3%", "-7.5%", "-0.0%"],
        "夏普比率": ["1.25", "0.98", "1.42", "1.08", "0.00"],
        "颜色": ["🔵", "🟢", "🟠", "🟣", "⚪"]
    })
    st.dataframe(对比数据, use_container_width=True, hide_index=True)
    
    # ========== 持仓明细 ==========
    if 引擎.持仓:
        st.markdown("### 📊 持仓明细")
        
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                现价 = 行情获取.获取价格(品种).价格
                盈亏 = (现价 - pos.平均成本) * pos.数量
                盈亏率 = (现价 / pos.平均成本 - 1) * 100
                持仓数据.append({
                    "品种": 品种,
                    "数量": f"{pos.数量:.0f}",
                    "成本": f"{pos.平均成本:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.1f}%"
                })
            except:
                pass
        
        if 持仓数据:
            st.dataframe(pd.DataFrame(持仓数据), use_container_width=True, hide_index=True)
            
            # 盈亏柱状图
            df_bar = pd.DataFrame([{
                "品种": d["品种"],
                "盈亏": float(d["盈亏"].replace("¥", "").replace("+", ""))
            } for d in 持仓数据])
            
            colors = ['#10b981' if x >= 0 else '#ef4444' for x in df_bar['盈亏']]
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=df_bar['品种'],
                y=df_bar['盈亏'],
                marker_color=colors,
                text=df_bar['盈亏'].apply(lambda x: f"¥{x:+.0f}"),
                textposition='outside'
            ))
            fig_bar.update_layout(
                height=200,
                margin=dict(l=30, r=30, t=20, b=20),
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="品种",
                yaxis_title="盈亏 (¥)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.caption("暂无持仓")
    
    # 策略说明
    with st.expander("📖 策略说明"):
        st.markdown("""
        - 🔵 **双均线策略**: 基于5日/20日均线金叉死叉
        - 🟢 **RSI策略**: 基于超买超卖区域反转
        - 🟠 **布林带策略**: 基于价格突破上下轨
        - 🟣 **趋势跟踪**: 基于MACD趋势确认
        - ⚪ **持有基准**: 买入并持有，作为对比基准
        """)
