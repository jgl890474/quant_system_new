# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 💼 当前持仓")
    
    if 引擎.持仓:
        数据 = []
        for 品种, pos in 引擎.持仓.items():
            价格 = 行情获取.获取价格(品种).价格
            pos.当前价格 = 价格
            盈亏 = pos.数量 * (价格 - pos.平均成本)
            盈亏率 = (价格 / pos.平均成本 - 1) * 100
            数据.append({
                "品种": 品种,
                "数量": f"{pos.数量:.0f}",
                "成本": f"{pos.平均成本:.2f}",
                "现价": f"{价格:.2f}",
                "盈亏": f"¥{盈亏:+,.2f}",
                "盈亏率": f"{盈亏率:+.1f}%"
            })
        st.dataframe(pd.DataFrame(数据), use_container_width=True, hide_index=True)
    else:
        st.caption("暂无持仓")
    
    # 风控状态
    with st.expander("🛡️ 风控状态"):
        if '风控引擎' in st.session_state:
            风控 = st.session_state.风控引擎
            总资金 = 引擎.获取总资产()
            状态 = 风控.获取风控状态(引擎, 总资金)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总仓位", 状态["总仓位比例"])
            col2.metric("单品种限制", 状态["单品种仓位限制"])
            col3.metric("止损/止盈", f"{状态['止损线']} / {状态['止盈线']}")
            col4.metric("今日盈亏", f"¥{风控.今日盈亏:+,.2f}")
