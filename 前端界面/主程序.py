import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import requests
import json
import sys
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ================== 配置中心 ==================
CONFIG = {
    "app": {
        "title": "量化交易系统 v5.0",
        "icon": "📊",
        "layout": "wide",
        "theme": "dark"
    },
    "trading": {
        "default_leverage": 1,
        "default_slippage": 0.0001,
        "commission_rate": 0.0005,
        "max_position_pct": 0.3
    },
    "risk": {
        "max_daily_loss": 0.05,
        "max_position_loss": 0.02,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.04
    },
    "api": {
        "retry_times": 3,
        "timeout": 10,
        "cache_ttl": 60
    },
    "ui": {
        "refresh_interval": 60,
        "chart_height": 350,
        "colors": {
            "primary": "#00d2ff",
            "positive": "#00ff88",
            "negative": "#ff4444",
            "neutral": "#ffaa00",
            "background": "#0a0c10",
            "card_bg": "#1a1d24"
        }
    }
}

# ================== 日志系统 ==================
class Logger:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger("QuantSystem")
            cls._instance.logger.setLevel(logging.INFO)
            if not cls._instance.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                cls._instance.logger.addHandler(handler)
        return cls._instance
    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def warning(self, msg): self.logger.warning(msg)

logger = Logger()

# ================== 数据模型 ==================
@dataclass
class MarketData:
    symbol: str
    price: float
    high: float
    low: float
    open: float
    volume: int
    timestamp: datetime
    source: str = "simulated"

@dataclass
class Order:
    symbol: str
    side: str
    price: float
    quantity: float
    order_type: str = "limit"
    status: str = "pending"
    order_time: datetime = None
    fill_time: datetime = None
    fill_price: float = None

@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    unrealized_pnl: float = 0
    realized_pnl: float = 0

# ================== 策略加载器 ==================
class StrategyLoader:
    """从策略库加载真实策略"""
    
    def __init__(self):
        self.strategies = []
        self._load_strategies()
    
    def _load_strategies(self):
        """从策略库文件加载策略"""
        try:
            # 尝试导入外汇策略
            from 策略库.外汇策略.外汇利差策略 import ForexCarryStrategy
            from 策略库.外汇策略.外汇突破策略 import ForexBreakoutStrategy
            from 策略库.外汇策略.外汇双均线 import ForexDualMAStrategy
            self.strategies.extend([
                {"name": "外汇利差策略", "class": ForexCarryStrategy, "symbol": "AUDJPY", "category": "外汇"},
                {"name": "外汇突破策略", "class": ForexBreakoutStrategy, "symbol": "EURUSD", "category": "外汇"},
                {"name": "外汇双均线", "class": ForexDualMAStrategy, "symbol": "GBPUSD", "category": "外汇"},
            ])
            logger.info("外汇策略加载成功")
        except Exception as e:
            logger.warning(f"外汇策略加载失败: {e}")
        
        try:
            # 尝试导入期货策略
            from 策略库.期货策略.期货趋势策略 import FuturesTrendStrategy
            from 策略库.期货策略.期货均值回归 import FuturesMeanReversionStrategy
            from 策略库.期货策略.期货ATR import FuturesATRStrategy
            self.strategies.extend([
                {"name": "期货趋势策略", "class": FuturesTrendStrategy, "symbol": "GC=F", "category": "期货"},
                {"name": "期货均值回归", "class": FuturesMeanReversionStrategy, "symbol": "CL=F", "category": "期货"},
                {"name": "期货ATR策略", "class": FuturesATRStrategy, "symbol": "SI=F", "category": "期货"},
            ])
            logger.info("期货策略加载成功")
        except Exception as e:
            logger.warning(f"期货策略加载失败: {e}")
        
        try:
            # 尝试导入加密货币策略
            from 策略库.加密货币策略.加密双均线策略 import CryptoDualMAStrategy
            from 策略库.加密货币策略.加密RSI策略 import CryptoRSIStrategy
            self.strategies.extend([
                {"name": "加密双均线", "class": CryptoDualMAStrategy, "symbol": "BTC-USD", "category": "加密货币"},
                {"name": "加密RSI策略", "class": CryptoRSIStrategy, "symbol": "ETH-USD", "category": "加密货币"},
            ])
            logger.info("加密货币策略加载成功")
        except Exception as e:
            logger.warning(f"加密货币策略加载失败: {e}")
        
        # 如果没有加载到任何策略，使用模拟策略
        if not self.strategies:
            logger.warning("未加载到真实策略，使用模拟策略")
            self._load_mock_strategies()
    
    def _load_mock_strategies(self):
        """加载模拟策略"""
        self.strategies = [
            {"name": "趋势跟踪策略", "class": None, "symbol": "EURUSD", "category": "外汇", "mock": True},
            {"name": "均值回归策略", "class": None, "symbol": "GC=F", "category": "期货", "mock": True},
            {"name": "突破交易策略", "class": None, "symbol": "BTC-USD", "category": "加密货币", "mock": True},
        ]
    
    def get_strategies(self) -> List[Dict]:
        return self.strategies
    
    def get_strategy_by_name(self, name: str) -> Optional[Dict]:
        for s in self.strategies:
            if s["name"] == name:
                return s
        return None

