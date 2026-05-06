# -*- coding: utf-8 -*-
import streamlit as st

def 显示弹窗(标题, 内容, 键名="弹窗"):
    """通用弹窗组件"""
    if st.session_state.get(键名, False):
        st.markdown(f"""
        <div style="position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); 
                    background-color:#1e1e2e; border-radius:16px; padding:24px; 
                    border:1px solid #00d2ff; z-index:1000; width:400px;">
            <h4 style="color:#00d2ff">{标题}</h4>
            <p style="white-space:pre-line">{内容}</p>
            <button onclick="location.reload()" style="background:#00d2ff; color:#000; 
                    border:none; padding:8px 20px; border-radius:20px; cursor:pointer; width:100%">关闭</button>
        </div>
        """, unsafe_allow_html=True)
        if st.button("关闭弹窗", key=f"关闭_{键名}"):
            st.session_state[键名] = False
            st.rerun()
