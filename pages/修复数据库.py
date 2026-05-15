# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="修复数据库", page_icon="🔧")

st.title("🔧 数据库修复工具")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔨 修复数据库表"):
        try:
            os.makedirs('data', exist_ok=True)
            conn = sqlite3.connect('data/trades.db')
            cursor = conn.cursor()
            
            # 创建交易记录表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS 交易记录 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                时间 TEXT,
                品种 TEXT,
                动作 TEXT,
                价格 REAL,
                数量 REAL,
                金额 REAL,
                盈亏 REAL,
                策略名称 TEXT,
                手续费 REAL DEFAULT 0,
                备注 TEXT
            )
            ''')
            
            # 创建持仓快照表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS 持仓快照 (
                品种 TEXT PRIMARY KEY,
                数量 REAL,
                平均成本 REAL,
                更新时间 TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            st.success("✅ 数据库表修复成功！")
            
        except Exception as e:
            st.error(f"修复失败: {e}")

with col2:
    if st.button("📋 查看交易记录"):
        try:
            conn = sqlite3.connect('data/trades.db')
            import pandas as pd
            df = pd.read_sql("SELECT * FROM 交易记录 ORDER BY 时间 DESC LIMIT 20", conn)
            conn.close()
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("暂无交易记录")
        except Exception as e:
            st.error(f"查询失败: {e}")

st.markdown("---")

if st.button("💰 查看当前持仓"):
    try:
        from 核心 import 订单引擎
        引擎 = 订单引擎()
        if 引擎.持仓:
            for 品种, pos in 引擎.持仓.items():
                st.metric(品种, f"{pos.数量:.4f}个", f"成本: ¥{pos.平均成本:.2f}")
        else:
            st.info("暂无持仓")
    except Exception as e:
        st.error(f"获取持仓失败: {e}")

st.markdown("---")
st.caption("💡 提示：修复后，重启系统持仓数据会保留")
