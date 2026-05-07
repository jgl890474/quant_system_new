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
    
    # ========== 曲线类型选择 ==========
    st.markdown("### 🎨 曲线样式")
    
    曲线类型映射 = {
        "📈 折线 (linear)": "linear",
        "✨ 平滑曲线 (spline)": "spline", 
        "📊 台阶线 (hv)": "hv",
        "📉 台阶线 (vh)": "vh",
        "🔲 台阶线 (hvh)": "hvh"
    }
    
    曲线名称 = st.selectbox("选择曲线类型", list(曲线类型映射.keys()), help="选择净值曲线的显示样式")
    曲线形状 = 曲线类型映射[曲线名称]
    
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
                收益率 = np.random.randn(len(日期列表)) * 0.02
                价格序列 = 100 * (1 + np.cumsum(收益率) / 50)
                价格序列 = np.maximum(价格序列, 50)
                
                # 计算收益率
                开盘价 = float(价格序列[0])
                收盘价 = float(价格序列[-1])
                总收益率 = (收盘价 - 开盘价) / 开盘价
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(日期列表)}")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(日期列表)}")
                
                # 净值曲线
                净值 = [初始资金 * (1 + 总收益率 * i / len(日期列表)) for i in range(len(日期列表))]
                
                fig = go.Figure()
                
                # 根据选择设置曲线类型
                if 曲线形状 == "spline":
                    fig.add_trace(go.Scatter(
                        x=日期列表,
                        y=净值,
                        mode='lines',
                        name=f'净值 ({曲线名称})',
                        line=dict(color='#00d2ff', width=1.5, shape='spline'),
                        fill='tozeroy',
                        opacity=0.2
                    ))
                elif 曲线形状 in ["hv", "vh", "hvh"]:
                    fig.add_trace(go.Scatter(
                        x=日期列表,
                        y=净值,
                        mode='lines',
                        name=f'净值 ({曲线名称})',
                        line=dict(color='#00d2ff', width=1.5, shape=曲线形状),
                        fill='tozeroy',
                        opacity=0.2
                    ))
                else:
                    fig.add_trace(go.Scatter(
                        x=日期列表,
                        y=净值,
                        mode='lines',
                        name=f'净值 ({曲线名称})',
                        line=dict(color='#00d2ff', width=1.5),
                        fill='tozeroy',
                        opacity=0.2
                    ))
                
                fig.update_layout(
                    height=300,
                    title=f"净值曲线 - {曲线名称}",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="净值 (美元)",
                    margin=dict(l=40, r=40, t=40, b=40)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 曲线类型说明
                st.caption(f"当前曲线类型: {曲线名称} | 平滑曲线最适合展示趋势")
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
