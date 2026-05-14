# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """
    首页 - 资金概览和实时行情
    """
    
    # 生成唯一的会话ID用于key
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    # ==================== 强制从 session_state 获取最新引擎 ====================
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    # ==================== 先刷新持仓（从数据库恢复） ====================
    if 引擎 and hasattr(引擎, '_恢复持仓'):
        引擎._恢复持仓()
        st.session_state.订单引擎 = 引擎
    
    # ==================== 更新持仓价格 ====================
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                结果 = 行情获取.获取价格(品种)
                if 结果 and hasattr(结果, '价格'):
                    当前价格 = 结果.价格
                    if 当前价格 and 当前价格 > 0 and 品种 in 引擎.持仓:
                        引擎.持仓[品种].当前价格 = 当前价格
            except Exception:
                pass
    
    # ==================== 计算资产 ====================
    初始资金 = getattr(引擎, '初始资金', 1000000)
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 引擎.可用资金
    
    总市值 = 0
    for 品种, pos in 引擎.持仓.items():
        数量 = getattr(pos, '数量', 0)
        成本价 = getattr(pos, '平均成本', 0)
        现价 = getattr(pos, '当前价格', 成本价)
        总市值 += 数量 * 现价
    
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
                        st.metric(品种["显示名"], f"¥{价格:,.0f}")
                    else:
                        st.metric(品种["显示名"], f"¥{价格:.2f}")
                else:
                    st.metric(品种["显示名"], "—")
            except Exception:
                st.metric(品种["显示名"], "—")
    
    # ==================== 快捷交易 ====================
    st.markdown("### 🚀 快捷交易")
    col1, col2 = st.columns(2)
    
    # ========== 买入 ==========
    with col1:
        st.markdown("#### 买入")
        可买品种列表 = ["EURUSD", "BTC-USD", "GC=F", "000001.SS", "AAPL"]
        st.caption(f"📊 可交易品种: {可买品种列表}")
        
        # 使用动态唯一key
        buy_key_suffix = st.session_state.page_key
        买入品种 = st.selectbox("选择品种", 可买品种列表, key=f"buy_symbol_{buy_key_suffix}")
        买入代码 = 转换品种代码(买入品种)
        
        # 仅用于显示预览价格
        try:
            预览价格 = 获取行情的价格(买入代码)
            if 预览价格 and 预览价格 > 0:
                st.caption(f"📌 参考价格: ¥{预览价格:.4f}")
            else:
                st.caption("📌 参考价格: 获取中...")
        except:
            st.caption("📌 参考价格: 获取失败")
        
        if 买入品种 == "000001.SS":
            单位提示, 默认数量, 步长 = "手 (1手=100股)", 1, 1
        elif 买入品种 == "EURUSD":
            单位提示, 默认数量, 步长 = "手 (1手=10000单位)", 1, 1
        elif 买入品种 == "BTC-USD":
            单位提示, 默认数量, 步长 = "个", 1, 1
        else:
            单位提示, 默认数量, 步长 = "股", 100, 10
        
        买入数量 = st.number_input(f"数量 ({单位提示})", min_value=1, value=默认数量, step=步长, key=f"buy_qty_{buy_key_suffix}")
        
        if 买入品种 == "000001.SS":
            实际股数 = 买入数量 * 100
            st.caption(f"预计花费: 按实时价格计算")
        elif 买入品种 == "EURUSD":
            实际单位 = 买入数量 * 10000
            st.caption(f"预计花费: 按实时价格计算")
        else:
            st.caption(f"预计花费: 按实时价格计算")
        
        if st.button("买入", type="primary", width="stretch", key=f"buy_btn_{buy_key_suffix}"):
            try:
                结果 = 引擎.买入(买入品种, None, 买入数量)
                if 结果.get("success"):
                    st.success(f"✅ 已买入 {买入品种} {买入数量} 单位")
                    st.session_state.订单引擎 = 引擎
                    # 刷新页面key避免重复
                    st.session_state.page_key = str(uuid.uuid4())[:8]
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"买入失败: {结果.get('error')}")
            except Exception as e:
                st.error(f"买入失败: {e}")
    
    # ========== 卖出 ==========
    with col2:
        st.markdown("#### 卖出")
        
        # 刷新持仓
        if hasattr(引擎, '_恢复持仓'):
            引擎._恢复持仓()
            st.session_state.订单引擎 = 引擎
        
        持仓品种列表 = list(引擎.持仓.keys())
        
        if 持仓品种列表:
            卖出选项 = []
            for 品种 in 持仓品种列表:
                pos = 引擎.持仓[品种]
                数量 = pos.数量
                if 品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                    卖出选项.append(f"{品种} (持仓: {数量:.4f})")
                else:
                    卖出选项.append(f"{品种} (持仓: {int(数量)})")
            
            # 使用动态唯一key
            sell_key_suffix = st.session_state.page_key
            卖出选项索引 = st.selectbox("选择持仓品种", range(len(卖出选项)), format_func=lambda i: 卖出选项[i], key=f"sell_select_{sell_key_suffix}")
            卖品种 = 持仓品种列表[卖出选项索引]
            pos = 引擎.持仓[卖品种]
            最大可卖数量 = pos.数量
            
            st.caption(f"持仓成本: ¥{pos.平均成本:.4f}")
            if 卖品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                st.caption(f"当前持仓数量: {最大可卖数量:.4f}")
            else:
                st.caption(f"当前持仓数量: {int(最大可卖数量)}")
            
            try:
                预览价格 = 获取行情的价格(卖品种)
                if 预览价格 and 预览价格 > 0:
                    st.caption(f"📌 参考价格: ¥{预览价格:.4f}")
                else:
                    st.caption("📌 参考价格: 获取中...")
            except:
                st.caption("📌 参考价格: 获取失败")
            
            if 卖品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                卖出数量 = st.number_input("数量", min_value=0.0, max_value=float(最大可卖数量), value=min(0.1, float(最大可卖数量)), step=0.01, format="%.4f", key=f"sell_qty_{sell_key_suffix}")
            else:
                max_qty = int(最大可卖数量)
                卖出数量 = st.number_input("数量", min_value=1, max_value=max_qty, value=min(1, max_qty), step=1, key=f"sell_qty_{sell_key_suffix}")
            
            if st.button("卖出", width="stretch", key=f"sell_btn_{sell_key_suffix}"):
                if 卖出数量 <= 0:
                    st.error("请输入数量")
                else:
                    try:
                        结果 = 引擎.卖出(卖品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {卖品种} {卖出数量} 单位")
                            if hasattr(引擎, '_恢复持仓'):
                                引擎._恢复持仓()
                            st.session_state.订单引擎 = 引擎
                            # 刷新页面key避免重复
                            st.session_state.page_key = str(uuid.uuid4())[:8]
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
        else:
            st.info("暂无持仓")
            st.selectbox("选择持仓品种", ["无持仓"], disabled=True, key="sell_disabled_home1")
            st.number_input("数量", min_value=1, value=100, disabled=True, key="sell_disabled_home2")
            st.button("卖出", disabled=True, width="stretch", key="sell_disabled_home3")


def 获取行情的价格(代码):
    try:
        结果 = 行情获取.获取价格(代码)
        if 结果 and hasattr(结果, '价格'):
            return 结果.价格
        return None
    except Exception as e:
        print(f"获取价格失败 {代码}: {e}")
        return None


def 转换品种代码(品种):
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
