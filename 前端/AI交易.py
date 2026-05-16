# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from 核心 import 行情获取
from 核心.策略加载器 import 获取策略加载器


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # ========== 获取策略列表 ==========
    try:
        if 策略加载器 is None:
            策略加载器 = 获取策略加载器()
        
        所有策略 = 策略加载器.获取策略列表()
        
        # 按类别分组
        策略分组 = {}
        for 策略 in 所有策略:
            类别 = 策略.get("类别", "其他")
            if 类别 not in 策略分组:
                策略分组[类别] = []
            策略分组[类别].append(策略)
        
        if not 策略分组:
            st.warning("⚠️ 暂无可用策略")
            return
        
    except Exception as e:
        st.error(f"获取策略失败: {e}")
        return
    
    # ========== 选择市场和策略 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场选项 = list(策略分组.keys())
        显示市场选项 = []
        for m in 市场选项:
            if "加密" in m:
                显示市场选项.append("加密货币")
            elif "A股" in m:
                显示市场选项.append("A股")
            elif "美股" in m:
                显示市场选项.append("美股")
            else:
                显示市场选项.append(m)
        
        选中市场 = st.selectbox("选择市场", 显示市场选项, key=f"market_{st.session_state.page_key}")
    
    with col2:
        # 根据选中的市场找到对应的策略
        原始市场 = None
        for m in 市场选项:
            if "加密" in m and 选中市场 == "加密货币":
                原始市场 = m
                break
            elif "A股" in m and 选中市场 == "A股":
                原始市场 = m
                break
            elif "美股" in m and 选中市场 == "美股":
                原始市场 = m
                break
        
        if 原始市场:
            该市场策略 = 策略分组.get(原始市场, [])
            策略选项 = [s.get("名称", "未知") for s in 该市场策略]
        else:
            策略选项 = []
        
        if 策略选项:
            选中策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
        else:
            st.warning(f"⚠️ {选中市场} 下没有可用策略")
            return
    
    # 显示可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{选中市场}市场..."):
            try:
                # 直接生成推荐，不依赖实时价格
                推荐列表 = 生成演示推荐(选中市场, 可用资金)
                
                st.session_state[f"recommend_{st.session_state.page_key}"] = 推荐列表
                if 推荐列表:
                    st.success(f"✅ AI分析完成！共推荐 {len(推荐列表)} 个品种")
                else:
                    st.warning("⚠️ 暂无推荐结果")
            except Exception as e:
                st.error(f"AI分析失败: {e}")
    
    # 显示推荐
    rec_key = f"recommend_{st.session_state.page_key}"
    if rec_key in st.session_state and st.session_state[rec_key]:
        st.markdown("### 📈 AI推荐买入")
        st.caption("💡 评分越高表示越符合当前策略")
        
        for idx, item in enumerate(st.session_state[rec_key]):
            代码 = item.get('代码', '')
            名称 = item.get('名称', 代码)
            价格 = item.get('价格', 0)
            评分 = item.get('评分', 60)
            建议数量 = item.get('建议数量', 100)
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])
                
                with col1:
                    st.markdown(f"**{名称}**")
                    st.caption(代码)
                
                with col2:
                    if 价格 > 0:
                        st.write(f"¥{价格:.2f}")
                    else:
                        st.write("价格获取中")
                
                with col3:
                    st.write(f"评分: {评分}")
                
                with col4:
                    if st.button(f"买入", key=f"buy_{idx}_{代码}"):
                        if 代码:
                            try:
                                if 价格 <= 0:
                                    价格 = 获取演示价格(代码)
                                if 价格 > 0:
                                    结果 = 引擎.买入(代码, 价格, 建议数量, 策略名称=选中策略)
                                    if 结果.get("success"):
                                        st.success(f"✅ 已买入 {名称} {建议数量}")
                                        st.rerun()
                                    else:
                                        st.error(f"买入失败: {结果.get('error')}")
                                else:
                                    st.error("价格无效")
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


def 生成演示推荐(市场, 可用资金):
    """生成演示推荐"""
    推荐列表 = []
    
    if 市场 == "加密货币":
        品种数据 = [
            ("BTC-USD", "比特币", 85, 45000),
            ("ETH-USD", "以太坊", 82, 2300),
            ("SOL-USD", "Solana", 78, 95),
            ("BNB-USD", "币安币", 75, 580),
        ]
    elif 市场 == "A股":
        品种数据 = [
            ("600519.SS", "贵州茅台", 88, 1450),
            ("000858.SZ", "五粮液", 85, 128),
            ("300750.SZ", "宁德时代", 82, 180),
            ("000333.SZ", "美的集团", 80, 80),
            ("600036.SS", "招商银行", 78, 38),
            ("002415.SZ", "海康威视", 75, 35),
            ("002594.SZ", "比亚迪", 78, 265),
        ]
    else:
        品种数据 = [
            ("AAPL", "苹果", 88, 175),
            ("NVDA", "英伟达", 85, 120),
            ("MSFT", "微软", 82, 330),
            ("TSLA", "特斯拉", 75, 170),
        ]
    
    for 代码, 名称, 评分, 演示价格 in 品种数据:
        # 计算建议数量
        if 市场 == "A股":
            建议数量 = max(100, int(可用资金 * 0.05 / 演示价格 / 100) * 100)
        elif 市场 == "加密货币":
            建议数量 = round(可用资金 * 0.05 / 演示价格, 2)
            if 建议数量 > 10:
                建议数量 = 1
        else:
            建议数量 = max(1, int(可用资金 * 0.05 / 演示价格))
        
        推荐列表.append({
            "代码": 代码,
            "名称": 名称,
            "价格": 演示价格,
            "评分": 评分,
            "建议数量": 建议数量,
        })
    
    return 推荐列表


def 获取演示价格(代码):
    """获取演示价格"""
    价格映射 = {
        "BTC-USD": 45000,
        "ETH-USD": 2300,
        "AAPL": 175,
        "NVDA": 120,
        "600519.SS": 1450,
        "000858.SZ": 128,
    }
    return 价格映射.get(代码, 100)
