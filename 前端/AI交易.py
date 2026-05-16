# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
from datetime import datetime

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 获取策略列表 ==========
    策略列表 = []
    if 策略加载器 is not None:
        try:
            策略列表 = 策略加载器.获取策略()
            st.success(f"✅ 已加载 {len(策略列表)} 个策略")
        except Exception as e:
            st.error(f"加载策略失败: {e}")
    
    # 按类别分组策略
    策略分组 = {}
    for s in 策略列表:
        类别 = s.get("类别", "其他")
        if 类别 not in 策略分组:
            策略分组[类别] = []
        策略分组[类别].append(s)
    
    # 获取启用的策略
    if '策略状态' not in st.session_state:
        st.session_state.策略状态 = {}
        for s in 策略列表:
            st.session_state.策略状态[s.get("名称")] = True
    
    # ========== 策略管理区域 ==========
    with st.expander("📋 策略管理 (勾选启用的策略)", expanded=True):
        col1, col2 = st.columns(2)
        
        # 显示策略勾选框
        策略项列表 = []
        for i, s in enumerate(策略列表):
            策略名 = s.get("名称", "")
            类别 = s.get("类别", "")
            col = col1 if i % 2 == 0 else col2
            with col:
                启用 = st.checkbox(
                    f"{类别} - {策略名}", 
                    value=st.session_state.策略状态.get(策略名, True),
                    key=f"ai_strategy_{策略名}"
                )
                st.session_state.策略状态[策略名] = 启用
                策略项列表.append({"名称": 策略名, "启用": 启用})
    
    # ========== 市场选择 ==========
    可用市场 = list(策略分组.keys())
    if not 可用市场:
        可用市场 = ["💰 外汇", "₿ 加密货币", "📈 A股", "🇺🇸 美股"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox("选择市场", 可用市场)
    
    with col2:
        策略选项 = ["综合推荐"] + [s.get("名称") for s in 策略分组.get(市场, [])]
        if len(策略选项) <= 1:
            策略选项 = ["综合推荐", "趋势跟踪", "网格交易"]
        策略 = st.selectbox("选择策略", 策略选项)
    
    st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    # ========== 根据市场显示品种 ==========
    if "加密货币" in 市场:
        交易品种 = [
            {"品种": "BTC-USD", "名称": "比特币", "价格": 79586.70, "步长": 0.01, "单位": "个"},
            {"品种": "ETH-USD", "名称": "以太坊", "价格": 2219.12, "步长": 0.01, "单位": "个"},
        ]
    elif "A股" in 市场:
        交易品种 = [
            {"品种": "000001.SS", "名称": "贵州茅台", "价格": 1680.00, "步长": 100, "单位": "股"},
            {"品种": "300750.SZ", "名称": "宁德时代", "价格": 220.50, "步长": 100, "单位": "股"},
        ]
    elif "美股" in 市场:
        交易品种 = [
            {"品种": "AAPL", "名称": "苹果", "价格": 185.50, "步长": 1, "单位": "股"},
            {"品种": "NVDA", "名称": "英伟达", "价格": 950.00, "步长": 1, "单位": "股"},
        ]
    else:
        交易品种 = [
            {"品种": "EURUSD", "名称": "欧元/美元", "价格": 1.0850, "步长": 0.01, "单位": "手"},
            {"品种": "GBPUSD", "名称": "英镑/美元", "价格": 1.2650, "步长": 0.01, "单位": "手"},
        ]
    
    # ========== AI自动交易区域 ==========
    st.markdown("---")
    st.markdown("### 🤖 AI自动交易")
    
    # 自动交易开关
    if 'auto_trade_running' not in st.session_state:
        st.session_state.auto_trade_running = False
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ 启动自动交易", type="primary"):
            st.session_state.auto_trade_running = True
            st.rerun()
    with col2:
        if st.button("⏸️ 停止自动交易"):
            st.session_state.auto_trade_running = False
            st.rerun()
    with col3:
        运行状态 = "🟢 运行中" if st.session_state.auto_trade_running else "🔴 已停止"
        st.markdown(f"**状态: {运行状态}**")
    
    # ========== 手动交易区域 ==========
    st.markdown("---")
    st.markdown("### 📊 手动交易")
    
    tab1, tab2 = st.tabs(["📈 买入", "📉 卖出"])
    
    with tab1:
        with st.form("buy_form"):
            买入品种 = st.selectbox("选择品种", [f"{item['名称']} ({item['品种']})" for item in 交易品种])
            if "(" in 买入品种:
                品种代码 = 买入品种.split("(")[-1].replace(")", "")
            else:
                品种代码 = 买入品种
            
            当前品种信息 = next((item for item in 交易品种 if item["品种"] == 品种代码), 交易品种[0])
            参考价格 = 当前品种信息["价格"]
            步长 = 当前品种信息["步长"]
            单位 = 当前品种信息["单位"]
            
            买入数量 = st.number_input(f"数量 ({单位})", min_value=步长, value=步长, step=步长)
            预计花费 = 参考价格 * 买入数量
            st.caption(f"📌 参考价格: ¥{参考价格:.4f} | 💰 预计花费: ¥{预计花费:,.2f}")
            
            if st.form_submit_button("确认买入", type="primary"):
                可用资金 = 引擎.获取可用资金()
                if 预计花费 <= 可用资金:
                    # 执行买入
                    try:
                        结果 = 引擎.买入(品种代码, None, 买入数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {品种代码} {买入数量} {单位}")
                            st.session_state.订单引擎 = 引擎
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"买入异常: {e}")
                else:
                    st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}, 可用: ¥{可用资金:,.2f}")
    
    with tab2:
        with st.form("sell_form"):
            持仓品种 = list(引擎.持仓.keys()) if 引擎.持仓 else []
            if 持仓品种:
                卖出品种 = st.selectbox("选择持仓品种", 持仓品种)
                pos = 引擎.持仓[卖出品种]
                最大数量 = getattr(pos, '数量', 0)
                
                if 卖出品种 in ["BTC-USD", "ETH-USD"]:
                    卖出数量 = st.number_input("数量 (个)", min_value=0.01, max_value=float(最大数量), value=min(0.01, float(最大数量)), step=0.01)
                else:
                    卖出数量 = st.number_input("数量 (股)", min_value=1, max_value=int(最大数量), value=min(1, int(最大数量)), step=1)
                
                st.caption(f"📊 可卖数量: {最大数量:.4f}" if 最大数量 < 1 else f"📊 可卖数量: {int(最大数量)}")
                
                if st.form_submit_button("确认卖出"):
                    try:
                        结果 = 引擎.卖出(卖出品种, None, 卖出数量)
                        if 结果.get("success"):
                            st.success(f"✅ 已卖出 {卖出品种} {卖出数量} 个单位")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"卖出失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"卖出异常: {e}")
            else:
                st.info("📭 暂无持仓")
    
    # ========== AI信号生成 ==========
    st.markdown("---")
    if st.button("🔍 生成AI交易信号", type="primary"):
        with st.spinner("AI正在分析市场..."):
            st.markdown("### 📈 AI交易信号")
            
            # 获取启用的策略
            启用策略 = [s for s in 策略项列表 if s["启用"]]
            if not 启用策略:
                st.warning("⚠️ 请先启用策略")
            else:
                for item in 交易品种:
                    # 随机模拟信号（实际应调用真实策略）
                    信号随机 = random.random()
                    if 信号随机 > 0.6:
                        信号, 颜色, 置信度 = "买入", "🟢", random.randint(70, 95)
                        建议数量 = item["步长"] * random.randint(1, 3)
                    elif 信号随机 > 0.3:
                        信号, 颜色, 置信度 = "持有", "🟡", random.randint(50, 70)
                        建议数量 = 0
                    else:
                        信号, 颜色, 置信度 = "卖出", "🔴", random.randint(40, 60)
                        建议数量 = item["步长"]
                    
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;">
                        <b>{item['名称']} ({item['品种']})</b><br>
                        价格: ¥{item['价格']:,.2f}<br>
                        信号: {颜色} {信号} (置信度: {置信度}%)<br>
                        基于策略: {', '.join([s['名称'] for s in 启用策略[:3]])}<br>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 自动交易
                    if st.session_state.auto_trade_running and 信号 == "买入" and 建议数量 > 0:
                        可用资金 = 引擎.获取可用资金()
                        预计花费 = item["价格"] * 建议数量
                        if 预计花费 <= 可用资金:
                            引擎.买入(item["品种"], None, 建议数量)
                            st.info(f"🤖 自动买入 {item['品种']} {建议数量} {item['单位']}")
    
    # ========== 底部 ==========
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
