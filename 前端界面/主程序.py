import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="量化交易系统", layout="wide")

# ==================== 内置数据获取（不依赖外部模块） ====================
def 获取股票数据():
    return pd.DataFrame({
        "代码": ["000001", "000858", "600519", "300750", "002415"],
        "名称": ["平安银行", "五粮液", "贵州茅台", "宁德时代", "海康威视"],
        "最新价": [11.56, 135.20, 1450.00, 205.50, 32.80],
        "涨跌幅": [random.uniform(-3, 5) for _ in range(5)],
        "量比": [random.uniform(0.5, 2.5) for _ in range(5)],
    })

def 获取加密货币数据():
    return pd.DataFrame({
        "代码": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"],
        "名称": ["比特币", "以太坊", "币安币", "Solana"],
        "最新价": [65000, 3200, 580, 150],
        "涨跌幅": [random.uniform(-5, 8) for _ in range(4)],
        "量比": [random.uniform(0.8, 2) for _ in range(4)],
    })

数据源映射 = {
    "股票": 获取股票数据,
    "加密货币": 获取加密货币数据,
}

# ==================== 风控参数 ====================
风控参数 = {
    "股票": {"止盈": 0.05, "止损": 0.03, "单只仓位": 0.3},
    "加密货币": {"止盈": 0.08, "止损": 0.05, "单只仓位": 0.2},
}

