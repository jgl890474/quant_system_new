# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 时间周期选择
    周期选择 = st.radio("选择周期", ["日", "月", "年"], horizontal=True)
    
    # 获取净值历史数据
    净值历史 = []
    
    # 从交易记录生成净值数据
    if 引擎.交易记录:
        # 按时间排序
        交易记录按时间 = sorted(引擎.交易记录, key=lambda x: x['时间'])
        
        # 计算每日净值
        当前净值 = 引擎.初始资金
        
        # 添加起始点
        净值历史.append({'日期':交易记录按时间[0]['时间'].date() if 交易记录按时间 else datetime.now().date(), '净值': 当前净值})
        
        for 记录 in 交易记录按时间:
            if 记录['动作'] == '买入':
                当前净值 -= 记录['价格'] * 记录['数量']
            elif 记录['动作'] == '卖出':
                当前净值 += 记录['价格'] * 记录['数量']
            净值历史.append({'日期': 记录['时间'].date(), '净值': 当前净值})
        
        # 添加当前净值
        净值历史.append({'日期': datetime.now().date(), '净值': 引擎.获取总资产()})
    else:
        # 生成演示数据
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            净值历史.append({'日期': date.date(), '净值': 引擎.初始资金 + (i - 15) * 10})
    
    # 转换为DataFrame
    df = pd.DataFrame(净值历史)
    df = df.drop_duplicates(subset=['日期'], keep='last')
    df = df.sort_values('日期')
    
    # 根据周期过滤数据（不使用resample避免错误）
    if 周期选择 == "月":
        # 按月取最后一天
        df['年月'] = df['日期'].apply(lambda x: x.strftime('%Y-%m'))
        月数据 = df.groupby('年月').last().reset_index()
        月数据['日期'] = pd.to_datetime(月数据['年月'] + '-01')
        df = 月数据
    elif 周期选择 == "年":
        # 按年取最后一天
        df['年'] = df['日期'].apply(lambda x: x.strftime('%Y'))
        年数据 = df.groupby('年').last().reset_index()
        年数据['日期'] = pd.to_datetime(年数据['年'] + '-01-01')
        df = 年数据
    
    # 创建图表
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['日期'],
        y=df['净值'],
        mode='lines+markers',
        line=dict(color='#00d2ff', width=2),
        marker=dict(size=4, color='#00d2ff'),
        fill='tozeroy',
        opacity=0.3,
        name='净资产'
    ))
    
    # 添加初始资金线
    fig.add_hline(
        y=引擎.初始资金,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"初始资金 ${引擎.初始资金:,.0f}",
        annotation_font_color="#e6e6e6"
    )
    
    fig.update_layout(
        height=400,
        title="资产变化曲线",
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        xaxis_title="日期",
        yaxis_title="资产 (美元)",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示当前资产
    col1, col2 = st.columns(2)
    col1.metric("当前资产", f"${引擎.获取总资产():,.0f}", delta=f"{(引擎.获取总资产() - 引擎.初始资金):+,.0f}")
    col2.metric("初始资产", f"${引擎.初始资金:,.0f}")
