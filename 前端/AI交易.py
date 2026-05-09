# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场选择
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    # 策略映射
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    
    策略类型 = st.selectbox("选择策略", 策略映射.get(市场, ["默认策略"]))
    
    # 存储AI推荐结果
    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner(f"AI 正在使用【{策略类型}】分析【{市场}】..."):
            try:
                结果 = AI引擎.AI推荐(市场, 策略类型)
                st.session_state.ai_list = 结果.get("推荐", [])
                if st.session_state.ai_list:
                    st.success(f"✅ AI 分析完成！共推荐 {len(st.session_state.ai_list)} 只标的")
                else:
                    st.warning("⚠️ 当前策略下未筛选出合适标的")
                st.rerun()
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # ✅ 显示推荐列表
    if st.session_state.ai_list:
        st.markdown("### 📈 AI 推荐买入（按策略打分）")
        
        for idx, item in enumerate(st.session_state.ai_list):
            code = item.get("代码", "")
            name = item.get("名称", "未知")
            price = item.get("价格", 0)
           趋势 = item.get("趋势", "未知")
           理由 = item.get("理由", "")
           得分 = item.get("得分", 0)
            
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: ${price:.4f}")
                with col2:
                    if 趋势 == "上涨":
                        st.markdown("🟢 趋势向上")
                    else:
                        st.markdown("🔴 趋势向下")
                    st.caption(f"得分: {得分}")
                with col3:
                    # ✅ 买入时传入策略名称
                    if st.button(f"买入", key=f"buy_{code}_{idx}"):
                        if price > 0:
                            with st.spinner(f"正在买入 {name}..."):
                                # 传入策略名称，用于交易记录
                                引擎.买入(code, price, 100, 策略名称=策略类型)
                                st.success(f"✅ 已买入 {name} 100股 @ ${price:.4f}")
                                st.rerun()
                        else:
                            st.error("价格无效，无法买入")
                
                if 理由:
                    st.caption(f"📝 {理由}")
                st.divider()
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            持仓数据.append({
                "品种": sym,
                "数量": int(pos.数量),
                "成本": round(pos.平均成本, 4),
                "现价": round(pos.当前价格, 4),
                "浮动盈亏": round((pos.当前价格 - pos.平均成本) * pos.数量, 2)
            })
        st.dataframe(持仓数据, use_container_width=True)
    else:
        st.info("暂无持仓")
    
    # 快速测试区
    st.markdown("---")
    st.markdown("### 🧪 快速测试（验证订单引擎）")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("测试买入 AAPL", use_container_width=True):
            引擎.买入("AAPL", 287.44, 10, 策略名称="测试")
            st.rerun()
    with col2:
        if st.button("查看持仓", use_container_width=True):
            if 引擎.持仓:
                for sym, pos in 引擎.持仓.items():
                    st.write(f"{sym}: {int(pos.数量)}股, 成本: {pos.平均成本:.2f}")
            else:
                st.info("暂无持仓")
