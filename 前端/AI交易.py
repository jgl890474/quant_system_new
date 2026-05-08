# -*- coding: utf-8 -*-
import streamlit as st
from 核心 import 行情获取

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # 市场选择
    市场 = st.selectbox("选择市场", ["A股", "美股", "外汇", "加密货币", "期货"])
    
    # 策略映射
    策略映射 = {
        "A股": ["量价策略", "双均线策略", "隔夜套利策略"],
        "美股": ["量价策略", "双均线策略", "动量策略"],
        "外汇": ["外汇利差策略"],
        "加密货币": ["加密双均线"],
        "期货": ["期货趋势策略"]
    }
    
    策略列表 = 策略映射.get(市场, ["默认策略"])
    策略类型 = st.selectbox("选择策略", 策略列表)
    
    if st.button("🚀 AI 分析", type="primary", use_container_width=True):
        with st.spinner(f"AI 正在分析{市场}..."):
            try:
                结果 = AI引擎.AI推荐(市场, 策略类型)
                
                st.success(f"✅ AI 推荐完成！置信度: {结果.get('置信度', 0)}%")
                推荐列表 = 结果.get("推荐", [])
                
                if 推荐列表:
                    st.markdown("### 📈 AI 推荐买入")
                    for idx, 股票 in enumerate(推荐列表):
                        # 使用唯一的key，避免变量覆盖
                        股票代码 = 股票.get('代码', '')
                        股票名称 = 股票.get('名称', '未知')
                        股票价格 = 股票.get('价格', 0)
                        
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1.5])
                            with col1:
                                st.markdown(f"**{股票名称}** ({股票代码})")
                            with col2:
                                st.markdown(f"价格: ${股票价格:.2f}")
                            with col3:
                                趋势 = 股票.get('趋势', '未知')
                                if 趋势 == "上涨":
                                    st.markdown("🟢 趋势向上")
                                else:
                                    st.markdown("🔴 趋势向下")
                            with col4:
                                # 使用唯一的key，确保每个按钮独立
                                button_key = f"buy_{股票代码}_{idx}"
                                if st.button(f"买入", key=button_key):
                                    if 股票价格 > 0 and 股票代码:
                                        st.info(f"正在买入 {股票名称}({股票代码}) @ ${股票价格:.2f}")
                                        # 直接传入正确的代码
                                        引擎.买入(股票代码, 股票价格, 100)
                                        st.success(f"✅ 已执行买入 {股票名称}")
                                        st.rerun()
                                    else:
                                        st.error(f"无法买入: 价格或代码无效")
                            
                            if 股票.get('理由'):
                                st.caption(f"📝 {股票['理由']}")
                            st.divider()
                else:
                    st.warning("暂无推荐股票")
                    
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📊 当前持仓")
    
    if 引擎.持仓:
        持仓数据 = []
        for 品种, pos in 引擎.持仓.items():
            持仓数据.append({
                "品种": 品种,
                "数量": int(pos.数量),
                "成本": f"{pos.平均成本:.2f}",
                "市值": f"{pos.数量 * pos.当前价格:.2f}"
            })
        st.dataframe(持仓数据, use_container_width=True)
    else:
        st.info("暂无持仓")
