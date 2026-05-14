# -*- coding: utf-8 -*-
import streamlit as st

def 显示(引擎, 策略加载器=None, AI引擎=None):
    st.subheader("🤖 AI 交易")
    st.success("AI交易模块已加载成功！")
    st.write(f"可用资金: ¥{引擎.获取可用资金():,.2f}")
