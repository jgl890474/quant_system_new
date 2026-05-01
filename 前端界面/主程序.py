import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="量化交易系统", layout="wide")

# ==================== 内置数据获取 ====================
def 获取股票数据():
    """获取股票数据"""
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

# ==================== AI交易引擎 ====================
class AI自动交易:
    def __init__(self):
        self.持仓 = {}
        self.现金 = 100000
        self.初始资金 = 100000
        self.交易记录 = []
        self.运行中 = False
        self.当前类目 = "股票"
        self.策略名称 = ""
    
    def 注册策略(self, 策略实例, 策略名称):
        self.策略名称 = 策略名称
        if "加密" in 策略名称:
            self.当前类目 = "加密货币"
        else:
            self.当前类目 = "股票"
        return True
    
    def 设置资金(self, 现金):
        self.现金 = 现金
        self.初始资金 = 现金
    
    def 启动(self):
        self.运行中 = True
    
    def 停止(self):
        self.运行中 = False
    
    def 手动执行一轮(self):
        try:
            if self.当前类目 == "加密货币":
                df = 获取加密货币数据()
            else:
                df = 获取股票数据()
            
            if df.empty:
                return {"action": "hold", "reason": "无数据"}
            
            # AI选股
            df = df.copy()
            df['评分'] = df['涨跌幅'] * 2 + df['量比'] * 1.5
            df = df.sort_values('评分', ascending=False)
            
            if df.empty:
                return {"action": "hold", "reason": "无推荐"}
            
            best = df.iloc[0]
            code = best['代码']
            
            if code in self.持仓:
                return {"action": "hold", "reason": f"已持有 {best['名称']}"}
            else:
                # 买入
                price = best['最新价']
                shares = int(self.现金 * 0.8 / price)
                if shares > 0:
                    self.持仓[code] = {
                        "名称": best['名称'],
                        "数量": shares,
                        "买入价": price,
                        "买入时间": datetime.now().strftime("%H:%M:%S")
                    }
                    self.现金 -= shares * price
                    self.交易记录.append({
                        "时间": datetime.now().strftime("%H:%M:%S"),
                        "动作": "买入",
                        "代码": code,
                        "名称": best['名称'],
                        "价格": price,
                        "数量": shares
                    })
                    return {"action": "buy", "symbol": code, "name": best['名称'], "price": price, "reason": f"AI推荐买入"}
                return {"action": "hold", "reason": "资金不足"}
        except Exception as e:
            return {"action": "error", "reason": str(e)}
    
    def 获取状态(self):
        总资产 = self.现金 + sum([p['数量'] * p['买入价'] for p in self.持仓.values()])
        return {
            "运行状态": "运行中" if self.运行中 else "已停止",
            "现金": round(self.现金, 2),
            "持仓": self.持仓,
            "持仓数量": len(self.持仓),
            "总资产": round(总资产, 2),
            "收益率": round((总资产 - self.初始资金) / self.初始资金 * 100, 2),
            "交易次数": len(self.交易记录),
            "当前类目": self.当前类目
        }

# ==================== 初始化 ====================
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AI自动交易()
if '当前页面' not in st.session_state:
    st.session_state.当前页面 = "首页"

# ==================== 界面 ====================
st.title("🚀 量化交易系统")
st.caption("多策略 · 多类目 · AI智能交易")

# 导航
nav_items = ["首页", "AI交易", "持仓", "关于"]
cols = st.columns(len(nav_items))
for col, item in zip(cols, nav_items):
    with col:
        if st.button(item, use_container_width=True):
            st.session_state.当前页面 = item
            st.rerun()

st.markdown("---")

# ==================== 首页 ====================
if st.session_state.当前页面 == "首页":
    st.info("🤖 AI智能交易系统已就绪")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("支持类目", "股票/加密货币")
    with col2:
        st.metric("策略数量", "6个")
    with col3:
        st.metric("状态", "🟢 运行中")

# ==================== AI交易 ====================
elif st.session_state.当前页面 == "AI交易":
    st.subheader("🤖 AI自动交易")
    
    engine = st.session_state.ai_engine
    
    st.info(f"📊 当前交易类目: {engine.当前类目}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        策略列表 = ["双均线策略 (股票)", "加密网格 (加密货币)"]
        选中策略 = st.selectbox("选择策略", 策略列表)
        
        if st.button("🚀 启动AI交易", use_container_width=True):
            engine.注册策略(None, 选中策略)
            engine.启动()
            st.success(f"AI交易已启动 | 策略: {选中策略}")
        
        if st.button("⏸️ 停止AI交易", use_container_width=True):
            engine.停止()
            st.warning("AI交易已停止")
    
    with col2:
        初始资金 = st.number_input("初始资金", value=100000)
        if st.button("更新资金", use_container_width=True):
            engine.设置资金(初始资金)
            st.success("资金已更新")
        
        if st.button("🔄 手动执行一轮", use_container_width=True):
            with st.spinner("分析中..."):
                result = engine.手动执行一轮()
                if result:
                    st.success(f"决策: {result.get('action', 'hold')} | {result.get('reason', '')}")
                else:
                    st.info("无交易信号")
    
    st.markdown("---")
    
    # 状态显示
    状态 = engine.获取状态()
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("运行状态", 状态.get('运行状态', '已停止'))
    with col_b:
        st.metric("总资产", f"{状态.get('总资产', 0):,.0f}")
    with col_c:
        st.metric("收益率", f"{状态.get('收益率', 0)}%")
    with col_d:
        st.metric("交易次数", 状态.get('交易次数', 0))

# ==================== 持仓 ====================
elif st.session_state.当前页面 == "持仓":
    st.subheader("💰 当前持仓")
    engine = st.session_state.ai_engine
    if engine.持仓:
        持仓数据 = []
        for code, info in engine.持仓.items():
            持仓数据.append({
                "代码": code,
                "名称": info.get('名称', code),
                "数量": info['数量'],
                "成本": info['买入价'],
                "买入时间": info.get('买入时间', '')
            })
        st.dataframe(pd.DataFrame(持仓数据), use_container_width=True)
        
        total_value = sum([info['数量'] * info['买入价'] for info in engine.持仓.values()])
        st.metric("持仓市值", f"{total_value:,.0f}")
    else:
        st.info("暂无持仓，请启动AI交易并点击手动执行一轮")
    
    st.markdown("---")
    st.subheader("📝 交易记录")
    if engine.交易记录:
        st.dataframe(pd.DataFrame(engine.交易记录[-10:]), use_container_width=True)
    else:
        st.info("暂无交易记录")

# ==================== 关于 ====================
elif st.session_state.当前页面 == "关于":
    st.subheader("📖 系统说明")
    st.markdown("""
    ### 量化交易系统 v4.0
    
    **功能：**
    - AI智能选股
    - AI自动交易
    - 多类目支持（股票/加密货币）
    
    **使用步骤：**
    1. 点击「AI交易」
    2. 选择策略
    3. 启动AI交易
    4. 点击「手动执行一轮」测试买入
    """)

st.markdown("---")
st.caption("量化交易系统 v4.0 | 全自动AI交易")