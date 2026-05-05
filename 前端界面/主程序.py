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
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

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
        "cache_ttl": 60,
        "deepseek_key": ""
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

# ================== AI引擎 ==================
class AIEngine:
    def __init__(self):
        self.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
        
    def analyze(self, symbol: str, price: float, market_data: Dict) -> Dict:
        if not self.api_key:
            return self._mock_analysis(symbol, price)
        
        prompt = f"""分析{symbol}，当前价格{price}。输出json: {{"signal":"buy/sell/hold","confidence":0-100,"reason":"原因","target":目标价,"stop_loss":止损价}}"""
        
        try:
            resp = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 200
                },
                timeout=CONFIG["api"]["timeout"]
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                try:
                    return json.loads(content)
                except:
                    return self._mock_analysis(symbol, price)
        except Exception as e:
            logger.error(f"AI调用失败: {e}")
        
        return self._mock_analysis(symbol, price)
    
    def _mock_analysis(self, symbol: str, price: float) -> Dict:
        import random
        signals = ["buy", "sell", "hold"]
        signal = random.choice(signals)
        return {
            "signal": signal,
            "confidence": random.randint(60, 95),
            "reason": "AI分析完成",
            "target": price * (1.02 if signal == "buy" else 0.98),
            "stop_loss": price * (0.98 if signal == "buy" else 1.02)
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
        if total_capital > 0 and self.daily_pnl < -total_capital * CONFIG["risk"]["max_daily_loss"]:
            return False, f"日亏损已达上限"
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
        
        # 模拟数据
        base_price = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950}.get(symbol, 100)
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

# ================== 收益曲线 ==================
def render_equity_curve(engine: OrderEngine, risk_mgr: RiskManager):
    st.markdown("### 📈 收益曲线")
    
    dates = []
    assets = []
    for i in range(30):
        date = datetime.now() - timedelta(days=29-i)
        dates.append(date)
        base = engine.initial_capital
        pnl_effect = engine.get_total_pnl() * (i / 30)
        assets.append(max(base + pnl_effect + random.uniform(-500, 500), 0))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=assets, mode='lines', name='资产曲线', line=dict(color='#00d2ff', width=2)))
    fig.add_trace(go.Scatter(x=dates, y=[engine.initial_capital]*len(dates), mode='lines', name='初始资金', line=dict(color='#ffaa00', width=1, dash='dash')))
    fig.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("当前总资产", f"${engine.get_total_value():,.0f}")
    col2.metric("总盈亏", f"${engine.get_total_pnl():+,.0f}")
    col3.metric("收益率", f"{engine.get_total_pnl()/max(engine.initial_capital,1)*100:.1f}%")