# ================== AI引擎 ==================
class AIEngine:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        
    def analyze(self, symbol: str, price: float, strategy_name: str, strategy_signal: str) -> Dict:
        """AI综合多策略信号做最终决策"""
        if not self.api_key:
            return self._mock_decision(strategy_signal)
        
        prompt = f"""你是量化交易AI仲裁者。品种:{symbol},当前价格:{price},策略信号:{strategy_signal}。
        输出json:{{"final_signal":"buy/sell/hold","confidence":0-100,"reason":"理由"}}"""
        
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                timeout=CONFIG["api"]["timeout"]
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    return self._mock_decision(strategy_signal)
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
        
        return self._mock_decision(strategy_signal)
    
    def _mock_decision(self, strategy_signal: str) -> Dict:
        signal = strategy_signal if strategy_signal in ["buy", "sell", "hold"] else "hold"
        return {
            "final_signal": signal,
            "confidence": random.randint(60, 90),
            "reason": "基于策略信号综合判断"
        }

# ================== 数据缓存 ==================
class DataCache:
    _cache = {}
    
    @classmethod
    def get(cls, key: str, ttl: int = 60):
        if key in cls._cache:
            data, timestamp = cls._cache[key]
            if (datetime.now() - timestamp).seconds < ttl:
                return data
        return None
    
    @classmethod
    def set(cls, key: str, value):
        cls._cache[key] = (value, datetime.now())

# ================== 风控引擎 ==================
class RiskManager:
    def __init__(self):
        self.daily_pnl = 0
        self.daily_trades = 0
        self.pnl_history = []
        self.asset_history = []
        
    def can_trade(self, symbol: str, side: str, quantity: float, price: float, total_capital: float) -> Tuple[bool, str]:
        position_value = quantity * price
        if total_capital > 0 and position_value / total_capital > CONFIG["trading"]["max_position_pct"]:
            return False, f"仓位超限"
        return True, "通过"
    
    def update_pnl(self, pnl: float, total_asset: float):
        self.daily_pnl += pnl
        self.pnl_history.append({"time": datetime.now(), "pnl": self.daily_pnl})
        self.asset_history.append({"time": datetime.now(), "asset": total_asset})

