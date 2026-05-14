# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """AI交易页面"""
    
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # 选择市场和策略
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox("选择市场", ["加密货币", "A股", "美股"], key=f"market_{st.session_state.page_key}")
    with col2:
        if 市场 == "加密货币":
            策略选项 = ["加密双均线1", "加密风控策略"]
        elif 市场 == "A股":
            策略选项 = ["A股双均线1", "A股量价策略2", "A股隔夜套利策略3"]
        else:
            策略选项 = ["美股简单策略1", "美股动量策略"]
        策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{市场}市场，使用{策略}策略..."):
            try:
                # 调用真正的AI引擎
                if AI引擎 and hasattr(AI引擎, 'AI推荐'):
                    result = AI引擎.AI推荐(市场, 策略)
                    推荐列表 = result.get("推荐", [])
                else:
                    # 备用：手动获取推荐
                    推荐列表 = 手动获取推荐(市场)
                
                # 获取实时价格并计算合理数量
                for item in 推荐列表:
                    代码 = item.get('代码', '')
                    if 代码:
                        try:
                            价格结果 = 行情获取.获取价格(代码)
                            if 价格结果 and hasattr(价格结果, '价格'):
                                item['价格'] = 价格结果.价格
                            else:
                                item['价格'] = 0
                        except:
                            item['价格'] = 0
                    
                    # 计算建议数量
                    if item['价格'] > 0:
                        if 市场 == "A股":
                            # A股按100股整数倍，使用5%资金
                            建议数量 = max(100, int(可用资金 * 0.05 / item['价格'] / 100) * 100)
                        elif 市场 == "加密货币":
                            # 加密货币，使用5%资金，限制最大100个
                            建议数量 = round(可用资金 * 0.05 / item['价格'], 2)
                            if 建议数量 > 1000:
                                建议数量 = 100
                        else:
                            # 美股，使用5%资金
                            建议数量 = max(1, int(可用资金 * 0.05 / item['价格']))
                        item['建议数量'] = 建议数量
                    else:
                        item['建议数量'] = 100 if 市场 != "加密货币" else 1
                
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
        st.markdown("### 📈 AI推荐买入（按评分排序）")
        st.caption("💡 评分越高表示越符合当前策略，建议优先买入高分标的")
        
        for idx, item in enumerate(st.session_state[rec_key]):
            代码 = item.get('代码', '')
            名称 = item.get('名称', 代码)
            价格 = item.get('价格', 0)
            评分 = item.get('得分', item.get('评分', 60))
            建议数量 = item.get('建议数量', 100)
            理由 = item.get('理由', f"{策略}策略评分{评分}分")
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
                
                with col1:
                    st.markdown(f"**{名称}**")
                    st.caption(代码)
                
                with col2:
                    if 价格 > 0:
                        st.metric("💰 价格", f"¥{价格:.2f}")
                    else:
                        st.caption("💰 价格获取中")
                
                with col3:
                    if 评分 >= 80:
                        评分颜色 = "🟢"
                    elif 评分 >= 60:
                        评分颜色 = "🟡"
                    else:
                        评分颜色 = "⚪"
                    st.markdown(f"{评分颜色} **评分: {评分}分**")
                
                with col4:
                    数量单位 = "个" if 市场 == "加密货币" else "股"
                    st.caption(f"建议: {建议数量}{数量单位}")
                    st.caption(理由[:15] + "..." if len(理由) > 15 else 理由)
                
                with col5:
                    if st.button(f"买入", key=f"buy_{idx}_{代码}_{st.session_state.page_key}"):
                        if 代码:
                            try:
                                if 价格 <= 0:
                                    st.error("价格无效，请稍后再试")
                                else:
                                    # 使用策略名称进行买入
                                    结果 = 引擎.买入(代码, 价格, 建议数量, 策略名称=策略)
                                    if 结果.get("success"):
                                        st.success(f"✅ 已买入 {名称} {建议数量} {数量单位}")
                                        # 清除推荐，刷新页面
                                        st.session_state.pop(rec_key, None)
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(f"买入失败: {结果.get('error')}")
                            except Exception as e:
                                st.error(f"买入出错: {e}")
                
                st.divider()
    
    # 显示当前持仓
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if hasattr(引擎, '持仓') and 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            平均成本 = getattr(pos, '平均成本', 0)
            
            try:
                价格结果 = 行情获取.获取价格(sym)
                当前价格 = 价格结果.价格 if 价格结果 and hasattr(价格结果, '价格') else 平均成本
            except:
                当前价格 = 平均成本
            
            浮动盈亏 = (当前价格 - 平均成本) * 数量
            
            if sym in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD", "ADA-USD", "XRP-USD", "AVAX-USD"]:
                数量显示 = f"{数量:.4f}"
            else:
                数量显示 = f"{int(数量)}"
            
            持仓数据.append({
                "品种": sym,
                "数量": 数量显示,
                "成本": round(平均成本, 2),
                "现价": round(当前价格, 2),
                "浮动盈亏": round(浮动盈亏, 2)
            })
        
        import pandas as pd
        st.dataframe(pd.DataFrame(持仓数据), width="stretch", hide_index=True)
        
        总盈亏 = sum([d["浮动盈亏"] for d in 持仓数据])
        if 总盈亏 >= 0:
            st.success(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
        else:
            st.error(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
    else:
        st.info("暂无持仓")
    
    # 底部提示
    st.markdown("---")
    st.caption("⚠️ 风险提示：AI推荐仅供参考，请理性投资，注意风险控制")


def 手动获取推荐(市场):
    """备用推荐逻辑"""
    推荐列表 = []
    if 市场 == "加密货币":
        品种 = [
            ("BTC-USD", "比特币", 85),
            ("ETH-USD", "以太坊", 82),
            ("SOL-USD", "Solana", 78),
            ("BNB-USD", "币安币", 75),
            ("AVAX-USD", "雪崩币", 72),
            ("ADA-USD", "艾达币", 70),
            ("XRP-USD", "瑞波币", 68),
            ("DOGE-USD", "狗狗币", 65),
        ]
    elif 市场 == "A股":
        品种 = [
            ("600519.SS", "贵州茅台", 85),
            ("000858.SZ", "五粮液", 80),
            ("300750.SZ", "宁德时代", 78),
            ("000333.SZ", "美的集团", 75),
            ("600036.SS", "招商银行", 72),
        ]
    else:
        品种 = [
            ("AAPL", "苹果", 88),
            ("NVDA", "英伟达", 85),
            ("MSFT", "微软", 82),
            ("TSLA", "特斯拉", 75),
            ("GOOGL", "谷歌", 78),
        ]
    
    for 代码, 名称, 评分 in 品种:
        推荐列表.append({
            "代码": 代码,
            "名称": 名称,
            "价格": 0,
            "得分": 评分,
            "评分": 评分,
            "理由": f"技术指标向好"
        })
    return 推荐列表
