with tabs[2]:
    st.markdown("### 🤖 AI 智能交易")
    st.caption("选择策略，系统会自动分析市场并给出买入/卖出信号 | 可开启AI自动交易")
    
    # ========== 获取策略列表 ==========
    策略数据 = []
    if 策略加载器 is not None:
        try:
            if hasattr(策略加载器, '获取策略'):
                策略数据 = 策略加载器.获取策略()
            elif hasattr(策略加载器, '获取策略列表'):
                策略数据 = 策略加载器.获取策略列表()
        except Exception as e:
            st.warning(f"获取策略失败: {e}")
    
    if not 策略数据:
        st.warning("等待策略加载...")
    else:
        # ========== 策略选择区域 ==========
        st.markdown("#### 📋 选择策略")
        
        # 按类别分三列显示
        col1, col2, col3 = st.columns(3)
        
        策略分组 = {}
        for s in 策略数据:
            类别 = s.get('类别', '其他')
            if 类别 not in 策略分组:
                策略分组[类别] = []
            策略分组[类别].append(s)
        
        # 存储选中的策略
        if 'selected_strategy' not in st.session_state:
            st.session_state.selected_strategy = None
        
        # 第一列：加密货币
        with col1:
            if "₿ 加密货币" in 策略分组:
                st.markdown("**₿ 加密货币**")
                for s in 策略分组["₿ 加密货币"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"crypto_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        # 第二列：A股
        with col2:
            if "📈 A股" in 策略分组:
                st.markdown("**📈 A股**")
                for s in 策略分组["📈 A股"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"stock_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        # 第三列：美股
        with col3:
            if "🇺🇸 美股" in 策略分组:
                st.markdown("**🇺🇸 美股**")
                for s in 策略分组["🇺🇸 美股"]:
                    策略名 = s.get('名称')
                    if st.button(f"{策略名}", key=f"us_{策略名}", use_container_width=True):
                        st.session_state.selected_strategy = s
                        st.session_state.ai_signal = None
                        st.rerun()
        
        st.markdown("---")
        
        # ========== 显示选中的策略 ==========
        if st.session_state.selected_strategy:
            选中策略 = st.session_state.selected_strategy
            st.markdown(f"#### 🎯 当前选中策略: **{选中策略.get('名称')}**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- 类别: {选中策略.get('类别')}")
                st.markdown(f"- 品种: {选中策略.get('品种')}")
            with col2:
                st.markdown(f"- 状态: 🟢 运行中")
            
            品种 = 选中策略.get('品种', 'BTC-USD')
            
            # 获取实时价格
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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 当前价格", f"¥{当前价格:,.2f}")
            with col2:
                st.metric("💰 可用资金", f"¥{引擎.获取可用资金():,.2f}")
            with col3:
                if 品种 in 引擎.持仓:
                    持仓量 = getattr(引擎.持仓[品种], '数量', 0)
                    st.metric("📦 当前持仓", f"{持仓量:.4f}个")
                else:
                    st.metric("📦 当前持仓", "无")
            
            st.markdown("---")
            
            # ========== AI信号分析 + 自动交易 ==========
            st.markdown("#### 🤖 AI信号与自动交易")
            
            # 自动交易开关
            col1, col2 = st.columns([1, 3])
            with col1:
                if 'ai_auto_trade' not in st.session_state:
                    st.session_state.ai_auto_trade = False
                自动开关 = st.checkbox("🤖 AI自动交易", value=st.session_state.ai_auto_trade)
                if 自动开关 != st.session_state.ai_auto_trade:
                    st.session_state.ai_auto_trade = 自动开关
                    if 自动开关:
                        st.success("✅ AI自动交易已开启")
                    else:
                        st.warning("⏸️ AI自动交易已关闭")
            with col2:
                if st.session_state.ai_auto_trade:
                    st.info("💡 AI将根据信号自动执行买卖，每60秒检查一次")
            
            # 生成信号按钮
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 生成AI信号", type="primary", use_container_width=True):
                    with st.spinner("AI正在分析市场..."):
                        信号 = generate_ai_signal(选中策略.get('名称'), 当前价格)
                        st.session_state.ai_signal = 信号
                        st.rerun()
            
            with col2:
                if st.button("🔄 刷新价格", use_container_width=True):
                    st.rerun()
            
            # 显示AI信号
            if 'ai_signal' in st.session_state and st.session_state.ai_signal:
                信号 = st.session_state.ai_signal
                
                # 根据信号颜色
                if 信号['信号'] == "买入":
                    信号颜色 = "🟢"
                    边框颜色 = "#2ecc71"
                elif 信号['信号'] == "卖出":
                    信号颜色 = "🔴"
                    边框颜色 = "#e74c3c"
                else:
                    信号颜色 = "🟡"
                    边框颜色 = "#f39c12"
                
                st.markdown(f"""
                <div style="border:2px solid {边框颜色}; border-radius:10px; padding:15px; margin:10px 0;">
                    <h4>📈 AI分析结果</h4>
                    <table style="width:100%">
                        <tr><td><b>策略</b></td><td>{选中策略.get('名称')}</td></tr>
                        <tr><td><b>品种</b></td><td>{品种}</td></tr>
                        <tr><td><b>当前价格</b></td><td>¥{当前价格:,.2f}</td></tr>
                        <tr><td><b>AI信号</b></td><td>{信号颜色} {信号['信号']}</td></tr>
                        <tr><td><b>置信度</b></td><td>{信号['置信度']}%</td></tr>
                        <tr><td><b>建议数量</b></td><td>{信号['建议数量']} 个</td></tr>
                        <tr><td><b>理由</b></td><td>{信号['理由']}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
                
                # AI自动执行
                if st.session_state.ai_auto_trade:
                    if 信号['信号'] == "买入" and 信号['建议数量'] > 0:
                        可用资金 = 引擎.获取可用资金()
                        预计花费 = 当前价格 * 信号['建议数量']
                        if 预计花费 <= 可用资金:
                            try:
                                结果 = 引擎.买入(品种, None, 信号['建议数量'])
                                if 结果.get("success"):
                                    st.success(f"🤖 AI自动买入 {品种} {信号['建议数量']} 个")
                                    st.session_state.ai_signal = None
                                    st.rerun()
                                else:
                                    st.error(f"AI买入失败: {结果.get('error')}")
                            except Exception as e:
                                st.error(f"AI买入异常: {e}")
                        else:
                            st.warning(f"资金不足，需要 ¥{预计花费:,.2f}")
                    
                    elif 信号['信号'] == "卖出" and 信号['建议数量'] > 0:
                        if 品种 in 引擎.持仓:
                            当前持仓 = getattr(引擎.持仓[品种], '数量', 0)
                            卖出数量 = min(信号['建议数量'], 当前持仓)
                            if 卖出数量 > 0:
                                try:
                                    结果 = 引擎.卖出(品种, None, 卖出数量)
                                    if 结果.get("success"):
                                        st.success(f"🤖 AI自动卖出 {品种} {卖出数量} 个")
                                        st.session_state.ai_signal = None
                                        st.rerun()
                                    else:
                                        st.error(f"AI卖出失败: {结果.get('error')}")
                                except Exception as e:
                                    st.error(f"AI卖出异常: {e}")
                            else:
                                st.info("持仓不足，无法卖出")
                        else:
                            st.info(f"没有持仓 {品种}")
                
                # 手动执行按钮
                if not st.session_state.ai_auto_trade:
                    col1, col2 = st.columns(2)
                    with col1:
                        if 信号['信号'] == "买入" and st.button("📈 执行买入建议", use_container_width=True):
                            可用资金 = 引擎.获取可用资金()
                            预计花费 = 当前价格 * 信号['建议数量']
                            if 预计花费 <= 可用资金:
                                结果 = 引擎.买入(品种, None, 信号['建议数量'])
                                if 结果.get("success"):
                                    st.success(f"✅ 已买入 {品种} {信号['建议数量']} 个")
                                    st.session_state.ai_signal = None
                                    st.rerun()
                                else:
                                    st.error(f"买入失败: {结果.get('error')}")
                            else:
                                st.error(f"资金不足，需要 ¥{预计花费:,.2f}")
                    with col2:
                        if 信号['信号'] == "卖出" and st.button("📉 执行卖出建议", use_container_width=True):
                            if 品种 in 引擎.持仓:
                                结果 = 引擎.卖出(品种, None, 信号['建议数量'])
                                if 结果.get("success"):
                                    st.success(f"✅ 已卖出 {品种} {信号['建议数量']} 个")
                                    st.session_state.ai_signal = None
                                    st.rerun()
                                else:
                                    st.error(f"卖出失败: {结果.get('error')}")
                            else:
                                st.error(f"没有持仓 {品种}")
            
            # ========== 手动交易区域 ==========
            st.markdown("---")
            st.markdown("#### 📊 手动交易")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 买入")
                买入数量 = st.number_input("买入数量", min_value=0.01, value=0.1, step=0.01, key="buy_qty")
                if st.button("📈 确认买入", type="primary", use_container_width=True):
                    可用资金 = 引擎.获取可用资金()
                    预计花费 = 当前价格 * 买入数量
                    if 预计花费 <= 可用资金:
                        try:
                            结果 = 引擎.买入(品种, None, 买入数量)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {品种} {买入数量} 个")
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        except Exception as e:
                            st.error(f"买入异常: {e}")
                    else:
                        st.error(f"❌ 资金不足！需要: ¥{预计花费:,.2f}")
            
            with col2:
                st.markdown("##### 卖出")
                卖出数量 = st.number_input("卖出数量", min_value=0.01, value=0.1, step=0.01, key="sell_qty")
                if st.button("📉 确认卖出", use_container_width=True):
                    if 品种 in 引擎.持仓:
                        try:
                            结果 = 引擎.卖出(品种, None, 卖出数量)
                            if 结果.get("success"):
                                st.success(f"✅ 已卖出 {品种} {卖出数量} 个")
                                st.rerun()
                            else:
                                st.error(f"卖出失败: {结果.get('error')}")
                        except Exception as e:
                            st.error(f"卖出异常: {e}")
                    else:
                        st.error(f"❌ 没有持仓 {品种}")
    
    # ========== 显示所有持仓 ==========
    st.markdown("---")
    st.markdown("#### 💼 当前持仓")
    if 引擎.持仓:
        for 品种名, pos in 引擎.持仓.items():
            数量持仓 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            # 获取实时盈亏
            try:
                if 行情获取:
                    价格结果 = 行情获取.获取价格(品种名)
                    if 价格结果 and hasattr(价格结果, '价格'):
                        现价 = 价格结果.价格
                    else:
                        现价 = 成本
                else:
                    现价 = 成本
            except:
                现价 = 成本
            盈亏 = (现价 - 成本) * 数量持仓
            st.metric(
                label=f"{品种名}",
                value=f"{数量持仓:.4f}个",
                delta=f"成本 ¥{成本:.2f} | 盈亏 ¥{盈亏:+.2f}"
            )
    else:
        st.info("暂无持仓")
    
    # 自动交易状态提示
    st.markdown("---")
    if st.session_state.get('ai_auto_trade', False):
        st.success("🤖 AI自动交易运行中 - 系统将根据信号自动买卖")
    else:
        st.info("💡 提示：开启「AI自动交易」后，系统将根据AI信号自动执行买卖")
