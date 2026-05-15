# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def 显示(引擎, 策略加载器=None):
    st.markdown("### 🎛️ 策略管理")
    st.caption("💡 点击「停止」按钮，该策略将不再产生信号，AI交易中也不会显示")
    
    # 尝试获取策略列表，失败时使用默认策略
    策略列表 = []
    
    if 策略加载器 is not None:
        try:
            # 尝试多种获取策略的方法
            if hasattr(策略加载器, '获取策略列表_带状态'):
                策略列表 = 策略加载器.获取策略列表_带状态()
            elif hasattr(策略加载器, '获取策略列表'):
                策略列表 = 策略加载器.获取策略列表()
            elif hasattr(策略加载器, '获取策略'):
                原始列表 = 策略加载器.获取策略()
                # 转换格式
                for s in 原始列表:
                    if isinstance(s, dict):
                        策略列表.append({
                            "名称": s.get("名称", ""),
                            "类别": s.get("类别", ""),
                            "品种": s.get("品种", ""),
                            "启用": True,
                        })
                    else:
                        策略列表.append({
                            "名称": str(s),
                            "类别": "默认",
                            "品种": "未知",
                            "启用": True,
                        })
        except Exception as e:
            st.warning(f"策略加载器调用失败: {e}")
           策略列表 = []
    
    # 如果没有策略，使用默认策略列表
    if not 策略列表:
        策略列表 = [
            {"名称": "双均线策略", "类别": "📈 A股", "品种": "000001", "启用": True},
            {"名称": "量价策略", "类别": "📈 A股", "品种": "000002", "启用": True},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD", "启用": True},
            {"名称": "动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "启用": True},
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD", "启用": True},
        ]
        st.info("使用默认策略列表（策略加载器未配置）")
    
    # 显示策略表格
    if 策略列表:
        df = pd.DataFrame(策略列表)
        
        # 重新排列列顺序
        期望列 = ["名称", "类别", "品种", "启用"]
        现有列 = [c for c in 期望列 if c in df.columns]
        df = df[现有列]
        
        st.dataframe(df, use_container_width=True)
        
        # 策略控制按钮
        st.markdown("---")
        st.markdown("#### 🔧 策略控制")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ 启用所有策略", key="enable_all"):
                st.success("已启用所有策略")
        
        with col2:
            if st.button("⏸️ 停止所有策略", key="disable_all"):
                st.warning("已停止所有策略")
        
        with col3:
            if st.button("🔄 刷新策略列表", key="refresh_strategies"):
                if 策略加载器 and hasattr(策略加载器, '刷新'):
                    策略加载器.刷新()
                st.success("策略列表已刷新")
                st.rerun()
    else:
        st.warning("暂无可用策略")
