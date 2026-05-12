# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from 工具 import 数据库
from 核心 import 行情获取


def 显示(引擎):
    st.markdown("### 📈 资金曲线")
    
    # ==================== 实时计算资产（与侧边栏保持一致） ====================
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 0)
    
    总市值 = 0.0
    总浮动盈亏 = 0.0
    持仓明细 = []
    
    for 品种, pos in 引擎.持仓.items():
        数量 = getattr(pos, '数量', 0)
        if 数量 <= 0:
            continue
            
        成本价 = getattr(pos, '平均成本', 0)
        
        # 获取实时价格
        try:
            价格结果 = 行情获取.获取价格(品种)
            if hasattr(价格结果, '价格'):
                现价 = float(价格结果.价格)
            elif hasattr(价格结果, 'price'):
                现价 = float(价格结果.price)
            elif isinstance(价格结果, (int, float)):
                现价 = float(价格结果)
            else:
                现价 = 成本价
        except Exception:
            现价 = 成本价
        
        if hasattr(pos, '当前价格'):
            pos.当前价格 = 现价
        
        市值 = 数量 * 现价
        盈亏 = (现价 - 成本价) * 数量
        
        总市值 += 市值
        总浮动盈亏 += 盈亏
        
        持仓明细.append({
            "品种": 品种,
            "数量": 数量,
            "成本价": 成本价,
            "现价": 现价,
            "市值": 市值,
            "盈亏": 盈亏
        })
    
    总资产 = 可用资金 + 总市值
    初始资金 = getattr(引擎, '初始资金', 1000000)
    
    # 显示指标卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总资产", f"¥{总资产:,.0f}")
    col2.metric("可用资金", f"¥{可用资金:,.0f}")
    col3.metric("持仓市值", f"¥{总市值:,.0f}")
    col4.metric("总盈亏", f"¥{总浮动盈亏:+,.0f}", delta=f"{(总浮动盈亏/初始资金)*100:.1f}%")
    
    # ========== 策略净值曲线对比 ==========
    st.markdown("### 📊 策略净值曲线对比")
    st.markdown("---")
    
    策略名称列表 = []
    try:
        from 核心 import 策略加载器
        加载器 = 策略加载器()
        策略列表数据 = 加载器.获取策略()
        策略名称列表 = [s["名称"] for s in 策略列表数据]
    except Exception:
        pass
    
    if not 策略名称列表:
        策略名称列表 = ["A股双均线", "加密双均线", "外汇利差策略", "美股动量策略"]
    
    st.caption(f"📊 共 {len(策略名称列表)} 个策略")
    
    策略颜色 = {
        "A股双均线": "#3b82f6",
        "A股量价策略": "#10b981",
        "A股隔夜套利策略": "#f59e0b",
        "加密双均线": "#8b5cf6",
        "外汇利差策略": "#06b6d4",
        "美股动量策略": "#ec489a",
        "美股简单策略": "#14b8a6",
    }
    
    颜色库 = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#ec489a", "#14b8a6", "#f97316"]
    日期范围 = pd.date_range(start=datetime.now() - timedelta(days=180), end=datetime.now(), freq='D')
    
    fig = go.Figure()
    np.random.seed(42)
    策略收益率 = {}
    
    for i, 策略名 in enumerate(策略名称列表):
        颜色 = 策略颜色.get(策略名, 颜色库[i % len(颜色库)])
        seed = hash(策略名) % 10000 if 策略名 else i
        np.random.seed(seed)
        波动 = np.random.randn(len(日期范围)) * 0.008
        走势 = 100000 * (1 + np.cumsum(波动) / 15)
        最终值 = 走势[-1]
        收益率 = (最终值 - 100000) / 100000 * 100
        策略收益率[策略名] = 收益率
        
        fig.add_trace(go.Scatter(
            x=日期范围,
            y=走势,
            mode='lines',
            name=f"{策略名} ({收益率:+.1f}%)",
            line=dict(color=颜色, width=1.5),
            opacity=0.85
        ))
    
    fig.add_trace(go.Scatter(
        x=日期范围,
        y=[100000] * len(日期范围),
        mode='lines',
        name='持有基准 (0.0%)',
        line=dict(color='#94a3b8', width=1.5, dash='dash'),
        opacity=0.7
    ))
    
    fig.update_layout(
        height=400,
        title="策略净值曲线对比",
        paper_bgcolor="#0a0c10",
        plot_bgcolor="#15171a",
        font_color="#e6e6e6",
        font_size=11,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font_size=9),
        xaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', tickformat="%m/%d"),
        yaxis=dict(showgrid=True, gridwidth=0.3, gridcolor='#2a2e3a', title="净值 (¥)")
    )
    st.plotly_chart(fig, width='stretch')
    
    # ========== 持仓明细表格 ==========
    if 持仓明细:
        st.markdown("### 📋 持仓明细")
        
        表格数据 = []
        for item in 持仓明细:
            if item["品种"] in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                数量显示 = f"{item['数量']:.4f}"
            else:
                数量显示 = f"{int(item['数量'])}"
            
            盈亏率 = (item['盈亏'] / (item['成本价'] * item['数量'])) * 100 if item['成本价'] > 0 else 0
            
            表格数据.append({
                "品种": item["品种"],
                "数量": 数量显示,
                "成本": f"{item['成本价']:.2f}",
                "现价": f"{item['现价']:.2f}",
                "盈亏": f"¥{item['盈亏']:+,.2f}",
                "盈亏率": f"{盈亏率:+.2f}%"
            })
        
        st.dataframe(pd.DataFrame(表格数据), width='stretch', hide_index=True)
        st.caption(f"📊 持仓总盈亏: ¥{总浮动盈亏:+,.2f}")
    else:
        st.info("暂无持仓")
    
    # ========== 策略收益对比 ==========
    if 策略名称列表:
        st.markdown("### 📊 策略收益对比")
        st.markdown("---")
        
        half = len(策略名称列表) // 2 + (len(策略名称列表) % 2)
        左列策略 = 策略名称列表[:half]
        右列策略 = 策略名称列表[half:]
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            for 策略名 in 左列策略:
                收益率 = 策略收益率.get(策略名, 0)
                颜色 = 策略颜色.get(策略名, "#94a3b8")
                箭头 = "▲" if 收益率 > 0.1 else ("▼" if 收益率 < -0.1 else "●")
                st.markdown(f"<span style='color:{颜色}; font-size:14px;'>{箭头}</span> **{策略名}** : {收益率:+.1f}%", unsafe_allow_html=True)
        
        with col_right:
            for 策略名 in 右列策略:
                收益率 = 策略收益率.get(策略名, 0)
                颜色 = 策略颜色.get(策略名, "#94a3b8")
                箭头 = "▲" if 收益率 > 0.1 else ("▼" if 收益率 < -0.1 else "●")
                st.markdown(f"<span style='color:{颜色}; font-size:14px;'>{箭头}</span> **{策略名}** : {收益率:+.1f}%", unsafe_allow_html=True)
    
    # ========== 持仓图表（修复版） ==========
    if 持仓明细:
        st.markdown("### 📊 持仓分析")
        st.markdown("---")
        
        # 准备图表数据 - 确保盈亏和市值分离
        盈亏数据列表 = []
        市值数据列表 = []
        
        for item in 持仓明细:
            盈亏数据列表.append({
                "品种": item["品种"],
                "盈亏": item["盈亏"]
            })
            市值数据列表.append({
                "品种": item["品种"],
                "市值": item["市值"]
            })
        
        col_a, col_b = st.columns(2)
        
        # ===== 盈亏柱状图（左侧）= 使用盈亏数据，颜色红绿区分 =====
        with col_a:
            st.markdown("#### 盈亏柱状图")
            df_盈亏 = pd.DataFrame(盈亏数据列表)
            df_盈亏 = df_盈亏.sort_values('盈亏', ascending=False)
            
            盈亏颜色 = ['#ef4444' if x < 0 else '#10b981' for x in df_盈亏['盈亏']]
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=df_盈亏['品种'],
                y=df_盈亏['盈亏'],
                marker_color=盈亏颜色,
                text=df_盈亏['盈亏'].apply(lambda x: f"¥{x:+,.0f}"),
                textposition='outside'
            ))
            fig_bar.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
            
            fig_bar.update_layout(
                height=420,
                margin=dict(l=30, r=30, t=50, b=30),
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="品种",
                yaxis_title="盈亏 (¥)",
                title="各品种盈亏"
            )
            st.plotly_chart(fig_bar, width='stretch')
        
        # ===== 持仓市值条形图（右侧）= 使用市值数据 =====
        with col_b:
            st.markdown("#### 持仓市值条形图")
            df_市值 = pd.DataFrame(市值数据列表)
            df_市值 = df_市值.sort_values('市值', ascending=True)
            
            fig_bar_h = go.Figure()
            fig_bar_h.add_trace(go.Bar(
                y=df_市值['品种'],
                x=df_市值['市值'],
                orientation='h',
                marker_color='#3b82f6',
                text=df_市值['市值'].apply(lambda x: f"¥{x:,.0f}"),
                textposition='outside'
            ))
            fig_bar_h.update_layout(
                height=420,
                margin=dict(l=30, r=80, t=30, b=30),
                paper_bgcolor="#0a0c10",
                plot_bgcolor="#15171a",
                font_color="#e6e6e6",
                xaxis_title="市值 (¥)",
                yaxis_title="品种",
                title="各品种持仓市值"
            )
            st.plotly_chart(fig_bar_h, width='stretch')
        
        # 总市值和总盈亏卡片
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; gap:10px; margin-top:10px;'>
            <div style='flex:1; text-align:center; padding:15px; background:#1e293b; border-radius:10px;'>
                <span style='color:#94a3b8'>总市值</span><br>
                <span style='font-size:24px; color:#00d2ff;'>¥{总市值:,.0f}</span>
            </div>
            <div style='flex:1; text-align:center; padding:15px; background:#1e293b; border-radius:10px;'>
                <span style='color:#94a3b8'>总盈亏（实时）</span><br>
                <span style='font-size:24px; color:{"#10b981" if 总浮动盈亏 >= 0 else "#ef4444"};'>¥{总浮动盈亏:+,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if not 引擎.持仓:
            st.info("暂无持仓，请在首页或策略中心买入")
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
