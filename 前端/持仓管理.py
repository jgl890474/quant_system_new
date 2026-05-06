# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取
from 工具 import 数据库  # 新增：导入数据库模块


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理和风控状态"""
    
    st.markdown("### 💼 当前持仓")
    
    if 引擎.持仓:
        数据 = []
        for 品种, 持仓对象 in 引擎.持仓.items():
            价格 = 行情获取.获取价格(品种).价格
            持仓对象.当前价格 = 价格
            盈亏 = 持仓对象.数量 * (价格 - 持仓对象.平均成本)
            数据.append({
                "品种": 品种,
                "数量": f"{持仓对象.数量:.4f}",
                "成本": f"{持仓对象.平均成本:.4f}",
                "现价": f"{价格:.4f}",
                "盈亏": f"${盈亏:+,.2f}"
            })
        st.dataframe(pd.DataFrame(数据), use_container_width=True, hide_index=True)
        
        # 新增：保存持仓快照到数据库
        数据库.保存持仓快照(引擎.持仓, 引擎.获取总资产())
        
    else:
        st.info("暂无持仓")
    
    st.markdown("### 📜 交易记录")
    if 引擎.交易记录:
        df = pd.DataFrame(引擎.交易记录[-10:])
        df['时间'] = df['时间'].dt.strftime('%H:%M:%S')
        st.dataframe(df, use_container_width=True)
    
    # 新增：从数据库加载历史交易记录按钮
    with st.expander("📁 查看数据库历史记录"):
        if st.button("加载数据库交易记录"):
            历史记录 = 数据库.获取交易记录(50)
            if not 历史记录.empty:
                st.dataframe(历史记录, use_container_width=True)
            else:
                st.info("数据库暂无交易记录")
    
    # ========== 风控状态显示 ==========
    st.markdown("### 🛡️ 风控状态")
    if '风控引擎' in st.session_state:
        风控 = st.session_state.风控引擎
        总资金 = 引擎.获取总资产()
        状态 = 风控.获取风控状态(引擎, 总资金)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总仓位", 状态["总仓位比例"], delta=f"限制 {状态['最大总仓位限制']}")
        col2.metric("单品种限制", 状态["单品种仓位限制"], delta="最大资金比例")
        col3.metric("止损/止盈", f"{状态['止损线']} / {状态['止盈线']}")
        col4.metric("今日盈亏", f"${风控.今日盈亏:+,.2f}", delta=f"上限 {状态['每日亏损上限']}")
        
        if st.button("🛡️ 立即执行风控平仓"):
            平仓记录 = 风控.执行风控平仓(引擎)
            if 平仓记录:
                st.warning(f"已自动平仓 {len(平仓记录)} 个品种")
                for 记录 in 平仓记录:
                    st.write(f"- {记录['品种']}: {记录['原因']}, 盈亏 {记录['盈亏']:+.2f}")
            else:
                st.info("没有触发风控的持仓")
    else:
        st.info("风控引擎未初始化")
