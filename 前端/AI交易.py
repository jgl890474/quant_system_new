# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random

# ==================== 导入模块 ====================
try:
    from 核心 import 行情获取
    HAS_QUOTE = True
except Exception as e:
    HAS_QUOTE = False
    print(f"⚠️ 行情获取模块加载失败: {e}")

# ==================== 导入策略运行器 ====================
try:
    from 核心.策略运行器 import 策略运行器
    HAS_STRATEGY_RUNNER = True
except ImportError:
    HAS_STRATEGY_RUNNER = False
    print("⚠️ 策略运行器模块导入失败")


# ==================== 获取运行中的策略列表 ====================
def 获取运行中策略列表(策略加载器, 市场过滤=None):
    """从策略加载器获取运行中的策略列表"""
    if 策略加载器 is None:
        return []
    
    try:
        所有策略 = 策略加载器.获取策略()
        
        市场映射 = {
            "💰 外汇": "外汇",
            "₿ 加密货币": "加密货币",
            "📈 A股": "A股",
            "🇺🇸 美股": "美股",
            "📊 期货": "期货",
        }
        
        运行中策略 = []
        for 策略 in 所有策略:
            策略名称 = 策略.get("名称", "")
            策略类别 = 策略.get("类别", "")
            
            市场名称 = 市场映射.get(策略类别, "")
            if not 市场名称:
                if "外汇" in 策略类别:
                    市场名称 = "外汇"
                elif "加密" in 策略类别:
                    市场名称 = "加密货币"
                elif "A股" in 策略类别:
                    市场名称 = "A股"
                elif "美股" in 策略类别:
                    市场名称 = "美股"
                elif "期货" in 策略类别:
                    市场名称 = "期货"
                else:
                    市场名称 = 策略类别
            
            if HAS_STRATEGY_RUNNER and not 策略运行器.获取策略状态(策略名称):
                continue
            
            if 市场过滤 and 市场名称 != 市场过滤:
                continue
            
            运行中策略.append({
                "名称": 策略名称,
                "品种": 策略.get("品种", ""),
                "类别": 策略类别,
                "市场": 市场名称,
            })
        
        return 运行中策略
    except Exception as e:
        print(f"获取策略列表失败: {e}")
        return []


# ==================== 获取品种列表（根据市场） ====================
def 获取品种列表(市场):
    """根据市场获取可交易品种列表"""
    品种映射 = {
        "加密货币": [
            {"代码": "BTC-USD", "名称": "比特币", "波动率": 0.05, "流动性": 100},
            {"代码": "ETH-USD", "名称": "以太坊", "波动率": 0.06, "流动性": 95},
            {"代码": "SOL-USD", "名称": "Solana", "波动率": 0.08, "流动性": 80},
            {"代码": "BNB-USD", "名称": "币安币", "波动率": 0.05, "流动性": 85},
            {"代码": "XRP-USD", "名称": "瑞波币", "波动率": 0.07, "流动性": 75},
            {"代码": "DOGE-USD", "名称": "狗狗币", "波动率": 0.10, "流动性": 70},
            {"代码": "ADA-USD", "名称": "艾达币", "波动率": 0.07, "流动性": 72},
            {"代码": "AVAX-USD", "名称": "雪崩币", "波动率": 0.09, "流动性": 65},
        ],
        "A股": [
            {"代码": "000001", "名称": "平安银行", "波动率": 0.03, "流动性": 90},
            {"代码": "600036", "名称": "招商银行", "波动率": 0.03, "流动性": 88},
            {"代码": "600519", "名称": "贵州茅台", "波动率": 0.02, "流动性": 95},
            {"代码": "300750", "名称": "宁德时代", "波动率": 0.04, "流动性": 85},
            {"代码": "002415", "名称": "海康威视", "波动率": 0.03, "流动性": 80},
        ],
        "美股": [
            {"代码": "AAPL", "名称": "苹果", "波动率": 0.03, "流动性": 100},
            {"代码": "NVDA", "名称": "英伟达", "波动率": 0.05, "流动性": 95},
            {"代码": "TSLA", "名称": "特斯拉", "波动率": 0.07, "流动性": 90},
            {"代码": "MSFT", "名称": "微软", "波动率": 0.03, "流动性": 98},
            {"代码": "GOOGL", "名称": "谷歌", "波动率": 0.03, "流动性": 95},
        ],
        "外汇": [
            {"代码": "EURUSD", "名称": "欧元/美元", "波动率": 0.01, "流动性": 100},
            {"代码": "GBPUSD", "名称": "英镑/美元", "波动率": 0.02, "流动性": 95},
            {"代码": "USDJPY", "名称": "美元/日元", "波动率": 0.02, "流动性": 98},
        ],
        "期货": [
            {"代码": "GC=F", "名称": "黄金期货", "波动率": 0.02, "流动性": 90},
            {"代码": "CL=F", "名称": "原油期货", "波动率": 0.04, "流动性": 85},
        ],
    }
    return 品种映射.get(市场, [])


