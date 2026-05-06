# 在 显示() 函数中添加
st.markdown("### 🛡️ 风控状态")
if '风控引擎' in st.session_state:
    风控 = st.session_state.风控引擎
    总资金 = 引擎.获取总资产()
    状态 = 风控.获取风控状态(引擎, 总资金)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总仓位", 状态["总仓位比例"], delta=f"限制 {状态['最大总仓位限制']}")
    col2.metric("单品种限制", 状态["单品种仓位限制"], delta="最大资金比例")
    col3.metric("止损/止盈", f"{状态['止损线']} / {状态['止盈线']}")
    col4.metric("今日盈亏", f"${风控.今日盈亏:+,.2f}", delta=f"上限 {状态['每日亏损上限']}")
    
    if st.button("🛡️ 立即执行风控平仓"):
        平仓记录 = 风控.执行风控平仓(引擎)
        if 平仓记录:
            st.warning(f"已自动平仓 {len(平仓记录)} 个品种")
            for 记录 in 平仓记录:
                st.write(f"- {记录['品种']}: {记录['原因']}, 盈亏 {记录['盈亏']:+.2f}")
        else:
            st.info("没有触发风控的持仓")