# ================== 订单引擎 ==================
class OrderEngine:
    def __init__(self):
        self.orders: List[Order] = []
        self.positions: Dict[str, Position] = {}
        self.trade_log: List[Dict] = []
        self.initial_capital = 100000.0
        self.current_capital = 100000.0
    
    def execute_order(self, order: Order, current_price: float) -> Tuple[bool, str]:
        try:
            commission = current_price * order.quantity * CONFIG["trading"]["commission_rate"]
            
            if order.side == "buy":
                if order.symbol in self.positions:
                    pos = self.positions[order.symbol]
                    total_qty = pos.quantity + order.quantity
                    total_cost = pos.quantity * pos.avg_price + order.quantity * current_price
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=total_qty,
                        avg_price=total_cost / total_qty,
                        current_price=current_price,
                        unrealized_pnl=0,
                        realized_pnl=pos.realized_pnl
                    )
                else:
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=order.quantity,
                        avg_price=current_price,
                        current_price=current_price,
                        unrealized_pnl=0
                    )
                self.trade_log.append({
                    "time": datetime.now(), "symbol": order.symbol, "action": "买入",
                    "price": current_price, "qty": order.quantity, "commission": commission
                })
                logger.info(f"买入 {order.symbol} @ {current_price}")
                
            elif order.side == "sell" and order.symbol in self.positions:
                pos = self.positions[order.symbol]
                realized_pnl = (current_price - pos.avg_price) * min(order.quantity, pos.quantity)
                
                if order.quantity >= pos.quantity:
                    del self.positions[order.symbol]
                else:
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=pos.quantity - order.quantity,
                        avg_price=pos.avg_price,
                        current_price=current_price,
                        unrealized_pnl=0,
                        realized_pnl=pos.realized_pnl + realized_pnl
                    )
                
                self.trade_log.append({
                    "time": datetime.now(), "symbol": order.symbol, "action": "卖出",
                    "price": current_price, "qty": order.quantity, "pnl": realized_pnl, "commission": commission
                })
                logger.info(f"卖出 {order.symbol} @ {current_price}, PnL: {realized_pnl:.2f}")
            
            order.status = "filled"
            order.fill_time = datetime.now()
            order.fill_price = current_price
            self._update_capital()
            return True, "成功"
        except Exception as e:
            logger.error(f"订单执行失败: {e}")
            return False, str(e)
    
    def _update_capital(self):
        total = self.initial_capital
        for pos in self.positions.values():
            total += pos.quantity * (pos.current_price - pos.avg_price) + pos.realized_pnl
        self.current_capital = max(total, 0)
    
    def get_total_value(self) -> float:
        total = self.initial_capital
        for pos in self.positions.values():
            total += pos.quantity * (pos.current_price - pos.avg_price) + pos.realized_pnl
        return max(total, 0)
    
    def get_total_pnl(self) -> float:
        return self.get_total_value() - self.initial_capital

# ================== 行情获取 ==================
class MarketDataProvider:
    def __init__(self):
        self.cache = DataCache()
    
    def get_price(self, symbol: str, force_refresh: bool = False) -> MarketData:
        cache_key = f"price_{symbol}"
        if not force_refresh:
            cached = self.cache.get(cache_key, CONFIG["api"]["cache_ttl"])
            if cached:
                return cached
        
        try:
            from data.market_data import get_1min_kline
            kline = get_1min_kline(symbol)
            if kline:
                data = MarketData(
                    symbol=symbol,
                    price=kline.get('close', 1.085),
                    high=kline.get('high', 1.085),
                    low=kline.get('low', 1.085),
                    open=kline.get('open', 1.085),
                    volume=kline.get('volume', 0),
                    timestamp=datetime.now(),
                    source="yfinance"
                )
                self.cache.set(cache_key, data)
                return data
        except Exception as e:
            logger.warning(f"获取行情失败: {e}")
        
        base_price = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950, "AUDJPY": 90, "GBPUSD": 1.25}.get(symbol, 100)
        data = MarketData(
            symbol=symbol,
            price=base_price * (1 + random.uniform(-0.005, 0.005)),
            high=base_price * 1.003,
            low=base_price * 0.997,
            open=base_price,
            volume=1000,
            timestamp=datetime.now(),
            source="simulated"
        )
        self.cache.set(cache_key, data)
        return data

# ================== 策略运行器 ==================
class StrategyRunner:
    """运行策略并获取信号"""
    
    @staticmethod
    def run_strategy(strategy_info: Dict, market_data: MarketData) -> str:
        """运行单个策略，返回buy/sell/hold"""
        try:
            if strategy_info.get("mock"):
                # 模拟策略逻辑
                return random.choice(["buy", "sell", "hold"])
            
            strategy_class = strategy_info.get("class")
            if strategy_class:
                # 实例化策略
                strategy = strategy_class(strategy_info["name"], strategy_info["symbol"], 10000)
                kline_data = {
                    "close": market_data.price,
                    "high": market_data.high,
                    "low": market_data.low,
                    "open": market_data.open,
                    "volume": market_data.volume
                }
                return strategy.on_data(kline_data)
        except Exception as e:
            logger.error(f"策略运行失败 {strategy_info['name']}: {e}")
        
        return "hold"

