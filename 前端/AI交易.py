# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
import datetime

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


def 获取运行中策略列表(策略加载器, 市场过滤=None):
    """从策略加载器获取运行中的策略列表"""
    if 策略加载器 is None:
        return []
    
    try:
        所有策略 = 策略加载器.获取策略()
        
        # 市场类别映射
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
            
            # 只显示运行中的策略
            if HAS_STRATEGY_RUNNER and not 策略运行器.获取策略状态(策略名称):
                continue
            
            if 市场过滤 and 市场名称 != 市场过滤:
                continue
            
            运行中策略.append({
                "名称": 策略名称,
                "品种": 策略.get("品种", ""),
                "类别": 策略类别,
                "市场": 市场名称,
                "原始策略": 策略
            })
        
        return 运行中策略
    except Exception as e:
        print(f"获取策略列表失败: {e}")
        return []


def 获取市场列表(策略加载器):
    """获取市场列表"""
    所有运行中策略 = 获取运行中策略列表(策略加载器)
    市场列表 = []
    for 策略 in 所有运行中策略:
        市场 = 策略.get("市场", "")
        if 市场 and 市场 not in 市场列表:
            市场列表.append(市场)
    return 市场列表


def 获取真实AI推荐(市场, 策略名称, 引擎, 策略加载器):
    """获取AI推荐"""
    推荐列表 = []
    
    所有策略 = 获取运行中策略列表(策略加载器, 市场)
    目标策略 = None
    for s in 所有策略:
        if s.get("名称") == 策略名称:
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
                    "品种": 品种,
                    "策略": 策略名称
                })
    except Exception as e:
        print(f"获取推荐失败: {e}")
    
    return 推荐列表


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
            return {"success": False, "error": f"资金不足"}
        
        结果 = 引擎.买入(代码, 价格, 数量)
        return 结果
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========== 显示函数 ==========
def 显示(引擎, 策略加载器, AI引擎):
    """AI 智能交易页面"""
    st.markdown("### 🤖 AI 智能交易")
    
    # 获取所有运行中的策略
    所有运行中策略 = 获取运行中策略列表(策略加载器)
    
    if not 所有运行中策略:
        st.warning("⚠️ 当前没有运行中的策略")
        st.info("💡 请在「策略中心」启动策略，或在侧边栏点击「刷新策略列表」")
        return
    
    # 获取市场列表
    市场列表 = []
    for 策略 in 所有运行中策略:
        市场 = 策略.get("市场", "")
        if 市场 and 市场 not in 市场列表:
            市场列表.append(市场)
    
    if not 市场列表:
        st.warning("⚠️ 无法获取市场列表")
        return
    
    选中的市场 = st.selectbox("选择市场", 市场列表)
    
    # 获取该市场下的策略
    该市场策略 = [s for s in 所有运行中策略 if s.get("市场") == 选中的市场]
    
    if not 该市场策略:
        st.warning(f"⚠️ 当前没有运行中的 {选中的市场} 策略")
        return
    
    策略选项 = [s.get("名称", "") for s in 该市场策略]
    选中的策略 = st.selectbox("选择策略", 策略选项)
    
    # 显示策略品种
    for 策略 in 该市场策略:
        if 策略.get("名称") == 选中的策略:
            品种 = 策略.get("品种", "")
            st.caption(f"📌 策略品种: {品种}")
            break
    
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    if "ai_list" not in st.session_state:
        st.session_state.ai_list = []
    
    if st.button("🚀 AI 分析", type="primary", width='stretch'):
        with st.spinner(f"AI 正在分析..."):
            try:
                st.session_state.ai_list = 获取真实AI推荐(选中的市场, 选中的策略, 引擎, 策略加载器)
                if st.session_state.ai_list:
                    st.success(f"✅ AI 分析完成！共推荐 {len(st.session_state.ai_list)} 只标的")
                else:
                    st.warning("⚠️ 当前策略下未筛选出合适标的")
                st.rerun()
            except Exception as e:
                st.error(f"AI 分析失败: {e}")
    
    # 显示推荐结果
    if st.session_state.ai_list:
        st.markdown("### 📈 AI 推荐买入")
        
        for idx, item in enumerate(st.session_state.ai_list):
            code = item.get("代码", "")
            name = item.get("名称", "未知")
            price = item.get("价格", 0)
            理由 = item.get("理由", "")
            
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{name}** ({code})")
                    st.caption(f"💰 价格: {price:.2f}")
                with col2:
                    st.caption(f"理由: {理由}")
                with col3:
                    if st.button(f"买入", key=f"buy_{code}_{idx}"):
                        if price > 0:
                            结果 = 执行买入(引擎, code, price, 100, "加密货币", 选中的策略)
                            if 结果.get("success"):
                                st.success(f"✅ 买入成功")
                                st.rerun()
                            else:
                                st.error(f"买入失败: {结果.get('error')}")
                st.divider()
    
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
    else:
        st.info("暂无持仓")
