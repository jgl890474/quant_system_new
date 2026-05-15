# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
from datetime import datetime

def 显示(引擎):
    st.markdown("### 🤖 AI智能交易系统")
    
    # ========== 市场与策略选择（不加key，让streamlit自动处理）==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场 = st.selectbox(
            "📊 交易市场",
            ["加密货币", "A股", "美股", "港股", "外汇"]
        )
    
    with col2:
        策略模式 = st.selectbox(
            "🎯 AI策略模式",
            ["保守型", "稳健型", "激进型", "自适应"]
        )
    
    # ========== AI信号按钮 ==========
    if st.button("🔍 获取AI信号", type="primary"):
        with st.spinner("AI分析中..."):
            # 模拟AI分析结果
            if 市场 == "加密货币":
                推荐 = [
                    {"品种": "BTC-USD", "信号": "买入", "置信度": 85, "目标价": 82000},
                    {"品种": "ETH-USD", "信号": "持有", "置信度": 72, "目标价": 3800},
                    {"品种": "SOL-USD", "信号": "观望", "置信度": 60, "目标价": 180},
                ]
            elif 市场 == "A股":
                推荐 = [
                    {"品种": "贵州茅台", "信号": "持有", "置信度": 78, "目标价": 1800},
                    {"品种": "宁德时代", "信号": "买入", "置信度": 82, "目标价": 250},
                    {"品种": "比亚迪", "信号": "卖出", "置信度": 65, "目标价": 280},
                ]
            elif 市场 == "美股":
                推荐 = [
                    {"品种": "NVDA", "信号": "买入", "置信度": 88, "目标价": 950},
                    {"品种": "AAPL", "信号": "持有", "置信度": 70, "目标价": 185},
                    {"品种": "TSLA", "信号": "观望", "置信度": 55, "目标价": 175},
                ]
            else:
                推荐 = [
                    {"品种": "示例品种1", "信号": "持有", "置信度": 75, "目标价": 100},
                    {"品种": "示例品种2", "信号": "买入", "置信度": 80, "目标价": 120},
                ]
            
            df = pd.DataFrame(推荐)
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ AI信号生成完成 | 市场: {市场} | 策略: {策略模式}")
    
    # ========== AI市场分析 ==========
    st.markdown("---")
    st.markdown("#### 📈 AI市场分析")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("市场情绪", "中性偏多", delta="+0.2")
        st.metric("波动率", "22.5%", delta="-1.2%")
    
    with col2:
        st.metric("资金流向", "净流入", delta="+1.8亿")
        st.metric("多空比", "1.35", delta="+0.08")
    
    with col3:
        st.metric("贪婪指数", "58", delta="+3")
        st.metric("成交量", "+12%", delta="+5%")
    
    # ========== 一键交易 ==========
    if st.button("⚡ 一键AI交易"):
        金额 = random.randint(1000, 50000)
        st.success(f"✅ 已触发 {市场} - {策略模式} 自动交易，金额: ¥{金额:,.0f}")
        
        # 添加到交易记录
        if hasattr(引擎, '交易记录'):
            引擎.交易记录.append({
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "动作": "AI自动买入",
                "品种": f"{市场}_AI",
                "数量": 0,
                "价格": 0,
                "金额": 金额
            })
    
    # ========== 持仓AI建议 ==========
    if hasattr(引擎, '持仓') and 引擎.持仓:
        st.markdown("---")
        st.markdown("#### 💼 持仓AI建议")
        
        for 品种, pos in 引擎.持仓.items():
            平均成本 = getattr(pos, '平均成本', 0)
            数量 = getattr(pos, '数量', 0)
            现价 = getattr(pos, '当前价格', 平均成本)
            
            if 数量 > 0:
                市值 = 数量 * 现价
                盈亏 = (现价 - 平均成本) * 数量
                盈亏率 = (盈亏 / (平均成本 * 数量)) * 100 if 平均成本 > 0 else 0
                
                if 盈亏 > 0:
                    建议 = "✅ 盈利中，建议设置移动止损"
                elif 盈亏 < 0:
                    建议 = "⚠️ 亏损中，建议确认止损点"
                else:
                    建议 = "ℹ️ 持平，等待方向"
                
                st.metric(
                    label=f"{品种}",
                    value=f"{数量} 单位 | 市值 ¥{市值:,.0f}",
                    delta=f"盈亏 ¥{盈亏:+,.0f} ({盈亏率:+.1f}%)"
                )
                st.caption(f"📌 AI建议: {建议}")
    
    st.markdown("---")
    st.caption("⚡ AI交易模块 v1.0 | 信号实时生成，仅供参考")
