"""
量化交易系统 - 完整版
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import random

st.set_page_config(page_title="量化交易系统", layout="wide")

# ==================== 数据获取 ====================
def 获取股票数据():
    """获取模拟股票数据"""
    return pd.DataFrame({
        "代码": ["000001", "000858", "600519", "300750", "002415"],
        "名称": ["平安银行", "五粮液", "贵州茅台", "宁德时代", "海康威视"],
        "最新价": [11.56, 135.20, 1450.00, 205.50, 32.80],
        "涨跌幅": [random.uniform(-3, 5) for _ in range(5)],
        "量比": [random.uniform(0.5, 2.5) for _ in range(5)],
    })

def 获取加密货币数据():
    """获取加密货币数据"""
    return pd.DataFrame({
        "代码": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"],
        "名称": ["比特币", "以太坊", "币安币", "Solana"],
        "最新价": [65000, 3200, 580, 150],
        "涨跌幅": [random.uniform(-3, 8) for _ in range(4)],
        "量比": [1.0, 1.0, 1.0, 1.0],
    })

# ==================== AI选股 ====================
def AI选股(df):
    if df.empty:
        return []
    df = df.copy()
    df['评分'] = df['涨跌幅'] * 2 + df['量比'] * 1.5
    df = df.sort_values('评分', ascending=False).head(3)
    理由库 = ["今日涨幅强势，量比放大", "技术形态走好", "量价配合良好"]
    结果 = []
    for i, (_, row) in enumerate(df.iterrows()):
        结果.append({
            "code": row['代码'],
            "name": row['名称'],
            "reason": 理由库[i % len(理由库)],
            "score": round(row['评分'], 1)
        })
    return 结果

# ==================== AI交易引擎 ====================
class AI交易引擎:
    def __init__(self):
        self.持仓 = {}
        self.现金 = 100000
        self.交易记录 = []
        self.运行中 = False
    
    def 买入(self, 代码, 名称, 价格):
        数量 = int(self.现金 * 0.8 /价格)
        if 数量 == 0:
            return
        self.现金 -= 数量 *价格
        self.持仓[代码] = {"名称": 名称, "数量": 数量, "买入价":价格}
        self.交易记录.append({"时间": datetime.now().strftime("%H:%M:%S"), "动作": "买入", "代码": 代码, "名称": 名称, "价格":价格, "数量": 数量})
    
    def 卖出(self, 代码, 价格):
        if 代码 not in self.持仓:
            return
        持仓 = self.持仓[代码]
        self.现金 += 持仓["数量"] *价格
        del self.持仓[代码]
        self.交易记录.append({"时间": datetime.now().strftime("%H:%M:%S"), "动作": "卖出", "代码": 代码, "名称": 持仓["名称"], "价格":价格})
    
    def AI交易(self, df):
        推荐 = AI选股(df)
        if 推荐:
            best = 推荐[0]
            if best['code'] not in self.持仓:
                self.买入(best['code'], best['name'], best.get('price', 100))
            return best
        return None

# ==================== 界面 ====================
st.title("🚀 量化交易系统")
st.caption("多策略 · 多类目 · AI智能交易")

# 导航
nav_items = ["首页", "AI选股", "AI交易", "持仓", "关于"]
cols = st.columns(len(nav_items))
for col, name in zip(cols, nav_items):
    with col:
        if st.button(name, use_container_width=True):
            st.session_state.页面 = name
            st.rerun()

if '页面' not in st.session_state:
    st.session_state.页面 = "首页"
if '引擎' not in st.session_state:
    st.session_state.引擎 = AI交易引擎()

# ==================== 首页 ====================
if st.session_state.页面 == "首页":
    st.info("🤖 AI智能交易系统")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("支持类目", "股票/加密货币")
    with col2:
        st.metric("策略数量", "6个")
    with col3:
        st.metric("状态", "🟢 就绪")

# ==================== AI选股 ====================
elif st.session_state.页面 == "AI选股":
    st.subheader("🤖 AI智能选股")
    
    类目 = st.selectbox("选择类目", ["股票", "加密货币"])
    
    if st.button("🔍 AI选股", type="primary"):
        with st.spinner("分析中..."):
            if 类目 == "股票":
                df = 获取股票数据()
            else:
                df = 获取加密货币数据()
            
            结果 = AI选股(df)
            if 结果:
                st.session_state.选股结果 = 结果
                st.success(f"推荐 {len(结果)} 只")
            else:
                st.warning("无推荐")
    
    if '选股结果' in st.session_state:
        for r in st.session_state.选股结果:
            st.markdown(f"""
            <div style="background:#262730; border-radius:10px; padding:12px; margin-bottom:10px; border-left:4px solid #00ff88;">
                <b>{r['name']}</b> ({r['code']})<br>
                💡 {r['reason']}<br>
                ⭐ 评分: {r['score']}
            </div>
            """, unsafe_allow_html=True)

# ==================== AI交易 ====================
elif st.session_state.页面 == "AI交易":
    st.subheader("🤖 AI自动交易")
    
    engine = st.session_state.引擎
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 启动AI交易", use_container_width=True):
            engine.运行中 = True
            st.success("AI交易已启动")
    with col2:
        if st.button("⏸️ 停止AI交易", use_container_width=True):
            engine.运行中 = False
            st.warning("AI交易已停止")
    
    if st.button("🔄 手动执行一轮", use_container_width=True):
        类目 = st.selectbox("选择类目", ["股票", "加密货币"], key="trade_cat")
        if 类目 == "股票":
            df = 获取股票数据()
        else:
            df = 获取加密货币数据()
        
        result = engine.AI交易(df)
        if result:
            st.success(f"决策: 买入 {result['name']}({result['code']}) | 评分: {result['score']}")
        else:
            st.info("无交易信号")
    
    # 状态
    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("现金", f"{engine.现金:,.0f}")
    with col_b:
        st.metric("持仓", len(engine.持仓))
    with col_c:
        st.metric("交易次数", len(engine.交易记录))
    
    if engine.持仓:
        st.subheader("当前持仓")
        df = pd.DataFrame([{"代码": k, "名称": v['名称'], "数量": v['数量'], "成本": v['买入价']} for k, v in engine.持仓.items()])
        st.dataframe(df, use_container_width=True)

# ==================== 持仓 ====================
elif st.session_state.页面 == "持仓":
    st.subheader("💰 当前持仓")
    engine = st.session_state.引擎
    if engine.持仓:
        df = pd.DataFrame([{"代码": k, "名称": v['名称'], "数量": v['数量'], "成本": v['买入价']} for k, v in engine.持仓.items()])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无持仓")
    
    if engine.交易记录:
        st.subheader("📝 交易记录")
        st.dataframe(pd.DataFrame(engine.交易记录[-10:]), use_container_width=True)

# ==================== 关于 ====================
elif st.session_state.页面 == "关于":
    st.subheader("📖 系统说明")
    st.markdown("""
    ### 量化交易系统 v4.0
    
    **功能：**
    - AI智能选股
    - AI自动交易
    - 多类目支持（股票/加密货币）
    """)

st.markdown("---")
st.caption("量化交易系统 v4.0 | 全自动AI交易")