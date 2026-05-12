# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from 核心 import 行情获取
from datetime import datetime


def 显示(引擎, 策略加载器=None, AI引擎=None):
    """显示持仓管理页面"""
    
    # ========== 强制从 session_state 重新获取引擎 ==========
    if '订单引擎' in st.session_state:
        引擎 = st.session_state.订单引擎
    
    st.markdown("### 💼 当前持仓")
    
    # ==================== 先更新所有持仓的当前价格 ====================
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        for 品种 in list(引擎.持仓.keys()):
            try:
                价格结果 = 行情获取.获取价格(品种)
                if 价格结果 and hasattr(价格结果, '价格'):
                    当前价格 = 价格结果.价格
                    if 当前价格 and 当前价格 > 0:
                        if 品种 in 引擎.持仓:
                            引擎.持仓[品种].当前价格 = 当前价格
            except Exception:
                pass
    
    # ========== 持仓显示 ==========
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        数据 = []
        持仓列表 = list(引擎.持仓.items())
        
        for 品种, pos in 持仓列表:
            try:
                数量 = float(getattr(pos, '数量', 0))
                成本价 = float(getattr(pos, '平均成本', 0))
                
                # 跳过数量为0的持仓
                if 数量 <= 0:
                    continue
                
                # 获取实时价格
                价格结果 = 行情获取.获取价格(品种)
                
                if hasattr(价格结果, '价格'):
                    现价 = float(价格结果.价格)
                elif hasattr(价格结果, 'price'):
                    现价 = float(价格结果.price)
                elif isinstance(价格结果, (int, float)):
                    现价 = float(价格结果)
                else:
                    现价 = 成本价
                
                pos.当前价格 = 现价
                盈亏 = (现价 - 成本价) * 数量
                盈亏率 = ((现价 - 成本价) / 成本价) * 100 if 成本价 > 0 else 0
                
                # 修复数量显示：加密货币显示4位小数，其他显示整数
                if 品种 in ["ETH-USD", "BTC-USD", "SOL-USD", "BNB-USD"]:
                    数量显示 = f"{数量:.4f}"
                else:
                    # 确保数量显示为整数，不要有千位分隔符
                    数量显示 = f"{int(数量)}"
                
                数据.append({
                    "品种": 品种,
                    "数量": 数量显示,
                    "成本": f"{成本价:.2f}",
                    "现价": f"{现价:.2f}",
                    "盈亏": f"¥{盈亏:+,.2f}",
                    "盈亏率": f"{盈亏率:+.2f}%",
                    "_数量": 数量,
                    "_成本价": 成本价
                })
                
            except Exception as e:
                print(f"处理 {品种} 时出错: {e}")
                continue
        
        if 数据:
            显示列 = ["品种", "数量", "成本", "现价", "盈亏", "盈亏率"]
            st.dataframe(pd.DataFrame(数据)[显示列], width='stretch', hide_index=True)
            
            # 显示总盈亏
            总盈亏 = 0.0
            for d in 数据:
                if d["盈亏"] != "---":
                    try:
                        盈亏值 = float(d["盈亏"].replace("¥", "").replace(",", ""))
                        总盈亏 += 盈亏值
                    except:
                        pass
            st.caption(f"📊 持仓总盈亏: ¥{总盈亏:+,.2f}")
            
            # ========== 平仓操作区 ==========
            st.markdown("---")
            st.markdown("### 📤 平仓操作")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                卖出品种选择 = st.selectbox("选择要平仓的品种", [d["品种"] for d in 数据], key="sell_select")
            with col2:
                卖出比例 = st.selectbox("卖出比例", ["100%", "75%", "50%", "25%"], key="sell_ratio")
            with col3:
                if st.button("✈️ 执行平仓", key="sell_position_btn"):
                    选中数据 = None
                    for d in 数据:
                        if d["品种"] == 卖出品种选择:
                            选中数据 = d
                            break
                    
                    if 选中数据:
                        数量 = float(选中数据["_数量"])
                        
                        if 卖出比例 == "100%":
                            卖出数量 = 数量
                        elif 卖出比例 == "75%":
                            卖出数量 = 数量 * 0.75
                        elif 卖出比例 == "50%":
                            卖出数量 = 数量 * 0.5
                        else:
                            卖出数量 = 数量 * 0.25
                        
                        # 获取当前价格
                        价格结果 = 行情获取.获取价格(卖出品种选择)
                        if hasattr(价格结果, '价格'):
                            当前价格 = 价格结果.价格
                        else:
                            当前价格 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        
                        if 当前价格 > 0:
                            结果 = 引擎.卖出(卖出品种选择, 当前价格, 卖出数量)
                            if 结果.get("success"):
                                st.success(f"✅ 成功卖出 {卖出品种选择} {卖出数量} 股")
                                # 关键：更新 session_state 中的引擎
                                st.session_state.订单引擎 = 引擎
                                st.rerun()
                            else:
                                st.error(f"卖出失败: {结果.get('error')}")
                        else:
                            st.error("获取当前价格失败")
            
            # ========== K线图表区域 ==========
            st.markdown("---")
            st.markdown("### 📈 品种K线图分析")
            
            品种列表 = [d["品种"] for d in 数据]
            选中品种 = st.selectbox("选择品种查看K线图", 品种列表, key="kline_select")
            
            if 选中品种:
                with st.spinner(f"正在加载 {选中品种} 的K线数据..."):
                    # 尝试导入K线获取函数
                    try:
                        df_kline = 行情获取.获取K线数据(选中品种)
                        if df_kline is not None and not df_kline.empty:
                            st.line_chart(df_kline.set_index('日期')['收盘'] if '日期' in df_kline.columns else df_kline)
                        else:
                            st.info(f"暂无 {选中品种} 的K线数据")
                    except Exception as e:
                        st.info(f"K线数据暂不可用: {str(e)[:50]}")
    else:
        st.caption("暂无持仓")
        
        # 显示调试信息：尝试从数据库恢复
        if st.button("🔄 尝试恢复持仓数据"):
            try:
                from 工具 import 数据库
                持仓数据 = 数据库.加载持仓快照()
                if 持仓数据:
                    st.info(f"从数据库找到 {len(持仓数据)} 条持仓记录，请刷新页面")
                else:
                    st.info("数据库中没有持仓记录")
            except:
                pass
    
    st.markdown("---")
    
    # ========== 止损止盈设置 ==========
    st.markdown("### 🛡️ 止损止盈设置")
    
    if '风控引擎' in st.session_state:
        风控 = st.session_state.风控引擎
        当前止损 = getattr(风控, '止损比例', 0.02) * 100
        当前止盈 = getattr(风控, '止盈比例', 0.04) * 100
        当前移动止损 = getattr(风控, '移动止损开关', True)
        当前回撤 = getattr(风控, '移动止损回撤', 0.02) * 100
    else:
        当前止损 = 2.0
        当前止盈 = 4.0
        当前移动止损 = True
        当前回撤 = 2.0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        止损比例 = st.number_input("止损比例 (%)", min_value=0.5, max_value=20.0, value=当前止损, step=0.5)
    with col2:
        止盈比例 = st.number_input("止盈比例 (%)", min_value=0.5, max_value=50.0, value=当前止盈, step=0.5)
    with col3:
        移动止损 = st.checkbox("开启移动止损", value=当前移动止损)
    
    if 移动止损:
        col4, col5, col6 = st.columns(3)
        with col4:
            移动止损回撤 = st.number_input("移动止损回撤 (%)", min_value=0.5, max_value=10.0, value=当前回撤, step=0.5)
    
    if st.button("应用风控参数", width='stretch'):
        if '风控引擎' in st.session_state:
            st.session_state.风控引擎.止损比例 = 止损比例 / 100
            st.session_state.风控引擎.止盈比例 = 止盈比例 / 100
            st.session_state.风控引擎.移动止损开关 = 移动止损
            if 移动止损:
                st.session_state.风控引擎.移动止损回撤 = 移动止损回撤 / 100
            st.success("✅ 风控参数已更新")
            st.rerun()
    
    st.markdown("---")
    
    # ========== 手动平仓按钮 ==========
    if 引擎 and hasattr(引擎, '持仓') and 引擎.持仓:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 一键平仓所有持仓", width='stretch'):
                for 品种 in list(引擎.持仓.keys()):
                    try:
                        价格结果 = 行情获取.获取价格(品种)
                        if hasattr(价格结果, '价格'):
                            现价 = 价格结果.价格
                        else:
                            现价 = 价格结果 if isinstance(价格结果, (int, float)) else 0
                        if 现价 > 0:
                            引擎.卖出(品种, 现价, 引擎.持仓[品种].数量)
                    except:
                        pass
                st.session_state.订单引擎 = 引擎
                st.success("✅ 已执行一键平仓")
                st.rerun()
        with col2:
            if st.button("🔄 刷新页面", width='stretch'):
                st.rerun()
    
    st.markdown("---")
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
