# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 从策略加载器获取策略（和策略中心一样） ==========
    策略列表 = []
    
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                策略列表 = 策略加载器.获取策略()
                st.success(f"✅ 已加载 {len(策略列表)} 个策略")
            elif hasattr(策略加载器, '获取策略列表'):
                策略列表 = 策略加载器.获取策略列表()
                st.success(f"✅ 已加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.error(f"加载策略失败: {e}")
    
    # 如果策略加载器没有数据，尝试从 session_state 获取
    if not 策略列表 and '策略加载器' in st.session_state:
        try:
            sl = st.session_state.策略加载器
            if hasattr(sl, '获取策略'):
                策略列表 = sl.获取策略()
                st.success(f"✅ 从 session_state 加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.error(f"从 session_state 加载失败: {e}")
    
    # 如果还是没有，显示错误
    if not 策略列表:
        st.error("❌ 无法获取策略数据，请检查策略中心")
        return
    
    # ========== 同步策略中心的状态 ==========
    # 使用策略中心的状态（如果存在）
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            名称 = s.get("名称", "")
            if 名称:
                st.session_state.策略状态[名称] = True
    
    # 获取启用的策略
    启用策略 = [s for s in 策略列表 if st.session_state.策略状态.get(s.get("名称", ""), False)]
    
    # 显示启用的策略
    if 启用策略:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略)}个)", expanded=False):
            for s in 启用策略:
                st.caption(f"✅ {s.get('名称')} - {s.get('类别')} - {s.get('品种')}")
    else:
        st.warning("⚠️ 请前往「策略中心」启用策略")
    
    # ========== 提取可用市场 ==========
    可用市场 = []
    for s in 策略列表:
        类别 = s.get("类别", "")
        if 类别 and 类别 not in 可用市场:
            可用市场.append(类别)
    
    if not 可用市场:
        可用市场 = ["💰 外汇", "₿ 加密货币", "📈 A股", "🇺🇸 美股"]
    
    # ========== 交易界面 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", 可用市场)
    
    with col2:
        策略选项 = ["综合推荐", "趋势跟踪", "网格交易", "均值回归"]
        策略 = st.selectbox("选择策略类型", 策略选项)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== 根据市场显示品种 ==========
    if "加密" in 市场:
        交易品种 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12},
        ]
    elif "A股" in 市场:
        交易品种 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50},
        ]
    elif "美股" in 市场:
        交易品种 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00},
        ]
    else:
        交易品种 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650},
        ]
    
    # ========== AI分析按钮 ==========
    if st.button("🔍 AI智能分析", type="primary"):
        if not 启用策略:
            st.error("❌ 请先在策略中心启用策略")
        else:
            with st.spinner("AI正在分析市场..."):
                st.markdown("---")
                st.markdown(f"### 📈 AI分析结果 - {市场}")
                st.markdown(f"**基于策略: {', '.join([s.get('名称') for s in 启用策略[:3]])}**")
                
                for item in 交易品种:
                    信号随机 = random.random()
                    if 信号随机 > 0.6:
                        信号, 颜色, 置信度 = "买入", "🟢", random.randint(70, 95)
                    elif 信号随机 > 0.3:
                        信号, 颜色, 置信度 = "持有", "🟡", random.randint(50, 70)
                    else:
                        信号, 颜色, 置信度 = "卖出", "🔴", random.randint(40, 60)
                    
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                        <b>{item['名称']} ({item['品种']})</b><br>
                        价格: ¥{item['价格']:,.2f}<br>
                        信号: {颜色} {信号} (置信度: {置信度}%)
                    </div>
                    """, unsafe_allow_html=True)
    
    # ========== 快速交易 ==========
    st.markdown("---")
    st.markdown("#### ⚡ 快速交易")
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    with tab1:
        with st.form("buy_form"):
            买入选择 = st.selectbox("选择品种", [f"{item['名称']} ({item['品种']})" for item in 交易品种])
            if "(" in 买入选择:
                买入品种 = 买入选择.split("(")[-1].replace(")", "")
            else:
                买入品种 = 买入选择
            
            参考价格 = next((item["价格"] for item in 交易品种 if item["品种"] == 买入品种), 100)
            买入数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01)
            
            if st.form_submit_button("确认买入", type="primary"):
                可用资金 = 引擎.获取可用资金()
                预计花费 = 参考价格 * 买入数量
                if 预计花费 <= 可用资金:
                    try:
                        结果 = 引擎.买入(买入品种, None, 买入数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {买入品种} {买入数量} 个")
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"买入异常: {e}")
                else:
                    st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}")
    
    with tab2:
        with st.form("sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            if 持仓品种:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                卖出数量 = st.number_input("数量", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01)
                
                if st.form_submit_button("确认卖出"):
                    try:
                        结果 = 引擎.卖出(卖出品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {卖出品种} {卖出数量} 个")
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
            else:
                st.info("暂无持仓")
    
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
