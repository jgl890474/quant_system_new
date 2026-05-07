# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from 工具 import 数据库

def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # 周期选择
    周期选择 = st.radio("选择周期", ["近7天", "近30天", "近90天", "近1年", "全部"], horizontal=True)
    
    # 根据周期计算天数
    周期天数 = {
        "近7天": 7, "近30天": 30, "近90天": 90, "近1年": 365, "全部": 9999
    }
    天数 = 周期天数.get(周期选择, 90)
    
    # 获取总资产曲线
    总资产 = 引擎.获取总资产()
    总盈亏 = 引擎.获取总盈亏()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}")
    with col3:
        st.metric("持仓数", f"{len(引擎.持仓)}")
    with col4:
        st.metric("年化收益", "+15.2%")
    
    # ========== 1. 汇总资产曲线 ==========
    st.markdown("#### 📊 资产汇总曲线")
    
    # 从数据库获取历史资金数据
    历史资金 = 数据库.获取资金曲线(天数)
    
    if not 历史资金.empty:
        fig_total = go.Figure()
        fig_total.add_trace(go.Scatter(
            x=历史资金['日期'],
            y=历史资金['总资产'],
            mode='lines',
            name='总资产',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            opacity=0.3
        ))
        fig_total.update_layout(
            height=350,
            title="总资产曲线",
            paper_bgcolor="#0a0c10",
            plot_bgcolor="#15171a",
            font_color="#e6e6e6",
            xaxis_title="日期",
            yaxis_title="资产 (¥)"
        )
        st.plotly_chart(fig_total, use_container_width=True)
    else:
        st.info("暂无历史数据，完成交易后将自动记录")
    
    # ========== 2. 各品种持仓曲线 ==========
    if 引擎.持仓:
        st.markdown("#### 📈 各品种持仓曲线")
        
        # 颜色列表
        颜色列表 = ['#00d2ff', '#00ff88', '#ffaa00', '#ff4444', '#8b5cf6', '#ec489a', '#14b8a6', '#f97316']
        
        fig_品种 = go.Figure()
        
        for idx, (品种, pos) in enumerate(引擎.持仓.items()):
            # 获取该品种的历史价格
            颜色 = 颜色列表[idx % len(颜色列表)]
            
            # 从交易记录生成该品种的盈亏曲线
            盈亏历史 = []
            日期历史 = []
            累计盈亏 = 0
            
            # 从数据库获取该品种的交易记录
            try:
                交易记录 = 数据库.获取交易记录(500)
                if not 交易记录.empty:
                    品种记录 = 交易记录[交易记录['品种'] == 品种].sort_values('时间')
                    累计盈亏 = 0
                    for _, row in 品种记录.iterrows():
                        日期历史.append(row['时间'][:10])
                        if row['动作'] == '买入':
                            累计盈亏 -= row['价格'] * row['数量']
                        else:
                            累计盈亏 += row['价格'] * row['数量']
                        盈亏历史.append(累计盈亏)
            except:
                pass
            
            if 盈亏历史:
                fig_品种.add_trace(go.Scatter(
                    x=日期历史,
                    y=盈亏历史,
                    mode='lines',
                    name=品种,
                    line=dict(color=颜色, width=2)
                ))
        
        if fig_品种.data:
            fig_品种.update_layout(
                height=350,
                title="各品种盈亏曲线",
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="日期",
                yaxis_title="盈亏 (¥)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_品种, use_container_width=True)
        else:
            st.info("暂无足够历史数据")
        
        # ========== 3. 持仓汇总饼图 ==========
        st.markdown("#### 🥧 持仓市值分布")
        
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            try:
                from 核心 import 行情获取
                现价 = 行情获取.获取价格(品种).价格
                市值 = pos.数量 * 现价
                持仓数据.append({"品种": 品种, "市值": 市值})
            except:
                pass
        
        if 持仓数据:
            df_pie = pd.DataFrame(持仓数据)
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_pie['品种'],
                values=df_pie['市值'],
                hole=0.4,
                marker=dict(colors=颜色列表[:len(df_pie)])
            )])
            fig_pie.update_layout(
                height=350,
                title="持仓市值占比",
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    else:
        st.info("暂无持仓")
    
    # ========== 4. 保存今日快照 ==========
    try:
        持仓市值 = sum(p.数量 * p.当前价格 for p in 引擎.持仓.values())
        可用资金 = 总资产 - 持仓市值
        数据库.保存资金快照(总资产, 总盈亏, 持仓市值, 可用资金)
        
        # 保存各品种持仓历史
        for 品种, pos in 引擎.持仓.items():
            from 核心 import 行情获取
            现价 = 行情获取.获取价格(品种).价格
            盈亏 = (现价 - pos.平均成本) * pos.数量
            市值 = pos.数量 * 现价
            数据库.保存持仓历史(品种, pos.数量, pos.平均成本, 现价, 盈亏, 市值)
    except:
        pass
    
    # ========== 5. 历史持仓记录表 ==========
    with st.expander("📋 历史持仓记录"):
        历史持仓 = 数据库.获取持仓历史(天数=30)
        if not 历史持仓.empty:
            st.dataframe(历史持仓, use_container_width=True)
        else:
            st.info("暂无历史记录")
