# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
import datetime

# ==================== 导入模块 ====================
try:
    from 核心 import 行情获取
    HAS_QUOTE = True
    print("✅ 行情获取模块已加载")
except Exception as e:
    HAS_QUOTE = False
    print(f"⚠️ 行情获取模块加载失败: {e}")

# ==================== 导入策略运行器（用于策略状态） ====================
try:
    from 核心.策略运行器 import 策略运行器
    HAS_STRATEGY_RUNNER = True
except ImportError:
    HAS_STRATEGY_RUNNER = False
    print("⚠️ 策略运行器模块导入失败")

# ==================== 获取策略列表（动态） ====================
def 获取策略列表_动态(策略加载器, 市场过滤=None):
    """从策略加载器获取策略列表，支持按市场过滤"""
    if 策略加载器 is None:
        return []
    
    try:
        所有策略 = 策略加载器.获取策略()
        
        # 只显示运行中的策略
        运行中策略 = []
        for 策略 in 所有策略:
            策略名称 = 策略.get("名称", "")
            
            # 检查策略是否运行中
            if HAS_STRATEGY_RUNNER:
                if not 策略运行器.获取策略状态(策略名称):
                    continue
            
            # 按市场过滤
            if 市场过滤:
                类别 = 策略.get("类别", "")
                if 类别 != 市场过滤:
                    continue
            
            运行中策略.append(策略)
        
        return 运行中策略
    except Exception as e:
        print(f"获取策略列表失败: {e}")
        return []

# ==================== 获取真实AI推荐 ====================
def 获取真实AI推荐(市场, 策略类型, 引擎, 策略加载器):
    """获取真实的AI推荐 - 使用策略的品种"""
    推荐列表 = []
    
    # 获取该策略的信息
    所有策略 = 获取策略列表_动态(策略加载器, 市场)
    目标策略 = None
    for s in 所有策略:
        if s.get("名称") == 策略类型:
            目标策略 = s
            break
    
    if not 目标策略:
        return 推荐列表
    
    品种 = 目标策略.get("品种", "")
    
    if not 品种:
        return 推荐列表
    
    try:
        if HAS_QUOTE:
            价格结果 = 行情获取.获取价格(品种)
            if 价格结果 and 价格结果.价格 > 0:
                价格 = 价格结果.价格
                推荐列表.append({
                    "代码": 品种,
                    "名称": f"{品种}",
                    "价格": 价格,
                    "趋势": "观望",
                    "得分": 50,
                    "理由": f"当前价格 ¥{价格:.2f}",
                    "市场": 市场,
                    "品种": 品种
                })
    except Exception as e:
        print(f"获取推荐失败: {e}")
    
    return 推荐列表

def 获取实时价格(代码, 市场类型):
    """获取实时价格 - 使用行情获取模块"""
    try:
        if HAS_QUOTE:
            价格结果 = 行情获取.获取价格(代码)
            if 价格结果 and 价格结果.价格 > 0:
                return 价格结果.价格
    except:
        pass
    return None

def 执行买入(引擎, 代码, 价格, 数量, 市场类型, 策略类型):
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
            return {"success": False, "error": f"资金不足"}
        
        结果 = 引擎.买入(代码, 价格, 数量)
        return 结果
    except Exception as e:
        return {"success": False, "error": str(e)}

