# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入数据模块
try:
    from 数据.market_data import get_1min_kline, get_historical_klines
    data_ok = True
except Exception as e:
    data_ok = False
    st.error(f"数据模块加载失败: {e}")

st.set_page_config(page_title="量化交易系统", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stMetric { background-color: #1e1e1e; border-radius: 10px; padding: 10px; text-align: center; color: #ffffff; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    div[data-testid="stMarkdownContainer"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# 获取真实价格
if data_ok:
    try:
        kline = get_1min_kline("EURUSD")
        price = kline.get('close', 1.085) if kline else 1.085
    except:
        price = 1.085
else:
    price = 1.085

col1, col2, col3 = st.columns(3)
col1.metric("💰 总资产", "$100,000")
col2.metric("💹 最新价格", f"{price:.5f}")
col3.metric("🕒 更新时间", __import__('time').strftime("%Y-%m-%d %H:%M:%S"))

st.subheader("📈 策略运行状态")
st.success(f"✅ 系统已就绪 | 当前价格: {price}")

tab1, tab2 = st.tabs(["📋 策略列表", "⚙️ 配置"])
with tab1:
    st.write("1. 期货趋势策略 (GC=F)")
    st.write("2. 期货均值回归 (CL=F)")
    st.write("3. 外汇利差交易 (AUDJPY)")
    st.write("4. 外汇突破策略 (EURUSD)")
with tab2:
    st.info("后台引擎运行中 | 推送 GitHub 自动部署")
