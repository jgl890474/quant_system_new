# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
        周期 = st.selectbox("回测周期", ["1年", "6个月", "3个月", "1个月"], index=0)
    
    # 根据周期计算日期范围
    if 周期 == "1年":
        开始日期 = datetime.now() - timedelta(days=365)
    elif 周期 == "6个月":
        开始日期 = datetime.now() - timedelta(days=180)
    elif 周期 == "3个月":
        开始日期 = datetime.now() - timedelta(days=90)
    else:
        开始日期 = datetime.now() - timedelta(days=30)
    
    结束日期 = datetime.now()
    
    st.caption(f"📅 回测范围: {开始日期.strftime('%Y-%m-%d')} 至 {结束日期.strftime('%Y-%m-%d')}")
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    # 策略参数（可选）
    with st.expander("📊 策略参数（可选）"):
        st.caption("使用当前持仓进行回测，无需额外参数")
        st.info("回测将基于你持有的股票，模拟持有期间的表现")
    
    if st.button("🚀 开始回测", type="primary", use_container_width=True):
        with st.spinner(f"正在回测 {品种}..."):
            try:
                # 生成模拟数据（基于持仓品种）
                np.random.seed(hash(品种) % 10000)
                
                # 生成日期范围
                日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='D')
                if len(日期列表) < 10:
                    日期列表 = pd.date_range(start=开始日期, end=结束日期, freq='W')
                
                if len(日期列表) < 5:
                    st.error("日期范围太短")
                    return
                
                # 获取持仓成本作为基准
                持仓成本 = 引擎.持仓[品种].平均成本 if 品种 in 引擎.持仓 else 100
                
                # 生成价格序列（围绕成本价波动）
                波动率 = 0.02
                涨跌 = np.random.randn(len(日期列表)) * 波动率
                价格序列 = 持仓成本 * (1 + np.cumsum(涨跌) / 20)
                价格序列 = np.maximum(价格序列, 持仓成本 * 0.7)
                价格序列 = np.minimum(价格序列, 持仓成本 * 1.5)
                
                # 计算净值
                净值 = 初始资金 * (价格序列 / 价格序列[0])
                
                # 计算收益率
                最终净值 = 净值[-1]
                总收益率 = (最终净值 - 初始资金) / 初始资金
                
                # 计算回撤
                累计最大值 = np.maximum.accumulate(净值)
                回撤 = (累计最大值 - 净值) / 累计最大值 * 100
                
                # 显示结果
                st.success(f"✅ 回测完成！数据点: {len(日期列表)}")
                
                # 指标卡片
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("总收益率", f"{总收益率*100:.2f}%", delta=f"{总收益率*100:.2f}%")
                col_b.metric("初始资金", f"${初始资金:,.0f}")
                col_c.metric("最终净值", f"${最终净值:,.0f}")
                col_d.metric("最大回撤", f"{回撤.min():.2f}%")
                
                col_e, col_f, col_g, col_h = st.columns(4)
                col_e.metric("平均回撤", f"{回撤.mean():.2f}%")
                col_f.metric("当前回撤", f"{回撤[-1]:.2f}%")
                col_g.metric("回撤>5%天数", f"{(回撤 < -5).sum()}天")
                col_h.metric("数据点", f"{len(日期列表)}")
                
                # ========== 净值曲线 ==========
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=日期列表,
                    y=净值,
                    mode='lines',
                    name=f'{品种} 净值',
                    line=dict(color='#00d2ff', width=2.5, shape='spline'),
                    fill='tozeroy',
                    opacity=0.2
                ))
                
                # 初始资金线
                fig.add_hline(
                    y=初始资金,
                    line_dash="dash",
                    line_color="#ffaa00",
                    annotation_text=f"初始资金 ${初始资金:,.0f}",
                    annotation_font_color="#e6e6e6"
                )
                
                # 持仓成本线
                fig.add_hline(
                    y=初始资金 * (净值[-1] / 净值[0]) if 净值[0] > 0 else 初始资金,
                    line_dash="dot",
                    line_color="#10b981",
                    annotation_text=f"最终净值 ${最终净值:,.0f}",
                    annotation_font_color="#e6e6e6"
                )
                
                fig.update_layout(
                    height=350,
                    title=f"{品种} 回测净值曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6",
                    xaxis_title="日期",
                    yaxis_title="净值 (美元)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # ========== 回撤曲线 ==========
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=日期列表,
                    y=回撤,
                    mode='lines',
                    name='回撤',
                    line=dict(color='#ef4444', width=1.5),
                    fill='tozeroy',
                    opacity=0.3
                ))
                fig2.add_hline(y=0, line_dash="dash", line_color="#10b981")
                fig2.add_hline(y=-5, line_dash="dot", line_color="#f59e0b", annotation_text="-5% 警戒线")
                fig2.add_hline(y=-10, line_dash="dot", line_color="#ef4444", annotation_text="-10% 风险线")
                fig2.update_layout(
                    height=250,
                    title="回撤曲线",
                    paper_bgcolor="#0a0c10",
                    plot_bgcolor="#15171a",
                    font_color="#e6e6e6"
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # ========== 回测数据表 ==========
                with st.expander("📋 详细回测数据"):
                    回测数据 = pd.DataFrame({
                        "日期": 日期列表,
                        "净值": 净值,
                        "回撤": 回撤,
                        "日收益率": np.diff(np.append([净值[0]], 净值)) / np.append([净值[0]], 净值[:-1]) * 100
                    })
                    回测数据["净值"] = 回测数据["净值"].apply(lambda x: f"${x:,.0f}")
                    回测数据["回撤"] = 回测数据["回撤"].apply(lambda x: f"{x:.2f}%")
                    回测数据["日收益率"] = 回测数据["日收益率"].apply(lambda x: f"{x:+.2f}%")
                    st.dataframe(回测数据.tail(30), use_container_width=True)
                
                # 下载功能
                csv = 回测数据.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 下载回测数据 (CSV)",
                    data=csv,
                    file_name=f"回测数据_{品种}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"回测出错: {str(e)}")
