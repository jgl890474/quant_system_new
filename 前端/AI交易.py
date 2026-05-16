# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    st.subheader("🤖 AI 智能交易")
    
    # 生成唯一key
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    # ========== 市场和策略定义 ==========
    市场选项 = ["A股", "加密货币", "美股"]
    策略映射 = {
        "A股": ["A股双均线1", "A股量价策略2", "A股隔夜套利策略3", "简单策略"],
        "加密货币": ["加密双均线1", "加密风控策略"],
        "美股": ["美股简单策略1", "美股动量策略"],
    }
    
    # ========== 选择市场和策略 ==========
    col1, col2 = st.columns(2)
    with col1:
        选中市场 = st.selectbox("选择市场", 市场选项, key=f"market_{st.session_state.page_key}")
    with col2:
        策略选项 = 策略映射.get(选中市场, ["默认策略"])
        选中策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
    
    # ========== 显示可用资金 ==========
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # ========== AI分析按钮 ==========
    if st.button("🚀 AI 分析", type="primary", width="stretch", key=f"analyze_btn"):
        with st.spinner(f"AI正在分析{选中市场}市场，使用{选中策略}策略..."):
            # 生成推荐
            推荐列表 = 生成推荐(选中市场, 可用资金)
            st.session_state['推荐结果'] = 推荐列表
            st.success(f"✅ 分析完成！共推荐 {len(推荐列表)} 个品种")
    
    # ========== 显示推荐结果 ==========
    if '推荐结果' in st.session_state and st.session_state['推荐结果']:
        推荐列表 = st.session_state['推荐结果']
        
        st.markdown("### 📈 AI推荐买入")
        st.caption("💡 评分越高表示越符合当前策略")
        
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
                    单位 = "股" if 选中市场 == "A股" else "个"
                    st.caption(f"建议: {item['数量']}{单位}")
                    st.caption(item.get('理由', '')[:15])
                
                with col5:
                    if st.button(f"买入", key=f"buy_{idx}"):
                        try:
                            结果 = 引擎.买入(item['代码'], item['价格'], item['数量'], 策略名称=选中策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {item['名称']}")
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        except Exception as e:
                            st.error(f"买入出错: {e}")
                
                st.divider()
    
    # ========== 显示持仓 ==========
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.write(f"- {品种}: {数量:.4f}个 @ ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    st.caption("💡 提示：点击「AI分析」获取推荐")


def 生成推荐(市场, 可用资金):
    """生成推荐"""
    推荐 = []
    
    if 市场 == "A股":
        数据 = [
            ("600519.SS", "贵州茅台", 88, 1450, 100, "白酒龙头"),
            ("000858.SZ", "五粮液", 85, 128, 200, "消费回暖"),
            ("300750.SZ", "宁德时代", 82, 180, 200, "新能源"),
            ("000333.SZ", "美的集团", 80, 80, 300, "家电龙头"),
            ("600036.SS", "招商银行", 78, 38, 500, "银行业绩好"),
            ("002415.SZ", "海康威视", 75, 35, 600, "安防龙头"),
            ("002594.SZ", "比亚迪", 78, 265, 100, "电动车"),
            ("601318.SS", "中国平安", 72, 42, 500, "保险龙头"),
        ]
        for 代码, 名称, 评分, 价格, 基数, 理由 in 数据:
            数量 = max(100, int(可用资金 * 0.05 / 价格 / 100) * 100)
            推荐.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "数量": 数量,
                "理由": 理由,
            })
    
    elif 市场 == "加密货币":
        数据 = [
            ("BTC-USD", "比特币", 85, 45000, 0.01, "趋势向上"),
            ("ETH-USD", "以太坊", 82, 2300, 0.1, "放量突破"),
            ("SOL-USD", "Solana", 78, 95, 1, "支撑位反弹"),
        ]
        for 代码, 名称, 评分, 价格, 基数, 理由 in 数据:
            数量 = round(可用资金 * 0.05 / 价格, 2)
            推荐.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "数量": 数量,
                "理由": 理由,
            })
    
    else:
        数据 = [
            ("AAPL", "苹果", 88, 175, 5, "业绩超预期"),
            ("NVDA", "英伟达", 85, 120, 8, "AI芯片"),
            ("MSFT", "微软", 82, 330, 3, "云计算"),
        ]
        for 代码, 名称, 评分, 价格, 基数, 理由 in 数据:
            数量 = max(1, int(可用资金 * 0.05 / 价格))
            推荐.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "数量": 数量,
                "理由": 理由,
            })
    
    return 推荐
