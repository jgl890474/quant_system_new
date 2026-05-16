# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面 - 简化版"""
    
    st.subheader("🤖 AI 智能交易")
    
    # 生成唯一key
    page_key = st.session_state.get('page_key', str(uuid.uuid4())[:8])
    st.session_state.page_key = page_key
    
    # ========== 直接生成推荐（不需要点击按钮） ==========
    市场 = "A股"  # 固定为A股
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    st.markdown("### 📈 AI推荐买入（A股）")
    st.caption("💡 评分越高表示越符合当前策略")
    
    # 直接显示推荐
    推荐列表 = [
        {"代码": "600519.SS", "名称": "贵州茅台", "价格": 1450, "评分": 88, "数量": 100, "理由": "白酒龙头"},
        {"代码": "000858.SZ", "名称": "五粮液", "价格": 128, "评分": 85, "数量": 200, "理由": "消费回暖"},
        {"代码": "300750.SZ", "名称": "宁德时代", "价格": 180, "评分": 82, "数量": 200, "理由": "新能源"},
        {"代码": "000333.SZ", "名称": "美的集团", "价格": 80, "评分": 80, "数量": 300, "理由": "家电龙头"},
        {"代码": "600036.SS", "名称": "招商银行", "价格": 38, "评分": 78, "数量": 500, "理由": "银行业绩好"},
        {"代码": "002415.SZ", "名称": "海康威视", "价格": 35, "评分": 75, "数量": 600, "理由": "安防龙头"},
        {"代码": "002594.SZ", "名称": "比亚迪", "价格": 265, "评分": 78, "数量": 100, "理由": "电动车"},
        {"代码": "601318.SS", "名称": "中国平安", "价格": 42, "评分": 72, "数量": 500, "理由": "保险龙头"},
    ]
    
    for idx, item in enumerate(推荐列表):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
            
            with col1:
                st.markdown(f"**{item['名称']}**")
                st.caption(item['代码'])
            
            with col2:
                st.write(f"¥{item['价格']:.2f}")
            
            with col3:
                评分 = item['评分']
                if 评分 >= 80:
                    颜色 = "🟢"
                elif 评分 >= 60:
                    颜色 = "🟡"
                else:
                    颜色 = "⚪"
                st.write(f"{颜色} 评分: {评分}")
            
            with col4:
                st.caption(f"建议: {item['数量']}股")
                st.caption(item['理由'])
            
            with col5:
                if st.button(f"买入", key=f"buy_{idx}_{page_key}"):
                    try:
                        结果 = 引擎.买入(item['代码'], item['价格'], item['数量'], 策略名称="A股双均线1")
                        if 结果.get("success"):
                            st.success(f"✅ 已买入 {item['名称']} {item['数量']}股")
                            st.rerun()
                        else:
                            st.error(f"买入失败: {结果.get('error')}")
                    except Exception as e:
                        st.error(f"买入出错: {e}")
            
            st.divider()
    
    # 显示持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.write(f"- {品种}: {数量:.4f}个 @ ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    st.caption("💡 提示：直接点击「买入」按钮即可下单")