# ==================== AI交易引擎 ====================
class AI交易引擎:
    def __init__(self):
        self.持仓 = {}
        self.现金 = 100000
        self.初始资金 = 100000
        self.交易记录 = []
        self.运行中 = False
        self.当前类目 = "股票"
        self.策略名称 = ""
        self.止盈 = 0.05
        self.止损 = 0.03
    
    def 注册策略(self, 策略实例, 策略名称):
        self.策略名称 = 策略名称
        if "加密" in 策略名称:
            self.当前类目 = "加密货币"
            参数 = 风控参数.get("加密货币", {"止盈": 0.08, "止损": 0.05})
        else:
            self.当前类目 = "股票"
            参数 = 风控参数.get("股票", {"止盈": 0.05, "止损": 0.03})
        self.止盈 = 参数["止盈"]
        self.止损 = 参数["止损"]
        return True
    
    def 设置资金(self, 现金):
        self.现金 = 现金
        self.初始资金 = 现金
    
    def 启动(self):
        self.运行中 = True
    
    def 停止(self):
        self.运行中 = False
    
    def 选股(self, df):
        if df.empty:
            return None
        df = df.copy()
        df['评分'] = df['涨跌幅'] * 2 + df['量比'] * 1.5
        df = df.sort_values('评分', ascending=False)
        if df.empty:
            return None
        return df.iloc[0]
    
    def 执行买入(self, 股票):
        code =股票['代码']
        name =股票['名称']
        price =股票['最新价']
        参数 = 风控参数.get(self.当前类目, {"单只仓位": 0.3})
        shares = int(self.现金 * 参数["单只仓位"] / price)
        if shares == 0:
            return False
        self.持仓[code] = {
            "名称": name, "数量": shares, "买入价": price,
            "买入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.现金 -= shares * price
        self.交易记录.append({
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "动作": "买入",
            "代码": code, "名称": name, "价格": price, "数量": shares
        })
        return True
    
    def 执行一轮(self):
        try:
            df = 数据源映射[self.当前类目]()
            if df.empty:
                return {"action": "hold", "reason": "无数据"}
            
            # 风控检查
            for code in list(self.持仓.keys()):
                row = df[df['代码'] == code]
                if not row.empty:
                    当前价 = row.iloc[0]['最新价']
                    买入价 = self.持仓[code]['买入价']
                    盈亏 = (当前价 - 买入价) / 买入价
                    if 盈亏 >= self.止盈:
                        self.现金 += self.持仓[code]['数量'] * 当前价
                        del self.持仓[code]
                        return {"action": "sell", "reason": f"止盈卖出，盈利{盈亏:.2%}"}
                    elif 盈亏 <= -self.止损:
                        self.现金 += self.持仓[code]['数量'] * 当前价
                        del self.持仓[code]
                        return {"action": "sell", "reason": f"止损卖出，亏损{盈亏:.2%}"}
            
            # AI选股
            best = self.选股(df)
            if best is None:
                return {"action": "hold", "reason": "无推荐"}
            
            code = best['代码']
            if code in self.持仓:
                return {"action": "hold", "reason": f"已持有 {best['名称']}"}
            
            self.执行买入(best)
            return {"action": "buy", "name": best['名称'], "price": best['最新价'], "reason": f"AI推荐，评分{best['评分']:.1f}"}
        except Exception as e:
            return {"action": "error", "reason": str(e)}
    
    def 获取状态(self):
        总资产 = self.现金 + sum([p['数量'] * p['买入价'] for p in self.持仓.values()])
        return {
            "运行状态": "运行中" if self.运行中 else "已停止",
            "当前类目": self.当前类目,
            "止盈": f"{self.止盈*100}%",
            "止损": f"{self.止损*100}%",
            "现金": round(self.现金, 2),
            "持仓": self.持仓,
            "持仓数量": len(self.持仓),
            "总资产": round(总资产, 2),
            "收益率": round((总资产 - self.初始资金) / self.初始资金 * 100, 2),
            "交易次数": len(self.交易记录)
        }

# ==================== 初始化 ====================
if '引擎' not in st.session_state:
    st.session_state.引擎 = AI交易引擎()
if '当前页面' not in st.session_state:
    st.session_state.当前页面 = "首页"

# ==================== 界面 ====================
st.title("🚀 量化交易系统 v5.0")
st.caption("多类目 · 多策略 · AI自动交易")

# 导航
nav_items = ["首页", "AI选股", "AI交易", "持仓", "关于"]
cols = st.columns(len(nav_items))
for col, name in zip(cols, nav_items):
    with col:
        if st.button(name, use_container_width=True):
            st.session_state.当前页面 = name
            st.rerun()

st.markdown("---")

# ==================== 首页 ====================
if st.session_state.当前页面 == "首页":
    st.info("🤖 量化交易系统 v5.0 已就绪")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("支持类目", "股票/加密货币")
    with col2:
        st.metric("策略数量", "4个")
    with col3:
        st.metric("状态", "🟢 运行中")
    with col4:
        st.metric("资金", f"{st.session_state.引擎.现金:,.0f}")

# ==================== AI选股 ====================
elif st.session_state.当前页面 == "AI选股":
    st.subheader("🤖 AI智能选股")
    类目 = st.selectbox("选择类目", ["股票", "加密货币"])
    if st.button("🔍 开始选股", type="primary"):
        with st.spinner("AI分析中..."):
            df = 数据源映射[类目]()
            df['评分'] = df['涨跌幅'] * 2 + df['量比'] * 1.5
            df = df.sort_values('评分', ascending=False).head(3)
            st.session_state.选股结果 = df.to_dict('records')
            st.success(f"推荐 {len(df)} 只")
    if '选股结果' in st.session_state:
        for r in st.session_state.选股结果:
            st.markdown(f"""
            <div style="background:#262730; border-radius:10px; padding:12px; margin-bottom:10px; border-left:4px solid #00ff88;">
                <b>{r['名称']}</b> ({r['代码']})<br>
                📈 涨幅: {r['涨跌幅']:.2f}% | 量比: {r['量比']:.2f}<br>
                ⭐ AI评分: {r['评分']:.1f}
            </div>
            """, unsafe_allow_html=True)

# ==================== AI交易 ====================
elif st.session_state.当前页面 == "AI交易":
    st.subheader("🤖 AI自动交易")
    engine = st.session_state.引擎
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📊 当前类目: {engine.当前类目} | 止盈: {engine.止盈*100}% | 止损: {engine.止损*100}%")
        策略列表 = ["双均线策略 (股票)", "加密网格 (加密货币)"]
        选中策略 = st.selectbox("选择策略", 策略列表)
        if st.button("🚀 启动AI交易", use_container_width=True):
            engine.注册策略(None, 选中策略)
            engine.启动()
            st.success(f"AI交易已启动")
        if st.button("⏸️ 停止AI交易", use_container_width=True):
            engine.停止()
            st.warning("AI交易已停止")
    with col2:
        初始资金 = st.number_input("初始资金", value=100000)
        if st.button("更新资金", use_container_width=True):
            engine.设置资金(初始资金)
            st.success("资金已更新")
        if st.button("🔄 执行一轮", use_container_width=True):
            with st.spinner("分析中..."):
                result = engine.执行一轮()
                if result:
                    st.success(f"决策: {result.get('action')} | {result.get('reason', '')}")
                else:
                    st.info("无交易信号")
    
    st.markdown("---")
    状态 = engine.获取状态()
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    with col_a:
        st.metric("运行状态", 状态.get('运行状态'))
    with col_b:
        st.metric("总资产", f"{状态.get('总资产', 0):,.0f}")
    with col_c:
        st.metric("收益率", f"{状态.get('收益率', 0)}%")
    with col_d:
        st.metric("交易次数", 状态.get('交易次数', 0))
    with col_e:
        st.metric("持仓数", 状态.get('持仓数量', 0))

# ==================== 持仓 ====================
elif st.session_state.当前页面 == "持仓":
    st.subheader("💰 当前持仓")
    engine = st.session_state.引擎
    if engine.持仓:
        df = pd.DataFrame([{
            "代码": k, "名称": v['名称'], "数量": v['数量'], "成本": v['买入价'],
            "市值": v['数量'] * v['买入价'], "买入时间": v.get('买入时间', '')
        } for k, v in engine.持仓.items()])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无持仓")
    
    st.markdown("---")
    st.subheader("📝 交易记录")
    if engine.交易记录:
        st.dataframe(pd.DataFrame(engine.交易记录[-20:]), use_container_width=True)
    else:
        st.info("暂无交易记录")

# ==================== 关于 ====================
elif st.session_state.当前页面 == "关于":
    st.subheader("📖 系统说明")
    st.markdown("""
    ### 量化交易系统 v5.0
    
    **功能：**
    - 🤖 AI智能选股
    - 🤖 AI自动交易
    - 📊 实时持仓监控
    - 🛡️ 自动止盈止损
    
    **支持类目：**
    | 类目 | 止盈 | 止损 |
    |------|------|------|
    | 股票 | 5% | 3% |
    | 加密货币 | 8% | 5% |
    
    **使用步骤：**
    1. 点击「AI交易」选择策略
    2. 点击「启动AI交易」
    3. 点击「执行一轮」测试买入
    """)

st.markdown("---")
st.caption("量化交易系统 v5.0")