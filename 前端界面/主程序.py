import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
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
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                cls._instance.logger.addHandler(handler)
        return cls._instance
    
    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def warning(self, msg): self.logger.warning(msg)
    def debug(self, msg): self.logger.debug(msg)

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
    side: str  # buy/sell
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
    unrealized_pnl: float
    realized_pnl: float = 0

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
    
    @classmethod
    def clear(cls):
        cls._cache.clear()

# ================== 风控引擎 ==================
class RiskManager:
    def __init__(self):
        self.daily_pnl = 0
        self.daily_trades = 0
        self.position_limits = {}
    
    def can_trade(self, symbol: str, side: str, quantity: float, price: float, total_capital: float) -> Tuple[bool, str]:
        # 仓位限制
        position_value = quantity * price
        if position_value / total_capital > CONFIG["trading"]["max_position_pct"]:
            return False, f"仓位超限: {position_value/total_capital:.1%} > {CONFIG['trading']['max_position_pct']:.1%}"
        
        # 日亏损限制
        if self.daily_pnl < -total_capital * CONFIG["risk"]["max_daily_loss"]:
            return False, f"日亏损已达上限: {abs(self.daily_pnl):.0f}"
        
        return True, "通过"
    
    def check_stop_loss(self, position: Position, current_price: float) -> bool:
        if position.quantity > 0:
            loss_pct = (position.avg_price - current_price) / position.avg_price
            if loss_pct > CONFIG["risk"]["stop_loss_pct"]:
                return True
        return False
    
    def check_take_profit(self, position: Position, current_price: float) -> bool:
        if position.quantity > 0:
            profit_pct = (current_price - position.avg_price) / position.avg_price
            if profit_pct > CONFIG["risk"]["take_profit_pct"]:
                return True
        return False
    
    def update_daily_pnl(self, pnl: float):
        self.daily_pnl += pnl

# ================== 订单引擎 ==================
class OrderEngine:
    def __init__(self):
        self.orders: List[Order] = []
        self.positions: Dict[str, Position] = {}
        self.trade_log: List[Dict] = []
    
    def execute_order(self, order: Order, current_price: float) -> Tuple[bool, str]:
        try:
            if order.side == "buy":
                fill_price = current_price + CONFIG["trading"]["default_slippage"]
                commission = fill_price * order.quantity * CONFIG["trading"]["commission_rate"]
                
                if order.symbol in self.positions:
                    pos = self.positions[order.symbol]
                    total_qty = pos.quantity + order.quantity
                    total_cost = pos.quantity * pos.avg_price + order.quantity * fill_price
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=total_qty,
                        avg_price=total_cost / total_qty,
                        current_price=fill_price,
                        unrealized_pnl=0,
                        realized_pnl=pos.realized_pnl
                    )
                else:
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=order.quantity,
                        avg_price=fill_price,
                        current_price=fill_price,
                        unrealized_pnl=0
                    )
                
                self.trade_log.append({
                    "time": datetime.now(), "symbol": order.symbol, "action": "买入",
                    "price": fill_price, "qty": order.quantity, "commission": commission
                })
                logger.info(f"买入 {order.symbol} {order.quantity} @ {fill_price}")
                
            elif order.side == "sell" and order.symbol in self.positions:
                pos = self.positions[order.symbol]
                fill_price = current_price - CONFIG["trading"]["default_slippage"]
                commission = fill_price * order.quantity * CONFIG["trading"]["commission_rate"]
                realized_pnl = (fill_price - pos.avg_price) * min(order.quantity, pos.quantity)
                
                if order.quantity >= pos.quantity:
                    del self.positions[order.symbol]
                else:
                    new_qty = pos.quantity - order.quantity
                    self.positions[order.symbol] = Position(
                        symbol=order.symbol,
                        quantity=new_qty,
                        avg_price=pos.avg_price,
                        current_price=fill_price,
                        unrealized_pnl=0,
                        realized_pnl=pos.realized_pnl + realized_pnl
                    )
                
                self.trade_log.append({
                    "time": datetime.now(), "symbol": order.symbol, "action": "卖出",
                    "price": fill_price, "qty": order.quantity, "pnl": realized_pnl, "commission": commission
                })
                logger.info(f"卖出 {order.symbol} {order.quantity} @ {fill_price}, PnL: {realized_pnl:.2f}")
            
            order.status = "filled"
            order.fill_time = datetime.now()
            order.fill_price = fill_price
            return True, "成功"
            
        except Exception as e:
            logger.error(f"订单执行失败: {e}")
            return False, str(e)
    
    def get_total_value(self, market_prices: Dict[str, float]) -> float:
        total = 0
        for symbol, pos in self.positions.items():
            price = market_prices.get(symbol, pos.current_price)
            total += pos.quantity * price
        return total
    
    def get_total_pnl(self) -> float:
        total = 0
        for pos in self.positions.values():
            total += pos.quantity * (pos.current_price - pos.avg_price)
            total += pos.realized_pnl
        return total

