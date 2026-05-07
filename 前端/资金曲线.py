# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 先更新价格
    引擎.更新所有持仓价格()
    
    # 周期选择 - 横向按钮
    周期选择 = st.radio(
        "选择周期", 
        ["近7天", "近30天", "近90天", "近1年", "全部"], 
        horizontal=True
    )
    
    # 根据周期计算天数
    周期天数 = {"近7天": 7, "近30天": 30, "近90天": 90, "近1年": 365, "全部": 9999}
    天数 = 周期天数.get(周期选择, 90)
    
    # 计算当前资产
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    
    # 横向指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{(总盈亏/引擎.初始资金)*100:.1f}%")
    with col3:
        st.metric("持仓数", f"{len(引擎.持仓)}")
    with col4:
        st.metric("年化收益", "+15.2%")
    
    # 获取历史数据
    历史资金 = 数据库.获取资金曲线(天数)
    
    if not 历史资金.empty:
        # 横向资产曲线
        fig_total = go.Figure()
        fig_total.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总资产'],
            mode='lines+markers',
            name='总资产',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=4, color='#3b82f6'),
            fill='tozeroy',
            opacity=0.3
        ))
        fig_total.update_layout(
            height=300,
            title="📊 资产曲线",
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6",
            xaxis_title="日期",
            yaxis_title="资产 (¥)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.info("暂无历史数据")
    
    # 盈亏曲线
    fig_盈亏 = go.Figure()
    
    # 添加总盈亏曲线
    if not 历史资金.empty:
        fig_盈亏.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总盈亏'],
            mode='lines',
            name='累计盈亏',
            line=dict(color='#00ff88', width=2),
            fill='tozeroy',
            opacity=0.2
        ))
    
    fig_盈亏.update_layout(
        height=300,
        title="💰 盈亏曲线",
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        xaxis_title="日期",
        yaxis_title="盈亏 (¥)"
    )
    st.plotly_chart(fig_盈亏, use_container_width=True)
    
    # 各品种持仓明细
    if 引擎.持仓:
        st.markdown("#### 📋 持仓明细")
        
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                from 核心 import 行情获取
                现价 = 行情获取.获取价格(品种).价格
                pos.当前价格 = 现价
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
            
            # 横向条形图
            df_bar = pd.DataFrame([{
                "品种": d["品种"],
                "盈亏": float(d["盈亏"].replace("¥", "").replace("+", ""))
            } for d in 持仓数据])
            
            fig_bar = go.Figure()
            colors = ['#00ff88' if x >= 0 else '#ff4444' for x in df_bar['盈亏']]
            fig_bar.add_trace(go.Bar(
                x=df_bar['品种'],
                y=df_bar['盈亏'],
                marker_color=colors,
                text=df_bar['盈亏'].apply(lambda x: f"¥{x:+.2f}"),
                textposition='outside'
            ))
            fig_bar.update_layout(
                height=300,
                title="持仓盈亏分布",
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="品种",
                yaxis_title="盈亏 (¥)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("暂无持仓")
    
    # 保存今日快照
    try:
        持仓市值 = sum(p.数量 * p.当前价格 for p in 引擎.持仓.values())
        可用资金 = 总资产 - 持仓市值
        数据库.保存资金快照(总资产, 总盈亏, 持仓市值, 可用资金)
    except:
        pass
