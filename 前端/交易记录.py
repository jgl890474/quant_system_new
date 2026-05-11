# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from 工具.数据库 import 获取交易记录


def 解析时间(时间字符串):
    """解析多种时间格式"""
    if pd.isna(时间字符串):
        return None
    try:
        # 尝试标准格式
        return pd.to_datetime(时间字符串, format='%Y-%m-%d %H:%M:%S')
    except:
        try:
            # 尝试 ISO 格式
            return pd.to_datetime(时间字符串, format='%Y-%m-%dT%H:%M:%S.%f')
        except:
            try:
                # 让 pandas 自动推断
                return pd.to_datetime(时间字符串)
            except:
                return None


def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    """显示交易记录页面（带筛选功能）"""
    st.subheader("📋 交易记录")
    
    try:
        # 获取交易记录
        所有记录 = 获取交易记录(限制数量=500)
        
        if not 所有记录 or len(所有记录) == 0:
            st.info("暂无交易记录")
            return
        
        # 转换为 DataFrame
        df = pd.DataFrame(所有记录)
        
        if df.empty:
            st.info("暂无交易记录")
            return
        
        # 统一时间格式
        df["时间"] = df["时间"].apply(解析时间)
        
        # 删除时间解析失败的行
        df = df.dropna(subset=["时间"])
        
        if df.empty:
            st.info("暂无有效交易记录")
            return
        
        # ========== 筛选器 ==========
        st.markdown("### 🔍 筛选条件")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            品种列表 = ["全部"] + sorted(df["品种"].unique().tolist())
            筛选品种 = st.selectbox("按品种筛选", 品种列表)
        
        with col2:
            动作列表 = ["全部"] + sorted(df["动作"].unique().tolist())
            筛选动作 = st.selectbox("按动作筛选", 动作列表)
        
        with col3:
            时间选项 = ["全部", "最近7天", "最近30天", "最近90天"]
            筛选时间 = st.selectbox("按时间筛选", 时间选项)
        
        with col4:
            if st.button("🔄 重置筛选"):
                st.rerun()
        
        # ========== 应用筛选 ==========
        df_filtered = df.copy()
        
        if 筛选品种 != "全部":
            df_filtered = df_filtered[df_filtered["品种"] == 筛选品种]
        
        if 筛选动作 != "全部":
            df_filtered = df_filtered[df_filtered["动作"] == 筛选动作]
        
        if 筛选时间 != "全部":
            now = datetime.now()
            if 筛选时间 == "最近7天":
                cutoff = now - timedelta(days=7)
            elif 筛选时间 == "最近30天":
                cutoff = now - timedelta(days=30)
            elif 筛选时间 == "最近90天":
                cutoff = now - timedelta(days=90)
            else:
                cutoff = None
            
            if cutoff:
                df_filtered = df_filtered[df_filtered["时间"] >= cutoff]
        
        # 显示筛选结果统计
        st.caption(f"共 {len(df_filtered)} 条记录（共 {len(df)} 条）")
        
        if df_filtered.empty:
            st.info("没有符合筛选条件的记录")
            return
        
        # 格式化时间显示
        df_display = df_filtered.copy()
        df_display["时间"] = df_display["时间"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # ========== 显示表格 ==========
        st.markdown("### 📋 交易明细")
        st.dataframe(
            df_display, 
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
        
        # ========== 统计信息 ==========
        st.markdown("---")
        st.markdown("### 📊 交易统计")
        
        # 统计所有记录
        总次数 = len(df_filtered)
        买入次数 = len(df_filtered[df_filtered["动作"] == "买入"]) if "动作" in df_filtered.columns else 0
        卖出次数 = len(df_filtered[df_filtered["动作"] == "卖出"]) if "动作" in df_filtered.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总交易次数", 总次数)
        col2.metric("买入/卖出", f"{买入次数} / {卖出次数}")
        
        # 盈亏统计（只统计卖出记录）
        卖出记录 = df_filtered[df_filtered["动作"] == "卖出"]
        
        if not 卖出记录.empty:
            总盈亏 = 卖出记录["盈亏"].sum()
            盈利次数 = len(卖出记录[卖出记录["盈亏"] > 0])
            亏损次数 = len(卖出记录[卖出记录["盈亏"] < 0])
            最大盈利 = 卖出记录["盈亏"].max() if 盈利次数 > 0 else 0
            最大亏损 = 卖出记录["盈亏"].min() if 亏损次数 > 0 else 0
            
            col3.metric("总盈亏", f"¥{总盈亏:+,.2f}")
            col4.metric("盈利/亏损次数", f"{盈利次数} / {亏损次数}")
            
            if 盈利次数 + 亏损次数 > 0:
                胜率 = 盈利次数 / (盈利次数 + 亏损次数) * 100
                st.metric("胜率", f"{胜率:.1f}%")
        else:
            col3.metric("总盈亏", "¥0.00")
            col4.metric("盈利/亏损次数", "0 / 0")
            st.info("暂无卖出记录，无法统计盈亏")
        
        st.markdown("---")
        
        # ==================== 盈亏分布 ====================
        if not 卖出记录.empty:
            st.subheader("📊 盈亏分布")
            
            盈亏数据 = 卖出记录.copy()
            盈亏数据 = 盈亏数据.sort_values("时间")
            盈亏数据["累计盈亏"] = 盈亏数据["盈亏"].cumsum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 单笔盈亏柱状图")
                
                fig_bar = go.Figure()
                
                盈利数据 = 盈亏数据[盈亏数据["盈亏"] > 0]
                if not 盈利数据.empty:
                    fig_bar.add_trace(go.Bar(
                        x=盈利数据["时间"].dt.strftime("%m-%d"),
                        y=盈利数据["盈亏"],
                        name="盈利",
                        marker_color='#2ECC71',
                        text=盈利数据["盈亏"].apply(lambda x: f"¥{x:,.0f}"),
                        textposition='outside'
                    ))
                
                亏损数据 = 盈亏数据[盈亏数据["盈亏"] < 0]
                if not 亏损数据.empty:
                    fig_bar.add_trace(go.Bar(
                        x=亏损数据["时间"].dt.strftime("%m-%d"),
                        y=亏损数据["盈亏"],
                        name="亏损",
                        marker_color='#E74C3C',
                        text=亏损数据["盈亏"].apply(lambda x: f"¥{x:,.0f}"),
                        textposition='outside'
                    ))
                
                fig_bar.update_layout(
                    title="单笔交易盈亏",
                    xaxis_title="交易日期",
                    yaxis_title="盈亏金额 (¥)",
                    height=400,
                    hovermode='x unified',
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("#### 盈亏占比")
                
                盈利总额 = 盈利数据["盈亏"].sum() if not 盈利数据.empty else 0
                亏损总额 = abs(亏损数据["盈亏"].sum()) if not 亏损数据.empty else 0
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['盈利', '亏损'],
                    values=[盈利总额, 亏损总额],
                    marker_colors=['#2ECC71', '#E74C3C'],
                    hole=0.4,
                    textinfo='label+percent'
                )])
                fig_pie.update_layout(title="盈亏金额占比", height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # 累计盈亏曲线
            st.subheader("📈 累计盈亏曲线")
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=盈亏数据["时间"],
                y=盈亏数据["累计盈亏"],
                mode='lines+markers',
                name='累计盈亏',
                line=dict(color='#3498DB', width=3),
                fill='tozeroy',
                fillcolor='rgba(52,152,219,0.1)'
            ))
            fig_line.add_hline(y=0, line_dash="dash", line_color="#95A5A6")
            fig_line.update_layout(
                title="累计盈亏走势",
                xaxis_title="交易时间",
                yaxis_title="累计盈亏 (¥)",
                height=450,
                hovermode='x unified',
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # 额外统计
            st.markdown("---")
            st.subheader("📊 交易统计详情")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**盈利统计**")
                st.metric("盈利总金额", f"¥{盈利总额:,.2f}")
                if len(盈利数据) > 0:
                    st.metric("平均盈利", f"¥{盈利总额/len(盈利数据):,.2f}")
                else:
                    st.metric("平均盈利", "¥0")
                st.metric("最大单笔盈利", f"¥{最大盈利:,.2f}")
            
            with col2:
                st.markdown("**亏损统计**")
                st.metric("亏损总金额", f"¥{亏损总额:,.2f}")
                if len(亏损数据) > 0:
                    st.metric("平均亏损", f"¥{亏损总额/len(亏损数据):,.2f}")
                else:
                    st.metric("平均亏损", "¥0")
                st.metric("最大单笔亏损", f"¥{最大亏损:,.2f}")
            
            with col3:
                st.markdown("**综合指标**")
                if len(盈利数据) + len(亏损数据) > 0:
                    胜率 = len(盈利数据) / (len(盈利数据) + len(亏损数据)) * 100
                    盈亏比 = abs(盈利总额 / 亏损总额) if 亏损总额 > 0 else 999
                    st.metric("胜率", f"{胜率:.1f}%")
                    st.metric("盈亏比", f"{盈亏比:.2f}")
                    st.metric("总交易次数", f"{len(盈利数据) + len(亏损数据)}")
        
        elif "盈亏" in df_filtered.columns and len(df_filtered[df_filtered["盈亏"] != 0]) == 0:
            st.info("暂无盈亏数据（只有买入记录，没有卖出记录）")
        
    except Exception as e:
        st.error(f"加载交易记录失败: {e}")
        st.info("请确保数据库已正确初始化")
