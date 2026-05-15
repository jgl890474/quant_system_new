# -*- coding: utf-8 -*-
from .首页 import 显示 as 显示首页
# from .策略中心 import 显示 as 显示策略中心  # 暂时注释掉
from .AI交易 import 显示 as 显示AI交易
from .持仓管理 import 显示 as 显示持仓管理
from .资金曲线 import 显示 as 显示资金曲线
from .回测 import 显示 as 显示回测
from .交易记录 import 显示 as 显示交易记录

# 临时定义一个假的策略中心显示函数
def 显示策略中心(引擎, 策略加载器=None, AI引擎=None):
    import streamlit as st
    st.markdown("### 🎛️ 策略管理")
    st.info("策略中心模块正在修复中，请稍后再试")
