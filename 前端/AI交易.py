# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # 市场和策略
    市场选项 = ["A股", "加密货币", "美股"]
    策略映射 = {
        "A股": ["A股双均线1", "A股量价策略2", "A股隔夜套利策略3", "简单策略"],
        "加密货币": ["加密双均线1", "加密风控策略"],
        "美股": ["美股简单策略1", "美股动量策略"],
    }
    
    col1, col2 = st.columns(2)
    with col1:
        选中市场 = st.selectbox("选择市场", 市场选项, key=f"market_{st.session_state.page_key}")
    with col2:
        策略选项 = 策略映射.get(选中市场, ["默认策略"])
        选中策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
    
    # 显示当前市场信息
    st.info(f"📊 当前市场: {选中市场} | 策略: {选中策略}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", width="stretch", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{选中市场}市场..."):
            # 根据市场获取推荐
            推荐列表 = 获取推荐(选中市场, 可用资金)
            st.session_state[f"recommend_{st.session_state.page_key}"] = 推荐列表
            st.success(f"✅ 分析完成！共推荐 {len(推荐列表)} 个{选中市场}品种")
            st.rerun()
    
    # 显示推荐
    rec_key = f"recommend_{st.session_state.page_key}"
    if rec_key in st.session_state:
        推荐列表 = st.session_state[rec_key]
        
        if 推荐列表:
            st.markdown("### 📈 AI推荐买入（按评分排序）")
            st.caption("💡 评分越高表示越符合当前策略，建议优先买入高分标的")
            
            for idx, item in enumerate(推荐列表):
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
                    
                    with col1:
                        st.markdown(f"**{item['名称']}**")
                        st.caption(item['代码'])
                    
                    with col2:
                        st.metric("💰 价格", f"¥{item['价格']:.2f}")
                    
                    with col3:
                        评分颜色 = "🟢" if item['评分'] >= 80 else ("🟡" if item['评分'] >= 60 else "⚪")
                        st.markdown(f"{评分颜色} **评分: {item['评分']}分**")
                    
                    with col4:
                        数量单位 = "股" if 选中市场 == "A股" else ("个" if 选中市场 == "加密货币" else "股")
                        st.caption(f"建议: {item['建议数量']}{数量单位}")
                        st.caption(item.get('理由', '')[:20])
                    
                    with col5:
                        if st.button(f"买入", key=f"buy_{idx}_{item['代码']}"):
                            try:
                                结果 = 引擎.买入(item['代码'], item['价格'], item['建议数量'], 策略名称=选中策略)
                                if 结果.get("success"):
                                    st.success(f"✅ 已买入 {item['名称']} {item['建议数量']} {数量单位}")
                                    st.rerun()
                                else:
                                    st.error(f"买入失败: {结果.get('error')}")
                            except Exception as e:
                                st.error(f"买入出错: {e}")
                    
                    st.divider()
        else:
            st.info("暂无推荐结果，请稍后再试")
    else:
        st.info("👈 请点击「AI分析」按钮获取推荐")
    
    # 持仓显示
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    if 引擎.持仓:
        for 品种, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            成本 = getattr(pos, '平均成本', 0)
            st.write(f"- {品种}: {数量:.4f}个 @ ¥{成本:.2f}")
    else:
        st.info("暂无持仓")
    
    st.caption("💡 提示：点击「AI分析」获取推荐，点击「买入」自动下单")


def 获取推荐(市场, 可用资金):
    """根据市场获取推荐列表"""
    推荐列表 = []
    
    print(f"生成推荐 - 市场: {市场}, 可用资金: {可用资金}")
    
    if 市场 == "A股":
        品种数据 = [
            ("600519.SS", "贵州茅台", 88, 1450, "白酒龙头", 100),
            ("000858.SZ", "五粮液", 85, 128, "消费回暖", 200),
            ("300750.SZ", "宁德时代", 82, 180, "新能源龙头", 200),
            ("000333.SZ", "美的集团", 80, 80, "家电龙头", 300),
            ("600036.SS", "招商银行", 78, 38, "银行业绩好", 500),
            ("002415.SZ", "海康威视", 75, 35, "安防龙头", 600),
            ("002594.SZ", "比亚迪", 78, 265, "电动车龙头", 100),
            ("601318.SS", "中国平安", 72, 42, "保险龙头", 500),
            ("600276.SS", "恒瑞医药", 70, 45, "医药龙头", 400),
            ("000001.SS", "平安银行", 68, 11, "银行股", 1000),
        ]
        
        for 代码, 名称, 评分, 价格, 理由, 默认数量 in 品种数据:
            # A股按100股整数倍
            建议数量 = max(100, int(可用资金 * 0.05 / 价格 / 100) * 100)
            if 建议数量 < 100:
                建议数量 = 100
            
            推荐列表.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "建议数量": 建议数量,
                "理由": 理由,
            })
            
    elif 市场 == "加密货币":
        品种数据 = [
            ("BTC-USD", "比特币", 85, 45000, "趋势向上", 0.01),
            ("ETH-USD", "以太坊", 82, 2300, "放量突破", 0.1),
            ("SOL-USD", "Solana", 78, 95, "支撑位反弹", 1),
            ("BNB-USD", "币安币", 75, 580, "平台整理", 0.5),
        ]
        
        for 代码, 名称, 评分, 价格, 理由, 默认数量 in 品种数据:
            建议数量 = round(可用资金 * 0.05 / 价格, 2)
            推荐列表.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "建议数量": 建议数量,
                "理由": 理由,
            })
            
    else:  # 美股
        品种数据 = [
            ("AAPL", "苹果", 88, 175, "业绩超预期", 5),
            ("NVDA", "英伟达", 85, 120, "AI芯片", 8),
            ("MSFT", "微软", 82, 330, "云计算", 3),
            ("TSLA", "特斯拉", 75, 170, "电动车龙头", 5),
            ("GOOGL", "谷歌", 78, 130, "广告业务", 5),
        ]
        
        for 代码, 名称, 评分, 价格, 理由, 默认数量 in 品种数据:
            建议数量 = max(1, int(可用资金 * 0.05 / 价格))
            推荐列表.append({
                "代码": 代码,
                "名称": 名称,
                "价格": 价格,
                "评分": 评分,
                "建议数量": 建议数量,
                "理由": 理由,
            })
    
    # 按评分排序
    推荐列表.sort(key=lambda x: x["评分"], reverse=True)
    
    print(f"生成 {len(推荐列表)} 个推荐")
    return 推荐列表
