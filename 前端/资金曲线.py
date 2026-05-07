# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    
    # ========== 动态从策略库获取策略列表 ==========
    st.markdown("### 📊 策略净值曲线对比")
    st.markdown("---")
    
    # 获取策略加载器
    try:
        from 核心 import 策略加载器
        加载器 = 策略加载器.策略加载器()
        策略列表 = 加载器.获取策略()
        策略名称列表 = [s["名称"] for s in 策略列表]
    except:
        # 默认策略
        策略名称列表 = ["A股双均线", "加密双均线", "外汇利差策略", "美股动量策略", "A股隔夜套利策略"]
    
    st.caption(f"📊 共加载 {len(策略名称列表)} 个策略")
    
    # 策略颜色映射（扩展颜色库）
    策略颜色 = {
        "A股双均线": "#3b82f6",
        "A股量价策略": "#10b981",
        "A股隔夜套利策略": "#f59e0b",
        "加密双均线": "#8b5cf6",
        "外汇利差策略": "#06b6d4",
        "美股动量策略": "#ec489a",
        "美股简单策略": "#14b8a6",
        "期货趋势策略": "#f97316",
        "默认": "#94a3b8"
    }
    
    # 生成日期范围
    日期范围 = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='D')
    
    fig = go.Figure()
    np.random.seed(42)
    
    # 动态添加每条策略曲线
    for i, 策略名 in enumerate(策略名称列表):
        # 获取颜色
        颜色 = 策略颜色.get(策略名, list(策略颜色.values())[i % len(策略颜色)])
        
        # 根据策略名生成不同的走势种子
        seed = hash(策略名) % 10000
        np.random.seed(seed)
        波动 = np.random.randn(len(日期范围)) * 0.008
        走势 = 100000 * (1 + np.cumsum(波动) / 15)
        
        # 计算最终收益率
        最终值 = 走势[-1]
        收益率 = (最终值 - 100000) / 100000 * 100
        
        # 添加曲线
        fig.add_trace(go.Scatter(
            x=日期范围,
            y=走势,
            mode='lines',
            name=f"{策略名} ({收益率:+.1f}%)",
            line=dict(color=颜色, width=1.5),
            opacity=0.85
        ))
    
    # 添加持有基准
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=[100000] * len(日期范围),
        mode='lines',
        name='持有基准 (0.0%)',
        line=dict(color='#94a3b8', width=1.5, dash='dash'),
        opacity=0.7
    ))
    
    fig.update_layout(
        height=400,
        title="策略净值曲线对比（线头显示收益率）",
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        font_size=11,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font_size=9),
        xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', tickformat="%m/%d"),
        yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', title="净值 (¥)")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== 策略收益对比表格 ==========
    st.markdown("### 📊 策略收益对比")
    
    对比数据 = []
    for 策略名 in 策略名称列表:
        seed = hash(策略名) % 10000
        np.random.seed(seed)
        波动 = np.random.randn(252) * 0.008
        走势 = 100000 * (1 + np.cumsum(波动) / 15)
        收益率 = (走势[-1] - 100000) / 100000 * 100
        对比数据.append({
            "策略名称": 策略名,
            "模拟收益率": f"{收益率:+.1f}%",
            "状态": "🟢 模拟"
        })
    
    对比_df = pd.DataFrame(对比数据)
    st.dataframe(对比_df, use_container_width=True, hide_index=True)
    
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
                height=250,
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
