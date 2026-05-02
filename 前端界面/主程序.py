import streamlit as st
import pandas as pd
from 数据接入模块 import 获取数据
from 策略引擎.策略加载器 import 策略加载器
from AI模块.AI交易引擎 import AI交易引擎

st.set_page_config(page_title="量化交易系统", layout="wide")

# 初始化
if '引擎' not in st.session_state:
    st.session_state.引擎 = AI交易引擎()

st.title("🚀 量化交易系统")
st.caption("模块化 · 多类目 · AI自动交易")

# 导航
菜单 = ["首页", "AI交易", "策略管理", "持仓"]
cols = st.columns(len(菜单))
for col, name in zip(cols, 菜单):
    if st.button(name, use_container_width=True):
        st.session_state.页面 = name

# 首页
if st.session_state.get('页面') == "首页":
    st.info("系统已就绪")

# AI交易
elif st.session_state.get('页面') == "AI交易":
    engine = st.session_state.引擎
    策略 = st.selectbox("选择策略", ["双均线策略 (股票)", "加密网格 (加密货币)"])
    if st.button("启动AI交易"):
        engine.注册策略(None, 策略)
        engine.执行一轮()
        st.success("执行完成")
    
    # 显示状态
    st.metric("现金", f"{engine.现金:.0f}")
    st.metric("持仓", len(engine.持仓))

# 策略管理
elif st.session_state.get('页面') == "策略管理":
    加载器 = 策略加载器()
    所有策略 = 加载器.加载所有策略()
    for 类目, 策略组 in 所有策略.items():
        st.write(f"📁 {类目}")
        for 名 in 策略组.keys():
            st.write(f"   - {名}")

# 持仓
elif st.session_state.get('页面') == "持仓":
    engine = st.session_state.引擎
    if engine.持仓:
        st.dataframe(pd.DataFrame(engine.持仓).T)
    else:
        st.info("暂无持仓")