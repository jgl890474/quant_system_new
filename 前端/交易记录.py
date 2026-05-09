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

    # 格式化时间
    df["交易时间"] = pd.to_datetime(df["时间"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["交易类型"] = df["动作"]
    df["盈亏金额"] = df["盈亏"]

    # 计算盈亏率（仅卖出时有意义）
    df["盈亏率"] = df.apply(
        lambda row: f"{row['盈亏'] / (row['价格'] * row['数量'] + 0.0001) * 100:.2f}%"
        if row["动作"] == "卖出" and row["价格"] > 0 else "",
        axis=1
    )

    # ✅ 保留原始股票代码用于联动（暂不跳转）
    df["品种代码"] = df["品种"]

    # 构建显示列
    show_cols = [
        "交易ID",
        "交易时间",
        "品种",
        "交易类型",
        "数量",
        "价格",
        "盈亏金额",
        "盈亏率",
        "策略名称"
    ]

    display_df = df.rename(columns={
        "id": "交易ID",
        "时间": "交易时间",
        "动作": "交易类型",
        "价格": "成交价格",
        "盈亏": "盈亏金额",
        "策略名称": "策略来源"
    })

    # ✅ 显示主表
    st.dataframe(
        display_df[show_cols],
        use_container_width=True,
        hide_index=True
    )

    # ✅ 模拟联动（不破坏系统）
    st.markdown("#### 🔗 联动说明（暂为演示）")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📌 演示：点击查看策略联动（策略来源）"):
            st.info("正式版会跳转至策略详情页")
    with col2:
        if st.button("📌 演示：点击查看持仓联动（品种）"):
            st.info("正式版会跳转至持仓管理页")

    # 导出 CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 导出交易记录 CSV",
        data=csv,
        file_name="交易记录.csv",
        mime="text/csv"
    )
