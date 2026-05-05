import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import requests
import json
import sys
import os
import importlib.util
import glob

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantSystem")

INITIAL_CAPITAL = 100000.0

# ================== 数据模型 ==================
class MarketData:
    def __init__(self, symbol, price, high, low, open_price, volume):
        self.symbol = symbol
        self.price = price
        self.high = high
        self.low = low
        self.open = open_price
        self.volume = volume
        self.timestamp = datetime.now()

class Position:
    def __init__(self, symbol, quantity, avg_price):
        self.symbol = symbol
        self.quantity = quantity
        self.avg_price = avg_price
        self.current_price = avg_price
        self.realized_pnl = 0

# ================== 策略基类 ==================
class BaseStrategy:
    def __init__(self, name, symbol, initial_capital):
        self.name = name
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
    
    def on_data(self, kline):
        return 'hold'
    
    def execute_signal(self, signal, price):
        if signal == 'buy' and self.capital >= price:
            self.position += 1
            self.capital -= price
        elif signal == 'sell' and self.position > 0:
            self.position -= 1
            self.capital += price

# ================== 策略加载器 ==================
class StrategyLoader:
    def __init__(self):
        self.strategies = []
        self.load_log = []
        self._load_all_strategies()
    
    def _load_all_strategies(self):
        strategy_base_path = "策略库"
        if not os.path.exists(strategy_base_path):
            self.load_log.append(f"❌ 策略库不存在")
            self._add_demo_strategies()
            return
        
        category_config = {
            "外汇策略": {"symbol": "EURUSD", "display": "外汇"},
            "期货策略": {"symbol": "GC=F", "display": "期货"},
            "加密货币策略": {"symbol": "BTC-USD", "display": "加密货币"},
            "A股策略": {"symbol": "000001.SS", "display": "A股"},
            "港股策略": {"symbol": "00700.HK", "display": "港股"},
            "美股策略": {"symbol": "AAPL", "display": "美股"},
        }
        
        for folder_name, config in category_config.items():
            folder_path = os.path.join(strategy_base_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            symbol = config["symbol"]
            display = config["display"]
            py_files = glob.glob(os.path.join(folder_path, "*.py"))
            
            for py_file in py_files:
                file_name = os.path.basename(py_file)
                if file_name in ["__init__.py", "__pycache__"] or file_name.endswith(".txt"):
                    continue
                
                strategy_name = file_name.replace(".py", "")
                
                try:
                    spec = importlib.util.spec_from_file_location(strategy_name, py_file)
                    module = importlib.util.module_from_spec(spec)
                    module.BaseStrategy = BaseStrategy
                    spec.loader.exec_module(module)
                    
                    strategy_class = None
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr_name.endswith("Strategy"):
                            if attr_name != "BaseStrategy":
                                strategy_class = attr
                                break
                    
                    if strategy_class:
                        self.strategies.append({
                            "name": strategy_name,
                            "class": strategy_class,
                            "symbol": symbol,
                            "category": display,
                            "file": py_file
                        })
                        self.load_log.append(f"✅ {display}/{strategy_name}")
                except Exception as e:
                    self.load_log.append(f"❌ {strategy_name}: {str(e)}")
        
        if not self.strategies:
            self._add_demo_strategies()
    
    def _add_demo_strategies(self):
        self.strategies = [
            {"name": "趋势跟踪策略", "class": None, "symbol": "EURUSD", "category": "演示", "demo": True},
            {"name": "均值回归策略", "class": None, "symbol": "GC=F", "category": "演示", "demo": True},
        ]
    
    def get_strategies(self):
        return self.strategies
    
    def get_strategy_by_name(self, name):
        for s in self.strategies:
            if s["name"] == name:
                return s
        return None

# ================== 策略运行器 ==================
class StrategyRunner:
    @staticmethod
    def run(strategy_info, market_data):
        if strategy_info.get("demo") or not strategy_info.get("class"):
            return random.choice(["buy", "sell", "hold"])
        try:
            instance = strategy_info["class"](strategy_info["name"], strategy_info["symbol"], 10000)
            kline = {"close": market_data.price, "high": market_data.high, "low": market_data.low, "open": market_data.open}
            return instance.on_data(kline)
        except Exception as e:
            return "hold"

# ================== AI引擎 ==================
class AIEngine:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    def analyze(self, symbol, price, strategy_signal):
        if not self.api_key:
            return {"final_signal": strategy_signal, "confidence": 75, "reason": "API未配置"}
        return {"final_signal": strategy_signal, "confidence": 70, "reason": "AI分析"}

# ================== 订单引擎 ==================
class OrderEngine:
    def __init__(self):
        self.positions = {}
        self.trade_log = []
        self.initial_capital = INITIAL_CAPITAL
    
    def buy(self, symbol, price, qty=1000):
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_qty = pos.quantity + qty
            total_cost = pos.quantity * pos.avg_price + qty * price
            pos.quantity = total_qty
            pos.avg_price = total_cost / total_qty
        else:
            self.positions[symbol] = Position(symbol, qty, price)
        self.trade_log.append({"time": datetime.now(), "action": "买入", "symbol": symbol, "price": price, "qty": qty})
    
    def sell(self, symbol, price, qty=1000):
        if symbol in self.positions and self.positions[symbol].quantity >= qty:
            pos = self.positions[symbol]
            pnl = (price - pos.avg_price) * qty
            pos.quantity -= qty
            pos.realized_pnl += pnl
            if pos.quantity <= 0:
                del self.positions[symbol]
            self.trade_log.append({"time": datetime.now(), "action": "卖出", "symbol": symbol, "price": price, "qty": qty, "pnl": pnl})
    
    def get_total_value(self):
        total = self.initial_capital
        for pos in self.positions.values():
            total += pos.realized_pnl
            total += pos.quantity * pos.current_price - pos.quantity * pos.avg_price
        return total
    
    def get_total_pnl(self):
        return self.get_total_value() - self.initial_capital

# ================== 行情获取 ==================
def get_price(symbol):
    try:
        from data.market_data import get_1min_kline
        kline = get_1min_kline(symbol)
        if kline:
            return MarketData(symbol, kline.get('close', 1.085), kline.get('high', 1.085), kline.get('low', 1.085), kline.get('open', 1.085), kline.get('volume', 0))
    except:
        pass
    base = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950, "000001.SS": 3000, "00700.HK": 350, "AAPL": 175}.get(symbol, 100)
    return MarketData(symbol, base * (1 + random.uniform(-0.005, 0.005)), base * 1.003, base * 0.997, base, 1000)

