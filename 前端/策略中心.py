# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from 核心 import 行情获取
from 核心.策略运行器 import 策略运行器


def 显示(引擎, 策略加载器, 策略信号):
    st.markdown("### 📊 策略中心")
    st.markdown("---")
    
    # ========== 策略管理面板 ==========
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 获取所有策略
    策略列表 = 策略加载器.获取策略()
    
    if not 策略列表:
        st.warning("暂无策略，请检查策略库目录")
        return
    
    # 按类别分组显示
    类别分组 = {}
    for 策略 in 策略列表:
        类别 = 策略.get("类别", "其他")
        if 类别 not in 类别分组:
            类别分组[类别] = []
        类别分组[类别].append(策略)
    
    # 显示策略管理表格
    for 类别, 策略组 in 类别分组.items():
        st.markdown(f"#### {类别}")
        
        for 策略 in 策略组:
            策略名称 = 策略.get("名称", "未知")
            品种 = 策略.get("品种", "未知")
            
            # 获取当前策略状态
            当前状态 = 策略运行器.获取策略状态(策略名称)
            状态文本 = "🟢 运行中" if 当前状态 else "🔴 已停止"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{策略名称}**")
                st.caption(f"品种: {品种}")
                st.caption(f"状态: {状态文本}")
            
            with col2:
                # 测试按钮（只显示信号，不执行交易）
                if st.button(f"🧪 测试", key=f"test_{策略名称}"):
                    with st.spinner(f"正在测试 {策略名称}..."):
                        try:
                            测试行情 = 行情获取.获取价格(品种)
                            if 测试行情 and hasattr(测试行情, '价格'):
                                from 核心.策略运行器 import 策略运行器 as 运行器
                                信号 = 运行器.运行(策略, 测试行情)
                                信号显示 = "🟢 买入" if 信号 == 'buy' else ("🔴 卖出" if 信号 == 'sell' else "⚪ 持有")
                                st.info(f"📡 当前信号: {信号显示}")
                            else:
                                st.error("获取行情失败")
                        except Exception as e:
                            st.error(f"测试失败: {e}")
            
            with col3:
                # 启停按钮
                if 当前状态:
                    if st.button(f"⏹️ 停止", key=f"stop_{策略名称}"):
                        策略运行器.设置策略状态(策略名称, False)
                        st.success(f"✅ 策略 [{策略名称}] 已停止")
                        st.rerun()
                else:
                    if st.button(f"▶️ 启动", key=f"start_{策略名称}"):
                        策略运行器.设置策略状态(策略名称, True)
                        st.success(f"✅ 策略 [{策略名称}] 已启动")
                        st.rerun()
            
            with col4:
                # 显示策略简要说明
                if "双均线" in 策略名称:
                    st.caption("📊 双均线策略")
                elif "风控" in 策略名称:
                    st.caption("🛡️ 风控策略")
                elif "量价" in 策略名称:
                    st.caption("📈 量价策略")
                elif "隔夜" in 策略名称:
                    st.caption("🌙 隔夜策略")
                else:
                    st.caption("📊 策略")
        
        st.markdown("---")
    
    # ========== 全局控制 ==========
    st.markdown("### 🌐 全局控制")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ 全部启动", width='stretch'):
            for 策略 in 策略列表:
                策略名称 = 策略.get("名称", "")
                if 策略名称:
                    策略运行器.设置策略状态(策略名称, True)
            st.success("✅ 所有策略已启动")
            st.rerun()
    
    with col2:
        if st.button("⏹️ 全部停止", width='stretch'):
            for 策略 in 策略列表:
                策略名称 = 策略.get("名称", "")
                if 策略名称:
                    策略运行器.设置策略状态(策略名称, False)
            st.warning("⚠️ 所有策略已停止")
            st.rerun()
    
    st.markdown("---")
    
    # ========== 策略信号显示 ==========
    st.markdown("### 📡 策略信号")
    st.caption("💡 只有「运行中」的策略才会显示信号")
    
    # 获取当前持仓品种
    持仓品种列表 = list(引擎.持仓.keys()) if 引擎.持仓 else []
    
    for 策略 in 策略列表:
        策略名称 = 策略.get("名称", "未知")
        品种 = 策略.get("品种", "未知")
        类别 = 策略.get("类别", "其他")
        
        # 检查策略是否启用（只显示运行中的策略信号）
        if not 策略运行器.获取策略状态(策略名称):
            continue
        
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{策略名称}**")
                st.caption(f"{类别} | {品种}")
            
            with col2:
                try:
                    当前价格 = 行情获取.获取价格(品种).价格
                    st.metric("价格", f"¥{当前价格:.2f}")
                except:
                    st.metric("价格", "获取中")
            
            with col3:
                try:
                    from 核心.策略运行器 import 策略运行器 as 运行器
                    信号 = 运行器.运行(策略, 行情获取.获取价格(品种))
                    
                    if 信号 == 'buy':
                        st.markdown("🟢 **买入**")
                        st.caption("建议开仓")
                    elif 信号 == 'sell':
                        st.markdown("🔴 **卖出**")
                        st.caption("建议平仓")
                    else:
                        st.markdown("⚪ **持有**")
                        st.caption("继续观望")
                except:
                    st.markdown("⚪ **等待**")
                    st.caption("数据加载中")
        
        st.markdown("---")