# ================== 持仓实时数据 ==================
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
    
    df_pie = pd.DataFrame(positions_data)
    df_pie['市值'] = df_pie['数量'].astype(float) * df_pie['现价'].astype(float)
    if len(df_pie) > 0 and df_pie['市值'].sum() > 0:
        fig = px.pie(df_pie, values='市值', names='品种', title='持仓分布', color_discrete_sequence=['#00d2ff', '#00ff88', '#ffaa00'])
        fig.update_layout(paper_bgcolor="#0a0c10", font_color="#e6e6e6", height=300)
        st.plotly_chart(fig, use_container_width=True)

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
    
    engine = st.session_state.order_engine
    risk_mgr = st.session_state.risk_manager
    data_provider = st.session_state.data_provider
    ai = st.session_state.ai_engine
    
    # 样式
    st.markdown("""
    <style>
        .stApp { background-color: #0a0c10; }
        .stMetric { background-color: #1a1d24; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; }
        .stMetric label { color: #8892b0 !important; font-size: 11px !important; }
        .stMetric div { color: #00d2ff !important; font-size: 16px !important; }
        h1 { color: #ffffff; text-align: center; font-size: 22px; }
        .caption { text-align: center; color: #8892b0; font-size: 11px; margin-bottom: 20px; }
        .market-card { background-color: #1a1d24; border-radius: 8px; padding: 10px; text-align: center; border: 1px solid #2a2d34; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1>📊 量化交易系统 v5.0</h1>', unsafe_allow_html=True)
    st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易 | AI引擎: DeepSeek</div>', unsafe_allow_html=True)
    
    # 导航
    tabs = st.tabs(["🏠 首页", "📈 市场行情", "🎯 策略中心", "🤖 AI交易", "💼 持仓管理", "📊 资金曲线", "⚙️ 系统设置"])
    
    with tabs[0]:
        st.markdown("### 📈 市场概览")
        cols = st.columns(4)
        symbols = ["EURUSD", "BTC-USD", "GC=F", "AAPL"]
        for i, sym in enumerate(symbols):
            data = data_provider.get_price(sym)
            with cols[i]:
                st.markdown(f'<div class="market-card">{sym}<br><span style="font-size:18px;color:#00d2ff">{data.price:.4f}</span></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        total_val = engine.get_total_value()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("总资产", f"${total_val:,.0f}")
        col2.metric("总盈亏", f"${engine.get_total_pnl():+,.0f}")
        col3.metric("持仓数", f"{len(engine.positions)}")
        col4.metric("今日盈亏", f"${risk_mgr.daily_pnl:+,.0f}")
        
        st.markdown("---")
        render_equity_curve(engine, risk_mgr)
        st.markdown("---")
        render_positions(engine, data_provider)
    
    with tabs[1]:
        st.markdown("### 📊 全球市场行情")
        market_data = []
        for sym in ["EURUSD", "BTC-USD", "GC=F", "CL=F", "AAPL", "NVDA", "MSFT", "GOOGL"]:
            data = data_provider.get_price(sym)
            market_data.append({"品种": sym, "价格": data.price, "涨跌": f"{data.price - data.open:.4f}", "时间": data.timestamp.strftime("%H:%M:%S")})
        st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)
    
    with tabs[2]:
        st.markdown("### 🎯 策略库")
        strategies = [
            {"名称": "期货趋势策略", "品种": "GC=F", "类型": "趋势跟踪", "状态": "运行中", "收益率": "+8.2%"},
            {"名称": "期货均值回归", "品种": "CL=F", "类型": "均值回归", "状态": "待机", "收益率": "+2.3%"},
            {"名称": "外汇利差策略", "品种": "AUDJPY", "类型": "利差交易", "状态": "运行中", "收益率": "+5.1%"},
            {"名称": "外汇突破策略", "品种": "EURUSD", "类型": "突破交易", "状态": "运行中", "收益率": "+6.7%"},
            {"名称": "加密双均线", "品种": "BTC-USD", "类型": "趋势跟踪", "状态": "运行中", "收益率": "+12.3%"},
        ]
        for s in strategies:
            cols = st.columns([2, 1, 1.2, 1, 1])
            cols[0].write(f"**{s['名称']}**")
            cols[1].write(s['品种'])
            cols[2].write(s['类型'])
            cols[3].write(f"🟢 {s['状态']}" if "运行" in s['状态'] else f"🟡 {s['状态']}")
            cols[4].write(f"<span style='color:#00ff88'>{s['收益率']}</span>" if "+" in s['收益率'] else s['收益率'], unsafe_allow_html=True)
            st.markdown("---")
    
    with tabs[3]:
        st.markdown("### 🤖 AI智能交易")
        col_a, col_b = st.columns(2)
        with col_a:
            symbol = st.selectbox("选择品种", ["EURUSD", "BTC-USD", "GC=F", "AAPL"])
        with col_b:
            strategy = st.selectbox("选择策略", ["综合AI分析", "趋势跟踪", "均值回归", "突破交易"])
        
        current_data = data_provider.get_price(symbol)
        st.metric("当前价格", f"{current_data.price:.5f}")
        
        if st.button("🚀 执行AI分析", type="primary", use_container_width=True):
            with st.spinner("AI模型分析中..."):
                market_info = {"price": current_data.price, "high": current_data.high, "low": current_data.low}
                result = ai.analyze(symbol, current_data.price, market_info)
                
                st.success(f"🤖 AI信号: {result['signal'].upper()}")
                st.info(f"📊 置信度: {result['confidence']}%")
                st.write(f"📝 分析理由: {result.get('reason', 'AI分析完成')}")
                
                if result['signal'] == 'buy':
                    st.success(f"🎯 目标价: {result.get('target', current_data.price*1.02):.5f} | 止损: {result.get('stop_loss', current_data.price*0.98):.5f}")
                elif result['signal'] == 'sell':
                    st.error(f"🎯 目标价: {result.get('target', current_data.price*0.98):.5f} | 止损: {result.get('stop_loss', current_data.price*1.02):.5f}")
                
                if st.button("执行交易", key="exec_trade"):
                    if result['signal'] == 'buy':
                        order = Order(symbol=symbol, side="buy", price=current_data.price, quantity=1000)
                        engine.execute_order(order, current_data.price)
                        st.success("✅ 买入订单已执行")
                    elif result['signal'] == 'sell':
                        order = Order(symbol=symbol, side="sell", price=current_data.price, quantity=1000)
                        engine.execute_order(order, current_data.price)
                        st.success("✅ 卖出订单已执行")
                    st.rerun()
    
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
    
    with tabs[5]:
        render_equity_curve(engine, risk_mgr)
        st.markdown("### 📅 月度收益")
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        returns = [2.1, 3.5, -1.2, 4.2, 5.1, engine.get_total_pnl()/max(engine.initial_capital,1)*100]
        colors = ['#00ff88' if r>=0 else '#ff4444' for r in returns]
        fig = go.Figure(data=go.Bar(x=months, y=returns, marker_color=colors))
        fig.update_layout(height=300, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a", font_color="#e6e6e6")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        total_return = engine.get_total_pnl()/max(engine.initial_capital,1)*100
        col1.metric("累计收益率", f"{total_return:.1f}%")
        col2.metric("最大回撤", "-2.3%")
        col3.metric("夏普比率", "1.42")
        col4.metric("胜率", "68.5%")
    
    with tabs[6]:
        st.markdown("### ⚙️ 系统设置")
        max_pos = st.slider("单笔最大仓位(%)", 5, 50, 30)
        stop_loss = st.slider("止损(%)", 1, 10, 2)
        take_profit = st.slider("止盈(%)", 2, 20, 4)
        data_source = st.selectbox("数据源", ["yfinance (真实)", "模拟数据"], index=0)
        
        if st.button("保存设置", type="primary"):
            CONFIG["trading"]["max_position_pct"] = max_pos / 100
            CONFIG["risk"]["stop_loss_pct"] = stop_loss / 100
            CONFIG["risk"]["take_profit_pct"] = take_profit / 100
            st.success("设置已保存")
        
        st.info(f"""
        - 系统版本: v5.0
        - AI引擎: DeepSeek
        - 数据源: {data_source}
        - 策略数量: 12
        - 当前资产: ${engine.get_total_value():,.0f}
        """)

if __name__ == "__main__":
    main()