def 显示(引擎, 策略加载器, AI引擎):
    st.markdown("### 🤖 AI 智能交易")
    
    # ========== 获取所有运行中的策略 ==========
    所有运行中策略 = 获取策略列表_动态(策略加载器)
    
    if not 所有运行中策略:
        st.warning("⚠️ 当前没有运行中的策略")
        st.info("💡 请在「策略中心」启动策略，或在侧边栏点击「刷新策略列表」")
        return
    
    # ========== 获取市场列表（从策略中提取） ==========
    市场列表 = []
    市场对应 = {
        "💰 外汇": "外汇",
        "₿ 加密货币": "加密货币",
        "📈 A股": "A股",
        "🇺🇸 美股": "美股",
        "📊 期货": "期货",
    }
    
    for 策略 in 所有运行中策略:
        类别 = 策略.get("类别", "")
        for k, v in 市场对应.items():
            if k == 类别 or v == 类别:
                市场名称 = v
                if 市场名称 not in 市场列表:
                    市场列表.append(市场名称)
                break
    
    if not 市场列表:
        市场列表 = ["A股", "加密货币", "美股", "外汇", "期货"]
    
    市场 = st.selectbox("选择市场", 市场列表)
    
    # ========== 获取该市场下的策略 ==========
    该市场策略 = 获取策略列表_动态(策略加载器, 市场)
    
    if not 该市场策略:
        st.warning(f"⚠️ 当前没有运行中的 {市场} 策略")
        st.info("💡 请在「策略中心」启动该市场的策略")
        return
    
    策略选项 = [s.get("名称", "") for s in 该市场策略]
    策略类型 = st.selectbox("选择策略", 策略选项)
    
    # ========== 显示策略信息 ==========
    for 策略 in 该市场策略:
        if 策略.get("名称") == 策略类型:
            品种 = 策略.get("品种", "")
            st.caption(f"📌 品种: {品种}")
            break
    
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []
    
    if st.button("🚀 AI 分析", type="primary", width='stretch'):
        with st.spinner(f"AI 正在使用【{策略类型}】分析【{市场}】..."):
            try:
                st.session_state.ai_list = 获取真实AI推荐(市场, 策略类型, 引擎, 策略加载器)
                if st.session_state.ai_list:
                    st.success(f"✅ AI 分析完成！共推荐 {len(st.session_state.ai_list)} 只标的")
                else:
                    st.warning("⚠️ 当前策略下未筛选出合适标的")
                st.rerun()
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    if st.session_state.ai_list:
        st.markdown("### 📈 AI 推荐买入（按策略打分）")
        
        for idx, item in enumerate(st.session_state.ai_list):
            code = item.get("代码", "")
            name = item.get("名称", "未知")
            price = item.get("价格", 0)
            趋势 = item.get("趋势", "未知")
            理由 = item.get("理由", "")
            得分 = item.get("得分", 0)
            市场类型 = item.get("市场", "未知")
            
            if 市场类型 == "A股":
                建议数量 = int(可用资金 * 0.1 / price / 100) * 100
                建议数量 = max(建议数量, 100)
                数量单位 = "股"
            elif 市场类型 == "加密货币":
                建议数量 = round(可用资金 * 0.1 / price, 4)
                数量单位 = "个"
            elif 市场类型 == "外汇":
                建议数量 = round(可用资金 * 0.1 / price, 2)
                数量单位 = "手"
            else:
                建议数量 = int(可用资金 * 0.1 / price / 100) * 100
                建议数量 = max(建议数量, 100)
                数量单位 = "股"
            
            if 建议数量 <= 0:
                建议数量 = 1 if 市场类型 == "加密货币" else 100
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: {price:.4f}")
                with col2:
                    if 趋势 in ["上涨", "强势"]:
                        st.markdown("🟢 趋势向上")
                    elif 趋势 == "下跌":
                        st.markdown("🔻 趋势向下")
                    else:
                        st.markdown("🟡 观望")
                    st.caption(f"得分: {得分}")
                with col3:
                    st.caption(f"建议: {建议数量}{数量单位}")
                    st.caption(f"金额: ¥{price * 建议数量:.0f}")
                with col4:
                    if st.button(f"买入", key=f"buy_{code}_{idx}"):
                        if price > 0:
                            实时价格 = 获取实时价格(code, 市场类型)
                            实际价格 = 实时价格 if 实时价格 else price
                            with st.spinner(f"正在买入 {name}..."):
                                结果 = 执行买入(引擎, code, 实际价格, 建议数量, 市场类型, 策略类型)
                                if 结果.get("success"):
                                    st.success(f"✅ {结果['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ 买入失败: {结果.get('error')}")
                        else:
                            st.error("价格无效")
                
                if 理由:
                    st.caption(f"📝 {理由}")
                st.divider()
    
    st.markdown("---")
    st.markdown("### 📦 当前持仓")
    
    if hasattr(引擎, '持仓') and 引擎.持仓:
        持仓数据 = []
        for sym, pos in 引擎.持仓.items():
            数量 = getattr(pos, '数量', 0)
            平均成本 = getattr(pos, '平均成本', 0)
            
            try:
                if HAS_QUOTE and 行情获取:
                    价格结果 = 行情获取.获取价格(sym)
                    if 价格结果 and hasattr(价格结果, '价格'):
                        当前价格 = 价格结果.价格
                    else:
                        当前价格 = 平均成本
                else:
                    当前价格 = 平均成本
            except Exception:
                当前价格 = 平均成本
            
            if hasattr(pos, '当前价格'):
                pos.当前价格 = 当前价格
            
            浮动盈亏 = (当前价格 - 平均成本) * 数量
            
            if sym in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                数量显示 = f"{数量:.4f}"
            else:
                数量显示 = f"{int(数量)}"
            
            持仓数据.append({
                "品种": sym,
                "数量": 数量显示,
                "成本": round(平均成本, 4),
                "现价": round(当前价格, 4),
                "浮动盈亏": round(浮动盈亏, 2)
            })
        
        st.dataframe(持仓数据, width='stretch', hide_index=True)
        
        总盈亏 = sum([d["浮动盈亏"] for d in 持仓数据])
        st.caption(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
    else:
        st.info("暂无持仓")
