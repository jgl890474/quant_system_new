# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from 核心 import 行情获取

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 💼 当前持仓")
    
    if 引擎.持仓:
        数据 = []
        for 品种, pos in 引擎.持仓.items():
            价格 = 行情获取.获取价格(品种).价格
            盈亏 = (价格 - pos.平均成本) * pos.数量
            数据.append({
                "品种": 品种, "数量": f"{pos.数量:.0f}",
                "成本": f"{pos.平均成本:.2f}", "现价": f"{价格:.2f}",
                "盈亏": f"${盈亏:+.2f}", "盈亏率": f"{(价格/pos.平均成本-1)*100:+.1f}%"
            })
        st.dataframe(pd.DataFrame(数据), use_container_width=True)
        
        if st.button("🗑️ 批量平仓", use_container_width=True):
            for 品种 in list(引擎.持仓.keys()):
                价格 = 行情获取.获取价格(品种).价格
                引擎.卖出(品种, 价格)
            st.rerun()
        
        # 饼图
        df_pie = pd.DataFrame([{
            "品种": d["品种"],
            "市值": float(d["现价"]) * float(d["数量"])
        } for d in 数据])
        if not df_pie.empty:
            fig = go.Figure(data=[go.Pie(labels=df_pie['品种'], values=df_pie['市值'], hole=0.4)])
            fig.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无持仓")