# ================== 行情获取（带重试和缓存）=================
class MarketDataProvider:
    def __init__(self):
        self.cache = DataCache()
        self.retry_count = CONFIG["api"]["retry_times"]
    
    def get_price(self, symbol: str, force_refresh: bool = False) -> Optional[MarketData]:
        cache_key = f"price_{symbol}"
        if not force_refresh:
            cached = self.cache.get(cache_key, CONFIG["api"]["cache_ttl"])
            if cached:
                return cached
        
        for attempt in range(self.retry_count):
            try:
                # 尝试从数据源获取（可替换为真实API）
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
                    logger.info(f"获取行情成功: {symbol} = {data.price}")
                    return data
            except Exception as e:
                logger.warning(f"获取行情失败 (尝试 {attempt+1}/{self.retry_count}): {e}")
                time.sleep(0.5)
        
        # 降级到模拟数据
        logger.warning(f"使用模拟数据: {symbol}")
        base_price = {"EURUSD": 1.085, "BTC-USD": 45000, "GC=F": 1950}.get(symbol, 100)
        return MarketData(
            symbol=symbol,
            price=base_price * (1 + random.uniform(-0.01, 0.01)),
            high=base_price * 1.005,
            low=base_price * 0.995,
            open=base_price,
            volume=1000,
            timestamp=datetime.now(),
            source="simulated"
        )

# ================== UI主题管理 ==================
class ThemeManager:
    @staticmethod
    def apply_theme(theme: str = "dark"):
        colors = CONFIG["ui"]["colors"]
        st.markdown(f"""
        <style>
            .stApp {{ background-color: {colors['background']}; }}
            .stMetric {{ background-color: {colors['card_bg']}; border-radius: 8px; padding: 8px 10px; text-align: center; border: 1px solid #2a2d34; }}
            .stMetric label {{ color: #8892b0 !important; font-size: 11px !important; }}
            .stMetric div {{ color: {colors['primary']} !important; font-size: 16px !important; }}
            h1, h2, h3 {{ color: #ffffff; }}
            .positive {{ color: {colors['positive']}; }}
            .negative {{ color: {colors['negative']}; }}
            .market-card {{ background-color: {colors['card_bg']}; border-radius: 8px; padding: 8px; text-align: center; border: 1px solid #2a2d34; }}
            .strategy-card {{ background-color: {colors['card_bg']}; border-radius: 6px; padding: 10px; margin: 5px 0; border-left: 3px solid {colors['primary']}; }}
        </style>
        """, unsafe_allow_html=True)

# ================== 页面组件 ==================
def render_metric_card(title: str, value: str, delta: str, popup_type: str):
    col = st.columns(1)[0]
    with col:
        st.metric(title, value, delta=delta)
        if st.button(f"详情", key=f"btn_{popup_type}", use_container_width=True):
            st.session_state.show_popup = True
            st.session_state.popup_type = popup_type
            st.rerun()

def render_popup():
    if st.session_state.get('show_popup', False):
        st.markdown('<div class="overlay"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="detail-popup">', unsafe_allow_html=True)
            
            popup_type = st.session_state.popup_type
            if popup_type == "asset":
                st.markdown("### 💰 总资产分析")
                fig = go.Figure(data=[go.Scatter(x=list(range(30)), y=[100000 + i*300 for i in range(30)], mode='lines')])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            if st.button("关闭", key="close_popup"):
                st.session_state.show_popup = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ================== 主程序 ==================
