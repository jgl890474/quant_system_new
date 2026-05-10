# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 工具.数据库 import 获取交易记录


def 显示():
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
        col1, col2, col3 = st.columns(3)
        
        # 买入卖出统计
        买入次数 = len(df[df["动作"] == "买入"]) if "动作" in df.columns else 0
        卖出次数 = len(df[df["动作"] == "卖出"]) if "动作" in df.columns else 0
        
        # 总盈亏
        if "盈亏" in df.columns:
            总盈亏 = df["盈亏"].sum()
            盈利次数 = len(df[df["盈亏"] > 0]) if "盈亏" in df.columns else 0
            亏损次数 = len(df[df["盈亏"] < 0]) if "盈亏" in df.columns else 0
        else:
            总盈亏 = 0
            盈利次数 = 0
            亏损次数 = 0
        
        col1.metric("总交易次数", len(df))
        col2.metric("买入/卖出", f"{买入次数} / {卖出次数}")
        col3.metric("总盈亏", f"¥{总盈亏:,.2f}", 
                    delta=f"盈利{盈利次数}次 / 亏损{亏损次数}次" if 盈利次数 + 亏损次数 > 0 else None)
        
        # 盈亏分布图
        if "盈亏" in df.columns and len(df[df["盈亏"] != 0]) > 0:
            st.subheader("📊 盈亏分布")
            
            # 筛选出有盈亏的交易（卖出）
            盈亏数据 = df[df["盈亏"] != 0].copy()
            if not 盈亏数据.empty:
                # 按时间排序
                盈亏数据 = 盈亏数据.sort_values("时间")
                盈亏数据["累计盈亏"] = 盈亏数据["盈亏"].cumsum()
                
                tab1, tab2 = st.tabs(["盈亏柱状图", "累计盈亏曲线"])
                
                with tab1:
                    st.bar_chart(盈亏数据.set_index("时间")["盈亏"])
                
                with tab2:
                    st.line_chart(盈亏数据.set_index("时间")["累计盈亏"])
        
    except Exception as e:
        st.error(f"加载交易记录失败: {e}")
        st.info("请确保数据库已正确初始化")
