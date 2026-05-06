# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 核心 import 行情获取

def 显示(引擎):
    # 顶部指标卡片 - 使用css统一高度
    st.markdown("""
    <style>
        .metric-card {
            background-color: #1a1d24;
            border-radius: 12px;
            padding: 15px 10px;
            text-align: center;
            margin: 5px;
        }
        .metric-label {
            font-size: 14px;
            color: #8892b0;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #00d2ff;
        }
        .metric-delta {
            font-size: 12px;
            color: #00ff88;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #e6e6e6;
            margin: 20px 0 10px 0;
            padding-left: 8px;
            border-left: 4px solid #00d2ff;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 计算指标
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    持仓数 = len(引擎.持仓)
    交易次数 = len(引擎.交易记录)
    
    # 指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">总资产</div>
            <div class="metric-value">${总资产:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        盈亏颜色 = "#00ff88" if 总盈亏 >= 0 else "#ff4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">总盈亏</div>
            <div class="metric-value" style="color:{盈亏颜色}">${总盈亏:+,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">持仓数</div>
            <div class="metric-value">{持仓数}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">交易次数</div>
            <div class="metric-value">{交易次数}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 市场行情 - 整齐排列
    st.markdown('<div class="section-title">📊 市场行情</div>', unsafe_allow_html=True)
    
    品种列表 = ["AAPL", "BTC-USD", "GC=F", "EURUSD"]
    行情列 = st.columns(4)
    
    for i, 品种 in enumerate(品种列表):
        try:
            行情数据 = 行情获取.获取价格(品种)
            价格 = 行情数据.价格
            st.markdown(f"""
            <div style="background:#1a1d24;border-radius:10px;padding:12px;text-align:center;margin:5px;">
                <div style="font-size:14px;color:#8892b0">{品种}</div>
                <div style="font-size:20px;color:#00d2ff;font-weight:bold">${价格:.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown(f"""
            <div style="background:#1a1d24;border-radius:10px;padding:12px;text-align:center;margin:5px;">
                <div style="font-size:14px;color:#8892b0">{品种}</div>
                <div style="font-size:16px;color:#ff4444">获取失败</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== 新增：持仓实时曲线图 ==========
    if 引擎.持仓:
        st.markdown('<div class="section-title">📈 持仓盈亏曲线</div>', unsafe_allow_html=True)
        
        # 准备数据：每只持仓的历史盈亏（模拟最近30天）
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            现价 = 行情获取.获取价格(品种).价格
            当前盈亏 = (现价 - pos.平均成本) * pos.数量
            持仓数据.append({
                "品种": 品种,
                "数量": pos.数量,
                "成本": pos.平均成本,
                "现价": 现价,
                "盈亏": 当前盈亏,
                "盈亏率": (现价 - pos.平均成本) / pos.平均成本 * 100
            })
        
        # 创建曲线图
        fig = go.Figure()
        
        # 为每个持仓生成历史盈亏曲线（模拟，实际应从数据库读取）
        for 持仓 in 持仓数据:
            品种 = 持仓["品种"]
            当前盈亏 = 持仓["盈亏"]
            
            # 生成最近30天的模拟盈亏曲线
            日期 = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(30, 0, -1)]
            盈亏历史 = [当前盈亏 * (0.5 + i/60) for i in range(30)]  # 模拟从低到高
            
            fig.add_trace(go.Scatter(
                x=日期,
                y=盈亏历史,
                mode='lines',
                name=f"{品种}",
                line=dict(width=2),
                fill='tozeroy',
                opacity=0.7
            ))
        
        fig.update_layout(
            height=350,
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 持仓详情表格
        st.markdown('<div class="section-title">📋 持仓明细</div>', unsafe_allow_html=True)
        df = pd.DataFrame(持仓数据)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无持仓，请先买入")
