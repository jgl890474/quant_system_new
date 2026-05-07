# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from 工具 import 数据库
from 核心 import 行情获取

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
    
    # 历史数据曲线
    历史资金 = 数据库.获取资金曲线(90)
    
    if not 历史资金.empty:
        # 资产曲线 - 细线蓝色
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总资产'],
            mode='lines',
            name='总资产',
            line=dict(color='#3b82f6', width=1),
            fill='tozeroy',
            opacity=0.15
        ))
        # 盈亏曲线 - 细线绿色
        fig.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总盈亏'],
            mode='lines',
            name='总盈亏',
            line=dict(color='#10b981', width=1),
            fill='tozeroy',
            opacity=0.15
        ))
        fig.update_layout(
            height=250,
            margin=dict(l=30, r=30, t=20, b=20),
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6",
            font_size=10,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a'),
            yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("暂无历史数据")
    
    # ========== 持仓长型看板 ==========
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
            # 表格
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
