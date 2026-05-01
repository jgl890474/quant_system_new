import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="量化交易系统", layout="wide")

# ==================== 数据获取 ====================
def 获取股票数据():
    return pd.DataFrame({
        "代码": ["000001", "000858", "600519", "300750", "002415", "000333", "002594"],
        "名称": ["平安银行", "五粮液", "贵州茅台", "宁德时代", "海康威视", "美的集团", "比亚迪"],
        "最新价": [11.56, 135.20, 1450.00, 205.50, 32.80, 58.30, 245.00],
        "涨跌幅": [random.uniform(-3, 5) for _ in range(7)],
        "量比": [random.uniform(0.5, 2.5) for _ in range(7)],
        "换手率": [random.uniform(0.5, 3) for _ in range(7)],
    })

def 获取加密货币数据():
    return pd.DataFrame({
        "代码": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
        "名称": ["比特币", "以太坊", "币安币", "Solana", "瑞波币"],
        "最新价": [65000, 3200, 580, 150, 0.52],
        "涨跌幅": [random.uniform(-5, 8) for _ in range(5)],
        "量比": [random.uniform(0.8, 2) for _ in range(5)],
    })

# ==================== AI决策引擎 ====================
class AI交易引擎:
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
        shares = int(self.现金 * 0.8 / price)
        if shares == 0:
            return False
        self.持仓[code] = {"名称": name, "数量": shares, "买入价": price, "买入时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.现金 -= shares * price
        self.交易记录.append({"时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "动作": "买入", "代码": code, "名称": name, "价格": price, "数量": shares})
        return True
    
    def 手动执行一轮(self):
        try:
            if self.当前类目 == "加密货币":
                df = 获取加密货币数据()
            else:
                df = 获取股票数据()
            if df.empty:
                return {"action": "hold", "reason": "无数据"}
            best = self.选股(df)
            if best is None:
                return {"action": "hold", "reason": "无推荐"}
            code = best['代码']
            if code in self.持仓:
                return {"action": "hold", "reason": f"已持有 {best['名称']}"}
            else:
                self.执行买入(best)
                return {"action": "buy", "symbol": code, "name": best['名称'], "price": best['最新价'], "reason": f"AI推荐买入，评分{best['评分']:.1f}"}
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

# ==================== 回测函数 ====================
def 双均线回测(price, 快线, 慢线, 初始资金):
    fast = pd.Series(price).rolling(window=快线).mean()
    slow = pd.Series(price).rolling(window=慢线).mean()
    signals = (fast > slow).astype(int).diff()
    cash, pos, vals = 初始资金, 0, []
    for i, p in enumerate(price):
        if signals.iloc[i] == 1 and cash > 0:
            pos = cash / p
            cash = 0
        elif signals.iloc[i] == -1 and pos > 0:
            cash = pos * p
            pos = 0
        vals.append(cash + pos * p)
    return vals, (vals[-1] - 初始资金) / 初始资金

# ==================== 初始化 ====================
if '引擎' not in st.session_state:
    st.session_state.引擎 = AI交易引擎()
if '当前页面' not in st.session_state:
    st.session_state.当前页面 = "首页"

# ==================== 界面 ====================
st.title("🚀 量化交易系统")
st.caption("多策略 · 多类目 · AI智能交易")

# 导航
nav_items = ["首页", "回测", "AI选股", "AI交易", "持仓", "关于"]
cols = st.columns(len(nav_items))
for col, name in zip(cols, nav_items):
    with col:
        if st.button(name, use_container_width=True):
            st.session_state.当前页面 = name
            st.rerun()

st.markdown("---")

# ==================== 首页 ====================
if st.session_state.当前页面 == "首页":
    st.info("🤖 量化交易系统已就绪")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("支持类目", "股票/加密货币")
    with col2:
        st.metric("策略数量", "5个")
    with col3:
        st.metric("交易状态", "🟢 就绪")
    with col4:
        st.metric("AI引擎", "已加载")

# ==================== 回测 ====================
elif st.session_state.当前页面 == "回测":
    st.subheader("📈 双均线策略回测")
    col1, col2 = st.columns([1, 2])
    with col1:
        类目 = st.selectbox("选择类目", ["股票", "加密货币"])
        快线 = st.slider("快线周期", 3, 50, 5)
        慢线 = st.slider("慢线周期", 10, 200, 20)
        初始资金 = st.number_input("初始资金", value=100000)
        if st.button("开始回测", type="primary"):
            with st.spinner("回测中..."):
                dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
                np.random.seed(42)
                if 类目 == "加密货币":
                    price = 50000 * np.exp(np.cumsum(np.random.normal(0.001, 0.03, len(dates))))
                else:
                    price = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, len(dates))))
                vals, ret = 双均线回测(price, 快线, 慢线, 初始资金)
                st.success(f"回测完成 | 收益率: {ret:.2%}")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=vals, mode='lines', name='权益', line=dict(color='#00ff88', width=2)))
                fig.update_layout(height=400, title="权益曲线")
                st.plotly_chart(fig, use_container_width=True)

# ==================== AI选股 ====================
elif st.session_state.当前页面 == "AI选股":
    st.subheader("🤖 AI智能选股")
    类目 = st.selectbox("选择类目", ["股票", "加密货币"])
    if st.button("🔍 开始选股", type="primary"):
        with st.spinner("AI分析中..."):
            if 类目 == "股票":
                df = 获取股票数据()
            else:
                df = 获取加密货币数据()
            df = df.copy()
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
    st.info(f"📊 当前交易类目: {engine.当前类目}")
    col1, col2 = st.columns(2)
    with col1:
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
        if st.button("🔄 手动执行一轮", use_container_width=True):
            with st.spinner("分析中..."):
                result = engine.手动执行一轮()
                if result:
                    st.success(f"决策: {result.get('action')} | {result.get('reason')}")
    st.markdown("---")
    状态 = engine.获取状态()
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("运行状态", 状态.get('运行状态'))
    with col_b:
        st.metric("总资产", f"{状态.get('总资产', 0):,.0f}")
    with col_c:
        st.metric("收益率", f"{状态.get('收益率', 0)}%")
    with col_d:
        st.metric("交易次数", 状态.get('交易次数', 0))

# ==================== 持仓 ====================
elif st.session_state.当前页面 == "持仓":
    st.subheader("💰 当前持仓")
    engine = st.session_state.引擎
    if engine.持仓:
        df = pd.DataFrame([{"代码": k, "名称": v['名称'], "数量": v['数量'], "成本": v['买入价'], "买入时间": v.get('买入时间', '')} for k, v in engine.持仓.items()])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无持仓")
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
    
    **功能模块：**
    - 📈 回测：双均线策略回测
    - 🤖 AI选股：智能推荐股票/加密货币
    - 🤖 AI交易：自动买卖决策
    - 💰 持仓：实时持仓监控
    
    **使用步骤：**
    1. 点击「AI交易」选择策略
    2. 点击「启动AI交易」
    3. 点击「手动执行一轮」测试买入
    """)

st.markdown("---")
st.caption("量化交易系统 v4.0 | 全功能版")