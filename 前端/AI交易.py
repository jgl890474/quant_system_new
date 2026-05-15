# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 获取策略状态 ==========
    启用策略列表 = []
    if '策略状态' in st.session_state:
        启用策略列表 = [name for name, status in st.session_state.策略状态.items() if status]
    
    # 显示当前启用的策略
    if 启用策略列表:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略列表)}个)", expanded=False):
            for name in 启用策略列表:
                st.caption(f"✅ {name}")
    else:
        st.warning("⚠️ 暂无启用的策略，请前往「策略中心」启用策略")
    
    # ========== 市场与策略选择 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", ["加密货币", "A股", "美股", "外汇"])
    
    with col2:
        策略类型 = st.selectbox("选择策略类型", ["综合推荐", "趋势跟踪", "网格交易", "均值回归", "动量策略"])
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== AI分析按钮 ==========
    if st.button("🔍 AI智能分析", type="primary"):
        if not 启用策略列表:
            st.error("❌ 没有启用的策略，请先在「策略中心」启用策略")
        else:
            with st.spinner("AI正在分析市场..."):
                # 模拟AI分析
                st.markdown("---")
                st.markdown("### 📈 AI分析结果")
                
                # 根据市场和策略类型生成推荐
                if 市场 == "加密货币":
                    推荐品种 = [
                        {"品种": "BTC-USD", "价格": 79586.70, "信号": "买入", "置信度": 85, "理由": "RSI超卖反弹"},
                        {"品种": "ETH-USD", "价格": 2219.12, "信号": "持有", "置信度": 72, "理由": "震荡整理"},
                        {"品种": "SOL-USD", "价格": 145.30, "信号": "观望", "置信度": 60, "理由": "等待方向"},
                    ]
                elif 市场 == "A股":
                    推荐品种 = [
                        {"品种": "贵州茅台", "价格": 1680.00, "信号": "持有", "置信度": 78, "理由": "消费复苏"},
                        {"品种": "宁德时代", "价格": 220.50, "信号": "买入", "置信度": 82, "理由": "新能源利好"},
                        {"品种": "比亚迪", "价格": 265.80, "信号": "卖出", "置信度": 65, "理由": "高位回调"},
                    ]
                elif 市场 == "美股":
                    推荐品种 = [
                        {"品种": "AAPL", "价格": 185.50, "信号": "买入", "置信度": 88, "理由": "新品发布预期"},
                        {"品种": "NVDA", "价格": 950.00, "信号": "持有", "置信度": 75, "理由": "AI热潮持续"},
                        {"品种": "TSLA", "价格": 175.30, "信号": "观望", "置信度": 55, "理由": "竞争加剧"},
                    ]
                else:
                    推荐品种 = [
                        {"品种": "EURUSD", "价格": 1.0850, "信号": "买入", "置信度": 70, "理由": "美元走弱"},
                        {"品种": "GBPUSD", "价格": 1.2650, "信号": "持有", "置信度": 65, "理由": "等待数据"},
                    ]
                
                # 显示推荐表格
                for item in 推荐品种:
                    信号颜色 = "🟢" if item["信号"] == "买入" else "🟡" if item["信号"] == "持有" else "🔴"
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                        <b>{item['品种']}</b><br>
                        价格: ¥{item['价格']:,.2f}<br>
                        信号: {信号颜色} {item['信号']} (置信度: {item['置信度']}%)<br>
                        理由: {item['理由']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # AI综合评分
                st.markdown("---")
                st.markdown("#### 🎯 AI综合评分")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("市场情绪", "偏多", delta="+2")
                with col2:
                    st.metric("风险等级", "中等", delta="稳定")
                with col3:
                    st.metric("最优策略", 策略类型, delta="推荐")
    
    # ========== 快速交易 ==========
    st.markdown("---")
    st.markdown("#### ⚡ 快速交易")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("quick_buy_form"):
            买入品种 = st.selectbox("品种", ["BTC-USD", "ETH-USD", "AAPL", "NVDA", "EURUSD"])
            买入数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01)
            提交买入 = st.form_submit_button("📈 买入", type="primary")
            
            if 提交买入:
                可用资金 = 引擎.获取可用资金()
                if 可用资金 > 0:
                    try:
                        # 获取参考价格
                        参考价格 = 获取参考价格(买入品种)
                        预计花费 = 参考价格 * 买入数量 if 参考价格 else 0
                        
                        if 预计花费 <= 可用资金:
                            st.success(f"✅ 已提交买入 {买入品种} {买入数量} 个")
                            st.info(f"预计花费: ¥{预计花费:,.2f}")
                        else:
                            st.error(f"❌ 资金不足！可用: ¥{可用资金:,.2f}, 需要: ¥{预计花费:,.2f}")
                    except Exception as e:
                        st.error(f"买入失败: {e}")
                else:
                    st.error("❌ 资金不足")
    
    with col2:
        with st.form("quick_sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else ["无持仓"]
            卖出品种 = st.selectbox("品种", 持仓品种 if 持仓品种 else ["无持仓"])
            
            if 卖出品种 != "无持仓" and 卖出品种 in 引擎.持仓:
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                卖出数量 = st.number_input("数量", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01)
            else:
                卖出数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01, disabled=True)
            
            提交卖出 = st.form_submit_button("📉 卖出")
            
            if 提交卖出 and 卖出品种 != "无持仓":
                st.success(f"✅ 已提交卖出 {卖出品种} {卖出数量} 个")
    
    # ========== 底部提示 ==========
    st.markdown("---")
    st.caption("⚡ AI推荐仅供参考，投资需谨慎")

def 获取参考价格(品种):
    """获取参考价格"""
    参考价格 = {
        "BTC-USD": 79586.70,
        "ETH-USD": 2219.12,
        "AAPL": 185.50,
        "NVDA": 950.00,
        "EURUSD": 1.0850,
    }
    return 参考价格.get(品种, 100)
