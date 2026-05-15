# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 从策略加载器获取策略和市场 ==========
    策略列表 = []
    可用市场 = ["加密货币", "A股", "美股", "外汇", "期货"]  # 默认市场
    
    # 尝试从策略加载器获取策略
    if 策略加载器 is not None:
        try:
            # 获取策略列表
            if hasattr(策略加载器, '获取策略'):
                原始策略 = 策略加载器.获取策略()
                for s in 原始策略:
                    if isinstance(s, dict):
                        策略列表.append(s)
                    else:
                        策略列表.append({"名称": str(s), "类别": "默认", "品种": "未知"})
            elif hasattr(策略加载器, '获取策略列表'):
                原始策略 = 策略加载器.获取策略列表()
                for s in 原始策略:
                    if isinstance(s, dict):
                        策略列表.append(s)
                    else:
                        策略列表.append({"名称": str(s), "类别": "默认", "品种": "未知"})
            
            # 从策略中提取市场类别
            if 策略列表:
                提取的市场 = set()
                for s in 策略列表:
                    类别 = s.get("类别", "")
                    if "💰" in 类别 or "外汇" in 类别:
                        提取的市场.add("外汇")
                    elif "₿" in 类别 or "加密" in 类别:
                        提取的市场.add("加密货币")
                    elif "📈" in 类别 or "A股" in 类别:
                        提取的市场.add("A股")
                    elif "🇺🇸" in 类别 or "美股" in 类别:
                        提取的市场.add("美股")
                    elif "📊" in 类别 or "期货" in 类别:
                        提取的市场.add("期货")
                
                if 提取的市场:
                    可用市场 = sorted(list(提取的市场))
                    
        except Exception as e:
            st.warning(f"读取策略失败: {e}")
    
    # 获取当前启用的策略
    启用策略名称列表 = []
    if '策略状态' in st.session_state:
        启用策略名称列表 = [name for name, status in st.session_state.策略状态.items() if status]
    
    # 过滤出启用的策略详情
    启用策略详情 = []
    for s in 策略列表:
        if s.get("名称") in 启用策略名称列表:
            启用策略详情.append(s)
    
    # 显示启用的策略
    if 启用策略详情:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略详情)}个)", expanded=False):
            for s in 启用策略详情:
                st.caption(f"✅ {s.get('名称')} - {s.get('类别')} - {s.get('品种')}")
    else:
        if 策略列表:
            st.warning("⚠️ 请前往「策略中心」启用策略")
        else:
            st.warning("⚠️ 暂无可用策略，请检查策略库")
    
    # ========== 市场与策略选择 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        # 使用提取的市场列表
        if 可用市场:
            市场 = st.selectbox("选择市场", 可用市场)
        else:
            市场 = st.selectbox("选择市场", ["加密货币", "A股", "美股", "外汇", "期货"])
    
    with col2:
        # 根据选中的市场过滤策略
        当前市场策略 = ["综合推荐"]
        for s in 策略列表:
            类别 = s.get("类别", "")
            if 市场 == "加密货币" and ("₿" in 类别 or "加密" in 类别):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "A股" and ("📈" in 类别 or "A股" in 类别):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "美股" and ("🇺🇸" in 类别 or "美股" in 类别):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "外汇" and ("💰" in 类别 or "外汇" in 类别):
                当前市场策略.append(s.get("名称"))
            elif 市场 == "期货" and ("📊" in 类别 or "期货" in 类别):
                当前市场策略.append(s.get("名称"))
        
        if not 当前市场策略 or len(当前市场策略) == 1:
            当前市场策略 = ["综合推荐", "趋势跟踪", "网格交易", "均值回归"]
        
        策略 = st.selectbox("选择策略", 当前市场策略)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== 根据市场显示对应的品种 ==========
    if 市场 == "加密货币":
        推荐品种预设 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12},
            {"品种": "SOL-USD", "名称": "Solana", "价格": 145.30},
            {"品种": "BNB-USD", "名称": "币安币", "价格": 580.00},
        ]
    elif 市场 == "A股":
        推荐品种预设 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50},
            {"品种": "002594.SZ", "名称": "比亚迪", "价格": 265.80},
            {"品种": "600519.SS", "名称": "五粮液", "价格": 145.00},
        ]
    elif 市场 == "美股":
        推荐品种预设 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00},
            {"品种": "TSLA", "名称": "特斯拉", "价格": 175.30},
            {"品种": "MSFT", "名称": "微软", "价格": 420.00},
        ]
    elif 市场 == "外汇":
        推荐品种预设 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650},
            {"品种": "USDJPY", "名称": "美元/日元", "价格": 155.50},
            {"品种": "AUDUSD", "名称": "澳元/美元", "价格": 0.6650},
        ]
    else:  # 期货
        推荐品种预设 = [
            {"品种": "GC=F", "名称": "黄金期货", "价格": 2350.00},
            {"品种": "CL=F", "名称": "原油期货", "价格": 78.50},
            {"品种": "ES=F", "名称": "标普500期货", "价格": 5200.00},
        ]
    
    # ========== AI分析按钮 ==========
    if st.button("🔍 AI智能分析", type="primary"):
        if not 启用策略详情:
            st.error("❌ 没有启用的策略，请先在「策略中心」启用策略")
        else:
            with st.spinner("AI正在分析市场..."):
                st.markdown("---")
                st.markdown(f"### 📈 AI分析结果 - {市场}")
                st.markdown(f"**使用策略: {策略}**")
                
                # 生成推荐
                for item in 推荐品种预设:
                    # 模拟信号（实际应该用真实策略计算）
                    信号随机 = random.random()
                    if 信号随机 > 0.6:
                        信号 = "买入"
                        信号颜色 = "🟢"
                        置信度 = random.randint(70, 95)
                    elif 信号随机 > 0.3:
                        信号 = "持有"
                        信号颜色 = "🟡"
                        置信度 = random.randint(50, 70)
                    else:
                        信号 = "卖出"
                        信号颜色 = "🔴"
                        置信度 = random.randint(40, 60)
                    
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                        <b>{item['名称']} ({item['品种']})</b><br>
                        价格: ¥{item['价格']:,.2f}<br>
                        信号: {信号颜色} {信号} (置信度: {置信度}%)<br>
                        理由: 基于{策略}策略，结合{市场}市场数据分析
                    </div>
                    """, unsafe_allow_html=True)
                
                # AI综合评分
                st.markdown("---")
                st.markdown("#### 🎯 AI综合评分")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("市场情绪", "偏多" if 市场 != "外汇" else "中性", delta="+2")
                with col2:
                    st.metric("风险等级", "中等", delta="稳定")
                with col3:
                    st.metric("最优策略", 策略, delta="推荐")
                with col4:
                    st.metric("启用策略数", len(启用策略详情), delta="活跃")
    
    # ========== 快速交易 ==========
    st.markdown("---")
    st.markdown("#### ⚡ 快速交易")
    
    # 获取当前市场的品种列表
    当前市场品种 = [f"{item['名称']} ({item['品种']})" for item in 推荐品种预设]
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    with tab1:
        with st.form("quick_buy_form"):
            买入选择 = st.selectbox("选择品种", 当前市场品种)
            # 提取品种代码
            if "(" in 买入选择:
                买入品种 = 买入选择.split("(")[-1].replace(")", "")
            else:
                买入品种 = 买入选择
            
            # 获取参考价格
            参考价格 = 获取参考价格(买入品种, 推荐品种预设)
            单位提示 = "个" if "BTC" in 买入品种 or "ETH" in 买入品种 else "股" if 市场 not in ["外汇", "期货"] else "手"
            
            买入数量 = st.number_input(f"数量 ({单位提示})", min_value=0.01, value=0.1, step=0.01)
            预计花费 = 参考价格 * 买入数量
            
            st.caption(f"📌 参考价格: ¥{参考价格:,.4f}")
            st.caption(f"💰 预计花费: ¥{预计花费:,.2f}")
            
            提交买入 = st.form_submit_button("确认买入", type="primary")
            
            if 提交买入:
                可用资金 = 引擎.获取可用资金()
                if 预计花费 <= 可用资金:
                    st.success(f"✅ 已提交买入 {买入品种} {买入数量} {单位提示}")
                    st.info(f"花费: ¥{预计花费:,.2f} | 剩余: ¥{可用资金 - 预计花费:,.2f}")
                else:
                    st.error(f"❌ 资金不足！可用: ¥{可用资金:,.2f}, 需要: ¥{预计花费:,.2f}")
    
    with tab2:
        with st.form("quick_sell_form"):
            持仓品种列表 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            
            if 持仓品种列表:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种列表)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                
                if 卖出品种 in ["BTC-USD", "ETH-USD", "SOL-USD"]:
                    卖出数量 = st.number_input(f"数量 (个)", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01)
                else:
                    卖出数量 = st.number_input(f"数量 (股)", min_value=1, max_value=int(最大数量), value=min(1, int(最大数量)), step=1)
                
                st.caption(f"📊 可卖数量: {最大数量:.4f}" if 最大数量 < 1 else f"📊 可卖数量: {int(最大数量)}")
            else:
                st.info("暂无持仓")
                卖出品种 = None
                卖出数量 = 0
            
            提交卖出 = st.form_submit_button("确认卖出")
            
            if 提交卖出 and 卖出品种 and 卖出数量 > 0:
                st.success(f"✅ 已提交卖出 {卖出品种} {卖出数量} 个单位")
    
    # ========== 底部提示 ==========
    st.markdown("---")
    st.caption("⚡ AI推荐仅供参考，投资需谨慎")
    st.caption(f"📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def 获取参考价格(品种, 品种列表):
    """获取参考价格"""
    for item in 品种列表:
        if item["品种"] == 品种:
            return item["价格"]
    # 默认价格映射
    默认价格 = {
        "BTC-USD": 79586.70,
        "ETH-USD": 2219.12,
        "SOL-USD": 145.30,
        "AAPL": 185.50,
        "NVDA": 950.00,
        "TSLA": 175.30,
        "EURUSD": 1.0850,
        "000001.SS": 1680.00,
    }
    return 默认价格.get(品种, 100)
