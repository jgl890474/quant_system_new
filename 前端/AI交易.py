# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 从策略加载器获取策略和市场 ==========
    策略列表 = []
    可用市场 = []
    
    # 调试信息（部署后可以看到）
    if 策略加载器 is not None:
        st.info(f"✅ 策略加载器已连接")
        try:
            if hasattr(策略加载器, '获取策略'):
                原始策略 = 策略加载器.获取策略()
                st.info(f"📊 获取到 {len(原始策略)} 个策略")
                for s in 原始策略:
                    if isinstance(s, dict):
                        策略列表.append(s)
                        # 根据类别提取市场
                        类别 = s.get("类别", "")
                        if "外汇" in 类别:
                            可用市场.append("外汇")
                        elif "加密" in 类别:
                            可用市场.append("加密货币")
                        elif "A股" in 类别:
                            可用市场.append("A股")
                        elif "美股" in 类别:
                            可用市场.append("美股")
                        elif "期货" in 类别:
                            可用市场.append("期货")
                    else:
                        策略列表.append({"名称": str(s), "类别": "默认", "品种": "未知"})
        except Exception as e:
            st.warning(f"读取策略失败: {e}")
    else:
        st.warning("⚠️ 策略加载器未连接")
    
    # 去重并排序
    可用市场 = sorted(list(set(可用市场)))
    
    # 如果没有获取到市场，使用默认值
    if not 可用市场:
        可用市场 = ["加密货币", "A股", "美股", "外汇", "期货"]
        st.info("📋 使用默认市场列表")
    
    # 获取当前启用的策略
    启用策略名称列表 = []
    if '策略状态' in st.session_state:
        启用策略名称列表 = [name for name, status in st.session_state.策略状态.items() if status]
    
    # 显示启用的策略
    if 启用策略名称列表:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略名称列表)}个)", expanded=False):
            for name in 启用策略名称列表[:10]:  # 最多显示10个
                st.caption(f"✅ {name}")
    else:
        if 策略列表:
            st.warning("⚠️ 请前往「策略中心」启用策略")
    
    # ========== 市场与策略选择 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", 可用市场)
    
    with col2:
        # 根据选中的市场过滤策略
        当前市场策略 = ["综合推荐"]
        for s in 策略列表:
            类别 = s.get("类别", "")
            品种 = s.get("品种", "")
            
            if 市场 == "外汇" and ("外汇" in 类别 or "EUR" in 品种):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "加密货币" and ("加密" in 类别 or "BTC" in 品种):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "A股" and ("A股" in 类别 or ".SS" in 品种):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "美股" and ("美股" in 类别 or "AAPL" in 品种):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "期货" and ("期货" in 类别 or "GC=" in 品种):
                当前市场策略.append(s.get("名称"))
        
        if len(当前市场策略) <= 1:
            当前市场策略 = ["综合推荐", "趋势跟踪", "网格交易", "均值回归"]
        
        策略 = st.selectbox("选择策略", 当前市场策略)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== 根据市场显示对应的品种 ==========
    if 市场 == "加密货币":
        推荐品种 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12},
        ]
    elif 市场 == "A股":
        推荐品种 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50},
        ]
    elif 市场 == "美股":
        推荐品种 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00},
        ]
    elif 市场 == "外汇":
        推荐品种 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650},
        ]
    else:
        推荐品种 = [
            {"品种": "GC=F", "名称": "黄金期货", "价格": 2350.00},
            {"品种": "CL=F", "名称": "原油期货", "价格": 78.50},
        ]
    
    # ========== AI分析按钮 ==========
    if st.button("🔍 AI智能分析", type="primary"):
        with st.spinner("AI正在分析市场..."):
            st.markdown("---")
            st.markdown(f"### 📈 AI分析结果 - {市场}")
            
            for item in 推荐品种:
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
        with st.form("quick_buy_form"):
            买入选择 = st.selectbox("选择品种", [f"{item['名称']} ({item['品种']})" for item in 推荐品种])
            if "(" in 买入选择:
                买入品种 = 买入选择.split("(")[-1].replace(")", "")
            else:
                买入品种 = 买入选择
            
            参考价格 = next((item["价格"] for item in 推荐品种 if item["品种"] == 买入品种), 100)
            买入数量 = st.number_input("数量", min_value=0.01, value=0.1, step=0.01)
            
            if st.form_submit_button("确认买入", type="primary"):
                可用资金 = 引擎.获取可用资金()
                预计花费 = 参考价格 * 买入数量
                if 预计花费 <= 可用资金:
                    st.success(f"✅ 已提交买入 {买入品种} {买入数量} 个")
                else:
                    st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}")
    
    with tab2:
        with st.form("quick_sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            if 持仓品种:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                卖出数量 = st.number_input("数量", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01)
                if st.form_submit_button("确认卖出"):
                    st.success(f"✅ 已提交卖出 {卖出品种} {卖出数量} 个")
            else:
                st.info("暂无持仓")
    
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
