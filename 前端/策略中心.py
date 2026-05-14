# -*- coding: utf-8 -*-
import streamlit as st
from 核心.策略加载器 import 策略加载器
from 核心.策略运行器 import 策略运行器


def 显示(引擎=None, 策略加载器=None, AI引擎=None):
    """策略中心页面"""
    st.subheader("🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    try:
        # 获取策略加载器
        if 策略加载器 is None:
            try:
                策略加载器 = 策略加载器()
            except:
                st.error("策略加载器初始化失败")
                return
        
        # 获取所有策略
        所有策略 = 策略加载器.获取策略()
        
        if not 所有策略:
            st.info("暂无可用策略")
            return
        
        # 按市场分组
        策略分组 = {}
        for 策略 in 所有策略:
            类别 = 策略.get("类别", "其他")
            if "外汇" in 类别:
                市场 = "💰 外汇"
            elif "加密" in 类别:
                市场 = "₿ 加密货币"
            elif "A股" in 类别:
                市场 = "📈 A股"
            elif "美股" in 类别:
                市场 = "🇺🇸 美股"
            else:
                市场 = "📊 其他"
            
            if 市场 not in 策略分组:
                策略分组[市场] = []
            策略分组[市场].append(策略)
        
        # 显示每个市场的策略
        for 市场, 策略列表 in 策略分组.items():
            st.markdown(f"### {市场}")
            
            for 策略 in 策略列表:
                策略名 = 策略.get("名称", "未知")
                品种 = 策略.get("品种", "未知")
                状态 = "🟢 运行中"
                
                # 检查策略状态
                if hasattr(策略运行器, '获取策略状态'):
                    if not 策略运行器.获取策略状态(策略名):
                        状态 = "🔴 已停止"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{策略名}**")
                        st.caption(f"品种: {品种}")
                    with col2:
                        st.markdown(f"状态: {状态}")
                    with col3:
                        if st.button(f"🧪 测试", key=f"test_{策略名}"):
                            st.info(f"测试 {策略名} 策略")
                    with col4:
                        if 状态 == "🟢 运行中":
                            if st.button(f"⏹️ 停止", key=f"stop_{策略名}"):
                                if hasattr(策略运行器, '设置策略状态'):
                                    策略运行器.设置策略状态(策略名, False)
                                    st.success(f"已停止 {策略名}")
                                    st.rerun()
                        else:
                            if st.button(f"▶️ 启动", key=f"start_{策略名}"):
                                if hasattr(策略运行器, '设置策略状态'):
                                    策略运行器.设置策略状态(策略名, True)
                                    st.success(f"已启动 {策略名}")
                                    st.rerun()
                    st.divider()
        
        # 全局控制
        st.markdown("---")
        st.markdown("### 🌐 全局控制")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ 全部启动", width="stretch"):
                for 策略 in 所有策略:
                    策略名 = 策略.get("名称", "")
                    if 策略名 and hasattr(策略运行器, '设置策略状态'):
                        策略运行器.设置策略状态(策略名, True)
                st.success("所有策略已启动")
                st.rerun()
        
        with col2:
            if st.button("⏹️ 全部停止", width="stretch"):
                for 策略 in 所有策略:
                    策略名 = 策略.get("名称", "")
                    if 策略名 and hasattr(策略运行器, '设置策略状态'):
                        策略运行器.设置策略状态(策略名, False)
                st.success("所有策略已停止")
                st.rerun()
                
    except Exception as e:
        st.error(f"加载策略失败: {e}")
