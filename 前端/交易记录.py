# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from 工具.数据库 import 获取交易记录


def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    """显示交易记录页面"""
    st.subheader("📋 交易记录")
    
    try:
        # 获取交易记录
        记录 = 获取交易记录(限制数量=200)
        
        if not 记录 or len(记录) == 0:
            st.info("暂无交易记录")
            return
        
        # 转换为 DataFrame
        df = pd.DataFrame(记录)
        
        # 检查 DataFrame 是否为空
        if df.empty:
            st.info("暂无交易记录")
            return
        
        # 显示表格
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "时间": st.column_config.TextColumn("时间", width="small"),
                "品种": st.column_config.TextColumn("品种", width="small"),
                "动作": st.column_config.TextColumn("动作", width="small"),
                "价格": st.column_config.NumberColumn("价格", format="%.2f"),
                "数量": st.column_config.NumberColumn("数量", format="%.0f"),
                "盈亏": st.column_config.NumberColumn("盈亏", format="%.2f"),
                "策略名称": st.column_config.TextColumn("策略名称", width="medium"),
            }
        )
        
        # 统计信息
        col1, col2, col3, col4 = st.columns(4)
        
        # 买入卖出统计
        买入次数 = len(df[df["动作"] == "买入"]) if "动作" in df.columns else 0
        卖出次数 = len(df[df["动作"] == "卖出"]) if "动作" in df.columns else 0
        
        # 总盈亏
        if "盈亏" in df.columns:
            总盈亏 = df["盈亏"].sum()
            盈利次数 = len(df[df["盈亏"] > 0])
            亏损次数 = len(df[df["盈亏"] < 0])
            最大盈利 = df["盈亏"].max() if len(df[df["盈亏"] > 0]) > 0 else 0
            最大亏损 = df["盈亏"].min() if len(df[df["盈亏"] < 0]) > 0 else 0
        else:
            总盈亏 = 0
            盈利次数 = 0
            亏损次数 = 0
            最大盈利 = 0
            最大亏损 = 0
        
        col1.metric("总交易次数", len(df))
        col2.metric("买入/卖出", f"{买入次数} / {卖出次数}")
        col3.metric("总盈亏", f"¥{总盈亏:,.2f}", 
                    delta=f"盈利{盈利次数}次 / 亏损{亏损次数}次" if 盈利次数 + 亏损次数 > 0 else None)
        col4.metric("最大单笔", f"¥{最大盈利:,.2f} / ¥{最大亏损:,.2f}")
        
        st.markdown("---")
        
        # ==================== 盈亏分布（彩色柱状图） ====================
        if "盈亏" in df.columns and len(df[df["盈亏"] != 0]) > 0:
            st.subheader("📊 盈亏分布")
            
            # 筛选出有盈亏的交易（卖出）
            盈亏数据 = df[df["盈亏"] != 0].copy()
            if not 盈亏数据.empty:
                # 按时间排序
                盈亏数据 = 盈亏数据.sort_values("时间")
                盈亏数据["累计盈亏"] = 盈亏数据["盈亏"].cumsum()
                盈亏数据["颜色"] = 盈亏数据["盈亏"].apply(lambda x: "盈利" if x > 0 else "亏损")
                
                # 创建两列布局
                col1, col2 = st.columns(2)
                
                with col1:
                    # ==================== 彩色盈亏柱状图 ====================
                    st.markdown("#### 📊 单笔盈亏柱状图")
                    
                    # 使用 Plotly 创建彩色柱状图
                    fig_bar = go.Figure()
                    
                    # 添加盈利柱（绿色）
                    盈利数据 = 盈亏数据[盈亏数据["盈亏"] > 0]
                    if not 盈利数据.empty:
                        fig_bar.add_trace(go.Bar(
                            x=盈利数据["时间"],
                            y=盈利数据["盈亏"],
                            name="盈利",
                            marker_color='#2ECC71',
                            marker_line_color='#27AE60',
                            marker_line_width=1,
                            text=盈利数据["盈亏"].apply(lambda x: f"¥{x:,.2f}"),
                            textposition='outside',
                            hovertemplate='%{x}<br>盈利: ¥%{y:,.2f}<extra></extra>'
                        ))
                    
                    # 添加亏损柱（红色）
                    亏损数据 = 盈亏数据[盈亏数据["盈亏"] < 0]
                    if not 亏损数据.empty:
                        fig_bar.add_trace(go.Bar(
                            x=亏损数据["时间"],
                            y=亏损数据["盈亏"],
                            name="亏损",
                            marker_color='#E74C3C',
                            marker_line_color='#C0392B',
                            marker_line_width=1,
                            text=亏损数据["盈亏"].apply(lambda x: f"¥{x:,.2f}"),
                            textposition='outside',
                            hovertemplate='%{x}<br>亏损: ¥%{y:,.2f}<extra></extra>'
                        ))
                    
                    fig_bar.update_layout(
                        title="单笔交易盈亏",
                        xaxis_title="交易时间",
                        yaxis_title="盈亏金额 (¥)",
                        height=400,
                        hovermode='x unified',
                        plot_bgcolor='white',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
                    )
                    fig_bar.update_xaxes(gridcolor='#E8E8E8')
                    fig_bar.update_yaxes(gridcolor='#E8E8E8', tickformat=',.0f')
                    
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # ==================== 盈亏饼图 ====================
                    st.markdown("#### 🥧 盈亏占比")
                    
                    盈利总额 = 盈利数据["盈亏"].sum() if not 盈利数据.empty else 0
                    亏损总额 = abs(亏损数据["盈亏"].sum()) if not 亏损数据.empty else 0
                    
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['盈利', '亏损'],
                        values=[盈利总额, 亏损总额],
                        marker_colors=['#2ECC71', '#E74C3C'],
                        hole=0.4,
                        textinfo='label+percent',
                        textposition='auto',
                        hovertemplate='%{label}<br>金额: ¥%{value:,.2f}<br>占比: %{percent}<extra></extra>'
                    )])
                    fig_pie.update_layout(
                        title="盈亏金额占比",
                        height=400,
                        annotations=[dict(text=f'¥{盈利总额 - 亏损总额:,.0f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                st.markdown("---")
                
                # ==================== 动态累计盈亏曲线 ====================
                st.subheader("📈 累计盈亏曲线")
                
                # 准备数据
                曲线数据 = 盈亏数据[["时间", "累计盈亏"]].copy()
                曲线数据["时间"] = pd.to_datetime(曲线数据["时间"])
                曲线数据 = 曲线数据.sort_values("时间")
                
                # 使用 Plotly 创建动态曲线
                fig_line = go.Figure()
                
                # 添加累计盈亏曲线
                fig_line.add_trace(go.Scatter(
                    x=曲线数据["时间"],
                    y=曲线数据["累计盈亏"],
                    mode='lines+markers',
                    name='累计盈亏',
                    line=dict(color='#3498DB', width=3),
                    marker=dict(
                        size=8,
                        color=曲线数据["累计盈亏"].apply(lambda x: '#2ECC71' if x >= 0 else '#E74C3C'),
                        symbol='circle',
                        line=dict(width=1, color='white')
                    ),
                    fill='tozeroy',
                    fillcolor='rgba(52,152,219,0.1)',
                    text=曲线数据["累计盈亏"].apply(lambda x: f"¥{x:,.2f}"),
                    textposition='top center',
                    hovertemplate='%{x|%Y-%m-%d %H:%M}<br>累计盈亏: ¥%{y:,.2f}<extra></extra>'
                ))
                
                # 添加零线参考线
                fig_line.add_hline(
                    y=0, 
                    line_dash="dash", 
                    line_color="#95A5A6",
                    annotation_text="盈亏平衡线",
                    annotation_position="bottom right"
                )
                
                # 添加最高点标记
                最高点 = 曲线数据["累计盈亏"].max()
                最高点位置 = 曲线数据[曲线数据["累计盈亏"] == 最高点]["时间"].iloc[0] if not 曲线数据.empty else None
                if 最高点位置:
                    fig_line.add_annotation(
                        x=最高点位置,
                        y=最高点,
                        text=f"最高点: ¥{最高点:,.2f}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#2ECC71",
                        ax=0,
                        ay=-30
                    )
                
                # 添加最低点标记
                最低点 = 曲线数据["累计盈亏"].min()
                最低点位置 = 曲线数据[曲线数据["累计盈亏"] == 最低点]["时间"].iloc[0] if not 曲线数据.empty else None
                if 最低点位置:
                    fig_line.add_annotation(
                        x=最低点位置,
                        y=最低点,
                        text=f"最低点: ¥{最低点:,.2f}",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#E74C3C",
                        ax=0,
                        ay=30
                    )
                
                fig_line.update_layout(
                    title="累计盈亏走势",
                    xaxis_title="交易时间",
                    yaxis_title="累计盈亏 (¥)",
                    height=450,
                    hovermode='x unified',
                    plot_bgcolor='white',
                    xaxis=dict(
                        tickformat='%m-%d %H:%M',
                        gridcolor='#E8E8E8'
                    ),
                    yaxis=dict(
                        gridcolor='#E8E8E8',
                        tickformat=',.0f'
                    )
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
                
                # ==================== 额外统计 ====================
                st.markdown("---")
                st.subheader("📊 交易统计详情")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📈 盈利统计**")
                    st.metric("盈利总金额", f"¥{盈利总额:,.2f}")
                    st.metric("平均盈利", f"¥{盈利总额/len(盈利数据):,.2f}" if len(盈利数据) > 0 else "¥0")
                    st.metric("最大单笔盈利", f"¥{最大盈利:,.2f}")
                
                with col2:
                    st.markdown("**📉 亏损统计**")
                    st.metric("亏损总金额", f"¥{亏损总额:,.2f}")
                    st.metric("平均亏损", f"¥{亏损总额/len(亏损数据):,.2f}" if len(亏损数据) > 0 else "¥0")
                    st.metric("最大单笔亏损", f"¥{最大亏损:,.2f}")
                
                with col3:
                    st.markdown("**⚖️ 综合指标**")
                    if len(盈利数据) + len(亏损数据) > 0:
                        胜率 = len(盈利数据) / (len(盈利数据) + len(亏损数据)) * 100
                        盈亏比 = abs(盈利总额 / 亏损总额) if 亏损总额 > 0 else float('inf')
                        st.metric("胜率", f"{胜率:.1f}%")
                        st.metric("盈亏比", f"{盈亏比:.2f}" if 盈亏比 != float('inf') else "∞")
                        st.metric("总交易次数", f"{len(盈利数据) + len(亏损数据)}")
        
        else:
            st.info("暂无盈亏数据（只有买入记录，没有卖出记录）")
        
    except Exception as e:
        st.error(f"加载交易记录失败: {e}")
        st.info("请确保数据库已正确初始化")