# ================== UI渲染函数 ==================
def render_positions(engine: OrderEngine, data_provider: MarketDataProvider):
    st.markdown("### 💼 持仓实时数据")
    
    if not engine.positions:
        st.info("暂无持仓")
        return
    
    positions_data = []
    for symbol, pos in engine.positions.items():
        current_data = data_provider.get_price(symbol)
        pos.current_price = current_data.price
        pos.unrealized_pnl = pos.quantity * (pos.current_price - pos.avg_price)
        
        positions_data.append({
            "品种": symbol,
            "数量": f"{pos.quantity:.4f}",
            "成本价": f"{pos.avg_price:.4f}",
            "现价": f"{pos.current_price:.4f}",
            "浮动盈亏": f"{pos.unrealized_pnl:+,.2f}",
            "盈亏%": f"{pos.unrealized_pnl/(max(pos.avg_price*pos.quantity,0.01))*100:.1f}%"
        })
    
    st.dataframe(pd.DataFrame(positions_data), use_container_width=True, hide_index=True)

# ================== 主程序 ==================
def main():
    st.set_page_config(page_title="量化交易系统", layout="wide", initial_sidebar_state="collapsed")
    
    # 初始化组件
    if 'order_engine' not in st.session_state:
        st.session_state.order_engine = OrderEngine()
    if 'risk_manager' not in st.session_state:
        st.session_state.risk_manager = RiskManager()
    if 'data_provider' not in st.session_state:
        st.session_state.data_provider = MarketDataProvider()
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = AIEngine()
    if 'strategy_loader' not in st.session_state:
        st.session_state.strategy_loader = StrategyLoader()
    
    engine = st.session_state.order_engine
    data_provider = st.session_state.data_provider
    ai = st.session_state.ai_engine
    strategy_loader = st.session_state.strategy_loader
    
    # 样式
    st.markdown("""
    <style>
        .stApp { background-color: #0a0c10; }
        .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; }
        .stMetric label { color: #8892b0 !important; font-size: 11px !important; }
        .stMetric div { color: #00d2ff !important; font-size: 16px !important; }
        h1 { color: #ffffff; text-align: center; font-size: 22px; }
        .caption { text-align: center; color: #8892b0; font-size: 11px; margin-bottom: 20px; }
        .strategy-card { background-color: #1a1d24; border-radius: 8px; padding: 12px; margin: 8px 0; border-left: 3px solid #00d2ff; cursor: pointer; }
        .strategy-card:hover { background-color: #252a36; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
    st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 | 真实策略库接入</div>', unsafe_allow_html=True)
    
    # 导航
    tabs = st.tabs(["🏠 首页", "📈 市场行情", "🎯 策略中心", "🤖 AI交易", "💼 持仓管理", "📊 资金曲线", "⚙️ 系统设置"])
    
    # ================== 首页 ==================
    with tabs[0]:
        st.markdown("### 📈 市场概览")
        cols = st.columns(4)
        symbols = ["EURUSD", "BTC-USD", "GC=F", "AAPL"]
        for i, sym in enumerate(symbols):
            data = data_provider.get_price(sym)
            with cols[i]:
                st.markdown(f'<div style="background-color:#1a1d24; border-radius:8px; padding:10px; text-align:center">{sym}<br><span style="font-size:18px;color:#00d2ff">{data.price:.4f}</span></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        total_val = engine.get_total_value()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总资产", f"${total_val:,.0f}")
        col2.metric("总盈亏", f"${engine.get_total_pnl():+,.0f}")
        col3.metric("持仓数", f"{len(engine.positions)}")
        col4.metric("今日盈亏", f"${st.session_state.risk_manager.daily_pnl:+,.0f}")
    
    # ================== 市场行情 ==================
    with tabs[1]:
        st.markdown("### 📊 全球市场行情")
        market_data = []
        for sym in ["EURUSD", "BTC-USD", "GC=F", "AUDJPY", "GBPUSD", "AAPL", "NVDA"]:
            data = data_provider.get_price(sym)
            market_data.append({"品种": sym, "价格": data.price, "涨跌": f"{data.price - data.open:.4f}"})
        st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)
    
    # ================== 策略中心 ==================
    with tabs[2]:
        st.markdown("### 🎯 策略库")
        st.caption("点击「运行」执行策略分析")
        
        strategies = strategy_loader.get_strategies()
        
        for s in strategies:
            with st.container():
                cols = st.columns([2, 1.5, 1, 1, 1, 1.5])
                cols[0].write(f"**{s['name']}**")
                cols[1].write(s['symbol'])
                cols[2].write(s['category'])
                cols[3].write("🟢 就绪")
                
                # 运行策略按钮
                if cols[4].button("▶ 运行", key=f"run_{s['name']}"):
                    # 获取行情
                    market_data = data_provider.get_price(s['symbol'])
                    # 运行策略
                    signal = StrategyRunner.run_strategy(s, market_data)
                    st.session_state[f"signal_{s['name']}"] = signal
                    st.success(f"{s['name']} 信号: {signal.upper()}")
                
                # 显示信号
                signal_key = f"signal_{s['name']}"
                if signal_key in st.session_state:
                    sig = st.session_state[signal_key]
                    color = "#00ff88" if sig == "buy" else "#ff4444" if sig == "sell" else "#ffaa00"
                    cols[5].markdown(f"<span style='color:{color};font-weight:bold'>{sig.upper()}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
    
    # ================== AI交易 ==================
    with tabs[3]:
        st.markdown("### 🤖 AI智能交易")
        
        # 选择策略
        strategies = strategy_loader.get_strategies()
        strategy_names = [s["name"] for s in strategies]
        selected_strategy = st.selectbox("选择策略", strategy_names)
        
        # 获取选中的策略信息
        strategy_info = strategy_loader.get_strategy_by_name(selected_strategy)
        if strategy_info:
            symbol = strategy_info["symbol"]
            current_data = data_provider.get_price(symbol)
            st.metric(f"{symbol} 当前价格", f"{current_data.price:.5f}")
            
            if st.button("🚀 执行AI分析", type="primary", use_container_width=True):
                with st.spinner("运行策略并调用AI分析..."):
                    # 1. 运行策略获取信号
                    strategy_signal = StrategyRunner.run_strategy(strategy_info, current_data)
                    st.info(f"📊 策略信号: {strategy_signal.upper()}")
                    
                    # 2. AI仲裁
                    result = ai.analyze(symbol, current_data.price, selected_strategy, strategy_signal)
                    
                    st.success(f"🤖 AI最终决策: {result['final_signal'].upper()}")
                    st.info(f"📊 置信度: {result['confidence']}%")
                    st.write(f"📝 理由: {result.get('reason', 'AI分析完成')}")
                    
                    # 3. 执行交易
                    if st.button("执行交易", key="exec_ai_trade"):
                        if result['final_signal'] == 'buy':
                            order = Order(symbol=symbol, side="buy", price=current_data.price, quantity=1000)
                            engine.execute_order(order, current_data.price)
                            st.success("✅ 买入订单已执行")
                        elif result['final_signal'] == 'sell':
                            order = Order(symbol=symbol, side="sell", price=current_data.price, quantity=1000)
                            engine.execute_order(order, current_data.price)
                            st.success("✅ 卖出订单已执行")
                        st.rerun()
    
    # ================== 持仓管理 ==================
    with tabs[4]:
        render_positions(engine, data_provider)
        st.markdown("---")
        st.markdown("### 📜 交易记录")
        if engine.trade_log:
            df_log = pd.DataFrame(engine.trade_log)
            df_log['time'] = pd.to_datetime(df_log['time']).dt.strftime('%H:%M:%S')
            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("暂无交易记录")
    
    # ================== 资金曲线 ==================
    with tabs[5]:
        st.markdown("### 📈 资金曲线")
        # 简化的资金曲线
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        assets = [engine.initial_capital + engine.get_total_pnl() * (i/30) for i in range(30)]
        fig = go.Figure(data=go.Scatter(x=dates, y=assets, mode='lines', line=dict(color='#00d2ff', width=2)))
        fig.update_layout(height=350, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("当前总资产", f"${engine.get_total_value():,.0f}")
        col2.metric("总盈亏", f"${engine.get_total_pnl():+,.0f}")
        col3.metric("收益率", f"{engine.get_total_pnl()/max(engine.initial_capital,1)*100:.1f}%")
    
    # ================== 系统设置 ==================
    with tabs[6]:
        st.markdown("### ⚙️ 系统设置")
        max_pos = st.slider("单笔最大仓位(%)", 5, 50, 30)
        if st.button("保存设置"):
            CONFIG["trading"]["max_position_pct"] = max_pos / 100
            st.success("设置已保存")
        
        st.info(f"""
        - 系统版本: v5.0
        - AI引擎: DeepSeek
        - 策略数量: {len(strategy_loader.get_strategies())}
        - 当前资产: ${engine.get_total_value():,.0f}
        """)

if __name__ == "__main__":
    main()