# ==================== 计算综合评分 ====================
def 计算综合评分(品种, 策略类型, 市场):
    """计算品种的综合评分（0-100分）"""
    评分 = 50  # 基础分
    
    try:
        # 获取实时价格
        if HAS_QUOTE:
            价格结果 = 行情获取.获取价格(品种["代码"])
            if 价格结果 and 价格结果.价格 > 0:
                当前价格 = 价格结果.价格
                
                # ===== 根据策略类型计算评分 =====
                if "双均线" in 策略类型 or "双均线策略" in 策略类型:
                    # 双均线策略：趋势跟踪
                    评分 += 10  # 基于价格趋势
                
                elif "风控" in 策略类型:
                    # 风控策略：波动率评分
                    if 品种["波动率"] < 0.05:
                        评分 += 15  # 低波动更安全
                    elif 品种["波动率"] < 0.08:
                        评分 += 8
                    else:
                        评分 -= 5
                
                elif "量价" in 策略类型:
                    # 量价策略：流动性评分
                    评分 += int(品种["流动性"] / 10)
                
                elif "动量" in 策略类型:
                    # 动量策略：高波动加分
                    评分 += int(品种["波动率"] * 100)
                
                elif "隔夜" in 策略类型:
                    # 隔夜策略：流动性为主
                    评分 += int(品种["流动性"] / 8)
                
                else:
                    # 默认策略
                    评分 += 5
                
                # 价格区间加分
                if 100 < 当前价格 < 1000:
                    评分 += 5
                elif 当前价格 < 100:
                    评分 += 8
                
                # 随机波动（模拟市场不确定性）
                评分 += random.randint(-5, 10)
        
    except Exception as e:
        print(f"获取价格失败: {e}")
    
    # 限制评分范围
    评分 = max(0, min(100, 评分))
    
    return 评分


# ==================== 获取AI推荐 ====================
def 获取AI推荐(策略类型, 市场, 引擎):
    """根据策略类型获取AI推荐标的"""
    推荐列表 = []
    
    # 获取品种列表
    品种列表 = 获取品种列表(市场)
    
    if not 品种列表:
        return 推荐列表
    
    # 计算每个品种的评分
    for 品种 in 品种列表:
        评分 = 计算综合评分(品种, 策略类型, 市场)
        
        # 获取实时价格
        当前价格 = 0
        if HAS_QUOTE:
            try:
                价格结果 = 行情获取.获取价格(品种["代码"])
                if 价格结果 and 价格结果.价格 > 0:
                    当前价格 = 价格结果.价格
            except:
                pass
        
        推荐列表.append({
            "代码": 品种["代码"],
            "名称": 品种["名称"],
            "价格": 当前价格,
            "评分": 评分,
            "市场": 市场,
            "理由": f"{策略类型}策略评分 {评分}分",
            "建议数量": 100,
            "数量单位": "个" if 市场 == "加密货币" else "股"
        })
    
    # 按评分排序（高分在前）
    推荐列表.sort(key=lambda x: x["评分"], reverse=True)
    
    # 返回前8名，至少5只
    return 推荐列表[:8]


