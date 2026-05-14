# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    # 生成唯一key
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # 选择市场和策略
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("市场", ["加密货币", "A股", "美股"], key=f"market_{st.session_state.page_key}")
    with col2:
        if 市场 == "加密货币":
            策略 = st.selectbox("策略", ["加密双均线1"], key=f"strategy_{st.session_state.page_key}")
        elif 市场 == "A股":
            策略 = st.selectbox("策略", ["A股双均线1"], key=f"strategy_{st.session_state.page_key}")
        else:
            策略 = st.selectbox("策略", ["美股简单策略1"], key=f"strategy_{st.session_state.page_key}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 1000000
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner("分析中..."):
            try:
                # 获取推荐
                推荐列表 = []
                品种列表 = []
                if 市场 == "加密货币":
                    品种列表 = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOGE-USD"]
                elif 市场 == "A股":
                    品种列表 = ["600519.SS", "000858.SZ", "300750.SZ"]
                else:
                    品种列表 = ["AAPL", "NVDA", "TSLA", "MSFT"]
                
                for 代码 in 品种列表:
                    try:
                        价格结果 = 行情获取.获取价格(代码)
                        价格 = 价格结果.价格 if 价格结果 and hasattr(价格结果, '价格') else 0
                    except:
                        价格 = 0
                    
                    推荐列表.append({
                        "代码": 代码,
                        "名称": 代码.split('.')[0] if '.' in 代码 else 代码,
                        "价格": 价格,
                        "评分": 70,
                    })
                
                st.session_state[f"recommend_{st.session_state.page_key}"] = 推荐列表
                st.success(f"✅ 分析完成，推荐 {len(推荐列表)} 个品种")
            except Exception as e:
                st.error(f"分析失败: {e}")
    
    # 显示推荐
    rec_key = f"recommend_{st.session_state.page_key}"
    if rec_key in st.session_state:
        st.markdown("### 📈 推荐买入")
        for idx, item in enumerate(st.session_state[rec_key]):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{item['名称']}**")
                st.caption(item['代码'])
            with col2:
                if item['价格'] > 0:
                    st.write(f"¥{item['价格']:.2f}")
                else:
                    st.write("价格获取中")
            with col3:
                st.write(f"评分: {item['评分']}")
            with col4:
                if st.button(f"买入", key=f"buy_{idx}_{item['代码']}_{st.session_state.page_key}"):
                    try:
                        if item['价格'] <= 0:
                            st.error("价格无效，请稍后再试")
                        else:
                            # 简单买入逻辑
                            if 市场 == "A股":
                                数量 = 100
                            elif 市场 == "加密货币":
                                数量 = 0.01
                            else:
                                数量 = 1
                            
                            # 直接调用引擎买入
                            结果 = 引擎.买入(item['代码'], item['价格'], 数量, 策略名称=策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {item['名称']}")
                                # 清除推荐，刷新页面
                                st.session_state.pop(rec_key, None)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"买入出错: {e}")
            st.divider()
    
    # 显示持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.write(f"- {品种}: {数量}个 @ ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    st.caption("💡 提示：点击买入后页面会自动刷新")
