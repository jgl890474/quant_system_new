# -*- coding: utf-8 -*-
import streamlit as st

def 显示指标卡片(标题, 数值, 变化=None):
    col = st.columns(1)[0]
    col.metric(标题, 数值, delta=变化)