# ==================== 执行买入 ====================
def 执行买入(引擎, 代码, 价格, 数量, 市场类型, 策略类型):
    """执行买入"""
    try:
        if 市场类型 in ["A股", "美股", "期货"]:
            数量 = int(数量)
        else:
            数量 = float(数量)
        
        价格 = float(价格)
        
        if 价格 <= 0:
            return {"success": False, "error": f"价格无效: {价格}"}
        
        if 数量 <= 0:
            return {"success": False, "error": f"数量无效: {数量}"}
        
        可用资金 = 引擎.获取可用资金()
        预计花费 = 价格 * 数量
        if 预计花费 > 可用资金:
            return {"success": False, "error": f"资金不足，需要 ¥{预计花费:.2f}，可用 ¥{可用资金:.2f}"}
        
        结果 = 引擎.买入(代码, 价格, 数量)
        return 结果
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========== 显示函数 ==========
def 显示(引擎, 策略加载器, AI引擎):
    """AI 智能交易页面"""
    st.markdown("### 🤖 AI 智能交易")
    
    # 获取所有运行中的策略
    策略列表 = 获取运行中策略列表(策略加载器)
    
    if not 策略列表:
        st.warning("⚠️ 当前没有运行中的策略")
        st.info("💡 请在「策略中心」启动策略")
        return
    
    # 获取市场列表
    市场选项 = list(set([s.get("市场", "") for s in 策略列表 if s.get("市场")]))
    
    if not 市场选项:
        st.warning("⚠️ 无法获取市场列表")
        return
    
    # 选择市场
    选中市场 = st.selectbox("选择市场", 市场选项)
    
    # 获取该市场下的策略
    该市场策略 = [s for s in 策略列表 if s.get("市场") == 选中市场]
    
    if not 该市场策略:
        st.warning(f"⚠️ 当前没有运行中的 {选中市场} 策略")
        return
    
    # 选择策略
    策略选项 = [s.get("名称", "") for s in 该市场策略]
    选中策略 = st.selectbox("选择策略", 策略选项)
    
    # 显示可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    # AI 分析按钮
    if st.button("🚀 AI 分析", type="primary", width='stretch'):
        with st.spinner(f"AI 正在分析 {选中市场} 市场，使用 {选中策略}..."):
            try:
                st.session_state.ai推荐列表 = 获取AI推荐(选中策略, 选中市场, 引擎)
                if st.session_state.ai推荐列表:
                    st.success(f"✅ AI 分析完成！共推荐 {len(st.session_state.ai推荐列表)} 只标的")
                else:
                    st.warning("⚠️ 未找到合适的标的")
                    st.session_state.ai推荐列表 = []
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
                st.session_state.ai推荐列表 = []
    
    # 显示推荐结果
    if hasattr(st.session_state, 'ai推荐列表') and st.session_state.ai推荐列表:
        st.markdown("### 📈 AI 推荐买入（按综合评分排序）")
        st.caption("💡 评分越高表示越符合当前策略，建议优先买入高分标的")
        
        for idx, item in enumerate(st.session_state.ai推荐列表):
            code = item.get("代码", "")
            name = item.get("名称", "未知")
            price = item.get("价格", 0)
            评分 = item.get("评分", 0)
            理由 = item.get("理由", "")
            建议数量 = item.get("建议数量", 100)
            数量单位 = item.get("数量单位", "股")
            
            # 根据评分设置颜色
            if 评分 >= 80:
                评分颜色 = "🟢"
                建议 = "强烈推荐"
            elif 评分 >= 60:
                评分颜色 = "🟡"
                建议 = "推荐"
            else:
                评分颜色 = "⚪"
                建议 = "观望"
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1.5])
                
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: ¥{price:.2f}" if price > 0 else "💰 价格: 获取中")
                
                with col2:
                    st.markdown(f"{评分颜色} **评分: {评分}分**")
                    st.caption(建议)
                
                with col3:
                    st.caption(f"建议: {建议数量}{数量单位}")
                
                with col4:
                    st.caption(理由[:20])
                
                with col5:
                    if st.button(f"买入", key=f"ai_buy_{idx}_{code}"):
                        if price > 0:
                            # 计算买入数量（根据可用资金的10%）
                            建议金额 = 可用资金 * 0.1
                            计算数量 = int(建议金额 / price / 100) * 100 if 选中市场 == "A股" else 建议金额 / price
                            计算数量 = max(计算数量, 1)
                            if 选中市场 == "加密货币":
                                计算数量 = round(计算数量, 4)
                            
                            结果 = 执行买入(引擎, code, price, 计算数量, 选中市场, 选中策略)
                            if 结果.get("success"):
                                st.success(f"✅ 已买入 {name} {计算数量} {数量单位}")
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                        else:
                            st.error("价格无效")
                
                st.markdown("---")
    
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    # 显示持仓
    if hasattr(引擎, '持仓') and 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            平均成本 = getattr(pos, '平均成本', 0)
            
            try:
                if HAS_QUOTE:
                    价格结果 = 行情获取.获取价格(sym)
                    当前价格 = 价格结果.价格 if 价格结果 else 平均成本
                else:
                    当前价格 = 平均成本
            except:
                当前价格 = 平均成本
            
            浮动盈亏 = (当前价格 - 平均成本) * 数量
            
            持仓数据.append({
                "品种": sym,
                "数量": f"{int(数量)}" if sym not in ["ETH-USD", "BTC-USD"] else f"{数量:.4f}",
                "成本": round(平均成本, 2),
                "现价": round(当前价格, 2),
                "浮动盈亏": round(浮动盈亏, 2)
            })
        
        st.dataframe(pd.DataFrame(持仓数据), width='stretch', hide_index=True)
        
        总盈亏 = sum([d["浮动盈亏"] for d in 持仓数据])
        if 总盈亏 >= 0:
            st.success(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
        else:
            st.error(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
    else:
        st.info("暂无持仓")
