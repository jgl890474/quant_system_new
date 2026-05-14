# -*- coding: utf-8 -*-
"""
图表增强组件 - K线图买卖点标注
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def 绘制带买卖点的K线图(df, 品种, 周期, 买入点列表=None, 卖出点列表=None):
    """
    绘制带买卖点标注的K线图
    
    参数:
        df: K线数据DataFrame，包含 日期、开盘、最高、最低、收盘、成交量
        品种: 品种代码
        周期: K线周期（日线/周线/60分钟等）
        买入点列表: [{'日期': date, '价格': price, '策略': '策略名'}, ...]
        卖出点列表: [{'日期': date, '价格': price, '策略': '策略名'}, ...]
    """
    
    dates = df['日期'].tolist()
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.55, 0.2, 0.25],
        subplot_titles=(f'{品种} - {周期} K线图', '成交量', 'MACD')
    )
    
    # ===== 第一行：K线图 =====
    fig.add_trace(go.Candlestick(
        x=dates,
        open=df['开盘'],
        high=df['最高'],
        low=df['最低'],
        close=df['收盘'],
        name='K线',
        showlegend=False
    ), row=1, col=1)
    
    # 均线
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['MA5'],
            mode='lines', name='MA5',
            line=dict(color='#FF6B6B', width=1.5)
        ), row=1, col=1)
    
    if 'MA10' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['MA10'],
            mode='lines', name='MA10',
            line=dict(color='#4ECDC4', width=1.5)
        ), row=1, col=1)
    
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['MA20'],
            mode='lines', name='MA20',
            line=dict(color='#FFE66D', width=1.5)
        ), row=1, col=1)
    
    # 布林带
    if 'BB_Upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['BB_Upper'],
            mode='lines', name='布林上轨',
            line=dict(color='#95A5A6', width=1, dash='dash')
        ), row=1, col=1)
    
    if 'BB_Lower' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['BB_Lower'],
            mode='lines', name='布林下轨',
            line=dict(color='#95A5A6', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(149,165,166,0.1)'
        ), row=1, col=1)
    
    # ===== 买入标注（绿色向上箭头） =====
    if 买入点列表:
        for b in 买入点列表:
            fig.add_annotation(
                x=b['日期'], y=b['价格'],
                text=f"🟢 买入 {b.get('策略', '')}",
                showarrow=True, arrowhead=2, arrowcolor="#2ECC71",
                ax=0, ay=-35,
                font=dict(color="#2ECC71", size=10),
                bgcolor="rgba(0,0,0,0.6)", borderpad=3
            )
            # 添加虚线辅助线
            fig.add_hline(
                y=b['价格'], line_dash="dot", 
                line_color="#2ECC71", opacity=0.3, 
                row=1, col=1
            )
    
    # ===== 卖出标注（红色向下箭头） =====
    if 卖出点列表:
        for s in 卖出点列表:
            fig.add_annotation(
                x=s['日期'], y=s['价格'],
                text=f"🔴 卖出 {s.get('策略', '')}",
                showarrow=True, arrowhead=2, arrowcolor="#E74C3C",
                ax=0, ay=35,
                font=dict(color="#E74C3C", size=10),
                bgcolor="rgba(0,0,0,0.6)", borderpad=3
            )
            # 添加虚线辅助线
            fig.add_hline(
                y=s['价格'], line_dash="dot", 
                line_color="#E74C3C", opacity=0.3, 
                row=1, col=1
            )
    
    # ===== 第二行：成交量 =====
    成交量颜色 = ['#2ECC71' if c >= o else '#E74C3C' 
                  for c, o in zip(df['收盘'], df['开盘'])]
    
    fig.add_trace(go.Bar(
        x=dates, y=df['成交量'],
        name='成交量', marker_color=成交量颜色,
        opacity=0.5, showlegend=False
    ), row=2, col=1)
    
    # ===== 第三行：MACD =====
    if 'MACD_Histogram' in df.columns:
        macd_colors = ['#2ECC71' if x >= 0 else '#E74C3C' 
                       for x in df['MACD_Histogram']]
        
        fig.add_trace(go.Bar(
            x=dates, y=df['MACD_Histogram'],
            name='MACD柱', marker_color=macd_colors,
            opacity=0.5, showlegend=False
        ), row=3, col=1)
    
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['MACD'],
            mode='lines', name='MACD',
            line=dict(color='#3498DB', width=1.5)
        ), row=3, col=1)
    
    if 'MACD_Signal' in df.columns:
        fig.add_trace(go.Scatter(
            x=dates, y=df['MACD_Signal'],
            mode='lines', name='信号线',
            line=dict(color='#E74C3C', width=1.5)
        ), row=3, col=1)
    
    # MACD零线
    fig.add_hline(y=0, line_dash="dash", line_color="#95A5A6", row=3, col=1)
    
    # ===== 布局设置 =====
    fig.update_layout(
        title=f"{品种} - 技术分析图表",
        height=750,
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            orientation='h', 
            yanchor='bottom', 
            y=1.02, 
            xanchor='center', 
            x=0.5
        ),
        plot_bgcolor='#0a0c10',
        paper_bgcolor='#0a0c10',
        font_color='#e6e6e6'
    )
    
    # 坐标轴样式
    fig.update_xaxes(title_text="日期", row=3, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="价格", row=1, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="成交量", row=2, col=1, gridcolor='#2a2e3a')
    fig.update_yaxes(title_text="MACD", row=3, col=1, gridcolor='#2a2e3a')
    
    return fig