# ================== 主程序 ==================
def main():
    st.set_page_config(page_title="量化交易系统", layout="wide")
    
    if 'engine' not in st.session_state:
        st.session_state.engine = OrderEngine()
    if 'strategy_loader' not in st.session_state:
        st.session_state.strategy_loader = StrategyLoader()
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = AIEngine()
    if 'signals' not in st.session_state:
        st.session_state.signals = {}
    
    engine = st.session_state.engine
    strategy_loader = st.session_state.strategy_loader
    ai_engine = st.session_state.ai_engine
    strategies = strategy_loader.get_strategies()
    
    st.markdown("""
    <style>
        .stApp { background-color: #0a0c10; }
        .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 10px; text-align: center; }
        h1 { color: white; text-align: center; font-size: 24px; }
        .caption { text-align: center; color: #8892b0; font-size: 12px; margin-bottom: 20px; }
        .category-title { color: #00d2ff; font-size: 18px; margin-top: 20px; margin-bottom: 10px; }
        .strategy-row { background-color: #1a1d24; border-radius: 8px; padding: 12px; margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
    st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 | 真实策略库接入</div>', unsafe_allow_html=True)
    
    with st.expander(f"📁 策略加载日志 (共{len(strategies)}个策略)"):
        for log in strategy_loader.load_log:
            st.text(log)
    
    tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线"])
    
    # 首页
    with tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        total_val = engine.get_total_value()
        total_pnl = engine.get_total_pnl()
        col1.metric("总资产", f"${total_val:,.0f}")
        col2.metric("总盈亏", f"${total_pnl:+,.0f}")
        col3.metric("持仓数", f"{len(engine.positions)}")
        col4.metric("交易次数", f"{len(engine.trade_log)}")
        
        st.markdown("### 📈 市场行情")
        cols = st.columns(4)
        for i, sym in enumerate(["EURUSD", "BTC-USD", "GC=F", "AAPL"]):
            data = get_price(sym)
            cols[i].markdown(f'<div style="background:#1a1d24;border-radius:8px;padding:10px;text-align:center"><b>{sym}</b><br><span style="color:#00d2ff;font-size:18px">{data.price:.4f}</span></div>', unsafe_allow_html=True)
    
    # 策略中心（带执行按钮）
    with tabs[1]:
        st.markdown("### 🎯 策略库")
        
        categories = {}
        for s in strategies:
            cat = s.get("category", "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s)
        
        for cat, cat_strategies in categories.items():
            st.markdown(f'<div class="category-title">📁 {cat} ({len(cat_strategies)})</div>', unsafe_allow_html=True)
            for idx, s in enumerate(cat_strategies):
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1.2, 1.2, 1, 1.5])
                    col1.write(f"**{s['name']}**")
                    col2.write(s['symbol'])
                    col3.write(s['category'])
                    
                    # 运行按钮
                    if col4.button(f"▶ 运行", key=f"run_{s['name']}_{idx}"):
                        market_data = get_price(s['symbol'])
                        signal = StrategyRunner.run(s, market_data)
                        st.session_state.signals[s['name']] = signal
                        st.success(f"信号: {signal.upper()}")
                    
                    # 显示信号和执行按钮
                    if s['name'] in st.session_state.signals:
                        sig = st.session_state.signals[s['name']]
                        color = "#00ff88" if sig == "buy" else "#ff4444" if sig == "sell" else "#ffaa00"
                        col5.markdown(f"<span style='color:{color};font-weight:bold'>{sig.upper()}</span>", unsafe_allow_html=True)
                        
                        # 手动执行按钮
                        if sig in ['buy', 'sell']:
                            if st.button(f"💸 执行{sig.upper()}", key=f"exec_{s['name']}_{idx}"):
                                price = get_price(s['symbol']).price
                                if sig == 'buy':
                                    engine.buy(s['symbol'], price)
                                    st.success(f"✅ 买入 {s['name']} @ {price:.4f}")
                                else:
                                    engine.sell(s['symbol'], price)
                                    st.success(f"✅ 卖出 {s['name']} @ {price:.4f}")
                                st.rerun()
                    st.markdown("---")
    
    # AI交易
    with tabs[2]:
        st.markdown("### 🤖 AI智能交易")
        strategy_names = [s["name"] for s in strategies]
        if strategy_names:
            selected = st.selectbox("选择策略", strategy_names)
            if st.button("🚀 AI分析并执行", type="primary", use_container_width=True):
                strategy_info = strategy_loader.get_strategy_by_name(selected)
                if strategy_info:
                    market_data = get_price(strategy_info["symbol"])
                    strategy_signal = StrategyRunner.run(strategy_info, market_data)
                    st.info(f"📊 策略信号: {strategy_signal.upper()}")
                    
                    result = ai_engine.analyze(strategy_info["symbol"], market_data.price, strategy_signal)
                    st.success(f"🤖 AI决策: {result['final_signal'].upper()}")
                    st.info(f"置信度: {result['confidence']}%")
                    
                    if result['final_signal'] == 'buy':
                        if st.button("确认执行买入", key="ai_buy"):
                            engine.buy(strategy_info["symbol"], market_data.price)
                            st.success("✅ 买入成功")
                            st.rerun()
                    elif result['final_signal'] == 'sell':
                        if st.button("确认执行卖出", key="ai_sell"):
                            engine.sell(strategy_info["symbol"], market_data.price)
                            st.success("✅ 卖出成功")
                            st.rerun()
    
    # 持仓管理
    with tabs[3]:
        st.markdown("### 💼 当前持仓")
        if engine.positions:
            data = []
            for sym, pos in engine.positions.items():
                price = get_price(sym).price
                pos.current_price = price
                pnl = pos.quantity * (price - pos.avg_price)
                data.append({"品种": sym, "数量": f"{pos.quantity:.4f}", "成本": f"{pos.avg_price:.4f}", "现价": f"{price:.4f}", "盈亏": f"${pnl:+,.2f}"})
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("暂无持仓")
        
        st.markdown("### 📜 交易记录")
        if engine.trade_log:
            df = pd.DataFrame(engine.trade_log[-10:])
            df['time'] = df['time'].dt.strftime('%H:%M:%S')
            st.dataframe(df, use_container_width=True)
    
    # 资金曲线
    with tabs[4]:
        st.markdown("### 📈 资金曲线")
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        values = [engine.initial_capital + i * (engine.get_total_value() - engine.initial_capital) / 30 for i in range(30)]
        fig = go.Figure(data=go.Scatter(x=dates, y=values, mode='lines', line=dict(color='#00d2ff', width=2)))
        fig.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        col1.metric("当前资产", f"${engine.get_total_value():,.0f}")
        col2.metric("初始资产", f"${engine.initial_capital:,.0f}")

if __name__ == "__main__":
    main()
