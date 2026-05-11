# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """
    首页 - 资金概览和实时行情
    """
    
    # ==================== 先更新所有持仓的当前价格 ====================
    if hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                结果 = 行情获取.获取价格(品种)
                if 结果 and hasattr(结果, '价格'):
                    当前价格 = 结果.价格
                    if 当前价格 and 当前价格 > 0:
                        if hasattr(引擎, '更新持仓价格'):
                            引擎.更新持仓价格(品种, 当前价格)
                        else:
                            if 品种 in 引擎.持仓:
                                引擎.持仓[品种].当前价格 = 当前价格
            except Exception:
                pass
    
    # ==================== 获取基础数据 ====================
    初始资金 = 引擎.获取初始资金() if hasattr(引擎, '获取初始资金') else 1000000
    可用资金 = 引擎.获取可用资金()
    
    # 计算持仓市值（按现价）和总成本
    总市值 = 0
    
    for 品种, pos in 引擎.持仓.items():
        数量 = pos.数量
        成本价 = pos.平均成本
        现价 = getattr(pos, '当前价格', 成本价)
        总市值 += 数量 * 现价
    
    # 正确计算各项指标
    持仓市值 = 总市值
    总资产 = 可用资金 + 持仓市值
    总盈亏 = 总资产 - 初始资金
    收益率 = (总盈亏 / 初始资金 * 100) if 初始资金 > 0 else 0
    
    # ==================== 指标卡片 ====================
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总资产", f"¥{总资产:,.0f}")
    with col2:
        st.metric("可用资金", f"¥{可用资金:,.0f}")
    with col3:
        st.metric("持仓市值", f"¥{持仓市值:,.0f}")
    with col4:
        st.metric("总盈亏", f"¥{总盈亏:+,.0f}", delta=f"{收益率:+.1f}%")
    
    # ==================== 实时行情 ====================
    st.markdown("### 📈 实时行情")
    
    # 定义行情品种及其对应的代码格式
    行情品种配置 = [
        {"显示名": "AAPL", "代码": "AAPL"},
        {"显示名": "BTC-USD", "代码": "BTC-USD"},
        {"显示名": "GC=F", "代码": "GC=F"},
        {"显示名": "EURUSD", "代码": "EURUSD=X"},
        {"显示名": "TSLA", "代码": "TSLA"},
        {"显示名": "NVDA", "代码": "NVDA"},
    ]
    
    行情列 = st.columns(len(行情品种配置))
    
    for i, 品种 in enumerate(行情品种配置):
        with 行情列[i]:
            try:
                价格 = 获取行情的价格(品种["代码"])
                if 价格 and 价格 > 0:
                    if "BTC" in 品种["代码"]:
                        st.metric(品种["显示名"], f"${价格:,.0f}")
                    else:
                        st.metric(品种["显示名"], f"${价格:.2f}")
                else:
                    st.metric(品种["显示名"], "—")
            except Exception as e:
                st.metric(品种["显示名"], "—")
    
    # ==================== 快捷交易 ====================
    st.markdown("### 🚀 快捷交易")
    
    col1, col2 = st.columns(2)
    
    # ========== 买入区域 ==========
    with col1:
        st.markdown("#### 买入")
        
        可买品种列表 = ["EURUSD", "BTC-USD", "GC=F", "000001.SS", "AAPL"]
        st.caption(f"📊 可交易品种: {可买品种列表}")
        
        买入品种 = st.selectbox("选择品种", 可买品种列表, key="buy_symbol_select")
        
        # 获取买入品种对应的代码格式
        买入代码 = 转换品种代码(买入品种)
        
        try:
            当前买入价 = 获取行情的价格(买入代码)
            st.caption(f"当前价格: ${当前买入价:.4f}" if 当前买入价 and 当前买入价 > 0 else "获取价格失败")
        except:
            当前买入价 = 0
            st.caption("获取价格失败")
        
        if 买入品种 == "000001.SS":
            单位提示 = "手 (1手=100股)"
            默认数量 = 1
            步长 = 1
        elif 买入品种 == "EURUSD":
            单位提示 = "手 (1手=10000单位)"
            默认数量 = 1
            步长 = 1
        elif 买入品种 == "BTC-USD":
            单位提示 = "个"
            默认数量 = 1
            步长 = 1
        else:
            单位提示 = "股"
            默认数量 = 100
            步长 = 10
        
        买入数量 = st.number_input(
            f"数量 ({单位提示})", 
            min_value=1, 
            value=默认数量, 
            step=步长, 
            key="buy_qty_input"
        )
        
        if 买入品种 == "000001.SS":
            实际股数 = 买入数量 * 100
            预计花费 = 当前买入价 * 实际股数 if 当前买入价 else 0
            st.caption(f"预计花费: ¥{预计花费:,.0f} (实际股数: {实际股数}股)" if 当前买入价 else "无法计算价格")
        elif 买入品种 == "EURUSD":
            实际单位 = 买入数量 * 10000
            预计花费 = 当前买入价 * 实际单位 if 当前买入价 else 0
            st.caption(f"预计花费: ¥{预计花费:,.0f} (实际单位: {实际单位})" if 当前买入价 else "无法计算价格")
        else:
            预计花费 = 当前买入价 * 买入数量 if 当前买入价 else 0
            st.caption(f"预计花费: ¥{预计花费:,.0f}" if 当前买入价 else "无法计算价格")
        
        # 修复：use_container_width=True -> width='stretch'
        if st.button("买入", type="primary", width='stretch', key="buy_button"):
            if not 当前买入价 or 当前买入价 <= 0:
                st.error("无法获取价格，请稍后再试")
            else:
                try:
                    引擎.买入(买入品种, 当前买入价, 买入数量)
                    st.success(f"✅ 已买入 {买入品种} {买入数量} 单位")
                    st.rerun()
                except Exception as e:
                    st.error(f"买入失败: {e}")
    
    # ========== 卖出区域 ==========
    with col2:
        st.markdown("#### 卖出")
        
        持仓品种列表 = list(引擎.持仓.keys())
        
        if 持仓品种列表:
            卖出选项 = [f"{品种} (持仓: {int(引擎.持仓[品种].数量)}股/单位)" for 品种 in 持仓品种列表]
            卖出选项索引 = st.selectbox(
                "选择持仓品种", 
                range(len(卖出选项)), 
                format_func=lambda i: 卖出选项[i], 
                key="sell_symbol_select"
            )
            卖品种 = 持仓品种列表[卖出选项索引]
            最大可卖数量 = int(引擎.持仓[卖品种].数量)
            
            st.caption(f"持仓成本: ${引擎.持仓[卖品种].平均成本:.4f}")
            
            try:
                当前卖出价 = 获取行情的价格(卖品种)
                st.caption(f"当前价格: ${当前卖出价:.4f}" if 当前卖出价 and 当前卖出价 > 0 else "获取价格失败")
            except:
                当前卖出价 = 0
                st.caption("获取价格失败")
            
            卖出数量 = st.number_input(
                "数量", 
                min_value=1, 
                max_value=最大可卖数量, 
                value=min(100, 最大可卖数量), 
                step=10, 
                key="sell_qty_input"
            )
            
            预计收入 = 当前卖出价 * 卖出数量 if 当前卖出价 else 0
            st.caption(f"预计收入: ¥{预计收入:,.0f}" if 当前卖出价 else "无法计算收入")
            
            # 修复：use_container_width=True -> width='stretch'
            if st.button("卖出", width='stretch', key="sell_button"):
                if not 当前卖出价 or 当前卖出价 <= 0:
                    st.error("无法获取价格，请稍后再试")
                else:
                    try:
                        引擎.卖出(卖品种, 当前卖出价, 卖出数量)
                        st.success(f"✅ 已卖出 {卖品种} {卖出数量} 单位")
                        st.rerun()
                    except Exception as e:
                        st.error(f"卖出失败: {e}")
        else:
            st.info("暂无持仓")
            st.selectbox("选择持仓品种", ["无持仓"], disabled=True, key="sell_symbol_disabled")
            st.number_input("数量", min_value=1, value=100, disabled=True, key="sell_qty_disabled")
            # 修复：use_container_width=True -> width='stretch'
            st.button("卖出", disabled=True, width='stretch', key="sell_button_disabled")


# ==================== 辅助函数 ====================
def 获取行情的价格(代码):
    """
    获取行情价格，支持多种代码格式
    """
    try:
        # 优先使用行情获取模块
        结果 = 行情获取.获取价格(代码)
        if 结果 and hasattr(结果, '价格'):
            return 结果.价格
        
        # 如果失败，尝试使用 yfinance 直接获取
        import yfinance as yf
        ticker = yf.Ticker(代码)
        
        # 尝试获取实时价格
        try:
            # 方法1：通过 info
            info = ticker.info
            if 'regularMarketPrice' in info:
                return info['regularMarketPrice']
            if 'currentPrice' in info:
                return info['currentPrice']
        except:
            pass
        
        # 方法2：通过历史数据
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
        
        return None
    except Exception as e:
        print(f"获取 {代码} 价格失败: {e}")
        return None


def 转换品种代码(品种):
    """
    将显示品种转换为yfinance可识别的代码
    """
    代码映射 = {
        "EURUSD": "EURUSD=X",
        "BTC-USD": "BTC-USD",
        "GC=F": "GC=F",
        "AAPL": "AAPL",
        "TSLA": "TSLA",
        "NVDA": "NVDA",
        "000001.SS": "000001.SS",
    }
    return 代码映射.get(品种, 品种)
