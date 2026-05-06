# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取

def 显示(引擎):
    st.markdown("### 💼 当前持仓")
    if 引擎.持仓:
        数据 = []
        for 品种, 持仓对象 in 引擎.持仓.items():
            价格 = 行情获取.获取价格(品种).价格
            持仓对象.当前价格 = 价格
            盈亏 = 持仓对象.数量 * (价格 - 持仓对象.平均成本)
            数据.append({"品种": 品种, "数量": f"{持仓对象.数量:.4f}", "成本": f"{持仓对象.平均成本:.4f}", "现价": f"{价格:.4f}", "盈亏": f"${盈亏:+,.2f}"})
        st.dataframe(pd.DataFrame(数据), use_container_width=True, hide_index=True)
    else:
        st.info("暂无持仓")
    
    st.markdown("### 📜 交易记录")
    if 引擎.交易记录:
        df = pd.DataFrame(引擎.交易记录[-10:])
        df['时间'] = df['时间'].dt.strftime('%H:%M:%S')
        st.dataframe(df, use_container_width=True)
