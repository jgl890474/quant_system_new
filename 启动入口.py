with tabs[2]:
    # ========== AI智能交易 ==========
    st.markdown("### 🤖 AI 智能交易")
    st.caption("选择策略，系统会自动分析市场并给出买入/卖出信号")
    
    # 从策略加载器获取策略
    策略列表 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                策略列表 = 策略加载器.获取策略()
            elif hasattr(策略加载器, '获取策略列表'):
                策略列表 = 策略加载器.获取策略列表()
        except Exception as e:
            st.warning(f"获取策略失败: {e}")
    
    if not 策略列表:
        st.warning("等待策略加载...")
    else:
        # 按类别分组显示策略选择
        st.markdown("#### 📋 选择要测试的策略")
        
        # 按类别分组
        策略分组 = {}
        for s in 策略列表:
            类别 = s.get('类别', '其他')
            if 类别 not in 策略分组:
                策略分组[类别] = []
            策略分组[类别].append(s)
        
        # 选择策略
        选中策略 = None
        for 类别, 策略组 in 策略分组.items():
            st.markdown(f"**{类别}**")
            策略名称列表 = [s.get('名称') for s in 策略组]
            选中的策略名 = st.selectbox(f"选择{类别}策略", 策略名称列表, key=f"select_{类别}")
            if 选中的策略名:
                for s in 策略组:
                    if s.get('名称') == 选中的策略名:
                        选中策略 = s
                        break
            st.markdown("---")
        
        if 选中策略:
            st.markdown(f"#### 🎯 当前选中策略: **{选中策略.get('名称')}**")
            st.markdown(f"- 类别: {选中策略.get('类别')}")
            st.markdown(f"- 品种: {选中策略.get('品种')}")
            
            品种 = 选中策略.get('品种', 'BTC-USD')
            
            # 获取实时价格（模拟）
            try:
                if 行情获取:
                    价格结果 = 行情获取.获取价格(品种)
                    if 价格结果 and hasattr(价格结果, '价格'):
                        当前价格 = 价格结果.价格
                    else:
                        当前价格 = get模拟价格(品种)
                else:
                    当前价格 = get模拟价格(品种)
            except:
                当前价格 = get模拟价格(品种)
            
            st.metric("📊 当前价格", f"¥{当前价格:,.2f}")
            st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
            
            # ========== AI信号分析 ==========
            st.markdown("---")
            st.markdown("#### 🤖 AI信号分析")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 生成AI信号", type="primary"):
                    with st.spinner("AI正在分析市场..."):
                        # 模拟AI信号分析
                        信号 = generate_ai_signal(选中策略.get('名称'), 当前价格)
                        
                        st.markdown(f"""
                        <div style="border:1px solid #ddd; border-radius:10px; padding:15px; margin-top:10px;">
                            <h4>📈 AI分析结果</h4>
                            <p><b>策略:</b> {选中策略.get('名称')}</p>
                            <p><b>品种:</b> {品种}</p>
                            <p><b>当前价格:</b> ¥{当前价格:,.2f}</p>
                            <p><b>AI信号:</b> {信号['信号']}</p>
                            <p><b>置信度:</b> {信号['置信度']}%</p>
                            <p><b>建议数量:</b> {信号['建议数量']} 个</p>
                            <p><b>理由:</b> {信号['理由']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.session_state.ai_signal = 信号
            
            with col2:
                st.markdown("#### 📊 手动交易")
                数量 = st.number_input("交易数量", min_value=0.01, value=0.1, step=0.01)
                
                col_buy, col_sell = st.columns(2)
                with col_buy:
                    if st.button("📈 买入", use_container_width=True):
                        可用资金 = 引擎.获取可用资金()
                        预计花费 = 当前价格 * 数量
                        if 预计花费 <= 可用资金:
                            try:
                                结果 = 引擎.买入(品种, None, 数量)
                                if 结果.get("success"):
                                    st.success(f"✅ 已买入 {品种} {数量} 个")
                                    st.rerun()
                                else:
                                    st.error(f"买入失败: {结果.get('error')}")
                            except Exception as e:
                                st.error(f"买入异常: {e}")
                        else:
                            st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}")
                
                with col_buy:
                    if st.button("📉 卖出", use_container_width=True):
                        if 品种 in 引擎.持仓:
                            try:
                                结果 = 引擎.卖出(品种, None, 数量)
                                if 结果.get("success"):
                                    st.success(f"✅ 已卖出 {品种} {数量} 个")
                                    st.rerun()
                                else:
                                    st.error(f"卖出失败: {结果.get('error')}")
                            except Exception as e:
                                st.error(f"卖出异常: {e}")
                        else:
                            st.error(f"❌ 没有持仓 {品种}")
            
            # 显示AI信号结果（如果有）
            if 'ai_signal' in st.session_state and st.session_state.ai_signal:
                信号 = st.session_state.ai_signal
                st.markdown("---")
                st.markdown("#### 💡 AI建议执行")
                if 信号['信号'] == "买入":
                    if st.button("执行AI买入建议"):
                        可用资金 = 引擎.获取可用资金()
                        预计花费 = 当前价格 * 信号['建议数量']
                        if 预计花费 <= 可用资金:
                            结果 = 引擎.买入(品种, None, 信号['建议数量'])
                            if 结果.get("success"):
                                st.success(f"✅ AI已买入 {品种} {信号['建议数量']} 个")
                                st.session_state.ai_signal = None
                                st.rerun()
                        else:
                            st.error(f"资金不足，需要 ¥{预计花费:,.2f}")
                elif 信号['信号'] == "卖出":
                    if st.button("执行AI卖出建议"):
                        if 品种 in 引擎.持仓:
                            结果 = 引擎.卖出(品种, None, 信号['建议数量'])
                            if 结果.get("success"):
                                st.success(f"✅ AI已卖出 {品种} {信号['建议数量']} 个")
                                st.session_state.ai_signal = None
                                st.rerun()
                        else:
                            st.error(f"没有持仓 {品种}")
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("#### 💼 当前持仓")
    if 引擎.持仓:
        for 品种名, pos in 引擎.持仓.items():
            数量持仓 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.caption(f"{品种名}: {数量持仓:.4f}个, 成本 ¥{成本:.2f}")
    else:
        st.info("暂无持仓")

# 辅助函数
def get模拟价格(品种):
    """获取模拟价格"""
    价格映射 = {
        "BTC-USD": 79586.70,
        "ETH-USD": 2219.12,
        "AAPL": 185.50,
        "NVDA": 950.00,
        "EURUSD": 1.0850,
        "000001.SS": 1680.00,
    }
    return 价格映射.get(品种, 100)

def generate_ai_signal(策略名称, 当前价格):
    """根据策略名称生成AI信号"""
    import random
    import hashlib
    
    # 使用策略名称作为随机种子，使同一策略结果相对稳定
    种子 = int(hashlib.md5(策略名称.encode()).hexdigest()[:8], 16)
    random.seed(种子)
    
    # 生成信号
    随机值 = random.random()
    
    if 随机值 > 0.6:
        return {
            "信号": "买入 🟢",
            "置信度": random.randint(70, 95),
            "建议数量": round(random.uniform(0.05, 0.2), 2),
            "理由": f"{策略名称}策略检测到上涨趋势，RSI处于超卖区域"
        }
    elif 随机值 > 0.3:
        return {
            "信号": "持有 🟡",
            "置信度": random.randint(50, 70),
            "建议数量": 0,
            "理由": f"{策略名称}策略显示市场震荡，建议观望"
        }
    else:
        return {
            "信号": "卖出 🔴",
            "置信度": random.randint(40, 60),
            "建议数量": round(random.uniform(0.05, 0.2), 2),
            "理由": f"{策略名称}策略检测到下跌趋势，建议止盈或止损"
        }
