import streamlit as st

st.error("=== AI交易模块已加载 ===")

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.error("=== 显示函数被调用了 ===")
    st.markdown("### 🤖 AI 智能交易")
    st.metric("可用资金", f"¥{引擎.获取可用资金():,.2f}")
    
    if st.button("测试按钮"):
        st.success("按钮工作正常")
