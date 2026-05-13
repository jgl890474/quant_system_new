# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

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
    
    # 获取策略品种
    选中品种 = ""
    for s in 该市场策略:
        if s.get("名称") == 选中策略:
            选中品种 = s.get("品种", "")
            st.caption(f"📌 策略品种: {选中品种}")
            break
    
    # 显示可用资金
    可用资金 = 引擎.获取可用资金() if hasattr(引擎, '获取可用资金') else 0
    st.caption(f"💰 可用资金: ¥{可用资金:,.2f}")
    
    # AI 分析按钮
    if st.button("🚀 AI 分析", type="primary", width='stretch'):
        if 选中品种:
            try:
                if HAS_QUOTE:
                    价格结果 = 行情获取.获取价格(选中品种)
                    if 价格结果 and 价格结果.价格 > 0:
                        st.success(f"✅ 分析完成！{选中品种} 当前价格: ¥{价格结果.价格:.2f}")
                        st.info(f"💡 建议: 可根据策略信号决定是否买入")
                    else:
                        st.error("获取价格失败")
                else:
                    st.error("行情模块未连接")
            except Exception as e:
                st.error(f"分析失败: {e}")
        else:
            st.error("无法获取策略品种")
    
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
                "数量": f"{int(数量)}",
                "成本": round(平均成本, 2),
                "现价": round(当前价格, 2),
                "浮动盈亏": round(浮动盈亏, 2)
            })
        
        st.dataframe(pd.DataFrame(持仓数据), width='stretch', hide_index=True)
    else:
        st.info("暂无持仓")
