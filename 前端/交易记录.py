# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from 工具.数据库 import 获取交易记录, 获取连接, 清空所有持仓, 数据库


def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    """显示交易记录页面（带筛选功能）"""
    st.subheader("📋 交易记录")
    
    # ========== 数据维护工具 ==========
    with st.expander("🛠️ 数据维护工具"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ 清空所有交易记录", width="stretch", type="secondary"):
                try:
                    conn = 获取连接()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM 交易记录")
                    cursor.execute("DELETE FROM 持仓快照")
                    conn.commit()
                    conn.close()
                    st.success("✅ 已清空所有交易记录和持仓")
                    st.rerun()
                except Exception as e:
                    st.error(f"清空失败: {e}")
        
        with col2:
            if st.button("🗑️ 删除异常记录（盈亏 > 10万）", width="stretch", type="secondary"):
                try:
                    conn = 获取连接()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM 交易记录 WHERE ABS(盈亏) > 100000 OR 盈亏 IS NULL")
                    删除数量 = cursor.rowcount
                    conn.commit()
                    conn.close()
                    st.success(f"✅ 已删除 {删除数量} 条异常记录")
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {e}")
        
        with col3:
            if st.button("🔧 修复时间格式", width="stretch", type="secondary"):
                try:
                    conn = 获取连接()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM 交易记录 WHERE 时间 IS NULL OR 时间 = ''")
                    删除数量 = cursor.rowcount
                    conn.commit()
                    conn.close()
                    st.success(f"✅ 已修复 {删除数量} 条时间异常记录")
                    st.rerun()
                except Exception as e:
                    st.error(f"修复失败: {e}")
    
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
        
        # ========== 清理和验证数据 ==========
        # 删除品种为空或空白的记录
        df = df[df["品种"].notna()]
        df = df[df["品种"].astype(str).str.strip() != ""]
        
        # 删除盈亏为空的记录（卖出时必须有盈亏）
        df = df[df["盈亏"].notna()]
        
        # 删除时间为空的记录
        df = df[df["时间"].notna()]
        df = df[df["时间"].astype(str).str.strip() != ""]
        
        # 修复时间格式
        try:
            df["时间_解析"] = pd.to_datetime(df["时间"], errors='coerce')
            df = df.dropna(subset=["时间_解析"])
            df["时间_显示"] = df["时间_解析"].dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            st.warning(f"时间解析警告: {e}")
            if "时间" in df.columns:
                df["时间_显示"] = df["时间"].astype(str)
            else:
                df["时间_显示"] = "未知"
        
        if df.empty:
            st.info("暂无有效交易记录")
            return
        
        # 确保策略名称列存在
        if "策略名称" not in df.columns:
            df["策略名称"] = ""
        
        # 填充空的策略名称
        df["策略名称"] = df["策略名称"].fillna("手动")
        
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
            策略列表 = ["全部"] + sorted(df["策略名称"].unique().tolist())
            筛选策略 = st.selectbox("按策略筛选", 策略列表)
        
        with col4:
            if st.button("🔄 重置筛选", width="stretch"):
                st.rerun()
        
        # ========== 应用筛选 ==========
        df_filtered = df.copy()
        
        if 筛选品种 != "全部":
            df_filtered = df_filtered[df_filtered["品种"] == 筛选品种]
        
        if 筛选动作 != "全部":
            df_filtered = df_filtered[df_filtered["动作"] == 筛选动作]
        
        if 筛选策略 != "全部":
            df_filtered = df_filtered[df_filtered["策略名称"] == 筛选策略]
        
        # 显示筛选结果统计
        st.caption(f"共 {len(df_filtered)} 条记录（共 {len(df)} 条）")
        
        if df_filtered.empty:
            st.info("没有符合筛选条件的记录")
            return
        
        # 准备显示用的数据框
        df_display = df_filtered.copy()
        df_display["时间"] = df_display["时间_显示"] if "时间_显示" in df_display.columns else df_display["时间"].astype(str)
        
        # 格式化显示
        df_display["价格显示"] = df_display["价格"].apply(lambda x: f"¥{x:.2f}")
        df_display["数量显示"] = df_display["数量"].apply(lambda x: f"{x:.4f}")
        df_display["盈亏显示"] = df_display["盈亏"].apply(lambda x: f"¥{x:+.2f}" if pd.notna(x) else "-")
        
        # ========== 显示表格 ==========
        st.markdown("### 📋 交易明细")
        st.dataframe(
            df_display[["时间", "品种", "动作", "价格显示", "数量显示", "盈亏显示", "策略名称"]], 
            width="stretch", 
            hide_index=True,
            column_config={
                "时间": st.column_config.TextColumn("时间", width="medium"),
                "品种": st.column_config.TextColumn("品种", width="small"),
                "动作": st.column_config.TextColumn("动作", width="small"),
                "价格显示": st.column_config.TextColumn("价格", width="small"),
                "数量显示": st.column_config.TextColumn("数量", width="small"),
                "盈亏显示": st.column_config.TextColumn("盈亏", width="small"),
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
        
        # 过滤异常盈亏
        if not 卖出记录.empty:
            卖出记录 = 卖出记录[卖出记录["盈亏"].between(-100000, 100000)]
        
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
                
                # 显示异常警告
                if abs(总盈亏) > 1000000:
                    st.warning(f"⚠️ 总盈亏异常（{总盈亏:,.2f}），可能存在错误数据")
        else:
            col3.metric("总盈亏", "¥0.00")
            col4.metric("盈利/亏损次数", "0 / 0")
            st.info("暂无有效卖出记录，无法统计盈亏")
        
        # ========== 按策略统计 ==========
        st.markdown("---")
        st.markdown("### 📊 按策略统计")
        
        if "策略名称" in df_filtered.columns and not 卖出记录.empty:
            try:
                # 修复：只选择盈亏列进行统计
                策略统计 = 卖出记录.groupby("策略名称")["盈亏"].agg(["sum", "count", "mean"]).round(2)
                策略统计.columns = ["总盈亏", "交易次数", "平均盈亏"]
                策略统计 = 策略统计.sort_values("总盈亏", ascending=False)
                
                st.dataframe(
                    策略统计,
                    width="stretch",
                    column_config={
                        "总盈亏": st.column_config.NumberColumn("总盈亏", format="¥%.2f"),
                        "交易次数": st.column_config.NumberColumn("交易次数"),
                        "平均盈亏": st.column_config.NumberColumn("平均盈亏", format="¥%.2f"),
                    }
                )
            except Exception as e:
                st.warning(f"策略统计失败: {e}")
        
        st.markdown("---")
        
        # ==================== 盈亏分布 ====================
        if not 卖出记录.empty and "时间_解析" in 卖出记录.columns:
            st.subheader("📊 盈亏分布")
            
            盈亏数据 = 卖出记录.sort_values("时间_解析")
            盈亏数据["累计盈亏"] = 盈亏数据["盈亏"].cumsum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 单笔盈亏柱状图")
                
                fig_bar = go.Figure()
                
                盈利数据 = 盈亏数据[盈亏数据["盈亏"] > 0]
                if not 盈利数据.empty:
                    fig_bar.add_trace(go.Bar(
                        x=盈利数据["时间_显示"] if "时间_显示" in 盈利数据.columns else 盈利数据.index,
                        y=盈利数据["盈亏"],
                        name="盈利",
                        marker_color='#2ECC71',
                        text=盈利数据["盈亏"].apply(lambda x: f"¥{x:,.0f}"),
                        textposition='outside'
                    ))
                
                亏损数据 = 盈亏数据[盈亏数据["盈亏"] < 0]
                if not 亏损数据.empty:
                    fig_bar.add_trace(go.Bar(
                        x=亏损数据["时间_显示"] if "时间_显示" in 亏损数据.columns else 亏损数据.index,
                        y=亏损数据["盈亏"],
                        name="亏损",
                        marker_color='#E74C3C',
                        text=亏损数据["盈亏"].apply(lambda x: f"¥{x:,.0f}"),
                        textposition='outside'
                    ))
                
                fig_bar.update_layout(
                    title="单笔交易盈亏",
                    xaxis_title="交易时间",
                    yaxis_title="盈亏金额 (¥)",
                    height=400,
                    hovermode='x unified',
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_bar, width="stretch")
            
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
                st.plotly_chart(fig_pie, width="stretch")
            
            st.markdown("---")
            
            # 累计盈亏曲线
            st.subheader("📈 累计盈亏曲线")
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=盈亏数据["时间_解析"],
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
            st.plotly_chart(fig_line, width="stretch")
            
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
                    胜率计算 = len(盈利数据) / (len(盈利数据) + len(亏损数据)) * 100
                    盈亏比 = abs(盈利总额 / 亏损总额) if 亏损总额 > 0 else 999
                    st.metric("胜率", f"{胜率计算:.1f}%")
                    st.metric("盈亏比", f"{盈亏比:.2f}")
                    st.metric("总交易次数", f"{len(盈利数据) + len(亏损数据)}")
        
        elif "盈亏" in df_filtered.columns and len(df_filtered[df_filtered["盈亏"] != 0]) == 0:
            st.info("暂无盈亏数据（只有买入记录，没有卖出记录）")
        
        # ========== 底部提示 ==========
        st.markdown("---")
        st.caption("💡 提示：盈亏只在卖出时计算，买入时显示为0")
        
    except Exception as e:
        st.error(f"加载交易记录失败: {e}")
        import traceback
        with st.expander("详细错误信息"):
            st.code(traceback.format_exc())
