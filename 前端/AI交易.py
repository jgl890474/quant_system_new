# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 直接定义市场列表（不依赖策略加载器） ==========
    可用市场 = ["💰 外汇", "₿ 加密货币", "📈 A股", "🇺🇸 美股"]
    
    # ========== 尝试从策略加载器获取启用的策略 ==========
    启用策略列表 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                所有策略 = 策略加载器.获取策略()
                for s in 所有策略:
                    if isinstance(s, dict):
                        策略名称 = s.get("名称", "")
                        if 策略名称:
                            启用策略列表.append(策略名称)
        except Exception as e:
            st.caption(f"读取策略失败: {e}")
    
    # 从 session_state 获取策略状态
    if '策略状态' in st.session_state:
        for name, status in st.session_state.策略状态.items():
            if status and name not in 启用策略列表:
                启用策略列表.append(name)
    
    # 显示启用的策略
    if 启用策略列表:
        with st.expander(f"📋 当前启用的策略 ({len(启用策略列表)}个)", expanded=False):
            for name in 启用策略列表[:8]:
                st.caption(f"✅ {name}")
    else:
        st.info("💡 暂无启用的策略，请前往「策略中心」启用策略")
    
    # ========== 市场与策略选择 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", 可用市场)
    
    with col2:
        策略选项 = ["综合推荐", "趋势跟踪", "网格交易", "均值回归", "动量策略"]
        策略 = st.selectbox("选择策略", 策略选项)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== 根据市场显示对应的品种 ==========
    if "加密货币" in 市场:
        推荐品种 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12},
            {"品种": "SOL-USD", "名称": "Solana", "价格": 145.30},
        ]
    elif "A股" in 市场:
        推荐品种 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50},
            {"品种": "002594.SZ", "名称": "比亚迪", "价格": 265.80},
        ]
    elif "美股" in 市场:
        推荐品种 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00},
            {"品种": "TSLA", "名称": "特斯拉", "价格": 175.30},
        ]
    else:  # 外汇
        推荐品种 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650},
            {"品种": "USDJPY", "名称": "美元/日元", "价格": 155.50},
        ]
    
    # ========== AI分析按钮 ==========
    if st.button("🔍 AI智能分析", type="primary"):
        with st.spinner("AI正在分析市场..."):
            st.markdown("---")
            st.markdown(f"### 📈 AI分析结果 - {市场}")
            st.markdown(f"**使用策略: {策略}**")
            
            for item in 推荐品种:
                # 模拟AI信号
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
                    信号: {颜色} {信号} (置信度: {置信度}%)<br>
                    理由: 基于{策略}策略，{市场}市场技术指标显示{信号}信号
                </div>
                """, unsafe_allow_html=True)
            
            # AI综合评分
            st.markdown("---")
            st.markdown("#### 🎯 AI综合评分")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("市场情绪", "偏多" if "加密" in 市场 else "中性", delta="+2")
            with col2:
                st.metric("风险等级", "中等", delta="稳定")
            with col3:
                st.metric("推荐度", "7.5/10", delta="建议关注")
    
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
            
            # 根据品种设置数量单位
            if "BTC" in 买入品种 or "ETH" in 买入品种:
                数量单位 = "个"
                买入数量 = st.number_input(f"数量 ({数量单位})", min_value=0.01, value=0.1, step=0.01, format="%.4f")
            else:
                数量单位 = "股"
                买入数量 = st.number_input(f"数量 ({数量单位})", min_value=1, value=100, step=10)
            
            预计花费 = 参考价格 * 买入数量
            st.caption(f"📌 参考价格: ¥{参考价格:.4f} | 💰 预计花费: ¥{预计花费:,.2f}")
            
            if st.form_submit_button("确认买入", type="primary"):
                可用资金 = 引擎.获取可用资金()
                预计花费 = 参考价格 * 买入数量
                if 预计花费 <= 可用资金:
                    st.success(f"✅ 已提交买入 {买入品种} {买入数量} {数量单位}")
                    st.info(f"花费: ¥{预计花费:,.2f} | 剩余: ¥{可用资金 - 预计花费:,.2f}")
                else:
                    st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}, 可用: ¥{可用资金:,.2f}")
    
    with tab2:
        with st.form("quick_sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            if 持仓品种:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                
                if 卖出品种 in ["BTC-USD", "ETH-USD", "SOL-USD"]:
                    卖出数量 = st.number_input("数量 (个)", min_value=0.01, max_value=float(最大数量), value=min(0.1, float(最大数量)), step=0.01, format="%.4f")
                else:
                    卖出数量 = st.number_input("数量 (股)", min_value=1, max_value=int(最大数量), value=min(100, int(最大数量)), step=10)
                
                st.caption(f"📊 可卖数量: {最大数量:.4f}" if 最大数量 < 1 else f"📊 可卖数量: {int(最大数量)}股")
                
                if st.form_submit_button("确认卖出"):
                    st.success(f"✅ 已提交卖出 {卖出品种} {卖出数量} 个单位")
            else:
                st.info("📭 暂无持仓")
    
    # ========== 底部 ==========
    st.markdown("---")
    st.caption("⚡ AI推荐仅供参考，投资需谨慎")
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
