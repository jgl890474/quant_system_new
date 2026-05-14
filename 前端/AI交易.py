# -*- coding: utf-8 -*-
import streamlit as st
import time
import uuid
from 核心 import 行情获取


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """
    AI交易页面 - 智能推荐和自动交易
    """
    
    # 生成唯一的会话ID用于key
    if 'page_key' not in st.session_state:
        st.session_state.page_key = str(uuid.uuid4())[:8]
    
    st.subheader("🤖 AI 智能交易")
    
    # ==================== 选择市场和策略 ====================
    col1, col2 = st.columns(2)
    with col1:
        市场 = st.selectbox(
            "选择市场",
            ["加密货币", "A股", "美股", "外汇", "期货"],
            key=f"market_select_{st.session_state.page_key}"
        )
    with col2:
        if 市场 == "加密货币":
            策略 = st.selectbox(
                "选择策略",
                ["加密双均线1", "加密风控策略"],
                key=f"strategy_select_{st.session_state.page_key}"
            )
        elif 市场 == "A股":
            策略 = st.selectbox(
                "选择策略",
                ["A股双均线1", "A股量价策略2", "A股隔夜套利策略3"],
                key=f"strategy_select_{st.session_state.page_key}"
            )
        elif 市场 == "美股":
            策略 = st.selectbox(
                "选择策略",
                ["美股简单策略1", "美股动量策略"],
                key=f"strategy_select_{st.session_state.page_key}"
            )
        elif 市场 == "外汇":
            策略 = st.selectbox("选择策略", ["外汇利差策略1"], key=f"strategy_select_{st.session_state.page_key}")
        else:
            策略 = st.selectbox("选择策略", ["期货趋势策略"], key=f"strategy_select_{st.session_state.page_key}")
    
    # 显示可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else getattr(引擎, '可用资金', 1000000)
    st.metric("💰 可用资金", f"¥{可用资金:,.2f}")
    
    # ==================== AI分析按钮 ====================
    if st.button("🚀 AI 分析", type="primary", width="stretch", key=f"ai_analyze_{st.session_state.page_key}"):
        with st.spinner(f"AI 正在分析 {市场} 市场，使用 {策略} 策略..."):
            try:
                # 获取推荐列表
                推荐列表 = 获取AI推荐(市场, 策略, 引擎)
                if 推荐列表:
                    st.session_state[f"ai_result_{st.session_state.page_key}"] = 推荐列表
                    st.success(f"✅ AI 分析完成！共推荐 {len(推荐列表)} 只标的")
                else:
                    st.warning("⚠️ 未找到合适的标的")
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # ==================== 显示推荐结果 ====================
    result_key = f"ai_result_{st.session_state.page_key}"
    if result_key in st.session_state and st.session_state[result_key]:
        推荐列表 = st.session_state[result_key]
        
        st.markdown("### 📈 AI 推荐买入（按综合评分排序）")
        st.caption("💡 评分越高表示越符合当前策略，建议优先买入高分标的")
        
        for idx, item in enumerate(推荐列表):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
                
                with col1:
                    st.markdown(f"**{item['名称']}**")
                    st.caption(item['代码'])
                
                with col2:
                    价格 = item.get('价格', 0)
                    if 价格 > 0:
                        st.metric("💰 价格", f"¥{价格:.2f}")
                    else:
                        st.caption("💰 价格: 获取中")
                
                with col3:
                    评分 = item.get('评分', 0)
                    if 评分 >= 80:
                        评分颜色 = "🟢"
                        建议 = "强烈推荐"
                    elif 评分 >= 60:
                        评分颜色 = "🟡"
                        建议 = "推荐"
                    else:
                        评分颜色 = "⚪"
                        建议 = "观望"
                    st.markdown(f"{评分颜色} **评分: {评分}分**")
                    st.caption(建议)
                
                with col4:
                    建议数量 = item.get('建议数量', 100)
                    数量单位 = item.get('数量单位', '个')
                    st.caption(f"建议: {建议数量}{数量单位}")
                
                with col5:
                    if st.button(f"买入", key=f"buy_{idx}_{item['代码']}_{st.session_state.page_key}"):
                        if 价格 > 0:
                            # 计算买入数量
                            if 市场 == "A股":
                                计算数量 = max(100, int(可用资金 * 0.1 / 价格 / 100) * 100)
                            elif 市场 == "加密货币":
                                计算数量 = round(可用资金 * 0.1 / 价格, 4)
                            else:
                                计算数量 = max(1, int(可用资金 * 0.1 / 价格))
                            
                            结果 = 执行买入(引擎, item['代码'], 价格, 计算数量, 市场, 策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {item['名称']} {计算数量} {数量单位}")
                                # 刷新结果
                                st.session_state.pop(result_key, None)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        else:
                            st.error("价格无效，请稍后再试")
                
                st.divider()
    
    # ==================== 显示当前持仓 ====================
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
            
            if sym in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
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


def 获取AI推荐(市场, 策略, 引擎):
    """获取AI推荐列表"""
    推荐列表 = []
    
    # 根据市场获取品种列表
    品种映射 = {
        "加密货币": [
            {"代码": "BTC-USD", "名称": "比特币", "波动率": 0.05},
            {"代码": "ETH-USD", "名称": "以太坊", "波动率": 0.06},
            {"代码": "SOL-USD", "名称": "Solana", "波动率": 0.08},
            {"代码": "BNB-USD", "名称": "币安币", "波动率": 0.05},
            {"代码": "DOGE-USD", "名称": "狗狗币", "波动率": 0.10},
            {"代码": "AVAX-USD", "名称": "雪崩币", "波动率": 0.09},
        ],
        "A股": [
            {"代码": "600519.SS", "名称": "贵州茅台", "波动率": 0.02},
            {"代码": "000858.SZ", "名称": "五粮液", "波动率": 0.03},
            {"代码": "300750.SZ", "名称": "宁德时代", "波动率": 0.04},
            {"代码": "000333.SZ", "名称": "美的集团", "波动率": 0.02},
        ],
        "美股": [
            {"代码": "AAPL", "名称": "苹果", "波动率": 0.03},
            {"代码": "NVDA", "名称": "英伟达", "波动率": 0.05},
            {"代码": "TSLA", "名称": "特斯拉", "波动率": 0.07},
            {"代码": "MSFT", "名称": "微软", "波动率": 0.03},
        ],
        "外汇": [
            {"代码": "EURUSD=X", "名称": "欧元/美元", "波动率": 0.01},
            {"代码": "GBPUSD=X", "名称": "英镑/美元", "波动率": 0.02},
        ],
        "期货": [
            {"代码": "GC=F", "名称": "黄金期货", "波动率": 0.02},
            {"代码": "CL=F", "名称": "原油期货", "波动率": 0.04},
        ],
    }
    
    品种列表 = 品种映射.get(市场, [])
    
    # 获取实时价格
    for 品种 in 品种列表:
        代码 = 品种["代码"]
        try:
            价格结果 = 行情获取.获取价格(代码)
            价格 = 价格结果.价格 if 价格结果 and hasattr(价格结果, '价格') else 0
        except:
            价格 = 0
        
        # 计算评分
        评分 = 50  # 基础分
        
        # 策略加分
        if "双均线" in 策略:
            评分 += 15
        elif "风控" in 策略:
            评分 += 10
        elif "量价" in 策略:
            评分 += 12
        elif "动量" in 策略:
            # 动量策略：高波动加分
            评分 += int(品种["波动率"] * 100)
        else:
            评分 += 8
        
        # 价格区间加分
        if 100 < 价格 < 1000:
            评分 += 5
        elif 价格 < 100 and 价格 > 0:
            评分 += 8
        
        # 限制评分范围
        评分 = max(0, min(100, 评分))
        
        推荐列表.append({
            "代码": 代码,
            "名称": 品种["名称"],
            "价格": 价格,
            "评分": 评分,
            "理由": f"{策略}策略评分 {评分}分",
            "建议数量": 100,
            "数量单位": "个" if 市场 == "加密货币" else "股"
        })
    
    # 按评分排序
    推荐列表.sort(key=lambda x: x["评分"], reverse=True)
    
    return 推荐列表[:8]


def 执行买入(引擎, 代码, 价格, 数量, 市场类型, 策略类型):
    """执行买入"""
    try:
        if 市场类型 in ["A股", "美股", "期货"]:
            数量 = int(数量)
        else:
            数量 = float(数量)
        
        if 价格 <= 0:
            return {"success": False, "error": f"价格无效: {价格}"}
        
        if 数量 <= 0:
            return {"success": False, "error": f"数量无效: {数量}"}
        
        结果 = 引擎.买入(代码, 价格, 数量, 策略名称=策略类型)
        return 结果
    except Exception as e:
        return {"success": False, "error": str(e)}