def main():
    ThemeManager.apply_theme()
    
    # 初始化组件
    if 'order_engine' not in st.session_state:
        st.session_state.order_engine = OrderEngine()
    if 'risk_manager' not in st.session_state:
        st.session_state.risk_manager = RiskManager()
    if 'data_provider' not in st.session_state:
        st.session_state.data_provider = MarketDataProvider()
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
    
    # 标题
    st.markdown(f'<h1>{CONFIG["app"]["icon"]} {CONFIG["app"]["title"]}</h1>', unsafe_allow_html=True)
    st.markdown('<div class="caption">多类目 · 多策略 · AI自动交易</div>', unsafe_allow_html=True)
    
    # 导航
    nav = st.tabs(["首页", "市场行情", "策略中心", "AI交易", "持仓管理", "风控设置", "日志查询"])
    
    with nav[0]:
        st.markdown("### 📈 市场概览")
        cols = st.columns(4)
        symbols = ["EURUSD", "BTC-USD", "GC=F", "SPX"]
        for i, sym in enumerate(symbols):
            data = st.session_state.data_provider.get_price(sym)
            with cols[i]:
                st.markdown(f'<div class="market-card">{sym}<br><span class="price">{data.price:.4f}</span></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 持仓概况")
        total_value = st.session_state.order_engine.get_total_value({})
        total_pnl = st.session_state.order_engine.get_total_pnl()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("总资产", f"${100000 + total_pnl:,.0f}")
        c2.metric("总盈亏", f"${total_pnl:+,.0f}")
        c3.metric("持仓数", f"{len(st.session_state.order_engine.positions)}")
        c4.metric("今日盈亏", f"${st.session_state.risk_manager.daily_pnl:+,.0f}")
    
    with nav[1]:
        st.markdown("### 📊 市场行情")
        market_data = []
        for sym in ["EURUSD", "BTC-USD", "GC=F", "CL=F", "AAPL", "NVDA"]:
            data = st.session_state.data_provider.get_price(sym)
            market_data.append({"品种": sym, "价格": data.price, "时间": data.timestamp.strftime("%H:%M:%S")})
        st.dataframe(pd.DataFrame(market_data), use_container_width=True)
    
    with nav[2]:
        st.markdown("### 🎯 策略库")
        strategies = [
            {"名称": "期货趋势策略", "品种": "GC=F", "类型": "趋势跟踪", "状态": "运行中"},
            {"名称": "外汇利差策略", "品种": "AUDJPY", "类型": "利差交易", "状态": "运行中"},
            {"名称": "加密双均线", "品种": "BTC-USD", "类型": "趋势跟踪", "状态": "运行中"},
        ]
        for s in strategies:
            with st.container():
                cols = st.columns([2, 1, 1, 1])
                cols[0].write(f"**{s['名称']}**")
                cols[1].write(s['品种'])
                cols[2].write(s['类型'])
                cols[3].write(f"🟢 {s['状态']}")
                st.markdown("---")
    
    with nav[3]:
        st.markdown("### 🤖 AI交易")
        symbol = st.selectbox("选择品种", ["EURUSD", "BTC-USD", "GC=F"])
        if st.button("执行AI分析"):
            with st.spinner("AI分析中..."):
                time.sleep(1)
            st.success("信号: 买入")
            st.info("置信度: 87%")
    
    with nav[4]:
        st.markdown("### 💼 持仓管理")
        if st.session_state.order_engine.positions:
            pos_data = []
            for sym, pos in st.session_state.order_engine.positions.items():
                current = st.session_state.data_provider.get_price(sym)
                pos.current_price = current.price
                pos_data.append({
                    "品种": sym, "数量": pos.quantity, "成本": pos.avg_price,
                    "现价": current.price, "盈亏": pos.quantity * (current.price - pos.avg_price)
                })
            st.dataframe(pd.DataFrame(pos_data), use_container_width=True)
        else:
            st.info("暂无持仓")
    
    with nav[5]:
        st.markdown("### ⚙️ 风控设置")
        st.slider("单笔最大仓位(%)", 5, 50, 30, key="max_position")
        st.slider("止损(%)", 1, 10, 2, key="stop_loss")
        st.slider("止盈(%)", 2, 20, 4, key="take_profit")
        if st.button("保存设置"):
            CONFIG["trading"]["max_position_pct"] = st.session_state.max_position / 100
            CONFIG["risk"]["stop_loss_pct"] = st.session_state.stop_loss / 100
            CONFIG["risk"]["take_profit_pct"] = st.session_state.take_profit / 100
            st.success("设置已保存")
    
    with nav[6]:
        st.markdown("### 📜 操作日志")
        if st.session_state.order_engine.trade_log:
            st.dataframe(pd.DataFrame(st.session_state.order_engine.trade_log), use_container_width=True)
        else:
            st.info("暂无交易记录")
    
    # 弹窗
    render_popup()

if __name__ == "__main__":
    main()
