import streamlit as st

st.set_page_config(page_title="测试", layout="wide")

st.title("✅ 量化交易系统 - 测试页面")

st.write("如果你能看到这个页面，说明 Streamlit Cloud 运行正常。")

# 测试导入
try:
    from 核心 import 订单引擎
    st.success("✅ 核心模块导入成功")
except Exception as e:
    st.error(f"❌ 核心模块导入失败: {e}")

try:
    from 前端 import 首页
    st.success("✅ 前端模块导入成功")
except Exception as e:
    st.error(f"❌ 前端模块导入失败: {e}")
