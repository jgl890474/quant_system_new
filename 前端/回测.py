# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def 显示():
    st.markdown("### 📈 策略回测系统")
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD", "GC=F"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1wk", "1mo"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=365))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                代码 = 品种
                
                # 显示调试信息
                st.info(f"正在获取数据: {代码}, 周期: {周期}, 范围: {开始日期} 至 {结束日期}")
                
                # 下载数据 - 使用更稳定的参数
                数据 = yf.download(
                    代码, 
                    start=开始日期, 
                    end=结束日期, 
                    interval=周期, 
                    progress=False,
                    auto_adjust=False,
                    threads=1
                )
                
                # 检查数据
                if 数据 is None or 数据.empty:
                    st.error(f"无法获取数据: {代码}")
                    st.info("建议：\n1. 尝试选择 AAPL 测试\n2. 尝试缩短日期范围\n3. 检查网络连接")
                    return
                
                # 获取收盘价（兼容不同版本）
                if 'Close' in 数据.columns:
                    收盘价 = 数据['Close']
                elif 'Adj Close' in 数据.columns:
                    收盘价 = 数据['Adj Close']
                else:
                    st.error("没有价格数据")
                    return
                
                # 转换为简单列表
                价格列表 = []
                for idx, val in 收盘价.items():
                    try:
                        # 尝试多种转换方式
                        if hasattr(val, 'values'):
                            val = val.values[0] if len(val.values) > 0 else val
                        if hasattr(val, 'item'):
                            val = val.item()
                        价格列表.append(float(val))
                    except Exception as e:
                        st.warning(f"跳过无效数据: {e}")
                        continue
                
                if len(价格列表) < 2:
                    st.error(f"有效数据不足，仅获取到 {len(价格列表)} 个数据点")
                    st.info("请尝试：\n1. 选择更长的日期范围\n2. 选择 AAPL 测试\n3. 检查数据源")
                    return
                
                # 计算收益率
                收盘价_开始 = 价格列表[0]
                收盘价_结束 = 价格列表[-1]
                总收益率 = (收盘价_结束 - 收盘价_开始) / 收盘价_开始
                最终资金 = 初始资金 * (1 + 总收益率)
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(价格列表)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终资金", f"${最终资金:,.0f}")
                col_d.metric("数据量", f"{len(价格列表)}")
                
                # 净值曲线
                fig = go.Figure()
                净值 = [初始资金 * (1 + 总收益率 * i / max(len(价格列表), 1)) for i in range(len(价格列表))]
                fig.add_trace(go.Scatter(
                    x=数据.index[:len(价格列表)], 
                    y=净值, 
                    mode='lines', 
                    name='净值',
                    line=dict(color='#00d2ff', width=2),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig.update_layout(
                    height=350,
                    title="净值曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="资产 (美元)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 价格走势
                with st.expander("📊 价格走势"):
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=数据.index[:len(价格列表)],
                        y=价格列表,
                        mode='lines',
                        name='收盘价',
                        line=dict(color='#ffaa00', width=2)
                    ))
                    fig2.update_layout(
                        height=300,
                        title=f"{品种} 价格走势",
                        paper_bgcolor="#0a0c10",
                        plot_bgcolor="#15171a",
                        font_color="#e6e6e6"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
                st.info("请尝试选择 AAPL 并缩短日期范围进行测试")
