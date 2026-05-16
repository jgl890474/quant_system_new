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
        # 优先使用传入的策略加载器，否则创建新的
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
            st.warning("⚠️ 暂无可用策略，请先在策略库中添加策略")
            return
        
    except Exception as e:
        st.error(f"获取策略列表失败: {e}")
        return
    
    # ========== 选择市场和策略 ==========
    col1, col2 = st.columns(2)
    
    with col1:
        市场选项 = list(策略分组.keys())
        选中市场 = st.selectbox("选择市场", 市场选项, key=f"market_{st.session_state.page_key}")
    
    with col2:
        该市场策略 = 策略分组.get(选中市场, [])
        策略选项 = [s.get("名称", "未知") for s in 该市场策略]
        
        if 策略选项:
            选中策略 = st.selectbox("选择策略", 策略选项, key=f"strategy_{st.session_state.page_key}")
        else:
            st.warning(f"⚠️ {选中市场} 下没有可用策略")
            return
    
    # 获取选中的策略详情
    当前策略 = None
    for s in 该市场策略:
        if s.get("名称") == 选中策略:
            当前策略 = s
            break
    
    # 显示策略信息
    if 当前策略:
        st.caption(f"📋 策略: {当前策略.get('名称', '')}")
        st.caption(f"📝 描述: {当前策略.get('描述', '无描述')}")
    
    # 可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # AI分析按钮
    if st.button("🚀 AI 分析", type="primary", key=f"analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI正在分析{选中市场}市场，使用{选中策略}策略..."):
            try:
                # 获取推荐列表
                推荐列表 = 获取AI推荐(选中市场, 选中策略, 引擎, 当前策略, 可用资金)
                
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
            理由 = item.get('理由', f"{选中策略}策略评分{评分}分")
            
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
                    数量单位 = "个" if 选中市场 == "加密货币策略" else "股"
                    st.caption(f"建议: {建议数量}{数量单位}")
                    if len(理由) > 15:
                        st.caption(理由[:15] + "...")
                    else:
                        st.caption(理由)
                
                with col5:
                    if st.button(f"买入", key=f"buy_{idx}_{代码}_{st.session_state.page_key}"):
                        if 代码:
                            try:
                                if 价格 <= 0:
                                    st.error("价格无效，请稍后再试")
                                else:
                                    结果 = 引擎.买入(代码, 价格, 建议数量, 策略名称=选中策略)
                                    if 结果.get("success"):
                                        st.success(f"✅ 已买入 {名称} {建议数量} {数量单位}")
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
    
    st.caption("💡 提示：点击买入后页面会自动刷新")


def 获取AI推荐(市场, 策略名称, 引擎, 策略详情, 可用资金):
    """获取AI推荐列表"""
    推荐列表 = []
    
    # 根据市场获取品种列表
    if "加密" in 市场:
        品种列表 = [
            {"代码": "BTC-USD", "名称": "比特币", "评分": 85},
            {"代码": "ETH-USD", "名称": "以太坊", "评分": 82},
            {"代码": "SOL-USD", "名称": "Solana", "评分": 78},
            {"代码": "BNB-USD", "名称": "币安币", "评分": 75},
            {"代码": "AVAX-USD", "名称": "雪崩币", "评分": 72},
            {"代码": "ADA-USD", "名称": "艾达币", "评分": 70},
        ]
        数量单位 = "个"
    elif "A股" in 市场:
        品种列表 = [
            {"代码": "600519.SS", "名称": "贵州茅台", "评分": 85},
            {"代码": "000858.SZ", "名称": "五粮液", "评分": 80},
            {"代码": "300750.SZ", "名称": "宁德时代", "评分": 78},
            {"代码": "000333.SZ", "名称": "美的集团", "评分": 75},
        ]
        数量单位 = "股"
    else:
        品种列表 = [
            {"代码": "AAPL", "名称": "苹果", "评分": 88},
            {"代码": "NVDA", "名称": "英伟达", "评分": 85},
            {"代码": "MSFT", "名称": "微软", "评分": 82},
            {"代码": "TSLA", "名称": "特斯拉", "评分": 75},
        ]
        数量单位 = "股"
    
    # 获取实时价格并计算建议数量
    for item in 品种列表:
        代码 = item["代码"]
        try:
            价格结果 = 行情获取.获取价格(代码)
            价格 = 价格结果.价格 if 价格结果 and hasattr(价格结果, '价格') else 0
        except:
            价格 = 0
        
        # 计算建议数量（使用可用资金的5%）
        if 价格 > 0:
            建议数量 = max(1, int(可用资金 * 0.05 / 价格))
            if "加密" in 市场:
                建议数量 = round(可用资金 * 0.05 / 价格, 2)
        else:
            建议数量 = 1
        
        推荐列表.append({
            "代码": 代码,
            "名称": item["名称"],
            "价格": 价格,
            "得分": item["评分"],
            "评分": item["评分"],
            "建议数量": 建议数量,
            "理由": f"{策略名称}策略推荐"
        })
    
    # 按评分排序
    推荐列表.sort(key=lambda x: x["得分"], reverse=True)
    
    return 推荐列表[:5]
