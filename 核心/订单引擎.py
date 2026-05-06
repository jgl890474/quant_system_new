def 买入(self, 品种, 价格, 数量=1000):
    # 获取风控引擎（从 session_state 或新建）
    风控 = st.session_state.get('风控引擎')
    if 风控:
        总资金 = self.获取总资产()
        允许, 理由 = 风控.检查新交易(品种, "买入", 数量, 价格, self, 总资金)
        if not 允许:
            st.error(理由)
            return
    
    # 原有买入逻辑
    if 品种 in self.持仓:
        pos = self.持仓[品种]
        总数量 = pos.数量 + 数量
        总成本 = pos.数量 * pos.平均成本 + 数量 * 价格
        pos.数量 = 总数量
        pos.平均成本 = 总成本 / 总数量
    else:
        self.持仓[品种] = 持仓数据(品种, 数量, 价格)
    self.交易记录.append({"时间": datetime.now(), "动作": "买入", "品种": 品种, "价格": 价格, "数量": 数量})
    st.success(f"✅ 买入 {品种} @ {价格:.4f}")
    
    st.rerun()
