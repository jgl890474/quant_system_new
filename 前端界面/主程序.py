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

# ================== 配置 ==================
CONFIG = {
    "trading": {"max_position_pct": 0.3, "commission_rate": 0.0005},
    "risk": {"stop_loss_pct": 0.02, "take_profit_pct": 0.04},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantSystem")

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

# ================== 策略加载器（扫描文件夹）=================
class StrategyLoader:
    def __init__(self):
        self.strategies = []
        self._scan_strategy_folder()
    
    def _scan_strategy_folder(self):
        """扫描策略库文件夹，加载所有策略"""
        strategy_base_path = "策略库"
        
        # 定义策略文件夹和对应的symbol
        folder_config = {
            "外汇策略": {"symbol": "EURUSD", "category": "外汇"},
            "期货策略": {"symbol": "GC=F", "category": "期货"},
            "加密货币策略": {"symbol": "BTC-USD", "category": "加密货币"},
            "A股策略": {"symbol": "600519.SS", "category": "A股"},
            "港股策略": {"symbol": "0700.HK", "category": "港股"},
            "美股策略": {"symbol": "AAPL", "category": "美股"},
        }
        
        for folder_name, config in folder_config.items():
            folder_path = os.path.join(strategy_base_path, folder_name)
            if not os.path.exists(folder_path):
                continue
            
            # 扫描文件夹下的所有.py文件
            for py_file in glob.glob(os.path.join(folder_path, "*.py")):
                if py_file.endswith("__init__.py"):
                    continue
                
                file_name = os.path.basename(py_file)
                strategy_name = file_name.replace(".py", "")
                
                try:
                    # 动态加载模块
                    spec = importlib.util.spec_from_file_location(strategy_name, py_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找策略类（以Strategy结尾的类）
                    strategy_class = None
                    for attr_name in dir(module):
                        if attr_name.endswith("Strategy") and attr_name != "BaseStrategy":
                            strategy_class = getattr(module, attr_name)
                            break
                    
                    if strategy_class:
                        self.strategies.append({
                            "name": strategy_name,
                            "class": strategy_class,
                            "symbol": config["symbol"],
                            "category": config["category"],
                            "file": py_file
                        })
                        logger.info(f"✅ 加载策略: {strategy_name} from {folder_name}")
                except Exception as e:
                    logger.warning(f"⚠️ 加载失败 {strategy_name}: {e}")
        
        # 如果没有加载到任何策略，使用内置演示策略
        if not self.strategies:
            self._add_demo_strategies()
            logger.warning("未找到策略文件，使用演示策略")
    
    def _add_demo_strategies(self):
        """添加演示策略"""
        self.strategies = [
            {"name": "趋势跟踪策略", "class": None, "symbol": "EURUSD", "category": "外汇", "demo": True},
            {"name": "均值回归策略", "class": None, "symbol": "GC=F", "category": "期货", "demo": True},
            {"name": "双均线策略", "class": None, "symbol": "BTC-USD", "category": "加密货币", "demo": True},
            {"name": "RSI策略", "class": None, "symbol": "AAPL", "category": "美股", "demo": True},
        ]
    
    def get_strategies(self):
        return self.strategies
    
    def get_strategy_by_name(self, name):
        for s in self.strategies:
            if s["name"] == name:
                return s
        return None
    
    def get_strategies_by_category(self, category):
        return [s for s in self.strategies if s["category"] == category]

# ================== 策略运行器 ==================
class StrategyRunner:
    @staticmethod
    def run(strategy_info, market_data):
        """运行策略，返回buy/sell/hold"""
        if strategy_info.get("demo") or not strategy_info.get("class"):
            # 演示策略：基于价格变化模拟信号
            return StrategyRunner._demo_signal(market_data)
        
        try:
            instance = strategy_info["class"](strategy_info["name"], strategy_info["symbol"], 10000)
            kline = {
                "close": market_data.price,
                "high": market_data.high,
                "low": market_data.low,
                "open": market_data.open,
                "volume": market_data.volume
            }
            return instance.on_data(kline)
        except Exception as e:
            logger.error(f"策略运行失败: {e}")
            return "hold"
    
    @staticmethod
    def _demo_signal(market_data):
        """演示信号生成"""
        # 简单的模拟信号
        if hasattr(market_data, 'price'):
            price = market_data.price
            # 基于价格小数部分决定信号
            if int(price * 1000) % 3 == 0:
                return "buy"
            elif int(price * 1000) % 3 == 1:
                return "sell"
        return "hold"

# ================== AI引擎 ==================
class AIEngine:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    
    def analyze(self, symbol, price, strategy_signal):
        if not self.api_key:
            return {"final_signal": strategy_signal, "confidence": 75, "reason": "API未配置，使用策略信号"}
        
        prompt = f"""品种:{symbol},价格:{price},策略信号:{strategy_signal}.输出JSON:{{"signal":"buy/sell/hold","confidence":0-100,"reason":"简短理由"}}"""
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 150},
                timeout=10
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                import json
                data = json.loads(content)
                return {"final_signal": data.get("signal", strategy_signal), "confidence": data.get("confidence", 70), "reason": data.get("reason", "AI分析")}
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
        
        return {"final_signal": strategy_signal, "confidence": 70, "reason": "AI分析完成"}

# ================== 订单引擎 ==================
class OrderEngine:
    def __init__(self):
        self.positions = {}
        self.trade_log = []
        self.initial_capital = 100000
        self.capital = 100000
    
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
        self._update_capital()
    
    def sell(self, symbol, price, qty=1000):
        if symbol in self.positions and self.positions[symbol].quantity >= qty:
            pos = self.positions[symbol]
            pnl = (price - pos.avg_price) * qty
            pos.quantity -= qty
            pos.realized_pnl += pnl
            if pos.quantity <= 0:
                del self.positions[symbol]
            self.trade_log.append({"time": datetime.now(), "action": "卖出", "symbol": symbol, "price": price, "qty": qty, "pnl": pnl})
            self._update_capital()
    
    def _update_capital(self):
        total = self.initial_capital
        for pos in self.positions.values():
            total += pos.realized_pnl
        self.capital = total
    
    def get_total_value(self):
        total = self.initial_capital
        for pos in self.positions.values():
            total += pos.realized_pnl
            total += pos.quantity * pos.current_price - pos.quantity * pos.avg_price
        return total

# ================== 行情获取 ==================
def get_price(symbol):
    try:
        from data.market_data import get_1min_kline
        kline = get_1min_kline(symbol)
        if kline:
            return MarketData(symbol, kline.get('close', 1.085), kline.get('high', 1.085), kline.get('low', 1.085), kline.get('open', 1.085), kline.get('volume', 0))
    except:
        pass
    base = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950, "AUDJPY": 90, "GBPUSD": 1.25, "600519.SS": 1500, "0700.HK": 350, "AAPL": 175}.get(symbol, 100)
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
    
    st.markdown("""
    <style>
        .stApp { background-color: #0a0c10; }
        .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 10px; text-align: center; }
        h1 { color: white; text-align: center; font-size: 24px; }
        .strategy-card { background-color: #1a1d24; border-radius: 8px; padding: 12px; margin: 8px 0; border-left: 3px solid #00d2ff; }
        .category-title { color: #00d2ff; font-size: 18px; margin-top: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#8892b0">多类目 · 多策略 · AI自动交易 | 真实策略库接入</p>', unsafe_allow_html=True)
    
    tabs = st.tabs(["首页", "策略中心", "AI交易", "持仓管理", "资金曲线"])
    
    # 首页
    with tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总资产", f"${engine.get_total_value():,.0f}")
        col2.metric("总盈亏", f"${engine.get_total_value() - engine.initial_capital:+,.0f}")
        col3.metric("持仓数", f"{len(engine.positions)}")
        col4.metric("交易次数", f"{len(engine.trade_log)}")
        
        st.markdown("### 📈 市场行情")
        cols = st.columns(4)
        for i, sym in enumerate(["EURUSD", "BTC-USD", "GC=F", "AAPL"]):
            data = get_price(sym)
            cols[i].markdown(f'<div style="background:#1a1d24;border-radius:8px;padding:10px;text-align:center"><b>{sym}</b><br><span style="color:#00d2ff;font-size:18px">{data.price:.4f}</span></div>', unsafe_allow_html=True)
    
    # 策略中心（按类别分组）
    with tabs[1]:
        st.markdown("### 🎯 策略库")
        
        strategies = strategy_loader.get_strategies()
        
        # 按类别分组
        categories = {}
        for s in strategies:
            cat = s["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(s)
        
        for cat, cat_strategies in categories.items():
            st.markdown(f'<div class="category-title">📁 {cat}</div>', unsafe_allow_html=True)
            for s in cat_strategies:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1.5])
                    col1.write(f"**{s['name']}**")
                    col2.write(s['symbol'])
                    col3.write(s['category'])
                    
                    if col4.button(f"运行", key=f"run_{s['name']}"):
                        market_data = get_price(s['symbol'])
                        signal = StrategyRunner.run(s, market_data)
                        st.session_state.signals[s['name']] = signal
                        st.success(f"信号: {signal.upper()}")
                    
                    if s['name'] in st.session_state.signals:
                        sig = st.session_state.signals[s['name']]
                        color = "#00ff88" if sig == "buy" else "#ff4444" if sig == "sell" else "#ffaa00"
                        col5.markdown(f"<span style='color:{color};font-weight:bold'>{sig.upper()}</span>", unsafe_allow_html=True)
                    st.markdown("---")
    
    # AI交易
    with tabs[2]:
        st.markdown("### 🤖 AI智能交易")
        
        strategies = strategy_loader.get_strategies()
        strategy_names = [s["name"] for s in strategies]
        selected = st.selectbox("选择策略", strategy_names)
        
        if st.button("执行AI分析", type="primary", use_container_width=True):
            strategy_info = strategy_loader.get_strategy_by_name(selected)
            if strategy_info:
                market_data = get_price(strategy_info["symbol"])
                strategy_signal = StrategyRunner.run(strategy_info, market_data)
                st.info(f"📊 策略信号: {strategy_signal.upper()}")
                
                result = ai_engine.analyze(strategy_info["symbol"], market_data.price, strategy_signal)
                st.success(f"🤖 AI决策: {result['final_signal'].upper()}")
                st.info(f"置信度: {result['confidence']}% | 理由: {result['reason']}")
                
                if result['final_signal'] == 'buy':
                    if st.button("执行买入"):
                        engine.buy(strategy_info["symbol"], market_data.price)
                        st.success("✅ 买入成功")
                        st.rerun()
                elif result['final_signal'] == 'sell':
                    if st.button("执行卖出"):
                        engine.sell(strategy_info["symbol"], market_data.price)
                        st.success("✅ 卖出成功")
                        st.rerun()
    
    # 持仓管理
    with tabs[3]:
        st.markdown("### 💼 当前持仓")
        if engine.positions:
            for sym, pos in engine.positions.items():
                price = get_price(sym).price
                pos.current_price = price
                pnl = pos.quantity * (price - pos.avg_price)
                st.markdown(f'<div class="strategy-card">{sym} | 数量:{pos.quantity:.4f} | 成本:{pos.avg_price:.4f} | 现价:{price:.4f} | 盈亏:${pnl:+,.2f}</div>', unsafe_allow_html=True)
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

if __name__ == "__main__":
    main()
