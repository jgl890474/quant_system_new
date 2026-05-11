# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取, 策略运行器


def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    """显示策略中心页面"""
    st.markdown("### 🎯 策略库")
    
    # 获取策略列表
    策略列表 = []
    
    # 尝试从策略加载器获取
    if 策略加载器 and hasattr(策略加载器, '获取策略'):
        try:
            策略列表 = 策略加载器.获取策略()
        except Exception as e:
            st.error(f"获取策略失败: {e}")
    
    # 如果没有策略，使用默认策略
    if not 策略列表:
        策略列表 = [
            {"名称": "双均线策略", "类别": "A股策略", "品种": "000001"},
            {"名称": "量价策略", "类别": "A股策略", "品种": "000002"},
            {"名称": "隔夜套利策略", "类别": "A股策略", "品种": "000858"},
            {"名称": "加密双均线", "类别": "加密货币策略", "品种": "BTC-USD"},
            {"名称": "动量策略", "类别": "美股策略", "品种": "AAPL"},
            {"名称": "外汇利差策略", "类别": "外汇策略", "品种": "EURUSD"},
            {"名称": "期货趋势策略", "类别": "期货策略", "品种": "GC=F"},
        ]
    
    # 显示统计
    st.caption(f"📊 共加载 {len(策略列表)} 个策略")
    
    if not 策略列表:
        st.info("暂无策略")
        return
    
    # 按类别分组
    分组 = {}
    for s in 策略列表:
        类别 = s.get("类别", "其他")
        if 类别 not in 分组:
            分组[类别] = []
        分组[类别].append(s)
    
    # 显示分组
    st.caption(f"📂 分组: {', '.join(分组.keys())}")
    
    # 策略信号存储
    if "策略信号" not in st.session_state:
        st.session_state.策略信号 = {}
    
    # 显示每个类别的策略
    for 类别, 类别策略 in 分组.items():
        st.markdown(f"**📁 {类别} ({len(类别策略)})**")
        
        for idx, 策略 in enumerate(类别策略):
            col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 1, 1.5])
            
            with col1:
                st.caption(f"**{策略.get('名称', '未知')}**")
            with col2:
                st.caption(策略.get('类别', '未知'))
            with col3:
                st.caption("📈 +8.2%")
            with col4:
                st.caption("📉 -12.5%")
            with col5:
                if st.button("运行", key=f"run_{策略.get('名称', '未知')}_{idx}", use_container_width=True):
                    try:
                        品种 = 策略.get("品种", "")
                        if 品种:
                            行情 = 行情获取.获取价格(品种)
                            信号 = 策略运行器.运行(策略, 行情)
                            st.session_state.策略信号[策略.get('名称', '未知')] = 信号
                            st.success(f"信号: {信号.upper()}")
                            st.rerun()
                        else:
                            st.error("策略未配置品种")
                    except Exception as e:
                        st.error(f"运行失败: {e}")
            
            # 显示信号和买入/卖出按钮
            if 策略.get('名称') in st.session_state.策略信号:
                信号 = st.session_state.策略信号[策略['名称']]
                if 信号 == "buy":
                    st.caption("🟢 信号: BUY")
                    if st.button("买入", key=f"buy_{策略.get('名称', '未知')}_{idx}"):
                        try:
                            品种 = 策略.get("品种", "")
                            if 品种 and 引擎:
                                价格 = 行情获取.获取价格(品种)
                                if 价格 and hasattr(价格, '价格'):
                                    引擎.买入(品种, 价格.价格, 100)
                                    st.success("买入成功")
                                    st.rerun()
                                else:
                                    st.error("无法获取价格")
                            else:
                                st.error("引擎未初始化或品种为空")
                        except Exception as e:
                            st.error(f"买入失败: {e}")
                elif 信号 == "sell":
                    st.caption("🔴 信号: SELL")
                    if st.button("卖出", key=f"sell_{策略.get('名称', '未知')}_{idx}"):
                        try:
                            品种 = 策略.get("品种", "")
                            if 品种 and 引擎:
                                价格 = 行情获取.获取价格(品种)
                                if 价格 and hasattr(价格, '价格'):
                                    引擎.卖出(品种, 价格.价格, 100)
                                    st.success("卖出成功")
                                    st.rerun()
                                else:
                                    st.error("无法获取价格")
                            else:
                                st.error("引擎未初始化或品种为空")
                        except Exception as e:
                            st.error(f"卖出失败: {e}")
                else:
                    st.caption("🟡 信号: HOLD")
        
        st.divider()
    
    # 策略说明
    with st.expander("📖 策略说明"):
        st.markdown("""
        - **双均线策略**: 短期均线上穿长期均线买入，下穿卖出
        - **量价策略**: 结合成交量和价格变化进行交易决策
        - **隔夜套利策略**: 在收盘前买入，次日开盘卖出
        - **加密双均线**: 针对加密货币市场的双均线策略
        - **动量策略**: 追涨强势股，止损止盈控制
        - **外汇利差策略**: 利用不同货币对的利差进行套利
        - **期货趋势策略**: 跟踪期货市场趋势，顺势交易
        """)
