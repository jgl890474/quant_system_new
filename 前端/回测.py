# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 回测.回测引擎 import 回测引擎

# 导入策略 - 逐行导入，避免语法错误
try:
    from 策略库.期货策略.期货趋势策略 import FuturesTrendStrategy
except:
    FuturesTrendStrategy = None

try:
    from 策略库.加密货币策略.加密双均线 import CryptoDualMAStrategy
except:
    CryptoDualMAStrategy = None

try:
    from 策略库.A股策略.A股双均线 import AStockDualMAStrategy
except:
    AStockDualMAStrategy = None

try:
    from 策略库.美股策略.美股双均线 import USStockDualMAStrategy
except:
    USStockDualMAStrategy = None

try:
    from 策略库.港股策略.港股双均线 import HKStockDualMAStrategy
except:
    HKStockDualMAStrategy = None


def 显示():
    st.markdown("### 📈 策略回测系统")
    st.markdown("使用真实历史数据回测策略表现")
    
    策略类型映射 = {}
    
    if FuturesTrendStrategy:
        策略类型映射["期货趋势策略"] = FuturesTrendStrategy
    if CryptoDualMAStrategy:
        策略类型映射["加密双均线"] = CryptoDualMAStrategy
    if AStockDualMAStrategy:
        策略类型映射["A股双均线"] = AStockDualMAStrategy
    if USStockDualMAStrategy:
        策略类型映射["美股双均线"] = USStockDualMAStrategy
    if HKStockDualMAStrategy:
        策略类型映射["港股双均线"] = HKStockDualMAStrategy
    
    if not 策略类型映射:
        st.error("没有找到任何策略，请检查策略库")
        return
    
    策略名称 = st.selectbox("选择策略", list(策略类型映射.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        品种 = st.selectbox("选择品种", ["AAPL", "BTC-USD", "EURUSD", "GC=F", "000001.SS", "00700.HK"])
    with col2:
        周期 = st.selectbox("K线周期", ["1d", "1h", "30m", "15m", "5m"])
    
    col3, col4 = st.columns(2)
    with col3:
        开始日期 = st.date_input("开始日期", datetime.now() - timedelta(days=500))
    with col4:
        结束日期 = st.date_input("结束日期", datetime.now())
    
    初始资金 = st.number_input("初始资金 (美元)", value=100000, step=10000)
    
    with st.expander("高级参数"):
        滑点基点 = st.number_input("滑点 (基点)", value=1, min_value=0, max_value=100) / 10000
        手续费率 = st.number_input("手续费率 (%)", value=0.05, min_value=0.0, max_value=1.0) / 100
    
    if st.button("开始回测", type="primary", use_container_width=True):
        with st.spinner("回测运行中..."):
            try:
                策略类 = 策略类型映射[策略名称]
                策略 = 策略类("回测策略", 品种, 初始资金)
                引擎 = 回测引擎(初始资金, 滑点基点, 手续费率)
                结果 = 引擎.运行回测(策略, 品种, 开始日期, 结束日期, 周期)
                
                if 结果.get("错误"):
                    st.error(f"回测失败: {结果['错误']}")
                    return
                
                st.success(f"回测完成！共 {结果['交易次数']} 笔交易")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("总收益率", f"{结果['总收益率']*100:.2f}%")
                c2.metric("年化收益率", f"{结果['年化收益率']*100:.2f}%")
                c3.metric("夏普比率", f"{结果['夏普比率']}")
                c4.metric("最大回撤", f"{结果['最大回撤率']*100:.2f}%")
                
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("胜率", f"{结果['胜率']*100:.2f}%")
                c6.metric("盈亏比", f"{结果['盈亏比']}")
                c7.metric("交易次数", f"{结果['交易次数']}")
                c8.metric("换手率", f"{结果['换手率']:.2f}")
                
                if not 结果['净值曲线'].empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=结果['净值曲线']['日期'],
                        y=结果['净值曲线']['净值'],
                        mode='lines',
                        name='净值',
                        line=dict(color='#00d2ff', width=2)
                    ))
                    fig.update_layout(height=400, paper_bgcolor="#0a0c10", plot_bgcolor="#15171a")
                    st.plotly_chart(fig, use_container_width=True)
                
                if "调试信息" in 结果:
                    with st.expander("调试信息"):
                        调试 = 结果["调试信息"]
                        st.write(f"K线数量: {调试['K线数量']}")
                        st.write(f"买入信号: {调试['买入信号次数']}")
                        st.write(f"卖出信号: {调试['卖出信号次数']}")
                        st.write(f"实际交易: {调试['实际交易次数']}")
                    
            except Exception as e:
                st.error(f"回测出错: {e}")
