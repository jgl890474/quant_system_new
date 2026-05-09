# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 工具 import 数据库

def 显示():
    st.markdown("### 📜 交易记录")

    df = 数据库.获取交易记录(200)

    if df.empty:
        st.info("暂无交易记录")
        return

    # ✅ 确保有数据才处理
    if "时间" not in df.columns:
        st.info("交易记录表结构异常")
        return

    # ✅ 安全处理时间格式
    try:
        df["交易时间"] = pd.to_datetime(df["时间"], errors='coerce').dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        df["交易时间"] = df["时间"].astype(str)

    # 填补空值
    df["盈亏"] = df["盈亏"].fillna(0)
    df["价格"] = df["价格"].fillna(0)
    df["数量"] = df["数量"].fillna(0)

    # 计算盈亏率（仅卖出）
    df["盈亏率"] = df.apply(
        lambda row: f"{row['盈亏'] / (row['价格'] * row['数量'] + 0.01) * 100:.2f}%"
        if row["动作"] == "卖出" and row["价格"] > 0 and row["数量"] > 0 else "",
        axis=1
    )

    # 手续费暂为0（可预留）
    df["手续费"] = 0

    # 选择显示列（使用安全列名）
    show_columns = ["id", "交易时间", "品种", "动作", "数量", "价格", "手续费", "盈亏", "盈亏率", "策略名称"]
    
    # 只保留存在的列
    show_columns = [col for col in show_columns if col in df.columns]

    display_df = df[show_columns].rename(columns={
        "id": "交易ID",
        "动作": "交易类型",
        "价格": "成交价格",
        "盈亏": "盈亏金额",
        "策略名称": "策略来源"
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 导出 CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 导出交易记录 CSV",
        data=csv,
        file_name="交易记录.csv",
        mime="text/csv"
    )
